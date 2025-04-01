# Betriebskostenabrechnung

Webbasierte Anwendung zur Verwaltung von Mietwohnungen in Österreich (bis zu 15 Einheiten, nicht MRG-unterworfen).

## Projektstatus (Stand: 2024-04-01)

*   Grundgerüst mit Flask erstellt.
*   Datenbankmodelle für Kern-Stammdaten (Wohnungen, Mieter, Verträge, Zähler, Rechnungen) implementiert und migriert.
*   Basis-Layout und Navigation vorhanden.
*   CSV-Import für Zählerstände und Mieter implementiert.
*   Basis-PDF-Generierung für Abrechnungen implementiert.

## Kernfunktionen (Geplant & Teilweise Implementiert)

*   Stammdatenverwaltung (Wohnungen, Mieter, Verträge, Zähler, Kostenarten) via UI (CRUD - *in Arbeit*).
*   Automatische indexgesicherte Mieterhöhungen.
*   Betriebskostenabrechnung mit flexiblen Kostenverteilschlüsseln (inkl. Personentage, spezifische Heizkostenlogik, direkte Kostenzuordnung).
*   Manuelle Datenerfassung und CSV-Import für Verbrauchsdaten.
*   PDF-Generierung für Abrechnungen und Mieterhöhungen.
*   Langzeitarchivierung von Dokumenten.
*   Dashboard & Berichte.
*   Datensicherung (Google Drive).

## Technologie-Stack

*   Python / Flask
*   SQLAlchemy / Flask-Migrate
*   SQLite (Entwicklung)
*   ReportLab (PDF)
*   pytest
*   Bootstrap 5
*   Flask-WTF

## Setup

1.  **Conda-Umgebung erstellen und aktivieren:**
    ```bash
    # Umgebung erstellen (falls noch nicht geschehen)
    # conda create --prefix ./env python=3.10 -y 
    conda activate ./env
    ```

2.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Datenbank initialisieren/aktualisieren:**
    ```bash
    # Beim ersten Mal oder nach Modelländerungen
    flask db upgrade
    ```

## Ausführung

*   **Entwicklungsserver starten:**
    ```bash
    flask run
    ```
    Die Anwendung ist dann unter http://127.0.0.1:5000 erreichbar.

*   **Tests ausführen:**
    ```bash
    pytest
    # oder spezifische Tests
    # pytest test/test_db_models_basic.py
    ``` 