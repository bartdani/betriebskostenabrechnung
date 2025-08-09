from datetime import date
from typing import Dict, List
from sqlalchemy import func
from app import db
from app.models import Apartment, CostType, ConsumptionData


def generate_warnings(period_start: date, period_end: date) -> Dict[str, List[dict]]:
    warnings: Dict[str, List[dict]] = {
        'missing_consumption': [],
        'invalid_consumption_values': [],
        'consumption_spikes': [],
    }

    # Alle Apartments und Verbrauchs-CostTypes bestimmen
    apartments = db.session.query(Apartment.id).all()
    consumption_cost_types = db.session.query(CostType.id).filter(CostType.type == 'consumption').all()

    apt_ids = [a.id for a in apartments]
    ct_ids = [c.id for c in consumption_cost_types]

    if not apt_ids or not ct_ids:
        return warnings

    # 1) Ungültige Verbrauchswerte (negativ oder None) im Zeitraum melden
    invalid_rows = db.session.query(ConsumptionData).filter(
        ConsumptionData.date >= period_start,
        ConsumptionData.date <= period_end,
        ConsumptionData.value <= 0
    ).all()

    for row in invalid_rows:
        warnings['invalid_consumption_values'].append({
            'apartment_id': row.apartment_id,
            'cost_type_id': row.cost_type_id,
            'date': row.date,
            'value': row.value,
        })

    # 2) Fehlende Verbrauchsdaten pro Apartment/CostType im Zeitraum
    # Aggregation der vorhandenen Werte
    present = db.session.query(
        ConsumptionData.apartment_id,
        ConsumptionData.cost_type_id,
        func.count(ConsumptionData.id)
    ).filter(
        ConsumptionData.date >= period_start,
        ConsumptionData.date <= period_end,
        ConsumptionData.cost_type_id.in_(ct_ids),
        ConsumptionData.apartment_id.in_(apt_ids),
        ConsumptionData.value > 0
    ).group_by(
        ConsumptionData.apartment_id, ConsumptionData.cost_type_id
    ).all()

    present_pairs = {(apt_id, ct_id) for (apt_id, ct_id, _) in present}

    for apt_id in apt_ids:
        for ct_id in ct_ids:
            if (apt_id, ct_id) not in present_pairs:
                warnings['missing_consumption'].append({
                    'apartment_id': apt_id,
                    'cost_type_id': ct_id,
                })

    # 3) Ausreißer (Spikes): Werte, die > 3 * Median aller positiven Werte im Zeitraum sind
    pos_values = [
        v for (v,) in db.session.query(ConsumptionData.value).filter(
            ConsumptionData.date >= period_start,
            ConsumptionData.date <= period_end,
            ConsumptionData.value > 0
        ).all()
    ]
    if pos_values:
        sorted_vals = sorted(pos_values)
        n = len(sorted_vals)
        if n % 2 == 1:
            median = sorted_vals[n // 2]
        else:
            median = 0.5 * (sorted_vals[n // 2 - 1] + sorted_vals[n // 2])

        threshold = 3.0 * median if median > 0 else None
        if threshold is not None:
            spike_rows = db.session.query(ConsumptionData).filter(
                ConsumptionData.date >= period_start,
                ConsumptionData.date <= period_end,
                ConsumptionData.value > threshold
            ).all()
            for row in spike_rows:
                warnings['consumption_spikes'].append({
                    'apartment_id': row.apartment_id,
                    'cost_type_id': row.cost_type_id,
                    'date': row.date,
                    'value': row.value,
                    'threshold': threshold,
                    'median': median,
                })

    return warnings


