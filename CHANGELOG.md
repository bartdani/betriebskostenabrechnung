# Changelog

## v0.3.0 (2025-08-09)

- Gebäude-Scope eingeführt:
  - Neues `Building`-Modell mit Migration
  - `Apartment.building_id` und `Invoice.building_id`
  - Globale Gebäudeauswahl im Navbar-Header (Session-basiert)
  - Gefilterte Listen: Wohnungen, Zähler, Verträge, Rechnungen
  - Abrechnungssummen nach Gebäude filterbar
- Neue/erweiterte UIs:
  - Zähler: CRUD, Einzel- und Bulk-Erfassung der Zählerstände
  - Verträge: CRUD
  - Rechnungen: CRUD
  - Abrechnung: Presets + Vorschau, Wizard
- PDF-Generierung:
  - Konfigurierbarer Header aus `instance/config.py`
  - Unterstützung für direkt zugeordnete Kosten
  - Heiz-/Warmwasser 30/70-Split (verbrauchsbasiert)
- Daten/Tools:
  - Seed-Skript mit idempotenten Demodaten (Wohnungen, Mieter, Verträge, Zähler, Zählerstände, Rechnungen)
  - Script `scripts/check_db.py` für DB-Checks/Reparatur
- Stabilität & Tests:
  - 131 Tests grün (CRUD, Allocation, PDF, UI-Flows)


