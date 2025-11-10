from mongoengine import Document, ReferenceField, StringField, IntField, LongField
from mongoengine import CASCADE
from datetime import datetime


class SmartWatch(Document):
    # Store user ID as IntField since Django uses integer IDs
    owner_id = IntField(required=True)
    watch_id = StringField(max_length=64, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    high_heart_rate_threshold = IntField(min_value=1, null=True, blank=True)
    low_heart_rate_threshold = IntField(min_value=1, null=True, blank=True)

    meta = {
        'indexes': [
            ('owner_id', 'name'),  # Compound index for unique_together equivalent
        ],
        'index_background': True,
    }

    def __str__(self) -> str:
        return f"{self.name} ({self.watch_id})"
    
    @property
    def owner(self):
        """Get the owner user object"""
        from accounts.models import CustomUser
        try:
            return CustomUser.objects.get(id=self.owner_id)
        except CustomUser.DoesNotExist:
            return None
    
    def get_high_threshold(self):
        """Get the high threshold, falling back to default if not set"""
        return self.high_heart_rate_threshold if self.high_heart_rate_threshold is not None else 98
    
    def get_low_threshold(self):
        """Get the low threshold, falling back to default if not set"""
        return self.low_heart_rate_threshold if self.low_heart_rate_threshold is not None else 25

    def clean(self):
        """Validate unique constraint for owner + name combination"""
        from mongoengine import ValidationError
        existing = SmartWatch.objects(owner_id=self.owner_id, name=self.name).first()
        if existing and (not self.pk or str(existing.pk) != str(self.pk)):
            raise ValidationError("A watch with this name already exists for this owner")


class WatchMetric(Document):
    watch = ReferenceField('SmartWatch', required=True, reverse_delete_rule=CASCADE)
    steps = IntField(min_value=0, default=0)
    heart_rate = IntField(min_value=1, required=True)
    timestamp = LongField(required=True)

    meta = {
        'indexes': [
            '-timestamp',  # Descending index for ordering
        ],
        'ordering': ['-timestamp'],
        'index_background': True,
    }

    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp)
        return f"{self.watch.watch_id} @ {dt.isoformat()}"

    def save(self, *args, **kwargs):
        # Call the parent save method first
        super().save(*args, **kwargs)
        
        self._check_heart_rate_thresholds()
        # Check heart rate thresholds and create alerts if necessary

    def _check_heart_rate_thresholds(self):
        """Check heart rate against thresholds and create alerts if needed"""
        # Reload watch to ensure we have latest data
        self.watch.reload()
        # Use the watch's custom thresholds if set, otherwise use defaults
        HIGH_THRESHOLD = self.watch.get_high_threshold()
        LOW_THRESHOLD = self.watch.get_low_threshold()
        
        if self.heart_rate > HIGH_THRESHOLD:
            Alert(
                watch=self.watch,
                alert_type="HIGH_HEART_RATE",
                heart_rate=self.heart_rate,
                timestamp=self.timestamp
            ).save()
        elif self.heart_rate < LOW_THRESHOLD:
            Alert(
                watch=self.watch,
                alert_type="LOW_HEART_RATE",
                heart_rate=self.heart_rate,
                timestamp=self.timestamp
            ).save()


class Alert(Document):
    ALERT_TYPES = [
        ('HIGH_HEART_RATE', 'High Heart Rate'),
        ('LOW_HEART_RATE', 'Low Heart Rate'),
    ]
    
    watch = ReferenceField('SmartWatch', required=True, reverse_delete_rule=CASCADE)
    alert_type = StringField(max_length=20, required=True, choices=ALERT_TYPES)
    heart_rate = IntField(min_value=1, required=True)
    timestamp = LongField(required=True)

    meta = {
        'indexes': [
            '-timestamp',  # Descending index for ordering
        ],
        'ordering': ['-timestamp'],
        'index_background': True,
    }

    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp)
        return f"{self.watch.watch_id} - {self.alert_type} ({self.heart_rate} BPM) @ {dt.isoformat()}"

