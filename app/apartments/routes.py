# Routen für den Apartments Blueprint
from flask import render_template, redirect, url_for, flash, request, abort, session
from . import apartments_bp # Importiere den Blueprint aus __init__.py
from app import db
from app.models import Apartment, Building
from .forms import ApartmentForm, OccupancyPeriodForm # Jetzt benötigt
from app.models import OccupancyPeriod

# Hier kommen die Routen-Definitionen hin... 

@apartments_bp.route('/')
def list_apartments():
    """Zeigt eine Liste aller Wohnungen."""
    q = Apartment.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.filter(Apartment.building_id == bid)
    apartments = q.order_by(Apartment.number).all()
    return render_template('apartments/list.html', apartments=apartments, title='Wohnungsübersicht')

@apartments_bp.route('/new', methods=['GET', 'POST'])
def create_apartment():
    """Erstellt eine neue Wohnung."""
    form = ApartmentForm()
    # Gebäude-Auswahl befüllen
    form.building_id.choices = [(b.id, b.name) for b in Building.query.order_by(Building.name)]
    if form.validate_on_submit():
        existing_apartment = Apartment.query.filter_by(number=form.number.data).first()
        if existing_apartment:
            flash(f'Eine Wohnung mit der Nummer "{form.number.data}" existiert bereits.', 'warning')
            return render_template('apartments/form.html', form=form, title='Neue Wohnung anlegen')

        apartment = Apartment(
            number=form.number.data,
            address=form.address.data,
            size_sqm=form.size_sqm.data,
            building_id=form.building_id.data if form.building_id.data else None
        )
        db.session.add(apartment)
        
        try:
            db.session.commit()
            flash(f'Wohnung "{apartment.number}" erfolgreich angelegt.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen der Wohnung: {e}', 'danger')
            return render_template('apartments/form.html', form=form, title='Neue Wohnung anlegen')
        
        return redirect(url_for('apartments.list_apartments'))
    
    return render_template('apartments/form.html', form=form, title='Neue Wohnung anlegen')

@apartments_bp.route('/<int:apartment_id>/edit', methods=['GET', 'POST'])
def edit_apartment(apartment_id):
    """Bearbeitet eine bestehende Wohnung."""
    apartment = db.session.get(Apartment, apartment_id) or abort(404)
    form = ApartmentForm(obj=apartment)
    form.building_id.choices = [(b.id, b.name) for b in Building.query.order_by(Building.name)]

    if form.validate_on_submit():
        new_number = form.number.data
        if new_number != apartment.number:
            existing_apartment = Apartment.query.filter(
                Apartment.id != apartment_id,
                Apartment.number == new_number
            ).first()
            if existing_apartment:
                flash(f'Eine andere Wohnung mit der Nummer "{new_number}" existiert bereits.', 'warning')
                return render_template('apartments/form.html', form=form, title='Wohnung bearbeiten', instance_id=apartment_id)
        
        try:
            form.populate_obj(apartment)
            db.session.commit()
            flash(f'Wohnung "{apartment.number}" erfolgreich aktualisiert.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren der Wohnung: {e}', 'danger')
            return render_template('apartments/form.html', form=form, title='Wohnung bearbeiten', instance_id=apartment_id)
        
        return redirect(url_for('apartments.list_apartments'))

    return render_template('apartments/form.html', form=form, title='Wohnung bearbeiten', instance_id=apartment_id) 


# OccupancyPeriod UI unter Apartments
@apartments_bp.route('/<int:apartment_id>/occupancy/')
def list_occupancy(apartment_id):
    apartment = db.session.get(Apartment, apartment_id) or abort(404)
    periods = OccupancyPeriod.query.filter_by(apartment_id=apartment_id).order_by(OccupancyPeriod.start_date).all()
    return render_template('apartments/occupancy_list.html', apartment=apartment, periods=periods, title='Belegungszeiträume')


@apartments_bp.route('/<int:apartment_id>/occupancy/new', methods=['GET', 'POST'])
def create_occupancy(apartment_id):
    apartment = db.session.get(Apartment, apartment_id) or abort(404)
    form = OccupancyPeriodForm()
    if form.validate_on_submit():
        period = OccupancyPeriod(
            apartment_id=apartment.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            number_of_occupants=form.number_of_occupants.data
        )
        try:
            db.session.add(period)
            db.session.commit()
            flash('Belegungszeitraum erfolgreich angelegt.', 'success')
            return redirect(url_for('apartments.list_occupancy', apartment_id=apartment.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen des Belegungszeitraums: {e}', 'danger')
    return render_template('apartments/occupancy_form.html', form=form, apartment=apartment, title='Neuer Belegungszeitraum')


@apartments_bp.route('/<int:apartment_id>/occupancy/<int:period_id>/edit', methods=['GET', 'POST'])
def edit_occupancy(apartment_id, period_id):
    apartment = db.session.get(Apartment, apartment_id) or abort(404)
    period = db.session.get(OccupancyPeriod, period_id) or abort(404)
    form = OccupancyPeriodForm(obj=period)
    if form.validate_on_submit():
        try:
            period.start_date = form.start_date.data
            period.end_date = form.end_date.data
            period.number_of_occupants = form.number_of_occupants.data
            db.session.commit()
            flash('Belegungszeitraum erfolgreich aktualisiert.', 'success')
            return redirect(url_for('apartments.list_occupancy', apartment_id=apartment.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren des Belegungszeitraums: {e}', 'danger')
    return render_template('apartments/occupancy_form.html', form=form, apartment=apartment, title='Belegungszeitraum bearbeiten')