import requests
import pandas as pd
import os
from django.shortcuts import render
from .forms import SensorHistoryForm
from .model_store import rf

# Global predictions list
latest_predictions = []
MAX_RECENT = 10

# ThingSpeak config
thingspeak_channel_id = os.getenv("THINGSPEAK_CHANNEL_ID", "3077306")
thingspeak_read_api_key = os.getenv("THINGSPEAK_READ_API_KEY", "RJKY2M6KAC4APH45")

def predict_next(request):
    prediction = None
    comparison = []  # List to hold actual vs predicted
    initial_data = {}

    # Step 1: Fetch latest 3 entries from ThingSpeak
    url = f"https://api.thingspeak.com/channels/{thingspeak_channel_id}/feeds.json"
    params = {"api_key": thingspeak_read_api_key, "results": 3}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        feeds = data.get("feeds", [])

        if len(feeds) > 0:
            # Reverse so oldest first, newest last
            feeds = feeds[::-1]

            # Correct fields mapping
            battery = [float(feed.get("field1", 0)) for feed in feeds]
            motion  = [float(feed.get("field3", 0)) for feed in feeds]
            hums    = [float(feed.get("field2", 0)) for feed in feeds]  # Or field3? Based on ThingSpeak payload
            temps   = [float(feed.get("field4", 0)) for feed in feeds]  # Temperature
            timestamps = [feed.get("created_at") for feed in feeds]

            # Pre-fill form with latest readings (use correct fields)
            initial_data = {
                "temp1": temps[0] if len(temps) >= 1 else None,
                "temp2": temps[1] if len(temps) >= 2 else None,
                "temp3": temps[2] if len(temps) >= 3 else None,
                "hum1": hums[0] if len(hums) >= 1 else None,
                "hum2": hums[1] if len(hums) >= 2 else None,
                "hum3": hums[2] if len(hums) >= 3 else None,
            }

    except Exception as e:
        print("Error fetching ThingSpeak data:", e)

    # Step 2: Handle prediction
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

                # Add to latest predictions
                latest_predictions.append(prediction)
                if len(latest_predictions) > MAX_RECENT:
                    latest_predictions.pop(0)

                # Prepare comparison table
                comparison = []
                for i in range(len(temps)):
                    comparison.append({
                        "timestamp": timestamps[i] if i < len(timestamps) else "-",
                        "actual_temp": round(temps[i], 2),
                        "predicted_temp": round(pred[0], 2),
                        "actual_hum": round(hums[i], 2),
                        "predicted_hum": round(pred[1], 2),
                    })

    else:
        form = SensorHistoryForm(initial=initial_data)

    return render(request, "ml/predict.html", {
        "form": form,
        "prediction": prediction,
        "comparison": comparison
    })
