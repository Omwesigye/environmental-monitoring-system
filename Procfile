web: python manage.py collectstatic --noinput && gunicorn iot_dashboard.wsgi --bind 0.0.0.0:$PORT
worker: python temp_humidity_motion_sensor_data_lora.py
