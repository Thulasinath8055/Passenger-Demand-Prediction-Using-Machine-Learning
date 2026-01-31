import pickle
import joblib
import pandas as pd

RF_MODEL_PATH = "models/rf_model.pkl"
DT_MODEL_PATH = "models/dt_model.pkl"
PROPHET_MODEL_PATH = "models/prophet_model.pkl"
ENCODER_PATH = "models/station_encoder.pkl"

rf_model = joblib.load(RF_MODEL_PATH)
dt_model = joblib.load(DT_MODEL_PATH)
station_encoder = joblib.load(ENCODER_PATH)

with open(PROPHET_MODEL_PATH, "rb") as f:
    prophet_model = pickle.load(f)


def _build_features(station, year, month, day, hour, dayofweek):
    station_encoded = station_encoder.transform([station])[0]

    return pd.DataFrame([{
        "station_encoded": station_encoded,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "dayofweek": dayofweek
    }])


def predict_rf(station, year, month, day, hour, dayofweek):
    df = _build_features(station, year, month, day, hour, dayofweek)
    return int(rf_model.predict(df)[0])


def predict_dt(station, year, month, day, hour, dayofweek):
    df = _build_features(station, year, month, day, hour, dayofweek)
    return int(dt_model.predict(df)[0])


def predict_prophet(date):
    future = pd.DataFrame({"ds": [date]})
    forecast = prophet_model.predict(future)
    return int(forecast["yhat"].iloc[0])
