from datetime import date
from flask import render_template, request
from . import warnings_bp
from app.validation import generate_warnings


@warnings_bp.route('/')
def list_warnings():
    # Einfache Parameter (optional), ansonsten aktueller Monat
    period_start_str = request.args.get('start')
    period_end_str = request.args.get('end')

    today = date.today()
    default_start = date(today.year, today.month, 1)
    default_end = date(today.year, today.month, 28)  # simpel, UI ist nur Demo

    if period_start_str and period_end_str:
        try:
            y1, m1, d1 = map(int, period_start_str.split('-'))
            y2, m2, d2 = map(int, period_end_str.split('-'))
            period_start = date(y1, m1, d1)
            period_end = date(y2, m2, d2)
        except Exception:
            period_start, period_end = default_start, default_end
    else:
        period_start, period_end = default_start, default_end

    warnings = generate_warnings(period_start=period_start, period_end=period_end)
    return render_template('warnings/list.html', warnings=warnings, period_start=period_start, period_end=period_end)


