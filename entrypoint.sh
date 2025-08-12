#!/usr/bin/env sh
set -e

# Standard: innerhalb des Containers liegt die App unter /app
export FLASK_APP=run.py

# Sicherstellen, dass das Instance-Verzeichnis existiert (wichtig für SQLite/Uploads)
mkdir -p /app/instance

# DB-Migrationen (nicht-fatal, falls keine Migration nötig)
flask db upgrade || true

# Server starten (Waitress, ruft Factory create_app auf)
exec waitress-serve --call app:create_app --host=0.0.0.0 --port=8000

