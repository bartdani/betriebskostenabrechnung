from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return "<h1>Betriebskostenabrechnung - Basis-Setup</h1>"

# Weitere Konfigurationen und Blueprints werden hier später hinzugefügt 