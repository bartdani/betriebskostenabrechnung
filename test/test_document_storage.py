import pytest
import os
import io
from werkzeug.datastructures import FileStorage
from datetime import date
from app.models import Contract, Tenant, Apartment
from app.storage import save_contract_pdf

# Die Fixtures 'app_context', 'test_db' und 'setup_for_contract_test' werden aus conftest.py bzw. anderen Testdateien verwendet.
# Falls setup_for_contract_test nicht global verfügbar ist, muss es hierher kopiert oder in conftest.py verschoben werden.
# Annahme: setup_for_contract_test ist verfügbar (oder wir erstellen hier eine ähnliche Basis)

@pytest.fixture
def db_with_contract(test_db):
    """Erstellt einen Basis-Vertrag für Tests."""
    a = Apartment(number='DOC_TEST_APT', address='Teststraße 1', size_sqm=50.0)
    test_db.session.add(a)
    test_db.session.flush()  # Ensure we have the ID
    
    t = Tenant(name='Doc Tester')
    test_db.session.add(t)
    test_db.session.flush()  # Ensure we have the ID
    
    # Setze die Beziehung über Contract
    c = Contract(
        tenant=t, 
        apartment=a, 
        start_date=date(2024, 1, 1), 
        rent_amount=600
    )
    test_db.session.add(c)
    test_db.session.commit()
    
    return {'contract_id': c.id, 'db': test_db}

def test_contract_model_pdf_field(db_with_contract):
    """Testet, ob das PDF-Dateinamenfeld im Contract-Modell funktioniert."""
    data = db_with_contract
    test_db = data['db']
    contract = test_db.session.get(Contract, data['contract_id'])
    
    assert contract.contract_pdf_filename is None # Standardwert
    
    pdf_filename = "test_contract.pdf"
    contract.contract_pdf_filename = pdf_filename
    test_db.session.add(contract)
    test_db.session.commit()
    
    retrieved_contract = test_db.session.get(Contract, data['contract_id'])
    assert retrieved_contract.contract_pdf_filename == pdf_filename

def test_save_contract_pdf_success(db_with_contract, tmp_path, app_context):
    """Testet das erfolgreiche Speichern einer simulierten PDF-Datei."""
    data = db_with_contract
    contract_id = data['contract_id']
    
    # Temporären Upload-Ordner für diesen Test verwenden
    upload_folder = tmp_path / "test_uploads" / "contracts"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app_context.config['UPLOAD_FOLDER_CONTRACTS'] = str(upload_folder)

    # Simuliertes FileStorage-Objekt mit verbessertem PDF-Header
    file_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n" # Validerer PDF-Header
    file_stream = io.BytesIO(file_content)
    mock_file_storage = FileStorage(
        stream=file_stream, 
        filename='vertrag_test.pdf', 
        content_type='application/pdf'
    )

    try:
        saved_filename = save_contract_pdf(mock_file_storage, contract_id)
        
        assert saved_filename is not None, "Dateiname sollte nicht None sein"
        assert saved_filename.startswith(f"contract_{contract_id}_"), "Dateiname sollte mit contract_ID_ beginnen"
        assert saved_filename.endswith(".pdf"), "Dateiname sollte mit .pdf enden"
        
        # Überprüfen, ob die Datei tatsächlich gespeichert wurde
        expected_path = upload_folder / saved_filename
        assert expected_path.exists(), f"Datei {saved_filename} wurde nicht gefunden"
        assert expected_path.read_bytes() == file_content, "Dateiinhalt stimmt nicht überein"
        
    finally:
        # Aufräumen nach dem Test
        if upload_folder.exists():
            for file in upload_folder.iterdir():
                file.unlink()
            upload_folder.rmdir()

def test_save_contract_pdf_wrong_type(db_with_contract, tmp_path, app_context):
    """Testet das Ablehnen einer Datei mit falschem Typ."""
    data = db_with_contract
    contract_id = data['contract_id']
    upload_folder = tmp_path / "test_uploads" / "contracts"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app_context.config['UPLOAD_FOLDER_CONTRACTS'] = str(upload_folder)

    file_stream = io.BytesIO(b"kein pdf")
    mock_file_storage = FileStorage(stream=file_stream, filename='test.txt')

    saved_filename = save_contract_pdf(mock_file_storage, contract_id)

    assert saved_filename is None
    # Sicherstellen, dass keine Datei erstellt wurde
    assert len(list(upload_folder.iterdir())) == 0

def test_save_contract_pdf_no_file(db_with_contract, tmp_path, app_context):
    """Testet den Fall, dass kein FileStorage-Objekt übergeben wird."""
    data = db_with_contract
    contract_id = data['contract_id']
    upload_folder = tmp_path / "test_uploads" / "contracts"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app_context.config['UPLOAD_FOLDER_CONTRACTS'] = str(upload_folder)
    
    saved_filename = save_contract_pdf(None, contract_id)
    assert saved_filename is None
    assert len(list(upload_folder.iterdir())) == 0 