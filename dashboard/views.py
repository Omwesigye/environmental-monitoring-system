from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import requests, os
import pandas as pd
from ml.model_store import rf  # import global model from your ml app

# ThingSpeak config
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "3077306")
THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "RJKY2M6KAC4APH45")

# ---------- Landing Page ----------
def landing(request):
    """
    Render the landing page with IoT dashboard and automatic ML predictions.
    """
    prediction_auto = None
    auto_error = None

    # --- Step 1: Get last 3 readings from ThingSpeak ---
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"api_key": THINGSPEAK_READ_API_KEY, "results": 3}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        feeds = response.json().get("feeds", [])

        if len(feeds) < 3:
            auto_error = "Not enough recent data (need at least 3 readings)."
        elif rf is None:
            auto_error = "No ML model loaded. Please upload one first."
        else:
            # Convert ThingSpeak timestamps + extract readings
            feeds = list(reversed(feeds))  # ensure correct order (oldest first)
            temps = [float(f.get("field4", 0)) for f in feeds]
            hums = [float(f.get("field2", 0)) for f in feeds]

            # Prepare features in lag order
            features = pd.DataFrame({
                "temp_lag1": [temps[-1]],
                "temp_lag2": [temps[-2]],
                "temp_lag3": [temps[-3]],
                "hum_lag1":  [hums[-1]],
                "hum_lag2":  [hums[-2]],
                "hum_lag3":  [hums[-3]],
            })

            # Predict next readings
            pred = rf.predict(features)[0]
            prediction_auto = {
                "temp": round(pred[0], 2),
                "hum":  round(pred[1], 2),
            }
    except Exception as e:
        auto_error = f"Prediction failed: {e}"

    # Pass predictions + errors to template
    return render(request, "landing.html", {
        "prediction_auto": prediction_auto,
        "auto_error": auto_error,
    })

# ---------- Charts Page ----------
def charts(request):
    return render(request, "dashboard/charts.html")

# ---------- Latest Sensor Data API ----------
def latest_sensor_data(request):
    """
    Return latest sensor reading from ThingSpeak as JSON.
    """
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"api_key": THINGSPEAK_READ_API_KEY, "results": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        feed = response.json().get("feeds", [])[0]

        dt_utc = datetime.strptime(feed["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        dt_uganda = dt_utc + timedelta(hours=3)
        timestamp = dt_uganda.isoformat() + "+03:00"

        data = {
            "timestamp": timestamp,
            "temperature": float(feed.get("field4", 0)),
            "humidity": float(feed.get("field2", 0)),
            "battery": float(feed.get("field1", 0)),
            "motion": int(feed.get("field3", 0)) if feed.get("field3") else 0,
        }
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)})

# ---------- Live Data Page ----------
def view_live_data(request):
    """
    Fetch last 10 readings from ThingSpeak and render live_data.html
    """
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"api_key": THINGSPEAK_READ_API_KEY, "results": 10}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        feeds = response.json().get("feeds", [])

        recent_readings = []
        for feed in feeds:
            dt_utc = datetime.strptime(feed["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            dt_uganda = dt_utc + timedelta(hours=3)
            timestamp = dt_uganda.isoformat() + "+03:00"
            reading = {
                "timestamp": timestamp,
                "battery": float(feed.get("field1", 0)),
                "humidity": float(feed.get("field2", 0)),
                "motion": int(feed.get("field3", 0)) if feed.get("field3") else 0,
                "temperature": float(feed.get("field4", 0)),
            }
            recent_readings.append(reading)

        # Reverse to show newest first
        recent_readings = list(reversed(recent_readings))

        return render(request, "live_data.html", {"recent_readings": recent_readings})

    except Exception as e:
        return render(request, "live_data.html", {
            "recent_readings": [],
            "error": f"Failed to fetch data: {str(e)}"
        })