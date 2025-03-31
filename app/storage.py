import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Bereinige den Dateinamen nicht mit secure_filename, da wir UUID verwenden
        # secure_name = secure_filename(unique_filename) # Nicht nötig bei UUID
        
        save_path = os.path.join(upload_folder, unique_filename)
        
        # Sicherstellen, dass der Ordner existiert (sollte durch __init__ schon sein, aber sicher ist sicher)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_storage.save(save_path)
        print(f"Successfully saved contract PDF: {unique_filename}")
        return unique_filename
        
    except KeyError:
        print("Error: UPLOAD_FOLDER_CONTRACTS not configured in Flask app.")
        return None
    except Exception as e:
        print(f"Error saving file: {e}")
        # Ggf. Logging hinzufügen
        return None 