import csv
import io
from datetime import datetime
from app import db
from app.models import Apartment, CostType, ConsumptionData, Tenant

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

def import_tenant_csv(file_path_or_stream):
    """
    Importiert Mieterdaten aus einer CSV-Datei oder einem Stream.

    CSV Format erwartet:
        Name (string, required): Name des Mieters.
        Kontaktinfo (string, optional): Kontaktinformationen (E-Mail, Tel, etc.).

    Args:
        file_path_or_stream: Pfad zur CSV-Datei oder ein File-like Object.

    Returns:
        dict: Ein Dictionary mit 'processed_rows' und 'skipped_rows'.
    """
    processed_rows = 0
    skipped_rows = 0
    required_headers = {'Name'} # Nur Name ist initial Pflicht
    optional_headers = {'Kontaktinfo'}
    all_expected_headers = required_headers.union(optional_headers)

    try:
        # Unterscheiden, ob Pfad oder Stream übergeben wurde
        if isinstance(file_path_or_stream, str):
            f = open(file_path_or_stream, 'r', encoding='utf-8')
            should_close = True
        else: # Annahme: file-like object
            if isinstance(file_path_or_stream, io.BytesIO):
                 file_path_or_stream.seek(0)
                 file_path_or_stream = io.StringIO(file_path_or_stream.read().decode('utf-8'))
            elif not isinstance(file_path_or_stream, io.StringIO):
                 raise TypeError("Stream must be StringIO or BytesIO")
            f = file_path_or_stream
            should_close = False

        reader = csv.DictReader(f)

        # Header validieren (Mindestens die Pflicht-Header müssen da sein)
        actual_headers = set(reader.fieldnames)
        if not required_headers.issubset(actual_headers):
            missing = required_headers - actual_headers
            print(f"Error: Missing required CSV headers: {missing}")
            if should_close: f.close()
            return {'processed_rows': 0, 'skipped_rows': -1}

        # Warnung für unerwartete Header (optional)
        unexpected = actual_headers - all_expected_headers
        if unexpected:
            print(f"Warning: Ignoring unexpected CSV headers: {unexpected}")

        for row_num, row in enumerate(reader, start=2):
            try:
                tenant_name = row.get('Name')
                contact_info = row.get('Kontaktinfo', '') # Default leer, wenn Spalte fehlt oder leer ist

                if not tenant_name:
                    print(f"Warning: Row {row_num}: Missing required field 'Name'. Skipping.")
                    skipped_rows += 1
                    continue

                # TODO: Duplikatsprüfung? (Optional, überspringen oder aktualisieren?)
                # existing_tenant = Tenant.query.filter_by(name=tenant_name).first()
                # if existing_tenant:
                #     print(f"Info: Row {row_num}: Tenant '{tenant_name}' already exists. Skipping.")
                #     skipped_rows += 1
                #     continue

                # Tenant-Objekt erstellen
                tenant_entry = Tenant(
                    name=tenant_name,
                    contact_info=contact_info
                    # apartment_id wird hier nicht gesetzt
                )
                db.session.add(tenant_entry)
                processed_rows += 1

            except KeyError as e: # Sollte durch row.get() abgefangen sein, aber sicherheitshalber
                print(f"Warning: Row {row_num}: Error accessing column {e}. Skipping.")
                skipped_rows += 1
            except Exception as e:
                print(f"Warning: Row {row_num}: Unexpected error processing row: {e}. Skipping.")
                skipped_rows += 1

        db.session.commit()
        print(f"Tenant CSV import finished. Processed: {processed_rows}, Skipped: {skipped_rows}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path_or_stream}")
        return {'processed_rows': 0, 'skipped_rows': -1}
    except Exception as e:
        db.session.rollback()
        print(f"Error during Tenant CSV import: {e}")
        # Bessere Schätzung für skipped rows bei generischem Fehler
        processed_in_batch = processed_rows
        skipped_in_batch = skipped_rows
        current_row_num = row_num if 'row_num' in locals() else 1
        total_rows_estimate = current_row_num -1 # Exklusive Header
        if total_rows_estimate < 0: total_rows_estimate = 0
        unaccounted_rows = total_rows_estimate - processed_in_batch - skipped_in_batch
        if unaccounted_rows < 0: unaccounted_rows = 0
        final_skipped = skipped_in_batch + unaccounted_rows
        return {'processed_rows': processed_in_batch, 'skipped_rows': final_skipped}
    finally:
        if 'should_close' in locals() and should_close and 'f' in locals() and f:
            f.close()

    return {'processed_rows': processed_rows, 'skipped_rows': skipped_rows} 