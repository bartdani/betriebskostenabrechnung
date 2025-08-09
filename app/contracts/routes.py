from flask import render_template, redirect, url_for, flash, abort, session
from app import db
from app.models import Contract, Tenant, Apartment
from . import contracts_bp
from .forms import ContractForm


def _populate_choices(form: ContractForm):
    form.tenant_id.choices = [(t.id, t.name) for t in Tenant.query.order_by(Tenant.name)]
    q = Apartment.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.filter(Apartment.building_id == bid)
    form.apartment_id.choices = [(a.id, a.number) for a in q.order_by(Apartment.number)]


@contracts_bp.route('/')
def list_contracts():
    q = Contract.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.join(Apartment, Contract.apartment_id == Apartment.id).filter(Apartment.building_id == bid)
    contracts = q.order_by(Contract.start_date.desc()).all()
    return render_template('contracts/list.html', contracts=contracts, title='Vertragsübersicht')


@contracts_bp.route('/new', methods=['GET', 'POST'])
def create_contract():
    form = ContractForm()
    _populate_choices(form)
    if form.validate_on_submit():
        c = Contract(
            tenant_id=form.tenant_id.data,
            apartment_id=form.apartment_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            rent_amount=form.rent_amount.data,
        )
        try:
            db.session.add(c)
            db.session.commit()
            flash('Vertrag erfolgreich angelegt.', 'success')
            return redirect(url_for('contracts.list_contracts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen des Vertrags: {e}', 'danger')
    return render_template('contracts/form.html', form=form, title='Neuer Vertrag')


@contracts_bp.route('/<int:contract_id>/edit', methods=['GET', 'POST'])
def edit_contract(contract_id: int):
    c = db.session.get(Contract, contract_id) or abort(404)
    form = ContractForm(obj=c)
    _populate_choices(form)
    if form.validate_on_submit():
        try:
            c.tenant_id = form.tenant_id.data
            c.apartment_id = form.apartment_id.data
            c.start_date = form.start_date.data
            c.end_date = form.end_date.data
            c.rent_amount = form.rent_amount.data
            db.session.commit()
            flash('Vertrag erfolgreich aktualisiert.', 'success')
            return redirect(url_for('contracts.list_contracts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren des Vertrags: {e}', 'danger')
    return render_template('contracts/form.html', form=form, title='Vertrag bearbeiten', instance_id=contract_id)


