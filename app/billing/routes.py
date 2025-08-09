from datetime import date
from flask import request, render_template, send_file, flash, session
from io import BytesIO

from app import db
from app.models import Contract
from app.pdf_generation import generate_utility_statement_pdf
from . import billing_bp
from app.pdf_generation import _format_euro as fmt_euro  # reuse formatting
from app.calculations import (
    calculate_share_allocation,
    calculate_consumption_allocation,
    calculate_person_day_allocation,
    calculate_heating_allocation,
    calculate_direct_allocation,
)
from app.models import CostType, ApartmentShare, ConsumptionData
from sqlalchemy import func


@billing_bp.route('/', methods=['GET', 'POST'])
def index():
    contracts = Contract.query.order_by(Contract.id.desc()).all()

    if request.method == 'POST':
        contract_id = int(request.form.get('contract_id'))
        start = request.form.get('period_start')
        end = request.form.get('period_end')
        preset = (request.form.get('preset') or 'standard').strip()
        action = (request.form.get('action') or 'pdf').strip()
        try:
            ps = date.fromisoformat(start)
            pe = date.fromisoformat(end)
        except Exception:
            flash('Ungültiges Zeitraumformat. Bitte YYYY-MM-DD verwenden.', 'danger')
            return render_template('billing/index.html', contracts=contracts, title='Abrechnung erstellen')

        # Presets in Cost-Items übersetzen (scoped auf Gebäude des Vertrags oder Session)
        contract = db.session.get(Contract, contract_id)
        building_id = None
        if contract and contract.apartment:
            building_id = contract.apartment.building_id
        if building_id is None:
            building_id = session.get('building_id')
        cost_items = []
        if preset == 'standard':
            # Beispielhaft: Wasser (consumption), Müll (person_days), Grundsteuer (share), Direktkosten
            # Finde typische Kostenarten fallweise, falls vorhanden
            water = CostType.query.filter_by(type='consumption').filter(CostType.name.ilike('%wasser%')).first()
            trash = CostType.query.filter_by(type='person_days').first()
            share = CostType.query.filter_by(type='share').first()
            if share:
                cost_items.append({'cost_type_id': share.id, 'total_cost': _sum_invoices_total(share.id, ps, pe, building_id)})
            if water:
                cost_items.append({'cost_type_id': water.id, 'total_cost': _sum_invoices_total(water.id, ps, pe, building_id)})
            if trash:
                cost_items.append({'cost_type_id': trash.id, 'total_cost': _sum_invoices_total(trash.id, ps, pe, building_id)})
            cost_items.append({'type': 'direct'})
        elif preset == 'heating_30_70':
            heat = CostType.query.filter_by(type='consumption').filter(CostType.name.ilike('%heiz%')).first()
            hot = CostType.query.filter_by(type='consumption').filter(CostType.name.ilike('%warmwasser%')).first()
            total_heat_related = _sum_invoices_total(heat.id, ps, pe, building_id) + _sum_invoices_total(hot.id, ps, pe, building_id) if (heat and hot) else 0.0
            if heat and hot and total_heat_related > 0:
                cost_items.append({
                    'type': 'heating',
                    'total_cost': total_heat_related,
                    'hot_water_percentage': 30.0,
                    'heating_consumption_cost_type_id': heat.id,
                    'hot_water_consumption_cost_type_id': hot.id,
                })
            cost_items.append({'type': 'direct'})
        elif preset == 'direct_only':
            cost_items.append({'type': 'direct'})

        if action == 'preview':
            rows, total = _preview_rows(contract_id, ps, pe, cost_items)
            return render_template('billing/index.html', contracts=contracts, title='Abrechnung erstellen',
                                   preview_rows=rows, preview_total_fmt=fmt_euro(total))
        else:
            pdf_bytes = generate_utility_statement_pdf(contract_id, ps, pe, cost_items)
            if not pdf_bytes:
                flash('PDF-Erstellung fehlgeschlagen.', 'danger')
                return render_template('billing/index.html', contracts=contracts, title='Abrechnung erstellen')

            return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True,
                             download_name=f'abrechnung_{contract_id}_{ps}_{pe}.pdf')

    return render_template('billing/index.html', contracts=contracts, title='Abrechnung erstellen')


def _sum_invoices_total(cost_type_id: int, ps: date, pe: date, building_id: int | None = None) -> float:
    from app.models import Invoice
    q = db.session.query(func.sum(Invoice.amount)).filter(
        Invoice.cost_type_id == cost_type_id,
        Invoice.period_start <= pe,
        Invoice.period_end >= ps,
    )
    if building_id is not None:
        q = q.filter(Invoice.building_id == building_id)
    total = q.scalar() or 0.0
    return float(total)


def _preview_rows(contract_id: int, ps: date, pe: date, cost_items: list[dict]):
    contract = db.session.get(Contract, contract_id)
    if not contract:
        return [], 0.0
    apartment = contract.apartment
    rows = []
    total = 0.0

    for item in cost_items:
        if item.get('type') == 'direct':
            alloc = calculate_direct_allocation(ps, pe)
            tenant_share = alloc.get(apartment.id, 0.0)
            name = 'Direkt zugeordnete Kosten'
            key_desc = 'Direkt (Rechnungen im Zeitraum)'
            total_cost = sum(alloc.values())
        elif item.get('type') == 'heating':
            total_cost = float(item.get('total_cost', 0.0))
            hot_perc = float(item.get('hot_water_percentage', 0.0))
            heat_ct = int(item.get('heating_consumption_cost_type_id'))
            hot_ct = int(item.get('hot_water_consumption_cost_type_id'))
            alloc = calculate_heating_allocation(total_cost, hot_perc, heat_ct, hot_ct, ps, pe)
            tenant_share = alloc.get(apartment.id, 0.0)
            key_desc = f"Heizung/Warmwasser Split ({hot_perc:.0f}% | {100-hot_perc:.0f}%) verbrauchsbasiert"
            name = 'Heiz-/Warmwasserkosten'
        else:
            ct_id = int(item.get('cost_type_id'))
            total_cost = float(item.get('total_cost', 0.0))
            from app.models import CostType
            ct = db.session.get(CostType, ct_id)
            name = ct.name if ct else f'Kostenart {ct_id}'
            alloc = {}
            key_desc = ''
            if ct and ct.type == 'share':
                alloc = calculate_share_allocation(ct_id, total_cost)
                share_entry = ApartmentShare.query.filter_by(apartment_id=apartment.id, cost_type_id=ct.id).first()
                share_val = share_entry.value if share_entry else 'N/A'
                key_desc = f"Anteil ({ct.unit}: {share_val})"
            elif ct and ct.type == 'consumption':
                alloc = calculate_consumption_allocation(ct_id, total_cost, ps, pe)
                total_apt_cons = db.session.query(func.sum(ConsumptionData.value)).filter(
                    ConsumptionData.apartment_id == apartment.id,
                    ConsumptionData.cost_type_id == ct.id,
                    ConsumptionData.date >= ps,
                    ConsumptionData.date <= pe,
                ).scalar() or 0.0
                key_desc = f"Verbrauch ({ct.unit}: {total_apt_cons:.2f})"
            elif ct and ct.type == 'person_days':
                alloc = calculate_person_day_allocation(ct_id, total_cost, ps, pe)
                from app.calculations import calculate_person_days
                pdays = calculate_person_days(apartment.id, ps, pe)
                key_desc = f"Personentage: {pdays}"
            tenant_share = alloc.get(apartment.id, 0.0)

        rows.append({
            'name': name,
            'total_cost_fmt': fmt_euro(total_cost),
            'key_desc': key_desc,
            'tenant_share_fmt': fmt_euro(tenant_share),
        })
        total += tenant_share

    return rows, total


@billing_bp.route('/wizard', methods=['GET', 'POST'])
def wizard():
    contracts = Contract.query.order_by(Contract.id.desc()).all()
    # Step 1 defaults
    step = request.values.get('step', '1')
    context = {'title': 'Abrechnung (Wizard)', 'contracts': contracts, 'step': step}

    if step == '1':
        if request.method == 'POST' and request.form.get('action') == 'next':
            contract_id = request.form.get('contract_id')
            ps = request.form.get('period_start')
            pe = request.form.get('period_end')
            if not contract_id or not ps or not pe:
                flash('Bitte Vertrag und Zeitraum angeben.', 'danger')
            else:
                # Proceed to step 2
                step = '2'
                context.update({'step': step, 'contract_id': contract_id, 'period_start': ps, 'period_end': pe})
                # preload types
                context.update(_wizard_step2_context())
                return render_template('billing/wizard.html', **context)
        return render_template('billing/wizard.html', **context)

    if step == '2':
        # Render selection of cost items (shares/consumptions/person_days/heating/direct)
        contract_id = request.form.get('contract_id') or request.args.get('contract_id')
        ps = request.form.get('period_start') or request.args.get('period_start')
        pe = request.form.get('period_end') or request.args.get('period_end')
        context.update({'contract_id': contract_id, 'period_start': ps, 'period_end': pe})
        if request.method == 'POST':
            action = request.form.get('action')
            cost_items = _build_cost_items_from_selection(request)
            if action == 'preview':
                rows, total = _preview_rows(int(contract_id), date.fromisoformat(ps), date.fromisoformat(pe), cost_items)
                context.update(_wizard_step2_context())
                context.update({'preview_rows': rows, 'preview_total_fmt': fmt_euro(total)})
                return render_template('billing/wizard.html', **context)
            elif action == 'pdf':
                pdf_bytes = generate_utility_statement_pdf(
                    int(contract_id), date.fromisoformat(ps), date.fromisoformat(pe), cost_items
                )
                if not pdf_bytes:
                    flash('PDF-Erstellung fehlgeschlagen.', 'danger')
                    context.update(_wizard_step2_context())
                    return render_template('billing/wizard.html', **context)
                return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True,
                                 download_name=f'abrechnung_{contract_id}_{ps}_{pe}.pdf')
        context.update(_wizard_step2_context())
        return render_template('billing/wizard.html', **context)

    # default
    return render_template('billing/wizard.html', **context)


def _wizard_step2_context():
    return {
        'share_types': CostType.query.filter_by(type='share').order_by(CostType.name).all(),
        'consumption_types': CostType.query.filter_by(type='consumption').order_by(CostType.name).all(),
        'person_day_types': CostType.query.filter_by(type='person_days').order_by(CostType.name).all(),
        'heating_candidates': CostType.query.filter_by(type='consumption').filter(CostType.name.ilike('%heiz%')).all(),
        'hot_water_candidates': CostType.query.filter_by(type='consumption').filter(CostType.name.ilike('%warmwasser%')).all(),
    }


def _build_cost_items_from_selection(req):
    # Basic sets
    items = []
    # Shares
    for sid in req.form.getlist('share_ids'):
        try:
            ct_id = int(sid)
            items.append({'cost_type_id': ct_id, 'total_cost': _sum_invoices_total(ct_id, date.fromisoformat(req.form['period_start']), date.fromisoformat(req.form['period_end']))})
        except Exception:
            continue
    # Consumption
    for cid in req.form.getlist('consumption_ids'):
        try:
            ct_id = int(cid)
            items.append({'cost_type_id': ct_id, 'total_cost': _sum_invoices_total(ct_id, date.fromisoformat(req.form['period_start']), date.fromisoformat(req.form['period_end']))})
        except Exception:
            continue
    # Person days
    for pid in req.form.getlist('person_days_ids'):
        try:
            ct_id = int(pid)
            items.append({'cost_type_id': ct_id, 'total_cost': _sum_invoices_total(ct_id, date.fromisoformat(req.form['period_start']), date.fromisoformat(req.form['period_end']))})
        except Exception:
            continue
    # Heating
    if req.form.get('use_heating') == 'on':
        try:
            heat_id = int(req.form.get('heating_ct_id'))
            hot_id = int(req.form.get('hot_water_ct_id'))
            perc = float(req.form.get('hot_water_percentage') or 30.0)
            total = _sum_invoices_total(heat_id, date.fromisoformat(req.form['period_start']), date.fromisoformat(req.form['period_end'])) + \
                    _sum_invoices_total(hot_id, date.fromisoformat(req.form['period_start']), date.fromisoformat(req.form['period_end']))
            if total > 0:
                items.append({'type': 'heating', 'total_cost': total, 'hot_water_percentage': perc,
                              'heating_consumption_cost_type_id': heat_id,
                              'hot_water_consumption_cost_type_id': hot_id})
        except Exception:
            pass
    # Direct
    if req.form.get('use_direct') == 'on':
        items.append({'type': 'direct'})
    return items


