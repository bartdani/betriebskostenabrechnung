# System Patterns & Architectural Decisions

## Overview
This document outlines key architectural patterns, design decisions, and reusable solutions employed in the project.

## Core Patterns
- **Web Framework:** Flask microframework with Blueprints for modular feature organization (e.g., `cost_types` Blueprint).
- **Database:** Relational database (SQLite for development/testing) accessed via SQLAlchemy ORM.
- **Migrations:** Flask-Migrate handles database schema changes.
- **Forms:** Flask-WTF provides form creation, validation, and CSRF protection (disabled in tests).
- **Templating:** Jinja2 for server-side HTML rendering, using a base template (`base.html`) and Bootstrap 5 for styling.
- **Testing:** pytest framework with fixtures (`conftest.py`) for setting up test clients and databases.

## Specific Implementation Patterns
- **Delete Confirmation:** Uses Bootstrap Modals directly triggered by buttons in the list view (`data-bs-target="#modalId{{ item.id }}"`). Each item gets its own pre-configured modal, avoiding the need for JavaScript for basic confirmation.
- **CSV Import:** Function-based approach (`app/import_data.py`) handling file path or stream input, validating headers, iterating rows with `csv.DictReader`, looking up related DB objects, validating/converting data per row, skipping invalid rows with warnings, and performing a single DB commit at the end.
- **PDF Generation (Basic):** Dedicated function (e.g., in `app/pdf_generation.py`) that takes key identifiers (contract_id, period) and cost data as input. Fetches detailed data from various models, calls calculation functions for allocations, and uses `reportlab` (Tables, Paragraphs) to structure and generate the PDF output.

## Architectural Decisions
- **Cost Type Association:** Costs are associated with `Apartment` entities, not directly with `Tenant` entities initially. `Tenant` association happens via `Contract`.
- **Consumption Data:** Stored per `Apartment` and `CostType` with a date.
- **Tenant-Apartment Link:** Currently optional in `Tenant` model (`apartment_id`), primary link established via `Contract` model.

## Core Architecture

[Describe the overall system architecture (e.g., MVC, Microservices, Monolith)]

## Key Design Patterns

[List and briefly describe major design patterns employed (e.g., Singleton, Factory, Observer)]

## Data Management

[Describe patterns related to data storage, access, and validation]

## UI/Frontend Patterns

[Describe common patterns used in the user interface (e.g., Component-based, State Management)]

## Backend Patterns

[Describe common patterns used in the backend logic]

## Berechnungsmuster

### Personentage-Berechnung
- Implementierung in `calculations.py`
- Berücksichtigung aller Wohnungen bei der Kostenverteilung
- Rückgabe von 0.00 für alle Wohnungen wenn keine Personentage vorhanden
- Validierung der Kostenart direkt im WTForms-Formular
- Typ-sichere Implementierung durch Type Hints 

## Testing Patterns

### Flash Message Testing
Bei Tests von Flash-Nachrichten folgende Best Practices beachten:

1. **Vermeidung exakter Nachrichtenvergleiche**
   - NICHT: `assert 'Wohnung "TestWohnung" erfolgreich angelegt.' in response_text`
   - BESSER: 
     ```python
     response_text = response.data.decode('utf-8')
     assert 'TestWohnung' in response_text  # Prüfe Objektname
     assert 'alert-success' in response_text  # Prüfe Nachrichtentyp
     assert 'erfolgreich' in response_text  # Prüfe Schlüsselwort
     ```

2. **Gründe für diese Praxis**
   - HTML-Escaping macht exakte Vergleiche problematisch (`"` wird zu `&quot;`)
   - Kleine Textänderungen würden Tests brechen
   - Mehrsprachigkeit wird einfacher unterstützbar

3. **Empfohlene Schlüsselwörter**
   - Erfolg: 'erfolgreich', 'success'
   - Warnung: 'existiert bereits', 'warning'
   - Fehler: 'Fehler', 'danger'
   - Bootstrap-Klassen: 'alert-success', 'alert-warning', 'alert-danger'

4. **Template-Struktur**
   ```html
   <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
       {{ message }}
       <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
   </div>
   ```

5. **Flash-Kategorien**
   - success: Erfolgreiche Aktionen
   - warning: Warnungen (z.B. Duplikate)
   - danger: Fehler
   - info: Informationen

6. **Beispiel-Implementation**
   ```python
   def test_create_apartment_success(client):
       response = client.post('/apartments/new', 
                            data={'number': '42', 'address': 'Test'}, 
                            follow_redirects=True)
       response_text = response.data.decode('utf-8')
       
       # Prüfe Erfolg durch mehrere Teil-Assertions
       assert '42' in response_text  # Wohnungsnummer wurde erstellt
       assert 'alert-success' in response_text  # Erfolgs-Nachricht
       assert 'erfolgreich' in response_text  # Positives Feedback
   ```

### SQLAlchemy Best Practices
- Verwende `db.session.get(Model, id)` statt `Model.query.get(id)` (SQLAlchemy 2.0)
- Kombiniere mit `abort(404)` für nicht gefundene Einträge: `db.session.get(Model, id) or abort(404)`

### Form Testing
- Validierungsfehler werden im HTML-Response überprüft
- Nutze das `macros.html` Template für konsistentes Form-Rendering
- Teste sowohl erfolgreiche als auch fehlgeschlagene Validierungen 