def test_nav_links_present_on_index(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # Link-Texte prüfen
    assert 'Dashboard' in html
    assert 'Wohnungen' in html
    assert 'Mieter' in html
    assert 'Zähler' in html


def test_nav_routes_accessible(client):
    # Index
    assert client.get('/').status_code == 200
    # Apartments
    assert client.get('/apartments/').status_code == 200
    # Tenants
    assert client.get('/tenants/').status_code == 200
    # Meters
    assert client.get('/meters/').status_code == 200


