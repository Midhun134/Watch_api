from django.conf import settings
from django.db import models
from datetime import datetime


class SmartWatch(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watches")
    watch_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    high_heart_rate_threshold = models.PositiveIntegerField(null=True, blank=True, help_text="High heart rate threshold (BPM). If not specified, uses default 98 BPM.")
    low_heart_rate_threshold = models.PositiveIntegerField(null=True, blank=True, help_text="Low heart rate threshold (BPM). If not specified, uses default 25 BPM.")

    class Meta:
        unique_together = [['owner', 'name']]  # Prevent duplicate watch names per user

    def __str__(self) -> str:
        return f"{self.name} ({self.watch_id})"
    
    def get_high_threshold(self):
        """Get the high threshold, falling back to default if not set"""
        return self.high_heart_rate_threshold if self.high_heart_rate_threshold is not None else 98
    
    def get_low_threshold(self):
        """Get the low threshold, falling back to default if not set"""
        return self.low_heart_rate_threshold if self.low_heart_rate_threshold is not None else 25


class WatchMetric(models.Model):
    watch = models.ForeignKey(SmartWatch, on_delete=models.CASCADE, related_name="metrics")
    steps = models.PositiveIntegerField(default=0)
    heart_rate = models.PositiveIntegerField()
    timestamp = models.BigIntegerField(db_index=True, help_text="Unix timestamp (epoch value)")

    class Meta:
        ordering = ["-timestamp", "-id"]

    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp) # Convert Unix timestamp to datetime
        return f"{self.watch.watch_id} @ {dt.isoformat()}" # Format the datetime to ISO format

    def save(self, *args, **kwargs):
        # Call the parent save method first
        super().save(*args, **kwargs)
        #calls the parent class's (Django's Model) save() method first to actually save the data to the database
        
        self._check_heart_rate_thresholds()
        # Check heart rate thresholds and create alerts if necessary

    def _check_heart_rate_thresholds(self):
        """Check heart rate against thresholds and create alerts if needed"""
        # Use the watch's custom thresholds if set, otherwise use defaults
        HIGH_THRESHOLD = self.watch.get_high_threshold()
        LOW_THRESHOLD = self.watch.get_low_threshold()
        
        if self.heart_rate > HIGH_THRESHOLD:
            Alert.objects.create(
                watch=self.watch,
                alert_type="HIGH_HEART_RATE",
                heart_rate=self.heart_rate,
                timestamp=self.timestamp
            )#alert.objects.create() creates a new Alert object and saves it to the database
        elif self.heart_rate < LOW_THRESHOLD:
            Alert.objects.create(
                watch=self.watch,
                alert_type="LOW_HEART_RATE",
                heart_rate=self.heart_rate,
                timestamp=self.timestamp
            )


class Alert(models.Model):
    ALERT_TYPES = [
        ('HIGH_HEART_RATE', 'High Heart Rate'),
        ('LOW_HEART_RATE', 'Low Heart Rate'),
    ]
    
    watch = models.ForeignKey(SmartWatch, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    heart_rate = models.PositiveIntegerField()
    timestamp = models.BigIntegerField(db_index=True, help_text="Unix timestamp (epoch value)")

    class Meta:
        ordering = ["-timestamp", "-id"]

    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp)
        return f"{self.watch.watch_id} - {self.alert_type} ({self.heart_rate} BPM) @ {dt.isoformat()}"


