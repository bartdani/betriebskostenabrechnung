import csv
import io
from datetime import datetime
from app import db
from app.models import Apartment, CostType, ConsumptionData

def import_consumption_csv(file_path_or_stream):
    """
    Importiert Verbrauchsdaten aus einer CSV-Datei oder einem Stream.

    Args:
        file_path_or_stream: Pfad zur CSV-Datei oder ein File-like Object.

    Returns:
        dict: Ein Dictionary mit 'processed_rows' und 'skipped_rows'.
    """
    processed_rows = 0
    skipped_rows = 0
    required_headers = {'apartment_number', 'cost_type_name', 'date', 'value'}
    
    try:
        # Unterscheiden, ob Pfad oder Stream übergeben wurde
        if isinstance(file_path_or_stream, str):
            f = open(file_path_or_stream, 'r', encoding='utf-8')
            should_close = True
        else: # Annahme: file-like object (z.B. aus StringIO für Tests)
            # Wichtig: Stream muss im Textmodus sein
            if isinstance(file_path_or_stream, io.BytesIO):
                 # Versuche BytesIO in StringIO umzuwandeln, wenn nötig
                 file_path_or_stream.seek(0)
                 file_path_or_stream = io.StringIO(file_path_or_stream.read().decode('utf-8'))
            elif not isinstance(file_path_or_stream, io.StringIO):
                 raise TypeError("Stream must be StringIO or BytesIO")
            f = file_path_or_stream
            should_close = False
        
        reader = csv.DictReader(f)
        
        # Header validieren
        if not required_headers.issubset(reader.fieldnames):
            missing = required_headers - set(reader.fieldnames)
            print(f"Error: Missing required CSV headers: {missing}")
            if should_close: f.close()
            return {'processed_rows': 0, 'skipped_rows': -1} # Spezieller Wert für Header-Fehler

        for row_num, row in enumerate(reader, start=2): # start=2 wegen Header
            try:
                apartment_number = row['apartment_number']
                cost_type_name = row['cost_type_name']
                date_str = row['date']
                value_str = row['value']

                # Zugehörige Objekte finden
                apartment = Apartment.query.filter_by(number=apartment_number).first()
                cost_type = CostType.query.filter_by(name=cost_type_name).first()

                if not apartment:
                    print(f"Warning: Row {row_num}: Apartment '{apartment_number}' not found. Skipping.")
                    skipped_rows += 1
                    continue
                
                if not cost_type:
                    print(f"Warning: Row {row_num}: CostType '{cost_type_name}' not found. Skipping.")
                    skipped_rows += 1
                    continue

                # Daten validieren/konvertieren
                try:
                    consumption_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    print(f"Warning: Row {row_num}: Invalid date format '{date_str}' (expected YYYY-MM-DD). Skipping.")
                    skipped_rows += 1
                    continue
                
                try:
                    consumption_value = float(value_str)
                except ValueError:
                    print(f"Warning: Row {row_num}: Invalid value format '{value_str}' (expected number). Skipping.")
                    skipped_rows += 1
                    continue

                # ConsumptionData-Objekt erstellen und hinzufügen
                consumption_entry = ConsumptionData(
                    apartment_id=apartment.id,
                    cost_type_id=cost_type.id,
                    date=consumption_date,
                    value=consumption_value
                )
                db.session.add(consumption_entry)
                processed_rows += 1

            except KeyError as e:
                print(f"Warning: Row {row_num}: Missing expected column {e}. Skipping.")
                skipped_rows += 1
            except Exception as e:
                print(f"Warning: Row {row_num}: Unexpected error processing row: {e}. Skipping.")
                skipped_rows += 1
        
        # Änderungen speichern
        db.session.commit()
        print(f"CSV import finished. Processed: {processed_rows}, Skipped: {skipped_rows}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {file_path_or_stream}")
        return {'processed_rows': 0, 'skipped_rows': -1}
    except Exception as e:
        db.session.rollback() # Bei generellem Fehler Rollback durchführen
        print(f"Error during CSV import: {e}")
        return {'processed_rows': processed_rows, 'skipped_rows': skipped_rows + (row_num - 1 - processed_rows - skipped_rows if 'row_num' in locals() else 0)} # Schätzung
    finally:
        if should_close and 'f' in locals() and f:
            f.close()
            
    return {'processed_rows': processed_rows, 'skipped_rows': skipped_rows} 