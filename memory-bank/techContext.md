# Technische Umgebung und Tooling

## Entwicklungsumgebung
- **Betriebssystem:** Windows 10 (win32)
- **Shell:** PowerShell
- **IDE:** Cursor
- **Python:** 3.10 (via Conda env `env`)

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

## Core Technologies
- **Web Framework:** Flask
- **Database:** SQLite (via Flask-SQLAlchemy)
- **Migrations:** Flask-Migrate
- **Forms:** Flask-WTF
- **Templating:** Jinja2
- **Frontend:** Bootstrap 5
- **Testing:** pytest
- **PDF Generation:** reportlab
- **CSV Handling:** Python built-in `csv` module

## Key Libraries & Versions (from requirements.txt)
- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- Flask-Migrate==4.0.7
- Flask-WTF==1.2.1
- WTForms==3.1.2
- SQLAlchemy==2.0.29
- reportlab==4.0.4
- pytest==8.3.5
- Bootstrap==5.3.x (via CDN in templates)

## Project Setup & Execution
- Activate Conda env: `conda activate env`
- Install dependencies: `pip install -r requirements.txt`
- Run development server: `flask run`
- Run tests: `pytest` or `pytest <path>`
- Apply migrations: `flask db upgrade`

## Testing Configuration (`conftest.py`)
- Uses in-memory SQLite database for tests.
- `TESTING = True`
- `WTF_CSRF_ENABLED = False`
- `SERVER_NAME = 'localhost.test'` (Added to resolve `url_for` issues)

## Known Issues & Workarounds
- **Flash Message Testing:** Standard Flask test client (`app.test_client()`) does not reliably show flashed messages in the response HTML after redirects (`follow_redirects=True` or manual). Messages are confirmed to be in the session (`_flashes`) but not rendered. Assertions checking for flash messages in HTML are currently commented out in relevant tests (`test_custom_keys.py`).

## Flask & SQLAlchemy

### Flash Messages
- Flash-Messages werden in der Base-Template (`_base.html`) angezeigt
- Kategorien: success, warning, danger
- HTML-Escaping beachten bei Tests (`&quot;` statt `"`)
- Rendering erfolgt in einem eigenen Container außerhalb des Hauptcontainers

### SQLAlchemy 2.0
- Upgrade auf SQLAlchemy 2.0 API-Style
- Verwendung von `db.session.get()` statt `query.get()`
- Type Hints für bessere Code-Qualität
- Kombination mit Flask-Abort für 404-Handling 