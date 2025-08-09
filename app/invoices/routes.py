from flask import render_template, redirect, url_for, flash, abort, session
from app import db
from app.models import Invoice, CostType, Contract
from . import invoices_bp
from .forms import InvoiceForm


def _populate_choices(form: InvoiceForm):
    form.cost_type_id.choices = [(ct.id, f"{ct.name} ({ct.unit})") for ct in CostType.query.order_by(CostType.name)]
    contracts = Contract.query.order_by(Contract.id).all()
    form.direct_allocation_contract_id.choices = [(0, '— keine —')] + [(c.id, f"Vertrag #{c.id}") for c in contracts]


@invoices_bp.route('/')
def list_invoices():
    q = Invoice.query
    bid = session.get('building_id')
    if bid is not None:
        q = q.filter(Invoice.building_id == bid)
    invoices = q.order_by(Invoice.date.desc()).all()
    return render_template('invoices/list.html', invoices=invoices, title='Rechnungsübersicht')


@invoices_bp.route('/new', methods=['GET', 'POST'])
def create_invoice():
    form = InvoiceForm()
    _populate_choices(form)
    if form.validate_on_submit():
        # Validierung Zeitraum
        if form.period_end.data < form.period_start.data:
            # Feldfehlermeldung anhängen, damit sie im Formular erscheint
            form.period_end.errors.append('Ende muss nach Start liegen')
            return render_template('invoices/form.html', form=form, title='Neue Rechnung')

        direct_id = form.direct_allocation_contract_id.data or None
        if isinstance(direct_id, int) and direct_id == 0:
            direct_id = None

        inv = Invoice(
            invoice_number=form.invoice_number.data or None,
            date=form.date.data,
            amount=form.amount.data,
            cost_type_id=form.cost_type_id.data,
            period_start=form.period_start.data,
            period_end=form.period_end.data,
            direct_allocation_contract_id=direct_id
        )
        try:
            db.session.add(inv)
            db.session.commit()
            flash('Rechnung erfolgreich angelegt.', 'success')
            return redirect(url_for('invoices.list_invoices'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen der Rechnung: {e}', 'danger')
    return render_template('invoices/form.html', form=form, title='Neue Rechnung')


@invoices_bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
def edit_invoice(invoice_id: int):
    inv = db.session.get(Invoice, invoice_id) or abort(404)
    form = InvoiceForm(obj=inv)
    _populate_choices(form)
    if form.validate_on_submit():
        if form.period_end.data < form.period_start.data:
            form.period_end.errors.append('Ende muss nach Start liegen')
            return render_template('invoices/form.html', form=form, title='Rechnung bearbeiten', instance_id=invoice_id)
        try:
            inv.invoice_number = form.invoice_number.data or None
            inv.date = form.date.data
            inv.amount = form.amount.data
            inv.cost_type_id = form.cost_type_id.data
            inv.period_start = form.period_start.data
            inv.period_end = form.period_end.data
            direct_id = form.direct_allocation_contract_id.data or None
            if isinstance(direct_id, int) and direct_id == 0:
                direct_id = None
            inv.direct_allocation_contract_id = direct_id
            db.session.commit()
            flash('Rechnung erfolgreich aktualisiert.', 'success')
            return redirect(url_for('invoices.list_invoices'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren der Rechnung: {e}', 'danger')
    return render_template('invoices/form.html', form=form, title='Rechnung bearbeiten', instance_id=invoice_id)


