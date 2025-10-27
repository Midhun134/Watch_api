from rest_framework import serializers
from datetime import datetime
from .models import SmartWatch, WatchMetric, Alert


class SmartWatchSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SmartWatch
        fields = ["id", "owner", "watch_id", "name", "high_heart_rate_threshold", "low_heart_rate_threshold"]
        read_only_fields = ["id", "owner"]
    
    def validate_high_heart_rate_threshold(self, value):
        """Validate high threshold is reasonable"""
        if value is not None and value < 1:
            raise serializers.ValidationError("High heart rate threshold must be a positive number")
        if value is not None and value > 300:
            raise serializers.ValidationError("High heart rate threshold seems unreasonably high")
        return value
    
    def validate_low_heart_rate_threshold(self, value):
        """Validate low threshold is reasonable"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Low heart rate threshold must be a positive number")
        if value is not None and value > 200:
            raise serializers.ValidationError("Low heart rate threshold seems unreasonably high")
        return value
    
    def validate(self, data):
        """Ensure high threshold is greater than low threshold if both are set"""
        high_threshold = data.get('high_heart_rate_threshold')
        low_threshold = data.get('low_heart_rate_threshold')
        
        if high_threshold is not None and low_threshold is not None:
            if high_threshold <= low_threshold:
                raise serializers.ValidationError(
                    "High heart rate threshold must be greater than low heart rate threshold"
                )
        
        return data


class WatchMetricSerializer(serializers.ModelSerializer):
    timestamp_readable = serializers.SerializerMethodField()
    
    class Meta:
        model = WatchMetric
        fields = ["id", "watch", "steps", "heart_rate", "timestamp", "timestamp_readable"]
        read_only_fields = ["id", "timestamp_readable"]

    def get_timestamp_readable(self, obj):
        """Convert epoch timestamp to readable datetime string"""
        return datetime.fromtimestamp(obj.timestamp).isoformat()
    
    def validate_timestamp(self, value):
        """Validate that timestamp is a reasonable epoch value"""
        if value < 0:
            raise serializers.ValidationError("Timestamp must be positive")
        # Check if timestamp is reasonable (not too far in past/future)
        current_time = datetime.now().timestamp()
        if value > current_time + 86400:  # More than 1 day in future
            raise serializers.ValidationError("Timestamp cannot be more than 1 day in the future")
        if value < current_time - 31536000:  # More than 1 year in past
            raise serializers.ValidationError("Timestamp cannot be more than 1 year in the past")
        return value


class AlertSerializer(serializers.ModelSerializer):
    timestamp_readable = serializers.SerializerMethodField()
    watch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = ["id", "watch", "watch_name", "alert_type", "heart_rate", "timestamp", "timestamp_readable"]
        read_only_fields = ["id", "timestamp_readable", "watch_name"]

    def get_timestamp_readable(self, obj):
        """Convert epoch timestamp to readable datetime string"""
        return datetime.fromtimestamp(obj.timestamp).isoformat()
    
    def get_watch_name(self, obj):
        """Get the name of the watch that generated the alert"""
        return obj.watch.name


