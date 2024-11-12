from flask import Flask, render_template, jsonify # type: ignore
import pandas as pd
import logging
import threading
import time

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the Excel file
datei_pfad = 'static/RaceDays_Beispiel.xlsx'
df = pd.DataFrame()

# Column configuration for each category
columns_info = {
    "Ak1 (5-8 Jahre)": ["Platz", "Ak1(5-8 Jahre)", "Zeit", "Bahn"],
    "Ak2 (9-12 Jahre)": ["Platz.1", "Ak2(9-12 Jahre)", "Zeit.1", "Bahn.1"],
    "Ak3 (13-17 Jahre)": ["Platz.2", "Ak3(13-17 Jahre)", "Zeit.2", "Bahn.2"],
    "Ak4 (18+ Jahre)": ["Platz.3", "Ak4(18+ Jahre)", "Zeit.3", "Bahn.3"],
    "Ak1 Mitarbeiter": ["Platz.4", "Ak1 Mitarbeiter", "Zeit.4", "Bahn.4"]
}

# Farben für jede Kategorie (im HTML-Template verwendet)
colors = {
    "Ak1 (5-8 Jahre)": "bg-red",
    "Ak2 (9-12 Jahre)": "bg-green",
    "Ak3 (13-17 Jahre)": "bg-yellow",
    "Ak4 (18+ Jahre)": "bg-blue",
    "Ak1 Mitarbeiter": "bg-purple"
}

# Function to load data from Excel file
def daten_laden():
    global df
    logging.info(f"Attempting to read file: {datei_pfad}")
    try:
        if datei_pfad.endswith('.xlsx'):
            df = pd.read_excel(datei_pfad, engine='openpyxl', sheet_name='Tabelle1')
        elif datei_pfad.endswith('.ods'):
            df = pd.read_excel(datei_pfad, engine='odf', sheet_name='Tabelle1')
        else:
            raise ValueError("Unsupported file format. Only .xlsx and .ods are supported.")
        logging.debug(f"File successfully read. Rows: {len(df)}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        df = pd.DataFrame()  # Fallback to an empty DataFrame in case of error

# Background process to update data every 5 minutes
def daten_aktualisieren():
    while True:
        logging.debug("Updating data")
        daten_laden()
        logging.debug("Data successfully updated")
        time.sleep(300)  # Wait 5 minutes

# Start the background update process
threading.Thread(target=daten_aktualisieren, daemon=True).start()

# Route to render the main page
@app.route('/')
def index():
    data = {}
    for label, cols in columns_info.items():
        try:
            data[label] = df[cols].to_dict(orient='records')
        except KeyError as e:
            logging.error(f"Missing column in DataFrame: {e}")
            data[label] = []  # Fallback to empty data if columns are missing

    return render_template('index.html', data=data, colors=colors)

# Route to provide data updates for AJAX requests
@app.route('/daten')
def daten():
    data = {}
    for label, cols in columns_info.items():
        try:
            data[label] = df[cols].to_dict(orient='records')
        except KeyError as e:
            logging.error(f"Missing column in DataFrame: {e}")
            data[label] = []  # Fallback to empty data if columns are missing

    return jsonify(data)

if __name__ == '__main__':
    daten_laden()  # Initial data load
    app.run(debug=True)
