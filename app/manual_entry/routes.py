from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Apartment, CostType, ConsumptionData
from app.forms import ManualConsumptionForm
from datetime import datetime

manual_entry_bp = Blueprint('manual_entry', 
                            __name__, 
                            template_folder='../templates/manual_entry',
                            url_prefix='/manual_entry')

@manual_entry_bp.route('/consumption', methods=['GET', 'POST'])
def consumption_entry():
    form = ManualConsumptionForm()

    # Dynamisches Befüllen der Auswahlfelder
    form.apartment_id.choices = [(apt.id, apt.number) for apt in Apartment.query.order_by(Apartment.number)]
    form.cost_type_id.choices = [
        (ct.id, f"{ct.name} ({ct.unit})") 
        for ct in CostType.query.filter_by(type='consumption').order_by(CostType.name)
    ]

    if form.validate_on_submit():
        # Datum von String zu datetime-Objekt konvertieren (wenn nötig, WTForms macht das oft schon)
        # date_obj = datetime.strptime(form.date.data, '%Y-%m-%d') # Annahme: WTForms liefert Date-Objekt
        date_obj = form.date.data

        new_consumption = ConsumptionData(
            apartment_id=form.apartment_id.data,
            cost_type_id=form.cost_type_id.data,
            date=datetime(date_obj.year, date_obj.month, date_obj.day), # Nur Datum, keine Zeit
            value=form.value.data,
            entry_type='manual' # WICHTIG: Herkunft speichern
        )
        try:
            db.session.add(new_consumption)
            db.session.commit()
            flash('Verbrauchsdaten erfolgreich manuell hinzugefügt.', 'success')
            # Formular zurücksetzen oder weiterleiten?
            # Hier: Weiterleiten zur gleichen Seite (zeigt leeres Formular)
            return redirect(url_for('manual_entry.consumption_entry')) 
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Speichern: {str(e)}', 'danger')
    
    # Bei GET-Request oder wenn Validierung fehlschlägt:
    return render_template('consumption_entry.html', title='Manuelle Verbrauchserfassung', form=form) 