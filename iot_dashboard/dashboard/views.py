from django.shortcuts import render
import requests
import json
from datetime import datetime

def charts(request):
    THINGSPEAK_API_URL = "https://api.thingspeak.com/channels/3077306/feeds.json?api_key=RJKY2M6KAC4APH45"

    response = requests.get(THINGSPEAK_API_URL)
    data = response.json()
    feeds = data['feeds']

    latest_per_day = {}

    for feed in feeds:
        ts = datetime.strptime(feed['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        day_str = ts.strftime('%d %b')  # "17 Sep", "18 Sep", ...

        # Keep only the latest feed for that day
        if day_str not in latest_per_day or ts > datetime.strptime(latest_per_day[day_str]['created_at'], '%Y-%m-%dT%H:%M:%SZ'):
            latest_per_day[day_str] = feed

    # Sort days chronologically
    sorted_days = sorted(
        latest_per_day.keys(),
        key=lambda d: datetime.strptime(d, '%d %b')
    )

    # Prepare lists for Chart.js
    labels = []
    temperature, humidity, battery, motion = [], [], [], []

    for day in sorted_days:
        labels.append(day)
        f = latest_per_day[day]
        temperature.append(float(f['field1'] or 0))
        humidity.append(float(f['field2'] or 0))
        battery.append(float(f['field3'] or 0))
        motion.append(float(f['field4'] or 0))

    context = {
        "timestamps_json": json.dumps(labels),   # <-- use the same name as in your template
        "temperature_json": json.dumps(temperature),
        "humidity_json": json.dumps(humidity),
        "battery_json": json.dumps(battery),
        "motion_json": json.dumps(motion),
    }

    return render(request, "dashboard/charts.html", context)
