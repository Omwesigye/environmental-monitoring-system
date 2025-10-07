from django.shortcuts import render, redirect
from .forms import SensorHistoryForm, ModelUploadForm
from .models import UploadedModel
from .model_store import rf
import joblib
import pandas as pd

# -----------------------------
# Upload ML model
# -----------------------------
def upload_model(request):
    """
    Upload a new Random Forest model.
    The model is saved to ml/models/ and immediately loaded for predictions.
    """
    if request.method == "POST":
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_model = form.save()  # saves the file
            # Load the model into memory immediately
            model_path = uploaded_model.model_file.path
            model = joblib.load(model_path)

            # Save it to the global model_store
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
    """
    Use the latest model to predict next temperature and humidity
    based on last 3 readings submitted via form.
    """
    prediction = None

    if request.method == "POST":
        form = SensorHistoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Prepare features in the same lag order as training
            latest_features = pd.DataFrame({
                "temp_lag1": [cd["temp3"]],
                "temp_lag2": [cd["temp2"]],
                "temp_lag3": [cd["temp1"]],
                "hum_lag1":  [cd["hum3"]],
                "hum_lag2":  [cd["hum2"]],
                "hum_lag3":  [cd["hum1"]],
            })

            # Make sure a model is loaded
            if rf is None:
                prediction = {"error": "No model loaded. Please upload a model first."}
            else:
                # Predict using the latest model
                pred = rf.predict(latest_features)[0]
                prediction = {
                    "temp": round(pred[0], 2),
                    "hum":  round(pred[1], 2),
                }
    else:
        form = SensorHistoryForm()

    return render(request, "ml/predict.html", {
        "form": form,
        "prediction": prediction
    })
