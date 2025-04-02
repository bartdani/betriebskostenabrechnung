from flask import render_template, flash, redirect, url_for, abort
from app import db
from app.tenants import bp_tenants
from app.tenants.forms import TenantForm
from app.models import Tenant

@bp_tenants.route('/')
def list_tenants():
    tenants = Tenant.query.all()
    return render_template('tenants/list.html', tenants=tenants)

@bp_tenants.route('/new', methods=['GET', 'POST'])
def create_tenant():
    form = TenantForm()
    if form.validate_on_submit():
        tenant = Tenant(
            name=form.name.data,
            contact_info=form.contact_info.data
        )
        try:
            db.session.add(tenant)
            db.session.commit()
            flash(f'Mieter "{tenant.name}" wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('tenants.list_tenants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Erstellen des Mieters: {e}', 'danger')
    return render_template('tenants/form.html', form=form, title='Neuer Mieter')

@bp_tenants.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_tenant(id):
    tenant = db.session.get(Tenant, id) or abort(404)
    form = TenantForm(obj=tenant)
    if form.validate_on_submit():
        try:
            tenant.name = form.name.data
            tenant.contact_info = form.contact_info.data
            db.session.commit()
            flash(f'Mieter "{tenant.name}" wurde erfolgreich aktualisiert.', 'success')
            return redirect(url_for('tenants.list_tenants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren des Mieters: {e}', 'danger')
    return render_template('tenants/form.html', form=form, title='Mieter bearbeiten')