Lastenheft: Verwaltungssoftware für Mietwohnungen (Österreich)
Stand: Final, inkl. Kostenverteilschlüssel & Präzisierung CRUD/Heizkostenlogik & Direktzuordnung

1. Einleitung
Webbasierte Anwendung zur Verwaltung von bis zu 15 nicht-MRG-unterworfenen Wohneinheiten in Österreich.
Kernfunktionen:

Automatische indexgesicherte Mieterhöhungen (ohne juristische Einzelfallprüfung).

Betriebskostenabrechnung mit flexiblen Kostenverteilschlüsseln, spezifischer Heizkostenlogik und direkter Kostenzuordnung.

Umfassende manuelle Verwaltung von Stamm- und Verbrauchsdaten (CRUD).

Langzeitarchivierung von Verträgen, Abrechnungen und Indexnachweisen.

Technologie-Stack: Python (Flask), SQLite, pytest, ReportLab (PDF), Bootstrap.

2. Funktionale Anforderungen
2.1 Wohnungsverwaltung
*   Anlegen, Anzeigen, Bearbeiten und Löschen (CRUD) von Wohnungseinheiten über die UI.
*   Erfassung relevanter Stammdaten pro Wohnung (z.B. Adresse, Größe, zugeordnete Zähler).

2.2 Mieterverwaltung
*   Anlegen, Anzeigen, Bearbeiten und Löschen (CRUD) von Mietern über die UI.
*   Erfassung von Mietverträgen mit:
    *   Indexklauseln (Basisindex, Berechnungsformel).
    *   Zugeordneten Zählern pro Wohnung.
    *   Einzugs- und Auszugsdaten.
*   Verwaltung der Bewohneranzahl pro Wohnung über Zeiträume (Erfassung von Startdatum, Enddatum, Personenanzahl) zur korrekten Berechnung der Personentage.
*   Dokumentenarchivierung für Verträge, Mieterhöhungsschreiben (PDF-Speicherung mit Schreibschutz).

2.3 Betriebskostenabrechnung
2.3.1 Kostenverteilschlüssel vs. Direkte Zuordnung

*   **Kostenverteilschlüssel (für Verteilung auf mehrere Parteien):**
    *   Definieren, *wie* Kosten auf mehrere Wohnungen/Mieter aufgeteilt werden.
    *   Werden systemweit angelegt und verwaltet (vordefiniert + benutzerdefiniert).
    *   Beispiele für vordefinierte Schlüssel:

        Schlüssel	Einheit	Art
        Gesamtwasser	m³	Verbrauch
        Heizfläche	m²	Anteil
        Heizkostenverteiler	Einheiten	Verbrauch
        Wohnfläche	m²	Anteil
        Personentage	Tage*Pers	Anteil (pro-rata)
        Brennstoffverbrauch (Heizung)	z.B. kWh Verbrauch (spezifisch)
        Brennstoffverbrauch (Warmwasser)	z.B. m³	Verbrauch (spezifisch)
        Heizkostenverbrauch über Grundkosten/Verbrauchskosten 30/70 Formel

    *   Benutzerdefinierte Schlüssel können über die UI angelegt werden (Name, Einheit, Art: Verbrauch oder Anteil).
        Beispiel: "Gartenpflege" in €, verteilt nach "Wohnfläche".

*   **Direkte Zuordnung (für Kosten einer einzelnen Partei):**
    *   Ermöglicht die Zuordnung eines Kostenbelegs direkt zu einem spezifischen Mieter/Vertrag, ohne Verteilung.
    *   Wird bei der Erfassung des Kostenbelegs als Alternative zur Auswahl eines Verteilschlüssels gewählt.

2.3.2 Abrechnungslogik

*   **Verteilung über Schlüssel:**
    *   Verbrauchsbasierte Kosten: Direkte Umlage nach gemessenem Verbrauch.
    *   Anteilsbasierte Kosten: Verteilung nach prozentualem Anteil.
    *   Personentage (Anteil pro-rata): Verteilung nach Bewohneranzahl * Anwesenheitstagen.
    *   Kombination von Schlüsseln: Aufteilung einer Kostenart auf mehrere Schlüssel.

*   **Spezifische Heizkostenlogik:**
    *   Erfassung der gesamten Brennstoffkosten (z.B. Gas, Öl) für den Abrechnungszeitraum.
        *   Aufteilung der Brennstoffkosten wenn die Kosten über mehrere Abrechnungszeiträume hinweg gehen.
    *   Erfassung der Zählerstände für die zentrale Heizungsanlage, aufgeteilt nach:
        *   Verbrauch für Raumwärme (z.B. über Wärmemengenzähler pro Wohnung oder zentraler Zähler).
        *   Verbrauch für Warmwasserbereitung (z.B. über separaten Zähler oder berechnet).
    *   Aufteilung der Brennstoffkosten auf Raumwärme und Warmwasser basierend auf den erfassten Verbräuchen oder festen Schlüsseln (falls keine getrennte Messung möglich).
    *   Verteilung der Kosten für Raumwärme auf die Wohnungen (z.B. nach Heizkostenverteiler-Einheiten oder Heizfläche).
    *   Verteilung der Kosten für Warmwasser auf die Wohnungen (z.B. nach Warmwasserzähler-Verbrauch oder Personentagen).

*   **Direkt zugeordnete Kosten:**
    *   Kosten, die bei der Erfassung direkt einem Mieter/Vertrag zugeordnet wurden, werden 1:1 auf dessen Abrechnung übernommen, ohne weitere Verteilung.
    
*   **Anteilsberechnung bei Änderungen:**
    *   Automatische Erkennung von Miet- und Bewohnerzahl-Zeiträumen.
    *   Pro-rata-temporis-Berechnung für alle verteilten Kostenarten.

2.3.3 Features

*   **Manuelle Datenerfassung & Verwaltung (CRUD):**
    *   Vollständige Verwaltung von Stammdaten (Wohnungen, Mieter inkl. Bewohnerzeiträume, Verträge, Kostenarten/Verteilschlüssel, Zähler) über UI.
    *   Erfassung und Korrektur von Verbrauchsdaten (Zählerstände etc.) über UI.
    *   **Erfassung von eingegangenen Rechnungen/Kostenbelegen:**
        *   Eingabe von Datum, Betrag, Kostenart, Zeitraum etc.
        *   **Auswahl der Zuordnung:**
            *   Entweder Auswahl eines **Kostenverteilschlüssels** für die Verteilung auf mehrere Parteien.
            *   Oder **direkte Zuordnung** zu einem spezifischen **Mieter/Vertrag**.

*   **Import:**
    *   CSV/Excel: Verbrauchsdaten, Mieterdaten.
    *   CSV/API: VPI-Daten.

*   **Abrechnungserstellung:**
    *   Generierung von PDF-Betriebskostenabrechnungen (inkl. verteilter und direkt zugeordneter Kosten).

2.3.4 Validierung und Warnungen
  - Systemprüfung vor Abrechnungserstellung (fehlende Stände, Sprünge, Vorauszahlungen, fehlende Kosten etc.).
  - Anzeige von Warnungen.

2.4 Indexgesicherte Mieterhöhungen
Automatische Berechnung und Generierung von Mieterhöhungsschreiben.

2.5 Dokumentenmanagement
Langzeitarchivierung von Abrechnungen, Indexnachweisen, Verträgen, Mieterhöhungsschreiben.
Suchfilter.

2.6 Dashboard & Berichte
Visualisierung Kostenverteilung, Export Rohdaten.

3. Nicht-funktionale Anforderungen
3.1 Technische Anforderungen
Datenbankdesign:

SQLite-Tabellen für: apartments, tenants, contracts, occupancy_periods, meters, meter_readings, cost_types, consumption_data, invoices (inkl. Zuordnungstyp: Schlüssel-ID oder Mieter/Vertrags-ID), allocations, utility_statements, documents.

Performance: Schnelle Berechnung, responsives UI.

3.2 Rechtliche Compliance: DSGVO, Revisionssicherheit.

3.3 Benutzerfreundlichkeit
Intuitive UI für die Verwaltung aller Stammdaten (Wohnungen, Mieter, Verträge, Schlüssel etc.).
Klare Darstellung von Zeiträumen (Verträge, Bewohneranzahl).
Responsive Design (Mobile/Desktop).

4. Systemarchitektur
4.1 Komponenten
Frontend: Flask/Jinja2/Bootstrap/Flask-WTF, Formulare.
Backend: Berechnungsmodule (Index, Kostenverteilung inkl. Heizung & Direktzuordnung), PDF-Generierung, DB-Interaktion.
Datenbank: SQLite.

4.2 Datenfluss
Datenerfassung (Manuell/Import) → Datenbank (inkl. Zuordnungstyp für Kosten).
Kostenberechnung (Verteilung via Schlüssel / Direktzuordnung) → Aggregation.
PDF-Generierung → Archivierung.

5. Abgrenzungen
Keine Integration Buchhaltung/Payment, keine digitalen Signaturen/Mieterzugriff, keine MRG-Logik.

6. Projektphasen (Angepasst)
Phase 1: Grundgerüst & Basis-CRUD (ca. 4-5 Wochen)
Phase 2: Kernfunktionen Abrechnung & Erweiterte CRUD (ca. 7-8 Wochen) - *inkl. Logik für Direktzuordnung bei Kostenerfassung*
Phase 3: Index & Abschluss CRUD (ca. 3-4 Wochen)
Integration des VPI-Datenimports.
Automatische Mieterhöhungsberechnung und PDF-Generierung.
Fertigstellung CRUD (Löschen-Funktionen, Detailansichten).
Dokumentenmanagement (Vertragsarchivierung).

Phase 4: Test, Doku & Feinschliff (ca. 4 Wochen)
pytest-Tests für alle Module (inkl. CRUD und Heizkostenlogik).
Benutzerhandbuch (Schwerpunkt: Stammdatenverwaltung, Schlüssel, Abrechnung).
Dashboard & Berichte.
Dokumentenmanagement-Features (Suche).
Performance-Tests & Optimierung.

Phase 5: Datensicherung über Google Drive API

7. Akzeptanzkriterien
Kostenverteilung:
*   Schlüssel korrekt implementiert.
*   Heizkostenlogik funktioniert.
*   **Direkte Kostenzuordnung zu Mietern funktioniert.**
CRUD-Operationen: Stammdaten und Kostenbelege können verwaltet werden.
PDF-Abrechnungen: Enthalten verteilte und direkte Kosten korrekt.
Performance: Ziele erreicht.

8. Offene Punkte (Geklärt)
Juristische Prüfung Indexklauseln → Anwender.
Datenquellen VPI → CSV/API.