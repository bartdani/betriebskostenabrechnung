import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Basispfad des Projekts bestimmen
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.abspath(os.path.join(basedir, '..', 'instance'))

# Sicherstellen, dass der instance-Ordner existiert
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__, instance_path=instance_path, instance_relative_config=False)

# Konfiguration laden (später evtl. aus config.py)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'eine-sehr-geheime-zeichenkette' # WICHTIG: Im Produktivbetrieb ändern!
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'sqlite:///../instance/app.db' # Pfad relativ zum app-Ordner
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Datenbank und Migrations-Engine initialisieren
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelle importieren, damit Migrate sie erkennt (nach db Initialisierung)
from app import models

# Blueprints registrieren
from app.tenants import bp_tenants as tenants_bp
app.register_blueprint(tenants_bp, url_prefix='/tenants') # NEU, mit Prefix

@app.route('/')
@app.route('/index')
def index():
    return "<h1>Betriebskostenabrechnung - Basis-Setup</h1>"

# Weitere Konfigurationen und Blueprints werden hier später hinzugefügt 