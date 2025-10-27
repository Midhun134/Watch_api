from django.contrib import admin
from .models import SmartWatch, WatchMetric


@admin.register(SmartWatch)
class SmartWatchAdmin(admin.ModelAdmin):
    list_display = ("id", "watch_id", "name", "owner")
    search_fields = ("watch_id", "name", "owner__email")


@admin.register(WatchMetric)
class WatchMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "get_watch_name", "get_watch_id", "steps", "heart_rate", "get_timestamp_readable")
    list_filter = ("timestamp",)
    search_fields = ("watch__watch_id", "watch__name")

    def get_watch_name(self, obj):
        return obj.watch.name
    get_watch_name.short_description = "Watch Name"

    def get_watch_id(self, obj):
        return obj.watch.watch_id
    get_watch_id.short_description = "Watch ID"
    
    def get_timestamp_readable(self, obj):
        from datetime import datetime
        return datetime.fromtimestamp(obj.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    get_timestamp_readable.short_description = "Timestamp"


# Register your models here.
