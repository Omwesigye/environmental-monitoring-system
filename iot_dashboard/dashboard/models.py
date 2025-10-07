from django.db import models

class SensorReading(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    battery = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    motion = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp} T={self.temperature} H={self.humidity}"
