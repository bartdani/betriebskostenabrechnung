## Completed Tasks
- Kostenverteilung (Personentage pro-rata) - Completed on 2024-08-02, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-kostenverteilung-personentage-pro-rata-v10)
- Kombinierte Schlüsselverteilung implementieren - Completed on 2024-08-01, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-kombinierte-schlusselverteilung-implementieren-v10)
- Flask-Setup mit Grundstruktur - Completed on 2024-07-31, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-flask-setup-mit-grundstruktur-v10)
- Datenbankmodell Basis implementieren - Completed on 2024-07-31, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-datenbankmodell-basis-implementieren-v10)
- Basis CSV-Import für Zählerstände implementieren - Completed on 2024-07-31, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-basis-csv-import-fuer-zaehlerstaende-implementieren-v10)
- Aufgabenliste aktualisieren (Basis: projectbrief.md) - Completed on 2024-07-29, see [archive entry](mdc:../docs/archive/completed_tasks.md#task-aufgabenliste-aktualisieren-basis-projectbriefmd-v10)

## REFLECTION

### What Went Well
- Das Hinzufügen des neuen `OccupancyPeriod`-Modells und die Datenbankmigration verliefen reibungslos.
- Die Aufteilung der Berechnungslogik in Hilfsfunktionen (`_get_relevant_occupancy_periods`, `calculate_person_days`) und die Hauptverteilungsfunktion (`calculate_person_day_allocation`) war klar und erleichterte die Implementierung.
- Die Implementierung der Datumslogik zur Berechnung der Überlappungstage zwischen Belegungs- und Abrechnungszeiträumen war korrekt.
- Die Testfälle deckten verschiedene Szenarien ab (volle/teilweise Überlappung, keine Überlappung, mehrere Perioden, keine Perioden).
- Das Debugging der Testfehler (fehlende Fixtures, fehlende Testdaten) war systematisch und führte zur erfolgreichen Behebung.

### Challenges
- Beim ersten Testlauf schlugen alle neuen Tests fehl, da die pytest Fixtures (`client`, `test_db`) aus `conftest.py` nicht korrekt verwendet wurden.
- Beim zweiten Testlauf schlugen die Tests fehl, da die Testdaten (insbesondere `Apartment`-Objekte) nicht innerhalb der Testfunktionen erstellt wurden, was zu `AttributeError` führte.
- Die Konsolenausgabe beim ersten `flask db upgrade` war durch einen `PSReadLine`-Fehler unklar, was eine erneute Ausführung zur Verifizierung notwendig machte.

### Lessons Learned
- Bei der Erstellung neuer Testdateien muss sorgfältig darauf geachtet werden, die korrekten Fixtures aus `conftest.py` zu importieren und zu verwenden.
- Jeder Test sollte seine eigenen, unabhängigen Testdaten erstellen, um Abhängigkeiten und unerwartete Seiteneffekte zu vermeiden (insbesondere bei Verwendung einer In-Memory-DB pro Test).
- Die Notwendigkeit von `db.session.rollback()` nach Tests, die erwartete Exceptions (wie `IntegrityError`) auslösen, ist wichtig, um die DB-Session für nachfolgende Tests sauber zu halten.
- Die Berechnung von Zeitintervallen und Überlappungen erfordert sorgfältige Logik, insbesondere die Berücksichtigung von inklusivem Start- und Enddatum ((end - start).days + 1).

### Improvements for Next Time
- Beim Erstellen neuer Testdateien sofort die `conftest.py` überprüfen und die korrekten Fixtures übernehmen.
- Eine Standard-Setup-Funktion oder ein `@pytest.mark.usefixtures('test_db', 'client')` könnte Boilerplate-Code in den Testdateien reduzieren, obwohl explizite Fixture-Argumente oft klarer sind.
- Die Erstellung von Basis-Testdaten (z.B. einige Apartments) könnte in einer Fixture in `conftest.py` zentralisiert werden, wenn sie von sehr vielen Tests benötigt wird, um Redundanz zu vermeiden.
- Die Logik zur Behandlung von Überlappungen bei `OccupancyPeriod` könnte in Zukunft durch einen Datenbank-Constraint (z.B. `EXCLUDE USING gist`) robuster gestaltet werden, falls SQLite dies unterstützt oder auf PostgreSQL gewechselt wird. 