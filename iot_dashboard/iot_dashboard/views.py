import requests
from django.http import JsonResponse
from datetime import datetime, timedelta
import os
import joblib
import numpy as np

# ThingSpeak configuration
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "3077306")
THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "RJKY2M6KAC4APH45")

# Path to the saved ML model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_models", "rf_model.pkl")

def get_last_n_readings(n=3):
    """
    Fetch the last n readings from ThingSpeak
    """
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"api_key": THINGSPEAK_READ_API_KEY, "results": n}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    feeds = response.json().get("feeds", [])
    
    temperatures = []
    humidities = []
    
    for feed in feeds:
        temperatures.append(float(feed.get("field4", 0)))
        humidities.append(float(feed.get("field2", 0)))
    
    return temperatures, humidities

def predict_next_reading(request):
    """
    Predict the next temperature and humidity using last 3 readings
    """
    try:
        # Load ML model
        model = joblib.load(MODEL_PATH)
        
        # Get last 3 readings
        temps, hums = get_last_n_readings(3)
        
        if len(temps) < 3 or len(hums) < 3:
            return JsonResponse({"error": "Not enough data to predict."})
        
        # Prepare input for model (flatten the last 3 readings)
        # Assuming your model expects input like [temp1, temp2, temp3, hum1, hum2, hum3]
        X = np.array([temps + hums]).reshape(1, -1)
        
        # Make prediction
        pred = model.predict(X)[0]
        
        # If your model predicts both temperature and humidity, adapt accordingly
        # Example: pred = [next_temp, next_humidity]
        next_temp = round(pred[0], 2)
        next_humidity = round(pred[1], 2)
        
        return JsonResponse({"temperature": next_temp, "humidity": next_humidity})
    
    except Exception as e:
        return JsonResponse({"error": str(e)})
