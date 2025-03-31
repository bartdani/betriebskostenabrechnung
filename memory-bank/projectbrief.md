Lastenheft: Verwaltungssoftware für Mietwohnungen (Österreich)
Stand: Final, inkl. Kostenverteilschlüssel

1. Einleitung
Webbasierte Anwendung zur Verwaltung von bis zu 15 nicht-MRG-unterworfenen Wohneinheiten in Österreich.
Kernfunktionen:

Automatische indexgesicherte Mieterhöhungen (ohne juristische Einzelfallprüfung).

Betriebskostenabrechnung mit flexiblen Kostenverteilschlüsseln.

Langzeitarchivierung von Verträgen, Abrechnungen und Indexnachweisen.

Technologie-Stack: Python (Flask), SQLite, pytest, ReportLab (PDF), Bootstrap.

2. Funktionale Anforderungen
2.1 Mieterverwaltung
Erfassung von Mietverträgen mit:

Indexklauseln (Basisindex, Berechnungsformel).

Zugeordneten Kostenverteilschlüsseln pro Wohnung.

Dokumentenarchivierung (PDF-Speicherung mit Schreibschutz).

2.2 Betriebskostenabrechnung
A. Kostenverteilschlüssel

Vordefinierte Schlüssel (siehe Tabelle) + benutzerdefinierte Schlüssel:

Schlüssel	Einheit	Art
Gesamtwasser	m³	Verbrauch
Heizfläche	m²	Anteil
Heizkostenverteiler	Einheiten	Verbrauch
Wohnfläche	m²	Anteil
... (alle gelisteten)		
Benutzerdefinierte Schlüssel:

Anlage neuer Schlüssel über UI (Name, Einheit, Art: Verbrauch oder Anteil).

Beispiel: "Gartenpflege" in €, verteilt nach "Wohnfläche".

B. Abrechnungslogik

Verbrauchsbasierte Kosten: Direkte Umlage nach gemessenem Verbrauch (z. B. Strom in kWh).
Anteilsbasierte Kosten: Verteilung nach prozentualem Anteil (z. B. Wohnfläche in m²).
Kombination von Schlüsseln:
Beispiel: Heizkosten = 50 % Verbrauch (Wärmemengenzähler) + 50 % Anteil (Wohnfläche).

+ Anteilsberechnung bei Mieterwechseln:
  - Automatische Erkennung von Mietzeiträumen pro Wohnung
  - Pro-rata-temporis-Berechnung für Verbrauchs- und Anteilskosten
  - Berücksichtigung von Einzugs- und Auszugsdaten aus Mietverträgen

C. Features

+ Manuelle Datenerfassung:
  - Für alle importierbaren Daten (Zählerstände, Indexwerte, Verbrauchsdaten) 
  - Maske mit Validierung entsprechend CSV-Importformat
  - Historische Korrekturen möglich mit Versionierung
  - Erfassung aller Daten auch über Eingabemasken möglich

Import von Verbrauchsdaten per CSV/Excel (z. B. Zählerstände).
Manuelle Eingabe von Werten über eine Maske.
Generierung von PDF-Abrechnungen mit detaillierter Aufschlüsselung der Kosten.

+D. Validierung und Warnungen
  - Systemprüfung vor Abrechnungserstellung:
    * Fehlende Zählerstände für mindestens 95% der Abrechnungsperiode
    * Unplausible Sprünge in Verbrauchswerten (>50% Änderung zum Vorjahr)
    * Nicht abgeglichene Vorauszahlungen
  - Warnungen erscheinen als:
    * Übersichtsliste mit betroffenen Wohnungen
    * Farbliche Hervorhebungen in der UI
    * Option zur Bestätigung/Überschreibung

2.3 Indexgesicherte Mieterhöhungen
Automatische Berechnung des Mietzinses basierend auf dem österreichischen Verbraucherpreisindex (VPI).

Generierung von Mieterhöhungsschreiben mit:

Basisindex, aktuellem Index, Berechnungsformel.

Keine juristische Prüfung (da vertraglich vereinbart).

2.4 Dokumentenmanagement
Langzeitarchivierung aller Abrechnungen, Indexnachweise und Mietverträge.

Suchfilter nach Jahr, Schlüsseltyp oder Wohnung.

2.5 Dashboard & Berichte
Visualisierung der Kostenverteilung pro Schlüssel (z. B. Kreisdiagramm für Anteile).

Export von Rohdaten in CSV/Excel.

3. Nicht-funktionale Anforderungen
3.1 Technische Anforderungen
Datenbankdesign:

SQLite-Tabellen für:

cost_types (vordefinierte + benutzerdefinierte Schlüssel).

consumption_data (Verbrauchswerte pro Wohnung).

allocations (Zuordnung von Kosten zu Schlüsseln).

Performance:

Schnelle Berechnung auch bei 15 Wohneinheiten und 20+ Kostenverteilschlüsseln.

3.2 Rechtliche Compliance
DSGVO-konforme Speicherung personenbezogener Daten.

Revisionssichere Archivierung (keine nachträgliche Änderung von Abrechnungs-PDFs).

3.3 Benutzerfreundlichkeit
Intuitive UI für die Anlage von Schlüsseln (Dropdowns für Art, Einheitenfeld).

Responsive Design (Mobile/Desktop).

4. Systemarchitektur
4.1 Komponenten
Frontend:

Flask/Jinja2-Templates mit Bootstrap.

Dynamische Formulare für Schlüsselverwaltung und Datenimport.

Backend:

Berechnungsmodule für:

Indexanpassungen (Mietzins).

Kostenverteilung (Verbrauch/Anteil).

PDF-Generierung mit ReportLab.

Datenbank:

SQLite mit Tabellen für Mieter, Verträge, Kostenarten und Abrechnungen.

4.2 Datenfluss
Datenimport (CSV/Manuell) → consumption_data.

Kostenberechnung → Aggregation nach Schlüsseln.

PDF-Generierung → Archivierung in documents.

5. Abgrenzungen
Nicht enthalten:

Integration mit Buchhaltungssystemen oder Zahlungsgateways.

Digitale Signaturen oder Mieterzugriff.

MRG-spezifische Logik (z. B. Richtwertmieten).

6. Projektphasen
Phase 1: Grundgerüst (4 Wochen)
Flask-Setup mit Authentifizierung.

Datenbankmodell für Mieter, Kostenarten und Verbrauchsdaten.

CSV-Import für Zählerstände.

Phase 2: Kernfunktionen (6 Wochen)
Implementierung der Kostenverteilungslogik (Verbrauch/Anteil).

UI für benutzerdefinierte Schlüssel.

PDF-Generierung für Abrechnungen.

Phase 3: Index-Mieterhöhungen (2 Wochen)
Integration des VPI-Datenimports (manuell/CSV).

Automatische Mieterhöhungsberechnung.

Phase 4: Test & Dokumentation (3 Wochen)
pytest-Tests für alle Berechnungsmodule.

Benutzerhandbuch (Schwerpunkt: Schlüsselverwaltung).

7. Akzeptanzkriterien
Kostenverteilung:

Alle vordefinierten Schlüssel sind korrekt implementiert (z. B. "Wohnfläche" als Anteil).

Benutzerdefinierte Schlüssel können ohne Code-Änderung angelegt werden.

PDF-Abrechnungen:

Enthalten eine detaillierte Aufschlüsselung der Kosten pro Schlüssel.

Performance:

Die Berechnung einer Abrechnung mit 15 Wohnungen dauert < 5 Sekunden.

8. Offene Punkte (Geklärt)
Juristische Prüfung der Indexklauseln → Muss vom Anwender sichergestellt werden.

Datenquellen für Indexwerte → Manueller Upload von VPI-CSV-Daten (Statistik Austria).