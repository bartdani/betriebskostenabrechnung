import pytest

@pytest.fixture

def test_index_route(client):
    """Testet, ob die Index-Route ('/') erfolgreich (Statuscode 200) antwortet."""
    response = client.get('/')
    assert response.status_code == 200

def test_index_route_content(client):
    """Testet, ob die Index-Route den erwarteten Inhalt enthält."""
    response = client.get('/')
    assert b"Betriebskostenabrechnung" in response.data
    assert b"Basis-Setup" in response.data 