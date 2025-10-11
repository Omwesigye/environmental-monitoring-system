from django.shortcuts import render, redirect
from .forms import SensorHistoryForm, ModelUploadForm
from .models import UploadedModel
from .model_store import rf
import joblib
import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# -----------------------------
# Global store for recent predictions (last 10)
# -----------------------------
latest_predictions = []
MAX_RECENT = 10

# ThingSpeak config
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "3077306")
THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "RJKY2M6KAC4APH45")

# -----------------------------
# Upload ML model
# -----------------------------
def upload_model(request):
    if request.method == "POST":
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_model = form.save()  # saves the file
            model_path = uploaded_model.model_file.path
            model = joblib.load(model_path)
            from . import model_store
            model_store.rf = model
            return redirect("predict_next")
    else:
        form = ModelUploadForm()
    return render(request, "ml/upload.html", {"form": form})

# -----------------------------
# Predict next readings
# -----------------------------
def predict_next(request):
    prediction = None
    if request.method == "POST":
        form = SensorHistoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            latest_features = pd.DataFrame({
                "temp_lag1": [cd["temp3"]],
                "temp_lag2": [cd["temp2"]],
                "temp_lag3": [cd["temp1"]],
                "hum_lag1":  [cd["hum3"]],
                "hum_lag2":  [cd["hum2"]],
                "hum_lag3":  [cd["hum1"]],
            })
            if rf is None:
                prediction = {"error": "No model loaded. Please upload a model first."}
            else:
                pred = rf.predict(latest_features)[0]
                prediction = {"temp": round(pred[0], 2), "hum": round(pred[1], 2)}

                # Save to recent predictions
                latest_predictions.append(prediction)
                if len(latest_predictions) > MAX_RECENT:
                    latest_predictions.pop(0)
    else:
        form = SensorHistoryForm()
    return render(request, "ml/predict.html", {"form": form, "prediction": prediction})

# -----------------------------
# View live data (last 10 ThingSpeak readings)
# -----------------------------
def view_live_data(request):
    """
    Fetch last 10 readings from ThingSpeak and display in a table.
    """
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"api_key": THINGSPEAK_READ_API_KEY, "results": 10}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        feeds = response.json().get("feeds", [])

        recent_readings = []
        for feed in reversed(feeds):  # newest first
            dt_utc = datetime.strptime(feed["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            dt_uganda = dt_utc + timedelta(hours=3)
            recent_readings.append({
                "timestamp": dt_uganda.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": float(feed.get("field4", 0)),
                "humidity": float(feed.get("field2", 0)),
                "motion": int(feed.get("field3", 0)) if feed.get("field3") else 0,
                "battery": float(feed.get("field1", 0)),
            })
    except Exception as e:
        recent_readings = []
        print("ThingSpeak fetch error:", e)

    return render(request, "live_data.html", {
        "recent_readings": recent_readings
    })
