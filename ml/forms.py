from django import forms
from .models import UploadedModel

# -----------------------------
# Form to upload Random Forest model
# -----------------------------
class ModelUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedModel
        fields = ["model_file"]
        labels = {
            "model_file": "Select Random Forest Model (joblib)"
        }

# -----------------------------
# Form to submit last 3 sensor readings
# -----------------------------
class SensorHistoryForm(forms.Form):
    temp1 = forms.FloatField(label="Temperature 1 (oldest)")
    temp2 = forms.FloatField(label="Temperature 2")
    temp3 = forms.FloatField(label="Temperature 3 (latest)")
    hum1  = forms.FloatField(label="Humidity 1 (oldest)")
    hum2  = forms.FloatField(label="Humidity 2")
    hum3  = forms.FloatField(label="Humidity 3 (latest)")