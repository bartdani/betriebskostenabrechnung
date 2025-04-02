import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
            'sqlite:///../instance/app.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Upload Ordner konfigurieren
        UPLOAD_FOLDER_CONTRACTS = os.path.join(app.instance_path, 'uploads', 'contracts')
        app.config['UPLOAD_FOLDER_CONTRACTS'] = UPLOAD_FOLDER_CONTRACTS

        # Sicherstellen, dass der Upload-Ordner existiert
        if not os.path.exists(UPLOAD_FOLDER_CONTRACTS):
            os.makedirs(UPLOAD_FOLDER_CONTRACTS)
    else:
        # Testkonfiguration übernehmen
        app.config.update(test_config)

    # Datenbank und Migrations-Engine initialisieren
    db.init_app(app)
    migrate.init_app(app, db)

    # Modelle importieren, damit Migrate sie erkennt (nach db Initialisierung)
    from app import models

    # Blueprints registrieren
    from app.tenants import bp_tenants as tenants_bp
    app.register_blueprint(tenants_bp)

    from app.apartments import apartments_bp
    app.register_blueprint(apartments_bp)

    from app.cost_types import cost_types_bp
    app.register_blueprint(cost_types_bp)

    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html', title='Startseite')

    return app