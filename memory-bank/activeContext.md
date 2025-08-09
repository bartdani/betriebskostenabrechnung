# Active Context

## Current Focus
Phase 2: PDF-Details verfeinern (Formatierung, Summen, Kopf-/Fußzeile). Warnsystem abgeschlossen.

## Recent Changes & Activities
- Zähler-CRUD (Blueprint, Forms, Routes, Templates) implementiert und Tests ergänzt (`test/test_crud_meters.py`).
- Navigation um Link zu Zählern erweitert.

## Pending Issues/Decisions
- Genaue Feldvalidierungen für das Wohnungsformular definieren.
- Design der Listen- und Formularansichten.

## Next Steps
- Priorisierung Phase 2:
  - UI für Erfassung von Kostenbelegen/Rechnungen (Invoices)
  - Erweiterte CRUD-UI für Verträge (Contracts)
  - Manuelle Datenerfassung für Zählerstände/Verbräuche

## Recent Completions
- Basis-CRUD-UI für Zähler abgeschlossen (2025-08-08).
- UI für Verwaltung von Bewohnerzahl-Zeiträumen abgeschlossen (2025-08-08).
- UI für Erfassung von Kostenbelegen/Rechnungen abgeschlossen (2025-08-08).
- Erweiterte CRUD-UI für Verträge abgeschlossen (2025-08-08).
- Logik für direkte Kostenzuordnung implementiert (2025-08-08).
- Heiz-/Warmwasser-Logik (verbrauchsbasiert, Split) implementiert (2025-08-08).
- PDF-Generierung um Heizpaket (Split) erweitert (2025-08-08).
- Warnsystem für Abrechnungsprüfung (Plausibilitätschecks) implementiert (2025-08-08).

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