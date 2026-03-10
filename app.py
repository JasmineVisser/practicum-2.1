import streamlit as st
import pandas as pd
import joblib

model = joblib.load("model.joblib")

st.title("Bike Rental Prediction")

season = st.number_input("Season")
yr = st.number_input("Year")
mnth = st.number_input("Month")
hr = st.number_input("Hour")
holiday = st.number_input("Holiday")
weekday = st.number_input("Weekday")
workingday = st.number_input("Working Day")
weathersit = st.number_input("Weather Situation")
temp = st.number_input("Temperature")
atemp = st.number_input("Feeling Temperature")
hum = st.number_input("Humidity")
windspeed = st.number_input("Wind Speed")

if st.button("Predict"):

    data = pd.DataFrame({
        "season":[season],
        "yr":[yr],
        "mnth":[mnth],
        "hr":[hr],
        "holiday":[holiday],
        "weekday":[weekday],
        "workingday":[workingday],
        "weathersit":[weathersit],
        "temp":[temp],
        "atemp":[atemp],
        "hum":[hum],
        "windspeed":[windspeed]
    })

    prediction = model.predict(data)

    st.success(f"Predicted bike rentals: {prediction[0]}")