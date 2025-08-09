import os
import sqlite3
import argparse

parser = argparse.ArgumentParser(description='SQLite DB Prüfer/Reparatur')
parser.add_argument('--repair', action='store_true', help='Fehlende Spalten in apartment hinzufügen (address, size_sqm)')
args = parser.parse_args()

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'app.db'))
print('DB:', db_path, 'exists:', os.path.exists(db_path))
if not os.path.exists(db_path):
    print('No DB file found')
    raise SystemExit(1)

con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print('tables:', tables)

if 'apartment' in tables:
    cols = [r[1] for r in con.execute("PRAGMA table_info(apartment)").fetchall()]
    print('apartment.columns:', cols)
    required = {'address', 'size_sqm'}
    missing = [c for c in sorted(required - set(cols))]
    if missing:
        print('missing apartment columns:', missing)
        if args.repair:
            if 'address' in missing:
                con.execute("ALTER TABLE apartment ADD COLUMN address TEXT NOT NULL DEFAULT ''")
            if 'size_sqm' in missing:
                con.execute("ALTER TABLE apartment ADD COLUMN size_sqm REAL NOT NULL DEFAULT 0")
            con.commit()
            cols2 = [r[1] for r in con.execute("PRAGMA table_info(apartment)").fetchall()]
            print('apartment.columns.after:', cols2)
else:
    print('apartment table not found')

con.close()


