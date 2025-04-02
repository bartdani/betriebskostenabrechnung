from flask import current_app
import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

# Erlaubte Dateitypen definieren
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Überprüft, ob die Dateiendung erlaubt ist."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_contract_pdf(file_storage, contract_id):
    """
    Speichert eine hochgeladene PDF-Datei für einen Vertrag sicher ab.

    Args:
        file_storage: Das FileStorage-Objekt aus dem Request.
        contract_id: Die ID des Vertrags, zu dem die Datei gehört.

    Returns:
        str: Der generierte, gespeicherte Dateiname oder None bei Fehlern.
    """
    if file_storage is None or file_storage.filename == '':
        print("Error: No file selected")
        return None

    if not allowed_file(file_storage.filename):
        print(f"Error: File type not allowed (only PDF): {file_storage.filename}")
        return None

    try:
        upload_folder = current_app.config['UPLOAD_FOLDER_CONTRACTS']
        # Extrahiere die ursprüngliche Dateiendung
        original_extension = file_storage.filename.rsplit('.', 1)[1].lower()
        # Generiere einen eindeutigen Namen
        unique_filename = f"contract_{contract_id}_{uuid.uuid4().hex}.{original_extension}"
        
        # Verwende pathlib für bessere Plattformunabhängigkeit
        upload_path = Path(upload_folder)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        save_path = upload_path / unique_filename
        file_storage.save(str(save_path))
        
        print(f"Successfully saved contract PDF: {unique_filename}")
        return unique_filename
        
    except KeyError:
        print("Error: UPLOAD_FOLDER_CONTRACTS not configured in Flask app.")
        return None
    except Exception as e:
        print(f"Error saving file: {e}")
        return None 