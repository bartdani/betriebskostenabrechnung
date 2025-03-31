import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from app import db
from app.models import Contract, Tenant, Apartment, CostType, ApartmentShare, ConsumptionData, OccupancyPeriod
from app.calculations import calculate_share_allocation, calculate_consumption_allocation, calculate_person_day_allocation
# TODO: Import calculate_combined_allocation if needed

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
    landlord_address = "Vermieter GmbH\nMusterstraße 1\n12345 Musterstadt"

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

        try:
            if cost_type.type == 'share':
                allocation_result = calculate_share_allocation(cost_type_id, total_cost)
                # Schlüsselinfo holen (angenommen, es gibt einen Eintrag)
                share_entry = ApartmentShare.query.filter_by(apartment_id=apartment.id, cost_type_id=cost_type.id).first()
                share_value = share_entry.value if share_entry else 'N/A'
                key_description = f"Anteil ({cost_type.unit}: {share_value})"
            elif cost_type.type == 'consumption':
                allocation_result = calculate_consumption_allocation(cost_type_id, total_cost, period_start, period_end)
                # Schlüsselinfo holen (Gesamtverbrauch der Wohnung im Zeitraum)
                total_apt_consumption = db.session.query(func.sum(ConsumptionData.value)).filter(
                    ConsumptionData.apartment_id == apartment.id,
                    ConsumptionData.cost_type_id == cost_type.id,
                    ConsumptionData.date >= period_start,
                    ConsumptionData.date <= period_end
                ).scalar() or 0.0
                key_description = f"Verbrauch ({cost_type.unit}: {total_apt_consumption:.2f})"
            # TODO: Add handling for 'person_days' and 'combined' types if needed
            elif cost_type.type == 'person_days': # Annahme, dass 'person_days' ein Typ ist
                 # Hier muss calculate_person_day_allocation verwendet werden
                 # Die Funktion calculate_person_day_allocation ist noch nicht definiert/importiert?
                 # Nehmen wir an, sie existiert und funktioniert ähnlich:
                 allocation_result = calculate_person_day_allocation(cost_type_id, total_cost, period_start, period_end)
                 # Schlüsselinfo holen (Personentage der Wohnung)
                 from app.calculations import calculate_person_days # Importieren
                 apt_person_days = calculate_person_days(apartment.id, period_start, period_end)
                 key_description = f"Personentage: {apt_person_days}"
            else:
                print(f"Warning: Unknown CostType type '{cost_type.type}' for ID {cost_type_id}. Cannot allocate.")
                key_description = f"Unbek. Typ: {cost_type.type}"

            # Anteil des Mieters aus dem Ergebnis holen
            tenant_share_cost = allocation_result.get(apartment.id, 0.0)

        except Exception as e:
            print(f"Error calculating allocation for CostType ID {cost_type_id}: {e}")
            # Fehler im Schlüssel und Anteil vermerken
            key_description = "Berechnungsfehler"
            tenant_share_cost = 0.0 # Sicherstellen, dass es ein Float ist

        table_data.append([
            Paragraph(cost_type.name, styles['Normal']), 
            f"{total_cost:.2f} €", 
            Paragraph(key_description, styles['Normal']), 
            f"{tenant_share_cost:.2f} €"
        ])
        total_tenant_cost += tenant_share_cost

    # Tabelle nur hinzufügen, wenn Daten vorhanden sind (Header + mind. 1 Zeile)
    if len(table_data) > 1:
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
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
    else:
        story.append(Paragraph("Keine Kostenpositionen zum Anzeigen vorhanden.", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

    # --- 4. Zusammenfassung --- 
    summary_style = styles['h3']
    summary_style.alignment = TA_RIGHT
    story.append(Paragraph(f"Gesamtkosten für Sie: {total_tenant_cost:.2f} €", summary_style))

    # --- 5. PDF generieren --- 
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error building PDF: {e}")
        return None

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data 