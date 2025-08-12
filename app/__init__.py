import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func


# Datenbank-Instanz erstellen
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    # Basispfad des Projekts bestimmen
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.abspath(os.path.join(basedir, '..', 'instance'))

    # Sicherstellen, dass der instance-Ordner existiert
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    app = Flask(__name__, instance_path=instance_path, instance_relative_config=False)

    if test_config is None:
        # Standardkonfiguration laden
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'eine-sehr-geheime-zeichenkette'
        # SQLite-DB absolut im instance-Ordner ablegen (vermeidet relative Pfadprobleme)
        default_sqlite_path = 'sqlite:///' + os.path.join(instance_path, 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or default_sqlite_path
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Upload Ordner konfigurieren
        UPLOAD_FOLDER_CONTRACTS = os.path.join(app.instance_path, 'uploads', 'contracts')
        app.config['UPLOAD_FOLDER_CONTRACTS'] = UPLOAD_FOLDER_CONTRACTS

        # Sicherstellen, dass der Upload-Ordner existiert
        if not os.path.exists(UPLOAD_FOLDER_CONTRACTS):
            os.makedirs(UPLOAD_FOLDER_CONTRACTS)

        # Optionale Instanzkonfiguration laden (z. B. PDF-Header/Logo)
        try:
            instance_config_path = os.path.join(app.instance_path, 'config.py')
            if os.path.exists(instance_config_path):
                app.config.from_pyfile(instance_config_path, silent=True)
        except Exception:
            # Konfigurationsdatei ist optional – Fehler hier nicht fatal machen
            pass
    else:
        # Testkonfiguration übernehmen
        app.config.update(test_config)

    # Datenbank und Migrations-Engine initialisieren
    db.init_app(app)
    migrate.init_app(app, db)

    # Modelle importieren, damit Migrate sie erkennt (nach db Initialisierung)
    from app import models
    from app.models import (
        Building,
        Apartment,
        Tenant,
        Contract,
        Invoice,
        ConsumptionData,
        CostType,
    )

    # Blueprints registrieren
    from app.tenants import bp_tenants as tenants_bp
    app.register_blueprint(tenants_bp)

    from app.apartments import apartments_bp
    app.register_blueprint(apartments_bp)

    from app.cost_types import cost_types_bp
    app.register_blueprint(cost_types_bp)

    # Meters Blueprint registrieren
    from app.meters import meters_bp
    app.register_blueprint(meters_bp)

    # Manual Entry Blueprint registrieren
    from app.manual_entry.routes import manual_entry_bp
    app.register_blueprint(manual_entry_bp)

    # Invoices Blueprint registrieren
    from app.invoices import invoices_bp
    app.register_blueprint(invoices_bp)

    # Warnings Blueprint registrieren
    from app.warnings import warnings_bp
    app.register_blueprint(warnings_bp)

    # Contracts Blueprint registrieren
    from app.contracts import contracts_bp
    app.register_blueprint(contracts_bp)

    # Billing Blueprint registrieren
    from app.billing import billing_bp
    app.register_blueprint(billing_bp)

    @app.route('/')
    @app.route('/index')
    def index():
        # Aggregierte Kennzahlen
        stats = {
            'buildings': db.session.query(Building).count(),
            'apartments': db.session.query(Apartment).count(),
            'tenants': db.session.query(Tenant).count(),
            'contracts': db.session.query(Contract).count(),
            'invoices': db.session.query(Invoice).count(),
        }

        # Optional nach Gebäude filtern, falls gewählt (nur für Rechnungen sinnvoll, da Feld vorhanden)
        selected_building_id = session.get('building_id')

        invoice_ct_query = (
            db.session.query(CostType.name.label('name'), func.sum(Invoice.amount).label('total'))
            .select_from(Invoice)
            .join(CostType, Invoice.cost_type_id == CostType.id)
        )
        if selected_building_id:
            invoice_ct_query = invoice_ct_query.filter(Invoice.building_id == selected_building_id)
        invoice_ct_query = invoice_ct_query.group_by(CostType.name).order_by(CostType.name)
        invoices_by_cost_type = invoice_ct_query.all()

        chart_invoices = {
            'labels': [row.name for row in invoices_by_cost_type],
            'data': [float(row.total or 0) for row in invoices_by_cost_type],
        }

        # Verbrauch nach Monat (SQLite: strftime). Gesamtsicht, da ConsumptionData kein building_id hat
        consumption_query = (
            db.session.query(
                func.strftime('%Y-%m', ConsumptionData.date).label('month'),
                func.sum(ConsumptionData.value).label('total'),
            )
            .group_by('month')
            .order_by('month')
        )
        consumption_by_month = consumption_query.all()
        chart_consumption = {
            'labels': [row.month for row in consumption_by_month],
            'data': [float(row.total or 0) for row in consumption_by_month],
        }

        return render_template(
            'index.html',
            title='Startseite',
            stats=stats,
            chart_invoices=chart_invoices,
            chart_consumption=chart_consumption,
        )

    # Navbar: Gebäude-Auswahl bereitstellen
    @app.context_processor
    def inject_building_selector():
        try:
            buildings = Building.query.order_by(Building.name).all()
        except Exception:
            buildings = []
        selected_building_id = session.get('building_id')
        return dict(navbar_buildings=buildings, selected_building_id=selected_building_id)

    @app.before_request
    def validate_selected_building():
        bid = session.get('building_id')
        if bid is not None:
            # Ungültige Auswahl stillschweigend zurücksetzen
            if not db.session.get(Building, bid):
                session.pop('building_id', None)

    @app.route('/ui/select-building', methods=['POST'])
    def ui_select_building():
        value = request.form.get('building_id', '').strip()
        if not value:
            session.pop('building_id', None)
        else:
            try:
                session['building_id'] = int(value)
            except ValueError:
                session.pop('building_id', None)
        ref = request.headers.get('Referer')
        return redirect(ref or url_for('index'))

    return app