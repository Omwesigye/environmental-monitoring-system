from django.urls import path
from .views import predict_next, upload_model

urlpatterns = [
    path("predict/", predict_next, name="predict_next"),
     path("upload/", upload_model, name="upload_model"),
]
