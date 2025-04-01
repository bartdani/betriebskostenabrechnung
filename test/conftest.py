import sys
import os
import pytest

# Füge das Projekt-Root-Verzeichnis zum Python-Pfad hinzu,
# damit pytest die Module im 'app'-Verzeichnis finden kann.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importiere erst NACHDEM der Pfad angepasst wurde
from app import app as flask_app, db

@pytest.fixture(scope='function')
def app_context():
    """Erstellt einen Anwendungskontext für Tests."""
    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='function')
def test_db(app_context):
    """Erstellt eine saubere Datenbank für jeden Test."""
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False # CSRF für Tests deaktivieren
    flask_app.config['SERVER_NAME'] = 'localhost' # Hinzugefügt für url_for
    
    # Stelle sicher, dass der Kontext aktiv ist, bevor db-Operationen erfolgen
    with flask_app.app_context():
        db.create_all()
        
        yield db # Gibt die DB-Instanz für den Test frei
        
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app_context):
    """Erstellt einen Test-Client für HTTP-Anfragen."""
    # Session-Konfiguration
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SERVER_NAME'] = 'localhost'
    
    # Client mit aktivierten Sessions erstellen
    test_client = flask_app.test_client()
    
    # Session-Kontext für den gesamten Test aktivieren
    with test_client.session_transaction() as sess:
        sess.clear()
        sess.update({})
    
    return test_client 