# Technische Umgebung und Tooling

## Entwicklungsumgebung
- **Betriebssystem:** Windows
- **Shell:** PowerShell

## Programmiersprachen & Frameworks
- **Python:** Hauptsprache (Version angeben, falls relevant)
- **Flask:** Web-Framework

## Datenbank
- **SQLite:** Datenbank für lokale Speicherung

## Bibliotheken
- **pytest:** Für Unit-Tests
- **ReportLab:** Zur PDF-Generierung
- **Bootstrap:** Frontend-Styling

## Testing
- **Framework:** pytest
- **Struktur:** Tests befinden sich im `test`-Verzeichnis.
- **Konvention:** Testdateien beginnen mit `test_*.py`.
- **Richtlinie:** Für jedes implementierte Feature/Modul soll mindestens ein Testfall erstellt werden und dann auch nur die betroffenen Tests ausgeführt werden.

## Entwicklungstools
- **IDE:** Cursor
- **Versionskontrolle:** Git
  - **Repository:** Lokal initialisiert
  - **Remote:** origin -> https://github.com/bartdani/betriebskostenabrechnung.git
- **Paketverwaltung:** Conda
  - **Umgebung:** `./env` (Erstellt mit `conda create --prefix ./env python=3.10 -y`) 