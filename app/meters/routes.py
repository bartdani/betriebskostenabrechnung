from flask import render_template, redirect, url_for, flash, abort, session
from app import db
from app.models import Meter, Apartment, ConsumptionData, CostType
from . import meters_bp
from .forms import MeterForm, MeterReadingForm
from datetime import datetime


def _populate_apartment_choices(form: MeterForm):
    q = Apartment.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.filter(Apartment.building_id == bid)
    apartments = q.order_by(Apartment.number).all()
    form.apartment_id.choices = [(a.id, a.number) for a in apartments]


@meters_bp.route('/')
def list_meters():
    q = Meter.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.join(Apartment, Meter.apartment_id == Apartment.id).filter(Apartment.building_id == bid)
    meters = q.order_by(Meter.serial_number).all()
    return render_template('meters/list.html', meters=meters, title='Zählerübersicht')


@meters_bp.route('/new', methods=['GET', 'POST'])
def create_meter():
    form = MeterForm()
    _populate_apartment_choices(form)
    if form.validate_on_submit():
        existing = Meter.query.filter_by(serial_number=form.serial_number.data).first()
        if existing:
            flash(f'Ein Zähler mit der Seriennummer "{form.serial_number.data}" existiert bereits.', 'warning')
            return render_template('meters/form.html', form=form, title='Neuer Zähler')

        meter = Meter(
            apartment_id=form.apartment_id.data,
            meter_type=form.meter_type.data,
            serial_number=form.serial_number.data,
            unit=form.unit.data,
        )
        try:
            db.session.add(meter)
            db.session.commit()
            flash(f'Zähler "{meter.serial_number}" erfolgreich angelegt.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen des Zählers: {e}', 'danger')
            return render_template('meters/form.html', form=form, title='Neuer Zähler')

        return redirect(url_for('meters.list_meters'))

    return render_template('meters/form.html', form=form, title='Neuer Zähler')


@meters_bp.route('/<int:meter_id>/edit', methods=['GET', 'POST'])
def edit_meter(meter_id: int):
    meter = db.session.get(Meter, meter_id) or abort(404)
    form = MeterForm(obj=meter)
    _populate_apartment_choices(form)
    form.instance_id.data = meter.id

    if form.validate_on_submit():
        new_serial = form.serial_number.data
        if new_serial != meter.serial_number:
            existing = Meter.query.filter(Meter.id != meter_id, Meter.serial_number == new_serial).first()
            if existing:
                flash(f'Ein anderer Zähler mit der Seriennummer "{new_serial}" existiert bereits.', 'warning')
                return render_template('meters/form.html', form=form, title='Zähler bearbeiten', instance_id=meter_id)

        try:
            meter.apartment_id = form.apartment_id.data
            meter.meter_type = form.meter_type.data
            meter.serial_number = form.serial_number.data
            meter.unit = form.unit.data
            db.session.commit()
            flash(f'Zähler "{meter.serial_number}" erfolgreich aktualisiert.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren des Zählers: {e}', 'danger')
            return render_template('meters/form.html', form=form, title='Zähler bearbeiten', instance_id=meter_id)

        return redirect(url_for('meters.list_meters'))

    return render_template('meters/form.html', form=form, title='Zähler bearbeiten', instance_id=meter_id)


@meters_bp.route('/readings/new', methods=['GET', 'POST'])
def create_meter_reading():
    form = MeterReadingForm()
    meters = Meter.query.order_by(Meter.serial_number).all()
    form.meter_id.choices = [(m.id, f"{m.serial_number} ({m.meter_type}) - {m.apartment.number}") for m in meters]

    if form.validate_on_submit():
        meter = db.session.get(Meter, form.meter_id.data)
        if not meter:
            abort(404)
        # Kostenart ableiten aus Meter-Typ? Annahme: vorhandene CostTypes passend benannt
        # Minimal: User erfasst direkt Wert, wir speichern als ConsumptionData mit cost_type via Mapping.
        cost_type = CostType.query.filter_by(unit=meter.unit, type='consumption').first()
        if not cost_type:
            # Fallback: erste consumption-Kostenart
            cost_type = CostType.query.filter_by(type='consumption').first()
        if not cost_type:
            # Als letzte Option eine generische Verbrauchs-Kostenart erzeugen
            cost_type = CostType(name=f"{meter.meter_type} (auto)", unit=meter.unit, type='consumption')
            db.session.add(cost_type)
            db.session.flush()
        date_obj = form.date.data
        new_entry = ConsumptionData(
            apartment_id=meter.apartment_id,
            cost_type_id=cost_type.id if cost_type else None,
            date=datetime(date_obj.year, date_obj.month, date_obj.day),
            value=form.value.data,
            entry_type='manual'
        )
        try:
            db.session.add(new_entry)
            db.session.commit()
            flash('Zählerstand wurde gespeichert.', 'success')
            return redirect(url_for('meters.list_meters'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Speichern: {e}', 'danger')

    return render_template('meters/reading_form.html', form=form, title='Zählerstand erfassen')


@meters_bp.route('/readings/bulk', methods=['GET', 'POST'])
def create_meter_readings_bulk():
    # Auswahl der Wohnung
    apartments = Apartment.query.order_by(Apartment.number).all()
    selected_apartment_id = request.args.get('apartment_id') if 'request' in globals() else None
    try:
        from flask import request
        selected_apartment_id = request.values.get('apartment_id') or selected_apartment_id
    except Exception:
        pass

    selected_apartment = None
    meters = []

    if selected_apartment_id:
        try:
            selected_apartment = db.session.get(Apartment, int(selected_apartment_id))
        except Exception:
            selected_apartment = None
    if selected_apartment:
        meters = Meter.query.filter_by(apartment_id=selected_apartment.id).order_by(Meter.serial_number).all()

    if 'request' in globals():
        from flask import request, redirect, url_for, flash, render_template
        if request.method == 'POST' and selected_apartment:
            date_str = request.form.get('date')
            try:
                y, m, d = map(int, date_str.split('-'))
                date_obj = datetime(y, m, d)
            except Exception:
                flash('Ungültiges Datum im Bulk-Formular.', 'danger')
                return render_template('meters/reading_bulk.html', apartments=apartments, selected_apartment=selected_apartment, meters=meters, title='Zählerstände (Bulk)')

            created = 0
            for meter in meters:
                val = request.form.get(f'value_{meter.id}')
                if val is None or str(val).strip() == '':
                    continue
                try:
                    fval = float(val)
                except ValueError:
                    continue

                cost_type = CostType.query.filter_by(unit=meter.unit, type='consumption').first()
                if not cost_type:
                    cost_type = CostType.query.filter_by(type='consumption').first()
                if not cost_type:
                    cost_type = CostType(name=f"{meter.meter_type} (auto)", unit=meter.unit, type='consumption')
                    db.session.add(cost_type)
                    db.session.flush()

                entry = ConsumptionData(
                    apartment_id=meter.apartment_id,
                    cost_type_id=cost_type.id,
                    date=date_obj,
                    value=fval,
                    entry_type='manual'
                )
                db.session.add(entry)
                created += 1

            try:
                db.session.commit()
                flash(f'{created} Zählerstände gespeichert.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Fehler beim Speichern: {e}', 'danger')

            return redirect(url_for('meters.create_meter_readings_bulk', apartment_id=selected_apartment.id))

        return render_template('meters/reading_bulk.html', apartments=apartments, selected_apartment=selected_apartment, meters=meters, title='Zählerstände (Bulk)')

