import pytest
from app import app as flask_app  # Importiere die Flask-App-Instanz

@pytest.fixture
def client():
    # Erstelle einen Test-Client für die Flask-App
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_index_route(client):
    """Testet, ob die Index-Route ('/') erfolgreich (Statuscode 200) antwortet."""
    response = client.get('/')
    assert response.status_code == 200

def test_index_route_content(client):
    """Testet, ob die Index-Route den erwarteten Inhalt enthält."""
    response = client.get('/')
    assert b"Betriebskostenabrechnung" in response.data
    assert b"Basis-Setup" in response.data 