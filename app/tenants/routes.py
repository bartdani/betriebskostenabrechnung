from app.tenants import bp_tenants
from flask import render_template

# Beispielroute (wird später erweitert)
@bp_tenants.route('/contracts')
def list_contracts():
    # Hier später Logik zum Laden und Anzeigen von Verträgen
    return render_template('tenants/contracts.html', title='Mietverträge')

# Weitere Routen für Mieter/Verträge hier hinzufügen 