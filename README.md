# Betriebskostenabrechnung

Webbasierte Anwendung zur Verwaltung von Mietwohnungen in Österreich (bis zu 15 Einheiten, nicht MRG-unterworfen).

## Kernfunktionen

*   Automatische indexgesicherte Mieterhöhungen
*   Betriebskostenabrechnung mit flexiblen Kostenverteilschlüsseln
*   Langzeitarchivierung von Dokumenten

## Technologie-Stack

*   Python / Flask
*   SQLite
*   ReportLab (PDF)
*   pytest
*   Bootstrap

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

3.  **(Optional) Anwendung starten:**
    ```bash
    # Befehl zum Starten der Flask-Anwendung (z.B. flask run) - wird später definiert
    ``` 