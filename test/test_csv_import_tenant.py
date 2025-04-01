import pytest
import csv
import io
from app import db
from app.models import Tenant
from app.import_data import import_tenant_csv

# Helper zum Erstellen von CSV-Strings
def create_csv_string(headers, data_rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data_rows)
    output.seek(0)
    return output

def test_import_tenant_csv_success(test_db, client): # client evtl. nicht nötig, aber test_db
    """Testet den erfolgreichen Import von Mietern."""
    csv_content = "Name,Kontaktinfo\nAlice Wunder,alice@mail.de\nBob Baumeister,0123456"
    csv_stream = io.StringIO(csv_content)

    result = import_tenant_csv(csv_stream)

    assert result['processed_rows'] == 2
    assert result['skipped_rows'] == 0

    alice = Tenant.query.filter_by(name="Alice Wunder").first()
    bob = Tenant.query.filter_by(name="Bob Baumeister").first()

    assert alice is not None
    assert alice.contact_info == "alice@mail.de"
    assert bob is not None
    assert bob.contact_info == "0123456"

def test_import_tenant_csv_missing_header(test_db, client):
    """Testet den Import mit fehlendem Pflicht-Header."""
    csv_content = "Kontaktinfo\nsome@mail.de"
    csv_stream = io.StringIO(csv_content)

    result = import_tenant_csv(csv_stream)

    assert result['processed_rows'] == 0
    assert result['skipped_rows'] == -1 # Spezieller Wert für Header-Fehler
    assert Tenant.query.count() == 0 # Nichts darf importiert worden sein

def test_import_tenant_csv_missing_name_in_row(test_db, client):
    """Testet den Import, wenn der Name in einer Zeile fehlt."""
    csv_content = "Name,Kontaktinfo\n,missing@name.com\nCharlie Chaplin,charlie@mail.com"
    csv_stream = io.StringIO(csv_content)

    result = import_tenant_csv(csv_stream)

    assert result['processed_rows'] == 1
    assert result['skipped_rows'] == 1

    charlie = Tenant.query.filter_by(name="Charlie Chaplin").first()
    assert charlie is not None
    assert charlie.contact_info == "charlie@mail.com"
    assert Tenant.query.count() == 1 # Nur Charlie wurde importiert

def test_import_tenant_csv_empty_file(test_db, client):
    """Testet den Import einer leeren Datei (nur Header)."""
    csv_content = "Name,Kontaktinfo"
    csv_stream = io.StringIO(csv_content)

    result = import_tenant_csv(csv_stream)

    assert result['processed_rows'] == 0
    assert result['skipped_rows'] == 0
    assert Tenant.query.count() == 0

def test_import_tenant_csv_unexpected_header(test_db, client):
    """Testet den Import mit einem zusätzlichen, unerwarteten Header."""
    csv_content = "Name,Kontaktinfo,Unerwartet\nDavid Da Vinci,david@art.com,extra_info"
    csv_stream = io.StringIO(csv_content)

    result = import_tenant_csv(csv_stream)

    assert result['processed_rows'] == 1
    assert result['skipped_rows'] == 0

    david = Tenant.query.filter_by(name="David Da Vinci").first()
    assert david is not None
    assert david.contact_info == "david@art.com"
    # Prüfen, dass das unerwartete Feld ignoriert wurde (kein Attribut 'Unerwartet')
    assert not hasattr(david, 'Unerwartet') 