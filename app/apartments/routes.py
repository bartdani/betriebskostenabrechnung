# Routen für den Apartments Blueprint
from flask import render_template, redirect, url_for, flash, request, abort
from . import apartments_bp # Importiere den Blueprint aus __init__.py
from app import db
from app.models import Apartment
from .forms import ApartmentForm # Jetzt benötigt

# Hier kommen die Routen-Definitionen hin... 

@apartments_bp.route('/')
def list_apartments():
    """Zeigt eine Liste aller Wohnungen."""
    apartments = Apartment.query.order_by(Apartment.number).all()
    return render_template('apartments/list.html', apartments=apartments, title='Wohnungsübersicht')

@apartments_bp.route('/new', methods=['GET', 'POST'])
def create_apartment():
    """Erstellt eine neue Wohnung."""
    form = ApartmentForm()
    if form.validate_on_submit():
        existing_apartment = Apartment.query.filter_by(number=form.number.data).first()
        if existing_apartment:
            flash(f'Eine Wohnung mit der Nummer "{form.number.data}" existiert bereits.', 'warning')
            return render_template('apartments/form.html', form=form, title='Neue Wohnung anlegen')

        apartment = Apartment(
            number=form.number.data,
            address=form.address.data,
            size_sqm=form.size_sqm.data
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