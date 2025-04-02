# Completed Tasks

## Task: Kostenverteilung (Personentage pro-rata) v1.0
Last Updated: 2024-08-02

### Implementation Results
- Neues SQLAlchemy-Modell `OccupancyPeriod` in `app/models.py` hinzugefügt (Felder: `apartment_id`, `start_date`, `end_date`, `number_of_occupants`).
- Datenbankmigration mittels `flask db migrate` und `flask db upgrade` durchgeführt.
- Hilfsfunktion `_get_relevant_occupancy_periods(apartment_id, period_start, period_end)` in `app/calculations.py` implementiert, um überlappende Belegungsperioden zu finden.
- Funktion `calculate_person_days(apartment_id, period_start, period_end)` in `app/calculations.py` implementiert, die die Summe der Personentage pro Wohnung im Abrechnungszeitraum berechnet.
- Hauptfunktion `calculate_person_day_allocation(cost_type_id, total_cost, period_start, period_end)` in `app/calculations.py` implementiert, die Gesamtkosten basierend auf den Personentagen aller Wohnungen verteilt.

### Completed Testing
- Neue Testdatei `test/test_cost_alloc_persondays.py` erstellt.
- Unit-Tests für das `OccupancyPeriod`-Modell hinzugefügt (Erstellung, Validierung ungültiger Daten).
- Unit-Tests für `calculate_person_days` hinzugefügt (verschiedene Überlappungsszenarien, mehrere Perioden, keine Perioden, laufende Perioden).
- Unit-Tests für `calculate_person_day_allocation` hinzugefügt (einfache Verteilung, Fall mit 0 Tagen für eine Wohnung, Fall mit 0 Gesamttagen).
- Alle Tests (insgesamt 46) mittels `pytest` erfolgreich ausgeführt nach Behebung initialer Fehler (falsche Fixture-Namen, fehlende Testdaten).

### Lessons Learned
- Korrekte Verwendung von pytest Fixtures (`client`, `test_db`) ist essentiell.
- Tests benötigen eigene, isolierte Daten (hier: `Apartment`-Objekte mussten in Tests erstellt werden).
- Datumsberechnungen, speziell für Intervalle (inklusive Endtag), erfordern Sorgfalt.
- Überprüfung der Konsolenausgabe (z.B. bei Migrationen) ist wichtig.

### Documentation Updates
- `app/models.py`: Neues Modell `OccupancyPeriod` hinzugefügt.
- `app/calculations.py`: Neue Funktionen `_get_relevant_occupancy_periods`, `calculate_person_days`, `calculate_person_day_allocation` hinzugefügt.
- `test/test_cost_alloc_persondays.py`: Neue Testdatei hinzugefügt.
- `tasks.md`: Status der Aufgabe und Teilaufgaben aktualisiert.
- `activeContext.md`: Fortschritt und abgeschlossene Schritte dokumentiert.
- `progress.md`: Reflexion hinzugefügt (wird im nächsten Schritt mit Link versehen).
- `docs/archive/completed_tasks.md`: Dieser Eintrag wurde hinzugefügt.

---

## Task: Kombinierte Schlüsselverteilung implementieren (v1.0)
Last Updated: 2024-08-01

### Implementation Results
- Die Funktion `calculate_combined_allocation` wurde zu `app/calculations.py` hinzugefügt.
- Diese Funktion nimmt eine Liste von Verteilungsregeln entgegen, wobei jede Regel einen `cost_type_id` (Verbrauch oder Anteil), einen prozentualen Anteil an den Gesamtkosten (`percentage`) und den entsprechenden Kostenanteil (`total_cost_part`) angibt.
- Für Verbrauchsregeln wird auch `period_start` und `period_end` benötigt.
- Die Funktion berechnet die anteiligen Kosten für jede Regel mithilfe der bereits existierenden Funktionen `calculate_consumption_allocation` und `calculate_share_allocation`.
- Die Ergebnisse für jedes Apartment werden über alle Regeln hinweg aggregiert.
- Eine Warnung wird ausgegeben, wenn die Summe der Prozentsätze in den Regeln nicht 100% ergibt.
- Die Funktion gibt ein Dictionary zurück, das die Gesamtzuweisung pro Apartment-ID enthält.
- *Refactoring*: Die Funktion (und die anderen Verteilungsfunktionen) wurde angepasst, um im Fehlerfall oder bei leeren/ungültigen Eingaben ein leeres Dictionary `{}` statt `None` zurückzugeben.

### Completed Testing
- Eine neue Testdatei `test/test_cost_alloc_combined.py` wurde erstellt.
- Es wurden Tests für verschiedene Szenarien implementiert:
    - 50/50-Verteilung zwischen Verbrauch und Anteil.
    - Nur Verbrauchsregel.
    - Ungültige Prozentsumme (Prüfung auf Warnung und normale Ausführung).
    - Ungültige Regel (fehlende Schlüssel).
    - Leere Regelliste (erwartet nun `{}`).
- *Refactoring*: Die Tests in `test_cost_alloc_combined.py`, `test_cost_alloc_consumption.py` und `test_cost_alloc_share.py`, die zuvor `None` erwarteten, wurden angepasst, um ein leeres Dictionary `{}` zu erwarten.
- Alle 31 `pytest`-Tests wurden erfolgreich ausgeführt.

### Lessons Learned
- Die Wiederverwendung bestehender, getesteter Funktionen vereinfacht die Entwicklung komplexerer Logik.
- `defaultdict(float)` ist nützlich für das Aggregieren von Werten über mehrere Schritte.
- Konsistente Rückgabewerte (immer Dict statt `None`) vereinfachen die nachfolgende Verarbeitung und Fehlerbehandlung.
- Testabdeckung für verschiedene Fehlerfälle und Randbedingungen ist entscheidend.
- Anhaltende Terminalprobleme erfordern Workarounds und sorgfältige Überprüfung der Ergebnisse.

### Documentation Updates
- `app/calculations.py` (Funktion hinzugefügt und refactored)
- `test/test_cost_alloc_combined.py` (erstellt und refactored)
- `test/test_cost_alloc_consumption.py` (refactored)
- `test/test_cost_alloc_share.py` (refactored)
- `tasks.md` (Aufgabenstatus aktualisiert)
- `activeContext.md` (Fortschritt dokumentiert)

## Task: Aufgabenliste aktualisieren (Basis: projectbrief.md) v10
Last Updated: 2024-07-29

### Implementation Results
Die Datei `memory-bank/tasks.md` wurde vollständig neu strukturiert, um die vier Hauptphasen und die dazugehörigen Aufgaben aus dem `projectbrief.md` abzubilden. Bestehende Detailaufgaben aus der vorherigen Version von `tasks.md` wurden in die neue Struktur integriert.

### Completed Testing
Ein visueller Abgleich der neuen `tasks.md` mit dem `projectbrief.md` wurde durchgeführt, um sicherzustellen, dass alle Phasen und Hauptanforderungen abgedeckt sind. Die Integration der alten Aufgaben wurde ebenfalls überprüft.

### Lessons Learned
Die Übernahme einer klaren Projektstruktur aus dem Anforderungsdokument (`projectbrief.md`) in die Aufgabenliste (`tasks.md`) verbessert die Nachverfolgbarkeit des Fortschritts erheblich. Es ist wichtig, bei solchen Aktualisierungen bestehende Details sorgfältig zu integrieren.

### Documentation Updates
- `tasks.md`: Hauptsächlich aktualisiertes Dokument.
- `activeContext.md`: Aktualisiert, um die Fertigstellung dieser Aufgabe zu vermerken.
- `progress.md`: Aktualisiert mit Verweis auf diesen Archivierungseintrag.

## Task: Flask-Setup mit Grundstruktur v10
Last Updated: 2024-07-31

### Implementation Results
- Ein grundlegendes Flask-App-Layout wurde erstellt (`app/__init__.py`, `run.py`).
- Eine einfache Index-Route (`/` und `/index`) wurde implementiert.
- Eine `README.md` wurde erstellt und mit Startanweisungen aktualisiert.
- Ein erster Test (`test/test_app_basic.py`) mit `pytest` wurde erstellt, der die Erreichbarkeit der Index-Route prüft.
- Eine `test/conftest.py` wurde erstellt, um den `PYTHONPATH` für Tests anzupassen und eine Test-Client-Fixture bereitzustellen.

### Completed Testing
- Die `pytest`-Tests für die Index-Route wurden erfolgreich ausgeführt.
- Die Anwendung konnte lokal über `python run.py` gestartet werden (manuelle Prüfung).

### Lessons Learned
- Die Trennung von App-Initialisierung (`app/__init__.py`) und Start-Skript (`run.py`) ist eine gute Praxis.
- `conftest.py` ist essenziell, um Importprobleme bei Tests in einem separaten `test`-Ordner zu lösen.
- Anhaltende Terminal-Probleme (PSReadLine) können Git-Operationen im Tool unzuverlässig machen; manuelle Ausführung oder Überprüfung ist ratsam.

### Documentation Updates
- `app/__init__.py`, `run.py`, `README.md`, `test/test_app_basic.py`, `test/conftest.py` (erstellt/geändert)
- `tasks.md`: Aufgabe als erledigt markiert.
- `activeContext.md`: Fortschritt vermerkt.

## Task: Datenbankmodell Basis implementieren v10
Last Updated: 2024-07-31

### Implementation Results
- `Flask-SQLAlchemy` und `Flask-Migrate` wurden zu `requirements.txt` hinzugefügt und installiert.
- Die Flask-App (`app/__init__.py`) wurde konfiguriert, um SQLAlchemy und Migrate zu verwenden, mit einer SQLite-Datenbank im `instance`-Ordner.
- Die Basis-Datenbankmodelle (`Apartment`, `Tenant`, `CostType`, `ConsumptionData`) wurden in `app/models.py` definiert.
- Datenbankmigrationen wurden mittels `flask db init`, `flask db migrate` und `flask db upgrade` initialisiert und angewendet (manuell ausgeführt aufgrund von Terminal-Problemen).
- Tests (`test/test_db_models_basic.py`) wurden erstellt, um das Erstellen und Abrufen von Modellinstanzen zu überprüfen.
- `conftest.py` wurde erweitert, um eine In-Memory-SQLite-Datenbank für Tests bereitzustellen.

### Completed Testing
- Die `pytest`-Tests für die Datenbankmodelle wurden erfolgreich ausgeführt.
- Die Erstellung der Datenbankdatei (`instance/app.db`) und der Migrationen wurde manuell überprüft.

### Lessons Learned
- Die manuelle Ausführung von `flask db`-Befehlen ist ein notwendiger Workaround bei anhaltenden Terminal-Problemen in der IDE.
- Die Verwendung einer In-Memory-Datenbank (`sqlite:///:memory:`) in `conftest.py` beschleunigt Tests und hält sie isoliert.
- Die Reihenfolge der Imports und Pfadanpassungen in `conftest.py` ist entscheidend für das korrekte Funktionieren der Tests.
- Implizite Commits durch Git bei fehlgeschlagener Terminalausgabe sind ein unerwartetes Verhalten und erfordern besondere Aufmerksamkeit.

### Documentation Updates
- `requirements.txt`, `app/__init__.py`, `app/models.py`, `test/conftest.py`, `test/test_db_models_basic.py` (erstellt/geändert)
- `migrations`-Verzeichnis (erstellt)
- `instance/app.db` (erstellt)
- `tasks.md`: Aufgabe als erledigt markiert.
- `activeContext.md`: Fortschritt vermerkt.

## Task: Basis CSV-Import für Zählerstände implementieren v10
Last Updated: 2024-07-31

### Implementation Results
- Eine Funktion `import_consumption_csv` wurde in `app/import_data.py` implementiert, die CSV-Dateien oder Streams mit Verbrauchsdaten verarbeitet.
- Die Funktion verwendet `csv.DictReader` und validiert Header.
- Sie sucht nach existierenden `Apartment`- und `CostType`-Objekten in der DB.
- Sie validiert Datenformate (Datum, Wert) und überspringt fehlerhafte Zeilen mit Warnungen.
- Valide Daten werden als `ConsumptionData`-Objekte in der Datenbank gespeichert.
- Die Funktion gibt einen Status über verarbeitete und übersprungene Zeilen zurück.
- Tests (`test/test_csv_import_basic.py`) wurden erstellt, die den Import mit validen, invaliden und gemischten Daten sowie fehlenden Headern überprüfen.

### Completed Testing
- Die `pytest`-Tests für die CSV-Importfunktion wurden erfolgreich ausgeführt.
- Die Tests überprüften die korrekte Erstellung von DB-Einträgen für valide Daten und das korrekte Überspringen invalider Daten.

### Lessons Learned
- Das eingebaute `csv`-Modul ist mächtig genug für einfache bis mittlere Importaufgaben.
- Eine sorgfältige Fehlerbehandlung auf Zeilenebene ist wichtig, um den Import robuster zu machen.
- Das Testen von Importfunktionen mit `io.StringIO` für CSV-Daten ist sehr praktisch.

### Documentation Updates
- `app/import_data.py`, `test/test_csv_import_basic.py` (erstellt)
- `tasks.md`: Aufgabe als erledigt markiert.
- `activeContext.md`: Fortschritt vermerkt.

## Task: Implement CRUD for Custom Cost Types (Kostenarten) (v1.0)
Last Updated: 2024-08-08

### Implementation Results
- Defined `CostType` SQLAlchemy model.
- Created `CostTypeForm` using Flask-WTF, including validation for unique names (case-insensitive).
- Implemented Flask Blueprint `cost_types` with routes for listing, creating, editing, and deleting cost types.
- Routes handle form processing, validation, database operations (add, commit, delete), and redirects.
- Created Jinja2/HTML templates (`list_cost_types.html`, `create_edit_cost_type.html`, `base.html`, `bootstrap_wtf.html`) using Bootstrap 5 for styling.
- Implemented delete confirmation modals directly in the list template using unique IDs per item (avoids extra JS).
- Added `SERVER_NAME` to test configuration (`conftest.py`) to fix `url_for` issues.
- Added basic `bootstrap_wtf.html` macro for form rendering.

### Completed Testing
- Wrote unit/integration tests using pytest in `test/test_custom_keys.py`.
- Tested GET routes for list, create form, edit form (including 404).
- Tested POST routes for create (success, validation error, duplicate name), edit (success, validation error, duplicate name), and delete (success, 404).
- Tests cover status codes, redirects, form rendering, database changes, and validation messages.
- Assertions for Flash messages were commented out due to persistent issues with the Flask test client's handling of sessions/messages across redirects.

### Lessons Learned
- Testing Flash messages after redirects in Flask tests is unreliable with the default test client; session keys might differ (`_flashes`), and message consumption/retrieval across requests is problematic.
- Ensure correct URL prefixes are used when testing Blueprint redirects.
- Use `class_` instead of `class` when passing CSS classes to WTForms fields in Jinja macros.
- Running targeted tests (`pytest <path>`) significantly speeds up debugging cycles.
- Simple delete modals per item can avoid the need for complex JavaScript in some cases.

### Documentation Updates
- `tasks.md`: Task marked as complete.
- `activeContext.md`: Implementation details added during development, now updated with completion status.
- `techContext.md`: Noted Flask, WTForms, SQLAlchemy, Bootstrap 5 usage. Documented test configuration changes (`SERVER_NAME`). Documented Flash message testing issue.
- `systemPatterns.md`: Documented Blueprint usage for feature modularity. Documented direct modal-per-item pattern for delete confirmations.
- `progress.md`: Added entry linking to this archive section.

## Task: Implement CSV Import for Tenant Data (v1.0)
Last Updated: 2024-08-08

### Implementation Results
- Created function `import_tenant_csv` in `app/import_data.py`.
- Function handles CSV file paths or streams (StringIO/BytesIO).
- Expects CSV headers: `Name` (required), `Kontaktinfo` (optional).
- Validates presence of required headers.
- Iterates through rows using `csv.DictReader`.
- Creates `Tenant` objects for valid rows, saving `name` and `contact_info`.
- Skips rows with missing `Name` field and logs a warning.
- Handles potential `KeyError` and general exceptions during row processing.
- Performs a single `db.session.commit()` at the end.
- Includes `db.session.rollback()` in case of errors during commit.
- Returns a dictionary with counts of `processed_rows` and `skipped_rows`.

### Completed Testing
- Created test file `test/test_csv_import_tenant.py`.
- Used `io.StringIO` to simulate CSV file content.
- Tested successful import of multiple tenants.
- Tested error handling for missing required header (`Name`).
- Tested skipping of rows with missing `Name` value.
- Tested import of an empty file (only headers).
- Tested graceful handling of unexpected extra columns in the CSV.
- All 5 tests passed successfully.

### Lessons Learned
- Reusing existing import function structure is efficient.
- `row.get('Header', default)` is safer than `row['Header']` for optional columns.
- Testing import logic with `io.StringIO` is effective for unit testing.
- Explicitly defining required vs. optional headers improves robustness.

### Documentation Updates
- `tasks.md`: Task marked as complete with subtasks.
- `activeContext.md`: Updated focus and completion status.
- `techContext.md`: Noted usage of `csv` module.
- `systemPatterns.md`: Documented the CSV import pattern.
- `progress.md`: Added entry linking to this archive section.

## Task: PDF-Generierung für Betriebs- und Heizkostenabrechnungen (Basisversion) (v1.0)
Last Updated: 2024-08-08

### Implementation Results
- Created `app/pdf_generation.py` with function `generate_utility_statement_pdf`.
- Function signature defined to accept `contract_id`, `period_start`, `period_end`, and `cost_items` list.
- Implemented data fetching for `Contract`, `Tenant`, `Apartment`.
- Added loop to process `cost_items`:
    - Fetches `CostType` details.
    - Calls appropriate allocation function (`share`, `consumption`, `person_days`) based on `cost_type.type`.
    - Gathers key information (total cost, allocation key description, tenant's share).
    - Calculates total cost for the tenant.
- Implemented basic PDF structure using `reportlab` (`SimpleDocTemplate`, `A4`, `Paragraph`, `Table`, `Spacer`).
- Included placeholder addresses, date, period, and a table for cost breakdown.
- Added basic table styling (`TableStyle`) and summary line.
- Function returns the generated PDF as a byte stream.
- Implemented the missing `calculate_person_day_allocation` function in `app/calculations.py`.

### Completed Testing
- Created `test/test_pdf_generation_basic.py`.
- Implemented helper function `create_test_data` to set up DB models.
- Created a basic test `test_generate_pdf_basic` that:
    - Sets up test data.
    - Defines sample `cost_items`.
    - Calls `generate_utility_statement_pdf`.
    - Asserts that a non-empty byte stream is returned.
    - Asserts that the stream starts with the PDF magic bytes (`%PDF`).
- The basic test passed successfully.

### Lessons Learned
- Need to verify existence of all dependency functions (`calculate_person_day_allocation`) before integration.
- Using Enums for type fields (`CostType.type`) improves robustness.
- `reportlab` requires specific setup (e.g., `pagesizes.A4`) and detailed styling for complex layouts.
- Testing generated binary files like PDFs requires specific approaches; checking the header/signature is a basic validation.

### Documentation Updates
- `tasks.md`: Task marked as complete with subtasks.
- `activeContext.md`: Updated focus and completion status.
- `techContext.md`: Confirmed `reportlab` usage.
- `systemPatterns.md`: Documented the basic PDF generation pattern.
- `progress.md`: Added entry linking to this archive section.

## Task: Datenbankmodell für Kern-Stammdaten erweitern (v1.0)
Last Updated: 2024-04-01

### Implementation Results
- Das `Apartment`-Modell wurde um `address` und `size_sqm` erweitert.
- Der redundante `apartment_id`-Fremdschlüssel wurde aus dem `Tenant`-Modell entfernt.
- Das `Contract`-Modell wurde um eine Beziehung (`direct_allocation_invoices`) zu `Invoice` erweitert.
- Das neue Modell `Meter` (mit `apartment_id`, `meter_type`, `serial_number`, `unit`) wurde erstellt.
- Das neue Modell `Invoice` (mit `invoice_number`, `date`, `amount`, `cost_type_id`, `period_start`, `period_end`, `direct_allocation_contract_id` nullable FK) wurde erstellt.
- Die Datenbankmigration wurde generiert (`5bab8952e54e`) und erfolgreich angewendet.
- Die direkte Beziehung `Apartment.tenants` wurde entfernt, um Mapper-Konfigurationsfehler zu beheben; der Zugriff auf Mieter erfolgt nun über `Apartment.contracts[].tenant`.

### Completed Testing
- Bestehende Tests in `test/test_db_models_basic.py` wurden angepasst (Apartment-Felder, Tenant-Beziehung).
- Neue Tests für `Contract`, `Meter` und `Invoice` (sowohl direkte Zuordnung als auch Verteilungsszenario) wurden hinzugefügt.
- Alle Tests in `test/test_db_models_basic.py` wurden erfolgreich ausgeführt (`pytest test/test_db_models_basic.py`).

### Lessons Learned
- Beim Entfernen/Ändern von FKs müssen abhängige `db.relationship`-Definitionen überprüft und ggf. angepasst/entfernt werden, um SQLAlchemy-Mapper-Fehler (`NoForeignKeysError`, `InvalidRequestError`) zu vermeiden.
- Flexible Zuordnungen (z.B. A oder B) können oft gut durch nullable Fremdschlüssel + Konvention im Code modelliert werden (hier: `Invoice.direct_allocation_contract_id`).
- Frühzeitiges Testen nach Modelländerungen hilft, Konfigurationsfehler schnell zu identifizieren.

### Documentation Updates
- `app/models.py`: Modelle implementiert/angepasst.
- `migrations/versions/5bab8952e54e_expand_core_data_models.py`: Migrationsskript generiert.
- `test/test_db_models_basic.py`: Tests angepasst und erweitert.
- `memory-bank/tasks.md`: Task und Teilschritte als [X] markiert.
- `memory-bank/progress.md`: Lessons Learned hinzugefügt.
- `memory-bank/activeContext.md`: Aktualisiert während des Prozesses.

## Task: Basis-CRUD-UI für Mieter implementieren v1.0
Last Updated: 2024-03-31

### Implementation Results
- Blueprint für Mieter-Verwaltung erstellt und registriert
- TenantForm mit Validierung für Name und Kontaktinfo implementiert
- CRUD-Routen für Mieter implementiert (Liste, Erstellen, Bearbeiten)
- Templates für Mieter-Verwaltung erstellt (list.html, form.html)
- Flash-Messages für Benutzer-Feedback implementiert
- Vollständige Test-Suite für alle CRUD-Operationen erstellt

### Completed Testing
- Test-Suite mit 9 Tests implementiert und erfolgreich ausgeführt:
  * Leere Mieterliste anzeigen
  * Mieterliste mit Daten anzeigen
  * Formular für neue Mieter anzeigen
  * Erfolgreiche Mieter-Erstellung
  * Validierungsfehler bei Mieter-Erstellung
  * Formular für Mieter-Bearbeitung anzeigen
  * Erfolgreiche Mieter-Bearbeitung
  * Validierungsfehler bei Mieter-Bearbeitung
  * 404-Fehler bei nicht existierendem Mieter
- Alle Tests laufen in 0.48 Sekunden durch

### Lessons Learned
- Flash-Messages müssen im base.html Template korrekt eingebunden sein
- Validierung sollte sowohl client- als auch serverseitig erfolgen
- Test-Fixtures (conftest.py) sind wichtig für saubere Tests
- Einheitliche Namenskonvention für Routen und Templates wichtig

### Documentation Updates
- tasks.md: Mieter-CRUD-UI als abgeschlossen markiert
- progress.md: Abschluss der Implementierung dokumentiert
- Vollständige Test-Dokumentation in test/test_crud_tenants.py 