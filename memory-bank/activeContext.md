# Active Context

## Current Focus
Implementierung der Basis-CRUD-UI für Wohnungen (`Apartment`: List, Create, Edit).

## Recent Changes & Activities
- Start der Arbeit an der CRUD-UI für Wohnungen.

## Pending Issues/Decisions
- Genaue Feldvalidierungen für das Wohnungsformular definieren.
- Design der Listen- und Formularansichten.

## Next Steps
- Planung der detaillierten Schritte für Blueprint, Forms, Routes, Templates und Tests.

## Recent Completions
- README.md aktualisieren wurde abgeschlossen. Nächster Fokus liegt auf Basis-CRUD-UI für Wohnungen.

## Current Implementation Status
- Initialisierung für CRUD-UI Wohnungen abgeschlossen.

## Recent Learnings

### Flash Messages & Testing (2024-04-01)
- Flash-Messages müssen im HTML-Response getestet werden, nicht in der Session
- HTML-Escaping bei Flash-Message Tests beachten (`&quot;` statt `"`)
- Flash-Messages in eigenem Container außerhalb des Hauptcontainers rendern

### SQLAlchemy Updates (2024-04-01)
- Migration auf SQLAlchemy 2.0 API-Style
- Verwendung von `db.session.get()` statt `query.get()`
- Verbesserte 404-Fehlerbehandlung mit `abort(404)`

### Form Testing (2024-04-01)
- Implementierung von `macros.html` für konsistentes Form-Rendering
- Validierungsfehler im HTML-Response testen
- Vollständige Test-Coverage für erfolgreiche und fehlgeschlagene Validierungen 