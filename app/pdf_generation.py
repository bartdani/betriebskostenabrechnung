import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
from flask import current_app
from sqlalchemy import func

from app import db
from app.models import Contract, Tenant, Apartment, CostType, ApartmentShare, ConsumptionData, OccupancyPeriod
from app.calculations import (
    calculate_share_allocation,
    calculate_consumption_allocation,
    calculate_person_day_allocation,
    calculate_heating_allocation,
    calculate_direct_allocation,
)
# TODO: Import calculate_combined_allocation if needed

def _format_euro(amount: float) -> str:
    # Deutsche Formatierung: Tausenderpunkt, Dezimalkomma
    s = f"{amount:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def _safe_config_get(key: str, default_value):
    try:
        value = current_app.config.get(key)
        return value if value is not None and value != "" else default_value
    except Exception:
        return default_value


def _resolve_logo_path(configured_path):
    try:
        if configured_path:
            if os.path.isabs(configured_path):
                return configured_path
            # relativ zum App-Root
            return os.path.join(current_app.root_path, configured_path)
    except Exception:
        pass
    # Fallback: statisches Logo neben diesem Modul
    return os.path.join(os.path.dirname(__file__), 'static', 'logo.png')


def _page_decorator(canvas, doc):
    canvas.saveState()
    # Header mit optionalem Logo und Adresse
    header_y = A4[1] - 1.5*cm
    configured_logo = _safe_config_get('PDF_LOGO_PATH', None)
    logo_path = _resolve_logo_path(configured_logo)
    try:
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            canvas.drawImage(logo, 2*cm, header_y - 1.0*cm, width=2.5*cm, height=1.0*cm, preserveAspectRatio=True, mask='auto')
    except Exception:
        # Logo ist optional – bei Fehler einfach ohne Logo rendern
        pass

    header_name = _safe_config_get('PDF_HEADER_NAME', 'Vermieter GmbH')
    header_address = _safe_config_get('PDF_HEADER_ADDRESS', 'Musterstraße 1, 12345 Musterstadt')
    header_contact = _safe_config_get('PDF_HEADER_CONTACT', 'E-Mail: info@vermieter.example | Tel: 01234 567890')

    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawRightString(A4[0] - 2*cm, header_y, header_name)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(A4[0] - 2*cm, header_y - 0.4*cm, header_address)
    canvas.drawRightString(A4[0] - 2*cm, header_y - 0.8*cm, header_contact)

    # Footer mit Seitenzahl
    footer_text = f"Seite {doc.page}"
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, footer_text)
    canvas.restoreState()


def generate_utility_statement_pdf(contract_id, period_start, period_end, cost_items):
    """
    Generiert eine Betriebskostenabrechnung als PDF für einen bestimmten Vertrag und Zeitraum.

    Args:
        contract_id (int): Die ID des Vertrags, für den die Abrechnung erstellt wird.
        period_start (date): Startdatum des Abrechnungszeitraums.
        period_end (date): Enddatum des Abrechnungszeitraums.
        cost_items (list): Eine Liste von Dictionaries, die die abzurechnenden Gesamtkosten enthalten.
                           Format: [{'cost_type_id': int, 'total_cost': float}, ...]

    Returns:
        bytes: Der Inhalt der generierten PDF-Datei als Byte-Stream, oder None bei Fehlern.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # --- 1. Daten abrufen --- 
    contract = db.session.get(Contract, contract_id)
    if not contract:
        print(f"Error: Contract with ID {contract_id} not found.")
        return None
    
    tenant = contract.tenant
    apartment = contract.apartment
    if not tenant or not apartment:
        print(f"Error: Tenant or Apartment not found for Contract ID {contract_id}.")
        return None

    # Platzhalter für Vermieteradresse
    landlord_address = _safe_config_get(
        'PDF_LANDLORD_ADDRESS',
        "Vermieter GmbH\nMusterstraße 1\n12345 Musterstadt",
    )

    # --- 2. PDF-Struktur aufbauen --- 
    story.append(Paragraph("Betriebs- und Heizkostenabrechnung", styles['h1']))
    story.append(Spacer(1, 0.5*cm))

    # Adressfelder
    # TODO: Echte Adressdaten verwenden, wenn verfügbar
    address_style = styles['Normal']
    address_style.alignment = TA_LEFT
    story.append(Paragraph(landlord_address.replace('\n', '<br/>'), address_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(tenant.name, address_style))
    if tenant.contact_info: # Annahme: contact_info enthält Adresse oder ist Teil davon
         story.append(Paragraph(tenant.contact_info.replace('\n', '<br/>'), address_style))
    story.append(Paragraph(f"Wohnung {apartment.number}", address_style))
    story.append(Paragraph(f"Vertrag #{contract.id}", address_style))
    story.append(Spacer(1, 1*cm))

    # Rechte Seite: Datum
    date_style = styles['Normal']
    date_style.alignment = TA_RIGHT
    story.append(Paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}", date_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(f"<b>Abrechnungszeitraum: {period_start.strftime('%d.%m.%Y')} - {period_end.strftime('%d.%m.%Y')}</b>", styles['Normal']))
    story.append(Spacer(1, 1*cm))

    # --- 3. Kostenpositionen verarbeiten und Tabelle erstellen --- 
    table_data = [['Kostenart', 'Gesamtkosten', 'Verteilschlüssel', 'Ihr Anteil']]
    total_tenant_cost = 0.0

    for item in cost_items:
        # Unterstützt Modi:
        # 1) Klassisch pro CostType: {cost_type_id, total_cost}
        # 2) Heizpaket: {'type': 'heating', 'total_cost', 'hot_water_percentage', 'heating_consumption_cost_type_id', 'hot_water_consumption_cost_type_id'}
        # 3) Direkte Kosten aus Rechnungen: {'type': 'direct'} (Gesamtsumme wird aus DB ermittelt)
        if item.get('type') == 'heating':
            total_cost = float(item.get('total_cost', 0.0))
            hot_water_percentage = float(item.get('hot_water_percentage', 0.0))
            heat_ct = int(item.get('heating_consumption_cost_type_id'))
            hot_ct = int(item.get('hot_water_consumption_cost_type_id'))

            allocation_result = calculate_heating_allocation(
                total_cost=total_cost,
                hot_water_percentage=hot_water_percentage,
                heating_consumption_cost_type_id=heat_ct,
                hot_water_consumption_cost_type_id=hot_ct,
                period_start=period_start,
                period_end=period_end,
            )
            tenant_share_cost = allocation_result.get(apartment.id, 0.0)
            key_description = f"Heizung/Warmwasser Split ({hot_water_percentage:.0f}% | {100-hot_water_percentage:.0f}%) verbrauchsbasiert"
            name = "Heiz-/Warmwasserkosten"
            total_for_row = total_cost
        elif item.get('type') == 'direct':
            # Direkte Kosten aus Rechnungen im Zeitraum ermitteln
            allocation_result = calculate_direct_allocation(period_start=period_start, period_end=period_end)
            tenant_share_cost = allocation_result.get(apartment.id, 0.0)
            total_for_row = sum(allocation_result.values())
            name = "Direkt zugeordnete Kosten"
            key_description = "Direkt zugeordnet (Rechnungen im Zeitraum)"
        else:
            cost_type_id = item.get('cost_type_id')
            total_cost = item.get('total_cost', 0.0)

            cost_type = db.session.get(CostType, cost_type_id)
            if not cost_type:
                print(f"Warning: CostType ID {cost_type_id} not found. Skipping item.")
                table_data.append([f"Unbekannt (ID: {cost_type_id})", f"{total_cost:.2f} €", "Fehler", "N/A"])
                continue

            allocation_result = {}
            key_description = "Fehler bei Berechnung"
            tenant_share_cost = 0.0
            name = cost_type.name
            total_for_row = total_cost

            try:
                if cost_type.type == 'share':
                    allocation_result = calculate_share_allocation(cost_type_id, total_cost)
                    share_entry = ApartmentShare.query.filter_by(apartment_id=apartment.id, cost_type_id=cost_type.id).first()
                    share_value = share_entry.value if share_entry else 'N/A'
                    key_description = f"Anteil ({cost_type.unit}: {share_value})"
                elif cost_type.type == 'consumption':
                    allocation_result = calculate_consumption_allocation(cost_type_id, total_cost, period_start, period_end)
                    total_apt_consumption = db.session.query(func.sum(ConsumptionData.value)).filter(
                        ConsumptionData.apartment_id == apartment.id,
                        ConsumptionData.cost_type_id == cost_type.id,
                        ConsumptionData.date >= period_start,
                        ConsumptionData.date <= period_end
                    ).scalar() or 0.0
                    key_description = f"Verbrauch ({cost_type.unit}: {total_apt_consumption:.2f})"
                elif cost_type.type == 'person_days':
                    allocation_result = calculate_person_day_allocation(cost_type_id, total_cost, period_start, period_end)
                    from app.calculations import calculate_person_days
                    apt_person_days = calculate_person_days(apartment.id, period_start, period_end)
                    key_description = f"Personentage: {apt_person_days}"
                else:
                    print(f"Warning: Unknown CostType type '{cost_type.type}' for ID {cost_type_id}. Cannot allocate.")
                    key_description = f"Unbek. Typ: {cost_type.type}"

                tenant_share_cost = allocation_result.get(apartment.id, 0.0)
            except Exception as e:
                print(f"Error calculating allocation for CostType ID {cost_type_id}: {e}")
                key_description = "Berechnungsfehler"
                tenant_share_cost = 0.0

        table_data.append([
            Paragraph(name, styles['Normal']), 
            _format_euro(total_for_row), 
            Paragraph(key_description, styles['Normal']), 
            _format_euro(tenant_share_cost)
        ])
        total_tenant_cost += tenant_share_cost

    # Tabelle nur hinzufügen, wenn Daten vorhanden sind (Header + mind. 1 Zeile)
    if len(table_data) > 1:
        # Summary-Zeile anhängen
        table_data.append([
            Paragraph('<b>Summe</b>', styles['Normal']),
            '',
            '',
            Paragraph(f"<b>{_format_euro(total_tenant_cost)}</b>", styles['Normal'])
        ])

        table = Table(table_data, colWidths=[5*cm, 3*cm, 5*cm, 3*cm]) # Spaltenbreiten angepasst
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertikal zentrieren
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            # ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'), # Gesamtkosten rechts
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Anteil rechts
            ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Schlüssel links
            ('FONTSIZE', (0, 1), (-1, -1), 9), # Kleinere Schrift für Daten
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            # Summary styling (letzte Zeile)
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.whitesmoke),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
    else:
        story.append(Paragraph("Keine Kostenpositionen zum Anzeigen vorhanden.", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

    # --- 4. Zusammenfassung --- 
    summary_style = styles['h3']
    summary_style.alignment = TA_RIGHT
    story.append(Paragraph(f"Gesamtkosten für Sie: {_format_euro(total_tenant_cost)}", summary_style))

    # --- 5. PDF generieren --- 
    try:
        doc.build(story, onFirstPage=_page_decorator, onLaterPages=_page_decorator)
    except Exception as e:
        print(f"Error building PDF: {e}")
        return None

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data 