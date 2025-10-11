from django.urls import path
from .views import predict_next, upload_model, view_live_data  # import the new view

urlpatterns = [
    path("predict/", predict_next, name="predict_next"),
    path("upload/", upload_model, name="upload_model"),
    path("live-data/", view_live_data, name="view_live_data"),  # new live data URL
]
