# Projekt: Verwaltungssoftware Mietwohnungen

## Übergreifende Aufgaben
- [X] Initiale Anforderungsanalyse abgeschlossen (Basis: projectbrief.md)
- [X] `requirements.txt` Datei erstellen
- [X] Conda-Umgebung `env` erstellen
- [X] Git-Repository initialisieren und mit GitHub verbinden
- [X] `README.md` erstellen und pushen

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
  - [ ] Dokumentenarchivierung für Verträge integrieren (PDF-Upload/Speicherung)
    - [ ] Test für Dokumentenarchivierung erstellen (`test/test_document_storage.py`)
- [ ] Betriebskostenabrechnungs-Logik implementieren
  - [ ] Kostenverteilung (Verbrauchsbasiert)
    - [ ] Test für verbrauchsbasierte Verteilung erstellen (`test/test_cost_alloc_consumption.py`)
  - [ ] Kostenverteilung (Anteilsbasiert)
    - [ ] Test für anteilsbasierte Verteilung erstellen (`test/test_cost_alloc_share.py`)
  - [ ] Kombination von Schlüsseln ermöglichen
    - [ ] Test für kombinierte Schlüssel erstellen (`test/test_cost_alloc_combined.py`)
  - [ ] Pro-rata-temporis-Berechnung bei Mieterwechseln
    - [ ] Test für Pro-rata-Berechnung erstellen (`test/test_cost_alloc_prorata.py`)
    - [ ] Datenbankerweiterung für Mieterperioden (`tenant_periods`)
    - [ ] UI für Mieterzeitraum-Editor
- [ ] UI für benutzerdefinierte Kostenverteilschlüssel erstellen
  - [ ] Test für Logik der benutzerdef. Schlüssel erstellen (`test/test_custom_keys.py`)
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