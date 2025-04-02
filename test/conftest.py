import sys
import os
import pytest

# Füge das Projekt-Root-Verzeichnis zum Python-Pfad hinzu,
# damit pytest die Module im 'app'-Verzeichnis finden kann.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importiere erst NACHDEM der Pfad angepasst wurde
from app import create_app, db

@pytest.fixture(scope='function')
def app_context():
    """Erstellt einen Anwendungskontext für Tests."""
    app_instance = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
        'SERVER_NAME': 'localhost'
    })
    
    with app_instance.app_context():
        db.create_all()  # Erstelle die Datenbanktabellen
        yield app_instance
        db.session.remove()
        db.drop_all()  # Räume die Datenbank nach dem Test auf

@pytest.fixture(scope='function')
def test_db(app_context):
    """Erstellt eine saubere Datenbank für jeden Test."""
    db.session.begin_nested()  # Erstelle einen Savepoint
    yield db
    db.session.rollback()  # Rolle alle Änderungen zurück
    db.session.remove()

@pytest.fixture(scope='function')
def client(app_context):
    """Erstellt einen Test-Client für HTTP-Anfragen."""
    app_context.config['SERVER_NAME'] = 'localhost'
    app_context.config['PREFERRED_URL_SCHEME'] = 'http'
    
    with app_context.test_client() as test_client:
        with app_context.app_context():
            yield test_client

@pytest.fixture
def runner(app_context):
    """Erstellt einen CLI-Runner für Kommandozeilen-Tests."""
    return app_context.test_cli_runner()