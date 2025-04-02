from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models import CostType
from app.cost_types import cost_types_bp
from app.cost_types.forms import CostTypeForm # Formular importieren
from sqlalchemy import func

# Route zum Anzeigen aller Kostenarten
@cost_types_bp.route('/')
def index():
    """Zeigt eine Liste aller benutzerdefinierten Kostenarten."""
    # TODO: Später filtern, um nur "benutzerdefinierte" anzuzeigen?
    # Vorerst alle anzeigen.
    cost_types = CostType.query.order_by(CostType.name).all()
    return render_template('cost_types/list.html', title='Kostenarten verwalten', cost_types=cost_types)

# Route zum Erstellen einer neuen Kostenart
@cost_types_bp.route('/new', methods=['GET', 'POST'])
def create_cost_type():
    """Erstellt eine neue benutzerdefinierte Kostenart."""
    form = CostTypeForm()
    if form.validate_on_submit():
        # Prüfen, ob der Name bereits existiert
        existing_cost_type = CostType.query.filter(func.lower(CostType.name) == func.lower(form.name.data)).first()
        if existing_cost_type:
            flash(f'Eine Kostenart mit dem Namen "{form.name.data}" existiert bereits.', 'warning')
            return render_template('cost_types/form.html', title='Neue Kostenart erstellen', form=form)
        
        new_cost_type = CostType(
            name=form.name.data,
            unit=form.unit.data,
            type=form.type.data
        )
        db.session.add(new_cost_type)
        try:
            db.session.commit()
            flash(f'Kostenart "{new_cost_type.name}" erfolgreich erstellt.', 'success')
            return redirect(url_for('cost_types.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Erstellen der Kostenart: {e}', 'danger')
            
    # GET Request oder Validierungsfehler
    return render_template('cost_types/form.html', title='Neue Kostenart erstellen', form=form)

# Route zum Bearbeiten einer Kostenart
@cost_types_bp.route('/<int:cost_type_id>/edit', methods=['GET', 'POST'])
def edit_cost_type(cost_type_id):
    """Bearbeitet eine vorhandene Kostenart."""
    cost_type = db.session.get(CostType, cost_type_id)
    if not cost_type:
        flash('Kostenart nicht gefunden.', 'danger')
        return redirect(url_for('cost_types.index'))

    form = CostTypeForm(obj=cost_type) # Formular mit vorhandenen Daten befüllen

    if form.validate_on_submit():
        # Prüfen, ob der neue Name bereits von einer *anderen* Kostenart verwendet wird
        new_name_lower = form.name.data.lower()
        existing_cost_type = CostType.query.filter(
            func.lower(CostType.name) == new_name_lower,
            CostType.id != cost_type_id # Ignoriere die aktuelle Kostenart
        ).first()
        if existing_cost_type:
            flash(f'Eine andere Kostenart mit dem Namen "{form.name.data}" existiert bereits.', 'warning')
            return render_template('cost_types/form.html', title=f'Kostenart bearbeiten: {cost_type.name}', form=form)
        
        # Daten aktualisieren
        cost_type.name = form.name.data
        cost_type.unit = form.unit.data
        cost_type.type = form.type.data
        try:
            db.session.commit()
            flash(f'Kostenart "{cost_type.name}" erfolgreich aktualisiert.', 'success')
            return redirect(url_for('cost_types.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren der Kostenart: {e}', 'danger')

    # GET Request oder Validierungsfehler
    return render_template('cost_types/form.html', title=f'Kostenart bearbeiten: {cost_type.name}', form=form)

# Route zum Löschen einer Kostenart
@cost_types_bp.route('/<int:cost_type_id>/delete', methods=['POST'])
def delete_cost_type(cost_type_id):
    """Löscht eine Kostenart."""
    cost_type = db.session.get(CostType, cost_type_id)
    if not cost_type:
        flash('Kostenart nicht gefunden.', 'danger')
        return redirect(url_for('cost_types.index'))

    try:
        # Hier könnte man prüfen, ob die Kostenart noch verwendet wird (z.B. in allocations, consumption_data, apartment_shares)
        # Wenn ja, Löschen verhindern oder kaskadierendes Löschen implementieren (Vorsicht!)
        # Vorerst: Direktes Löschen erlauben.
        cost_type_name = cost_type.name # Namen merken für Flash-Nachricht
        db.session.delete(cost_type)
        db.session.commit()
        flash(f'Kostenart "{cost_type_name}" erfolgreich gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Löschen der Kostenart: {e}. Wird sie noch verwendet?', 'danger')

    return redirect(url_for('cost_types.index')) 