from flask import Flask, render_template, jsonify # type: ignore
import pandas as pd
import logging
import threading
import time

# Flask-Anwendung initialisieren
app = Flask(__name__)

# Konfiguriere Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Pfad zur Datei
datei_pfad = 'Carerabahn_02/RaceDays_Beispiel (1).ods' # Pfad zur Datei

# Globale Variable für DataFrame
df = pd.DataFrame()

# Funktion zum Laden der Daten
def daten_laden():
    global df
    logging.info(f"Versuche Datei zu lesen: {datei_pfad}")
    try:
        if datei_pfad.endswith('.xlsx'):
            df = pd.read_excel(datei_pfad, engine='openpyxl', sheet_name='Tabelle1')
        elif datei_pfad.endswith('.ods'):
            df = pd.read_excel(datei_pfad, engine='odf', sheet_name='Tabelle1')
        else:
            raise ValueError("Nicht unterstütztes Dateiformat. Nur .xlsx und .ods werden unterstützt.")
        logging.debug(f"Datei erfolgreich gelesen. Anzahl der Zeilen: {len(df)}")
    except Exception as e:
        logging.error(f"Fehler beim Lesen der Datei: {e}")
        df = pd.DataFrame()  # Leere DataFrame für den Fall eines Fehlers
# Hintergrundprozess zum Aktualisieren der Daten alle 5 Minuten
def daten_aktualisieren():
    while True:
        logging.debug("Aktualisiere die Daten")
        daten_laden()
        logging.debug("Daten erfolgreich aktualisiert")
        time.sleep(300)  # 5 Minuten warten
        #time.sleep(10)  # 10 Sekunden warten

# Starte den Aktualisierungsprozess in einem separaten Thread
threading.Thread(target=daten_aktualisieren, daemon=True).start()

# Route zur Anzeige der Hauptseite
@app.route('/')
def index():
    columns_info = {
        "Ak1 (5-8 Jahre)": ["Platz", "Ak1(5-8 Jahre)", "Zeit", "Bahn"],
        "Ak2 (9-12 Jahre)": ["Platz", "Ak2(9-12 Jahre)", "Zeit", "Bahn"],
        "Ak3 (13-17 Jahre)": ["Platz", "Ak3(13-17 Jahre)", "Zeit", "Bahn"],
        "Ak4 (18+ Jahre)": ["Platz", "Ak4(18+ Jahre)", "Zeit", "Bahn"],
        "Ak1 Mitarbeiter": ["Platz", "Ak1 Mitarbeiter", "Zeit", "Bahn"]
    }
    
    data = {}
    for label, cols in columns_info.items():
        data[label] = df[cols].to_dict(orient='records')
    
    return render_template('index.html', data=data)

# Route zur Datenaktualisierung für AJAX-Requests
@app.route('/daten')
def daten():
    columns_info = {
        "Ak1 (5-8 Jahre)": ["Platz", "Ak1(5-8 Jahre)", "Zeit", "Bahn"],
        "Ak2 (9-12 Jahre)": ["Platz.1", "Ak2(9-12 Jahre)", "Zeit.1", "Bahn.1"],
        "Ak3 (13-17 Jahre)": ["Platz.2", "Ak3(13-17 Jahre)", "Zeit.2", "Bahn.2"],
        "Ak4 (18+ Jahre)": ["Platz.3", "Ak4(18+ Jahre)", "Zeit.3", "Bahn.3"],
        "Ak1 Mitarbeiter": ["Platz.4", "Ak1 Mitarbeiter", "Zeit.4", "Bahn.4"]
    }
    
    data = {}
    for label, cols in columns_info.items():
        data[label] = df[cols].to_dict(orient='records')
    
    return jsonify(data)

if __name__ == '__main__':
    daten_laden()  # Initiales Laden der Daten
    app.run(debug=True)
