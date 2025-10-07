# ml/models.py
from django.db import models
import os

def model_upload_path(instance, filename):
    # Save all uploaded models to ml/models/ folder
    return os.path.join("ml", "models", filename)

class UploadedModel(models.Model):
    model_file = models.FileField(upload_to=model_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model_file.name
