# Projekt: Verwaltungssoftware Mietwohnungen

## Übergreifende Aufgaben
- [X] Initiale Anforderungsanalyse abgeschlossen (Basis: projectbrief.md)
- [X] `requirements.txt` Datei erstellen
- [X] Conda-Umgebung `env` erstellen
- [X] Git-Repository initialisieren und mit GitHub verbinden
- [X] `README.md` erstellen und pushen
- [X] SQLAlchemy LegacyAPIWarnings beheben

## Phase 1: Grundgerüst (ca. 4 Wochen)
- [X] Flask-Setup mit Grundstruktur (Authentifizierung optional/später)
  - [X] Test für Grundstruktur/Erreichbarkeit erstellen (`test/test_app_basic.py`)
- [X] Datenbankmodell Basis implementieren (Mieter, Kostenarten, initiale Verbrauchsdaten-Tabelle)
  - [X] Test für DB-Modell Basis erstellen (`test/test_db_models_basic.py`)
- [X] Basis CSV-Import für Zählerstände implementieren
  - [X] Test für CSV-Import Basis erstellen (`test/test_csv_import_basic.py`)

## Phase 2: Kernfunktionen (ca. 6 Wochen)
- [X] Mieterverwaltung implementieren
  - [X] Mietverträge erfassen (inkl. Indexklauseln, Kostenverteilschlüssel-Zuordnung)
    - [X] Test für Mietervertragslogik erstellen (`test/test_tenant_contracts.py`)
  - [X] Dokumentenarchivierung für Verträge integrieren (PDF-Upload/Speicherung)
    - [X] Test für Dokumentenarchivierung erstellen (`test/test_document_storage.py`)
- [X] Betriebskostenabrechnungs-Logik implementieren
  - [X] Kostenverteilung (Verbrauchsbasiert)
    - [X] Test für verbrauchsbasierte Verteilung erstellen (`test/test_cost_alloc_consumption.py`)
  - [X] Kostenverteilung (Anteilsbasiert)
    - [X] Test für anteilsbasierte Verteilung erstellen (`test/test_cost_alloc_share.py`)
  - [X] Kostenverteilung (Personentage pro-rata) - Completed on 2024-08-02
    - [X] Datenmodell für Bewohnerzahl-Zeiträume erstellen/erweitern (z.B. `OccupancyPeriod`)
      - [X] Define `OccupancyPeriod` model in `app/models.py` (`apartment_id`, `start_date`, `end_date`, `number_of_occupants`)
      - [X] Generate DB migration script for `OccupancyPeriod`
      - [X] Apply DB migration
    - [X] Logik für Personentage-Berechnung implementieren
      - [X] Implement helper function to get relevant occupancy periods for a given apartment and billing period in `app/calculations.py`
      - [X] Implement `calculate_person_days` function in `app/calculations.py`
      - [X] Implement `calculate_person_day_allocation` function in `app/calculations.py`
    - [X] Test für Personentage-Verteilung erstellen (`test/test_cost_alloc_persondays.py`)
      - [X] Create test file `test/test_cost_alloc_persondays.py`
      - [X] Write test cases for `OccupancyPeriod` model
      - [X] Write test cases for `calculate_person_days` helper function
      - [X] Write test cases for `calculate_person_day_allocation`
      - [X] Ensure all tests pass
  - [X] Kombination von Schlüsseln ermöglichen (2024-08-01)
    - [X] Funktion `calculate_combined_allocation` in `app/calculations.py` implementieren
    - [X] Test `test/test_cost_alloc_combined.py` erstellen
    - [X] Reflektion und Archivierung
  - [X] Refactoring: Konsistente Rückgabewerte für Verteilungsfunktionen (immer Dict) (2024-08-01)
    - [X] `app/calculations.py` anpassen
    - [X] Relevante Tests anpassen (`test/test_cost_alloc_*.py`)
- [ ] UI für benutzerdefinierte Kostenverteilschlüssel erstellen - [IN PROGRESS]
  - [ ] Abhängigkeiten hinzufügen
    - [ ] `Flask-WTF` zu `requirements.txt` hinzufügen
    - [ ] Abhängigkeiten installieren (`pip install -r requirements.txt`)
  - [ ] Formular definieren (`app/forms.py`)
    - [ ] `CostTypeForm` mit Feldern `name`, `unit`, `type` (SelectField) erstellen
  - [ ] Flask Blueprint erstellen (`app/cost_types/routes.py`)
    - [ ] Blueprint `cost_types_bp` definieren
    - [ ] Blueprint in `app/__init__.py` registrieren
  - [ ] (Creative Phase - UI Design)
    - [ ] Layout für Listenseite entwerfen (Tabelle, Buttons)
    - [ ] Design für Formularseite entwerfen (Erstellen/Bearbeiten)
    - [ ] Bootstrap-Styling planen
    - [ ] Anzeige von Validierungsfehlern planen
  - [ ] Routen und Logik implementieren (`app/cost_types/routes.py`)
    - [ ] Route für Liste (GET)
    - [ ] Route für Erstellen (GET, POST)
    - [ ] Route für Bearbeiten (GET, POST)
    - [ ] Route für Löschen (POST/DELETE mit Bestätigung)
  - [ ] Templates erstellen (`app/templates/cost_types/`)
    - [ ] `list_cost_types.html` erstellen
    - [ ] `create_edit_cost_type.html` erstellen
    - [ ] Basis-Template anpassen/erweitern
    - [ ] Flask-WTF Makros verwenden
  - [ ] Test für Logik der benutzerdef. Schlüssel erstellen (`test/test_custom_keys.py`)
    - [ ] Testdatei erstellen
    - [ ] Tests für GET-Routen schreiben
    - [ ] Tests für POST-Routen (Erstellen, Bearbeiten, Löschen) schreiben
    - [ ] Validierungstests schreiben
  - [ ] Tests ausführen und debuggen
- [ ] PDF-Generierung für Betriebskostenabrechnungen (Basisversion)
  - [ ] Test für PDF-Generierung Basis erstellen (`test/test_pdf_generation_basic.py`)
- [ ] Manuelle Datenerfassung ermöglichen (für alle Importtypen)
  - [ ] Test für manuelle Datenerfassung erstellen (`test/test_manual_data_entry.py`)
  - [ ] Datenbankerweiterung für manuelle Einträge (`consumption_data.entry_type`)
  - [ ] UI-Maske für manuelle Zählerstandserfassung
- [ ] Warnsystem für Abrechnungsprüfung implementieren
  - [ ] Test für Warnsystem-Logik erstellen (`test/test_validation_warnings.py`)
  - [ ] Logik für Plausibilitätschecks (fehlende Stände, Sprünge, Vorauszahlungen)
  - [ ] Warnungsdashboard/Anzeige im Abrechnungsmodul

## Phase 3: Index-Mieterhöhungen (ca. 2 Wochen)
- [ ] VPI-Datenimport ermöglichen (manuell/CSV)
  - [ ] Test für VPI-Datenimport erstellen (`test/test_vpi_import.py`)
- [ ] Automatische Berechnung der Indexanpassung implementieren
  - [ ] Test für Indexanpassungsberechnung erstellen (`test/test_index_calculation.py`)
- [ ] Generierung von Mieterhöhungsschreiben (PDF)
  - [ ] Test für PDF-Generierung (Erhöhung) erstellen (`test/test_pdf_generation_increase.py`)

## Phase 4: Test & Dokumentation (ca. 3 Wochen)
- [ ] Umfassende Integrations- und End-to-End-Tests schreiben (Ergänzung zu Unit-Tests)
  - [ ] Testfall: Kompletter Abrechnungslauf mit Mieterwechsel
  - [ ] Testfall: Manuelle vs. importierte Daten Konsistenzcheck (Integration)
  - [ ] Testfall: Warnungsgenerierung bei fehlenden Daten (Integration)
- [ ] Benutzerhandbuch erstellen (Schwerpunkt: Schlüsselverwaltung, Abrechnungsprozess)

## Weitere Features & Nicht-Funktionale Anforderungen
- [ ] Dokumentenmanagement erweitern (Langzeitarchivierung, Suchfilter)
  - [ ] Test für erweiterte Doku-Features erstellen (`test/test_document_mgmt_advanced.py`)
- [ ] Dashboard & Berichte implementieren (Visualisierung Kostenverteilung, CSV/Excel-Export)
  - [ ] Test für Dashboard/Berichtslogik erstellen (`test/test_dashboard_reports.py`)
- [ ] Performance-Optimierung sicherstellen (< 5 Sek. für 15 WE)
  - [ ] Performance-Tests implementieren (`test/test_performance.py`)
- [ ] DSGVO-Konformität prüfen und sicherstellen
- [ ] Revisionssichere Archivierung von PDFs gewährleisten
- [ ] Benutzerfreundlichkeit & Responsive Design verbessern

## In Progress
- [ ] Implement CRUD for Custom Cost Types (Kostenarten)
  - [X] Define DB Model (`CostType`)
  - [X] Create Forms (`CostTypeForm`)
  - [X] Implement CRUD Routes (Blueprint: `cost_types`)
  - [X] Create HTML Templates (`list`, `create_edit`)
  - [X] Write Tests (`test_custom_keys.py`)
  - [ ] Add JavaScript for Delete Confirmation Modal

## Planned / Backlog
- [ ] Implement Tenant Contracts CRUD
- [ ] Implement Document Upload/Storage
- [ ] Implement Cost Allocation Logic (Share, Consumption, PersonDays, Combined)
- [ ] Implement CSV Import for Tenant Data
- [ ] User Authentication & Authorization
- [ ] Reporting Features
- [ ] Improve UI/UX

## Completed Tasks
- [X] Initial Project Setup - Completed on YYYY-MM-DD 