
import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime

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

def save_prediction(data, prediction):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO predictions (
        timestamp, season, yr, mnth, hr, holiday,
        weekday, workingday, weathersit,
        temp, atemp, hum, windspeed, prediction
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        *data,
        prediction
    ))

    conn.commit()
    conn.close()


def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()
    return df


model = joblib.load("model.joblib")


st.title("🚲 Bike Rental Prediction App")

st.write("""
Deze app is onderdeel van **Practicumopdracht 3**.

De app:
- voorspelt het aantal fietsverhuringen  
- slaat elke voorspelling automatisch op in een SQLite‑database  
- bewaart alle inputwaarden + timestamp  
- toont een geschiedenis van alle voorspellingen  
- maakt het mogelijk om synthetische data te gebruiken om app‑gebruik te simuleren  
""")

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
hum = st.slider("Humidity", 0.0, 1.0, 0.5)
windspeed = st.slider("Wind Speed", 0.0, 1.0, 0.2)


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

    save_prediction(list(data.iloc[0]), prediction)


st.header("📊 Prediction History")

st.write("""
Hieronder zie je alle voorspellingen die door de app zijn gedaan.
Elke rij bevat:

- de timestamp  
- alle inputwaarden  
- de voorspelde waarde  

Dit maakt het mogelijk om voorspellingen over tijd te analyseren.
""")

history_df = load_data()

if not history_df.empty:
    st.dataframe(history_df)

    st.subheader("Voorspellingen over tijd")
    st.line_chart(history_df["prediction"])
else:
    st.info("Nog geen voorspellingen opgeslagen.")
