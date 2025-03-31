# Projekt: Verwaltungssoftware Mietwohnungen

## Übergreifende Aufgaben
- [X] Initiale Anforderungsanalyse abgeschlossen (Basis: projectbrief.md)
- [X] `requirements.txt` Datei erstellen
- [X] Conda-Umgebung `env` erstellen
- [ ] Git-Repository initialisieren und mit GitHub verbinden

## Phase 1: Grundgerüst (ca. 4 Wochen)
- [ ] Flask-Setup mit Grundstruktur und Authentifizierung
- [ ] Datenbankmodell Basis implementieren (Mieter, Kostenarten, initiale Verbrauchsdaten-Tabelle)
- [ ] Basis CSV-Import für Zählerstände implementieren

## Phase 2: Kernfunktionen (ca. 6 Wochen)
- [ ] Mieterverwaltung implementieren
  - [ ] Mietverträge erfassen (inkl. Indexklauseln, Kostenverteilschlüssel-Zuordnung)
  - [ ] Dokumentenarchivierung für Verträge integrieren (PDF-Upload/Speicherung)
- [ ] Betriebskostenabrechnungs-Logik implementieren
  - [ ] Kostenverteilung (Verbrauchsbasiert)
  - [ ] Kostenverteilung (Anteilsbasiert)
  - [ ] Kombination von Schlüsseln ermöglichen
  - [ ] Pro-rata-temporis-Berechnung bei Mieterwechseln
    - [ ] Datenbankerweiterung für Mieterperioden (`tenant_periods`)
    - [ ] UI für Mieterzeitraum-Editor
- [ ] UI für benutzerdefinierte Kostenverteilschlüssel erstellen
- [ ] PDF-Generierung für Betriebskostenabrechnungen (Basisversion)
- [ ] Manuelle Datenerfassung ermöglichen (für alle Importtypen)
  - [ ] Datenbankerweiterung für manuelle Einträge (`consumption_data.entry_type`)
  - [ ] UI-Maske für manuelle Zählerstandserfassung
- [ ] Warnsystem für Abrechnungsprüfung implementieren
  - [ ] Logik für Plausibilitätschecks (fehlende Stände, Sprünge, Vorauszahlungen)
  - [ ] Warnungsdashboard/Anzeige im Abrechnungsmodul

## Phase 3: Index-Mieterhöhungen (ca. 2 Wochen)
- [ ] VPI-Datenimport ermöglichen (manuell/CSV)
- [ ] Automatische Berechnung der Indexanpassung implementieren
- [ ] Generierung von Mieterhöhungsschreiben (PDF)

## Phase 4: Test & Dokumentation (ca. 3 Wochen)
- [ ] Umfassende pytest-Tests für alle Berechnungsmodule schreiben
  - [ ] Testfall: Manuelle vs. importierte Daten Konsistenzcheck
  - [ ] Testfall: Warnungsgenerierung bei fehlenden Daten
  - [ ] Testfall: Pro-rata-Berechnung bei Mieterwechsel (inkl. Überlappung)
- [ ] Benutzerhandbuch erstellen (Schwerpunkt: Schlüsselverwaltung, Abrechnungsprozess)

## Weitere Features & Nicht-Funktionale Anforderungen
- [ ] Dokumentenmanagement erweitern (Langzeitarchivierung, Suchfilter)
- [ ] Dashboard & Berichte implementieren (Visualisierung Kostenverteilung, CSV/Excel-Export)
- [ ] Performance-Optimierung sicherstellen (< 5 Sek. für 15 WE)
- [ ] DSGVO-Konformität prüfen und sicherstellen
- [ ] Revisionssichere Archivierung von PDFs gewährleisten
- [ ] Benutzerfreundlichkeit & Responsive Design verbessern 