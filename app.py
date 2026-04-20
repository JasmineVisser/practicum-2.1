import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
from datetime import datetime

st.title("🚲 Bike Rental Prediction App – Practicum 2 & 3")

st.write("""
Deze app gebruikt mijn getrainde regressiemodel (Practicum 2) 
en slaat alle voorspellingen op in een SQLite-database (Practicum 3).
Daarnaast kan ik synthetische data genereren om app-gebruik te simuleren.
""")

# ---------------------------------------------------------
# MODEL LADEN
# ---------------------------------------------------------
model = joblib.load("model.joblib")

# ---------------------------------------------------------
# DATABASE INITIALISEREN
# ---------------------------------------------------------
DB_NAME = "predictions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            season INTEGER,
            yr INTEGER,
            mnth INTEGER,
            hr INTEGER,
            holiday INTEGER,
            weekday INTEGER,
            workingday INTEGER,
            weathersit INTEGER,
            temp REAL,
            atemp REAL,
            hum REAL,
            windspeed REAL,
            prediction REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_prediction(row):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO predictions (
            timestamp, season, yr, mnth, hr, holiday, weekday, workingday,
            weathersit, temp, atemp, hum, windspeed, prediction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        row["season"], row["yr"], row["mnth"], row["hr"],
        row["holiday"], row["weekday"], row["workingday"],
        row["weathersit"], row["temp"], row["atemp"],
        row["hum"], row["windspeed"], row["prediction"]
    ))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# INPUTVELDEN
# ---------------------------------------------------------
st.header("Voer de inputwaarden in")

season = st.selectbox("Season", [1, 2, 3, 4],
                      format_func=lambda x: ["Spring", "Summer", "Fall", "Winter"][x-1])

yr = st.selectbox("Year", [0, 1], format_func=lambda x: "2011" if x == 0 else "2012")

mnth = st.slider("Month", 1, 12, 6)
hr = st.slider("Hour of the day", 0, 23, 12)

holiday = st.selectbox("Holiday", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
weekday = st.slider("Weekday", 0, 6, 3)
workingday = st.selectbox("Working day", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")

weathersit = st.selectbox("Weather Situation", [1, 2, 3],
                          format_func=lambda x: {
                              1: "Clear / Few clouds",
                              2: "Mist / Cloudy",
                              3: "Light Snow / Rain"
                          }[x])

temp = st.slider("Temperature (normalized)", 0.0, 1.0, 0.5)
atemp = st.slider("Feeling Temperature (normalized)", 0.0, 1.0, 0.5)
hum = st.slider("Humidity", 0.0, 1.0, 1.0)
windspeed = st.slider("Wind Speed", 0.0, 1.0, 0.2)

# ---------------------------------------------------------
# VOORSPELLING + LOGGING
# ---------------------------------------------------------
if st.button("Predict Bike Rentals"):
    data = pd.DataFrame({
        "season": [season],
        "yr": [yr],
        "mnth": [mnth],
        "hr": [hr],
        "holiday": [holiday],
        "weekday": [weekday],
        "workingday": [workingday],
        "weathersit": [weathersit],
        "temp": [temp],
        "atemp": [atemp],
        "hum": [hum],
        "windspeed": [windspeed]
    })

    prediction = model.predict(data)[0]

    st.subheader("Prediction Result")
    st.success(f"Estimated bike rentals: **{int(prediction)} bikes** 🚲")

    # Opslaan in database
    row = data.iloc[0].to_dict()
    row["prediction"] = float(prediction)
    save_prediction(row)

    st.info("Voorspelling opgeslagen in database ✔️")

# ---------------------------------------------------------
# SYNTHETISCHE DATA GENEREREN
# ---------------------------------------------------------
st.header("Synthetische data genereren (Practicum 3)")

def generate_synthetic_data(n=1000):
    synthetic = pd.DataFrame()
    synthetic["season"] = np.random.choice([1,2,3,4], n)
    synthetic["yr"] = np.random.choice([0,1], n)
    synthetic["mnth"] = np.random.randint(1,13,n)
    synthetic["hr"] = np.random.randint(0,24,n)
    synthetic["holiday"] = np.random.choice([0,1], n, p=[0.97,0.03])
    synthetic["weekday"] = np.random.randint(0,7,n)
    synthetic["workingday"] = np.random.choice([0,1], n, p=[0.3,0.7])
    synthetic["weathersit"] = np.random.choice([1,2,3], n, p=[0.6,0.3,0.1])
    synthetic["temp"] = np.random.uniform(0,1,n)
    synthetic["atemp"] = np.random.uniform(0,1,n)
    synthetic["hum"] = np.random.uniform(0,1,n)
    synthetic["windspeed"] = np.random.uniform(0,1,n)
    return synthetic

if st.button("Generate 100 synthetic predictions"):
    syn = generate_synthetic_data(100)
    syn["prediction"] = model.predict(syn)

    for _, row in syn.iterrows():
        save_prediction(row.to_dict())

    st.success("100 synthetische voorspellingen opgeslagen ✔️")

# ---------------------------------------------------------
# DATABASE PREVIEW
# ---------------------------------------------------------
st.header("📊 Laatste voorspellingen")

conn = sqlite3.connect(DB_NAME)
df_preview = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC LIMIT 10", conn)
conn.close()

st.dataframe(df_preview)
