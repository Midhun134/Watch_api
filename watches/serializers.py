from rest_framework_mongoengine import serializers
from rest_framework import serializers as drf_serializers
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from .models import SmartWatch, WatchMetric, Alert, BPRecommendation


class SmartWatchSerializer(serializers.DocumentSerializer):
    owner = drf_serializers.CharField(read_only=True)  # Show as ObjectId string
    
    class Meta:
        model = SmartWatch
        fields = ["id", "owner", "watch_id", "name", "high_heart_rate_threshold", "low_heart_rate_threshold"]
        read_only_fields = ["id", "owner"]
    
    def create(self, validated_data):
        """Set owner from the current user"""
        validated_data['owner'] = self.context['request'].user
        watch = SmartWatch(**validated_data)
        watch.save()
        return watch
    
    def to_representation(self, instance):
        """Convert owner reference to ObjectId string for output"""
        ret = super().to_representation(instance)
        if instance.owner:
            ret['owner'] = str(instance.owner.id)
        return ret
    
    def validate_high_heart_rate_threshold(self, value):
        """Validate high threshold is reasonable"""
        if value is not None and value < 1:
            raise drf_serializers.ValidationError("High heart rate threshold must be a positive number")
        if value is not None and value > 300:
            raise drf_serializers.ValidationError("High heart rate threshold seems unreasonably high")
        return value
    
    def validate_low_heart_rate_threshold(self, value):
        """Validate low threshold is reasonable"""
        if value is not None and value < 1:
            raise drf_serializers.ValidationError("Low heart rate threshold must be a positive number")
        if value is not None and value > 200:
            raise drf_serializers.ValidationError("Low heart rate threshold seems unreasonably high")
        return value
    
    def validate(self, data):
        """Ensure high threshold is greater than low threshold if both are set"""
        high_threshold = data.get('high_heart_rate_threshold')
        low_threshold = data.get('low_heart_rate_threshold')
        
        if high_threshold is not None and low_threshold is not None:
            if high_threshold <= low_threshold:
                raise drf_serializers.ValidationError(
                    "High heart rate threshold must be greater than low heart rate threshold"
                )
        
        return data


class WatchMetricSerializer(serializers.DocumentSerializer):
    timestamp_readable = drf_serializers.SerializerMethodField()
    watch = drf_serializers.CharField()  # Accept ObjectId as string
    
    class Meta:
        model = WatchMetric
        fields = ["id", "watch", "steps", "heart_rate", "timestamp", "timestamp_readable"]
        read_only_fields = ["id", "timestamp_readable"]

    def get_timestamp_readable(self, obj):
        """Convert epoch timestamp to readable datetime string"""
        return datetime.fromtimestamp(obj.timestamp).isoformat()
    
    def validate_watch(self, value):
        """Validate and convert watch ObjectId string to SmartWatch reference"""
        # If already a SmartWatch instance, return it
        if isinstance(value, SmartWatch):
            return value
        
        try:
            # Try to convert string to ObjectId
            if isinstance(value, str):
                watch_id = ObjectId(value)
            else:
                watch_id = value
            
            # Check if watch exists
            watch = SmartWatch.objects(id=watch_id).first()
            if not watch:
                raise drf_serializers.ValidationError("Watch with this ID does not exist")
            return watch
        except InvalidId:
            raise drf_serializers.ValidationError("Invalid watch ID format")
        except drf_serializers.ValidationError:
            raise
        except Exception:
            raise drf_serializers.ValidationError("Invalid watch ID format")
    
    def validate_timestamp(self, value):
        """Validate that timestamp is a reasonable epoch value"""
        if value < 0:
            raise drf_serializers.ValidationError("Timestamp must be positive")
        # Check if timestamp is reasonable (not too far in past/future)
        current_time = datetime.now().timestamp()
        if value > current_time + 86400:  # More than 1 day in future
            raise drf_serializers.ValidationError("Timestamp cannot be more than 1 day in the future")
        if value < current_time - 31536000:  # More than 1 year in past
            raise drf_serializers.ValidationError("Timestamp cannot be more than 1 year in the past")
        return value
    
    def create(self, validated_data):
        """Create WatchMetric with watch reference"""
        watch = validated_data.pop('watch')
        watch_metric = WatchMetric(watch=watch, **validated_data)
        watch_metric.save()
        return watch_metric
    
    def to_representation(self, instance):
        """Convert watch reference to ObjectId string for output"""
        ret = super().to_representation(instance)
        if instance.watch:
            ret['watch'] = str(instance.watch.id)
        return ret


class AlertSerializer(serializers.DocumentSerializer):
    timestamp_readable = drf_serializers.SerializerMethodField()
    watch_name = drf_serializers.SerializerMethodField()
    watch = drf_serializers.CharField(read_only=True)  # Read-only, show as ObjectId string
    
    class Meta:
        model = Alert
        fields = ["id", "watch", "watch_name", "alert_type", "heart_rate", "timestamp", "timestamp_readable"]
        read_only_fields = ["id", "watch", "timestamp_readable", "watch_name"]

    def get_timestamp_readable(self, obj):
        """Convert epoch timestamp to readable datetime string"""
        return datetime.fromtimestamp(obj.timestamp).isoformat()
    
    def get_watch_name(self, obj):
        """Get the name of the watch that generated the alert"""
        return obj.watch.name
    
    def to_representation(self, instance):
        """Convert watch reference to ObjectId string for output"""
        ret = super().to_representation(instance)
        if instance.watch:
            ret['watch'] = str(instance.watch.id)
        return ret

class BestBPSerializer(drf_serializers.Serializer):
    """
    Accepts an 'age' (21-70) and returns a recommended systolic/diastolic pair.
    Simple formula: systolic increases ~0.5 mm per year from 110 at age 21,
    diastolic increases ~0.1 mm per year from 70 at age 21.
    """
    age = drf_serializers.IntegerField(min_value=21, max_value=70)

    @staticmethod
    def compute_bp(age: int):
        systolic = int(round(110 + (age - 21) * 0.5))
        diastolic = int(round(70 + (age - 21) * 0.1))
        return systolic, diastolic

class BPRecommendationSerializer(serializers.DocumentSerializer):
    user = drf_serializers.CharField(read_only=True)

    class Meta:
        model = BPRecommendation
        fields = ["id", "user", "age", "systolic", "diastolic", "recommended_bp", "timestamp"]
        read_only_fields = ["id", "user", "systolic", "diastolic", "recommended_bp", "timestamp"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.user:
            ret['user'] = str(instance.user.id)
        return ret


