from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_mongoengine import viewsets as mongo_viewsets
from .models import SmartWatch, WatchMetric, Alert
from .serializers import SmartWatchSerializer, WatchMetricSerializer, AlertSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, SmartWatch):
            # For mongoengine, compare owner_id with user id
            return obj.owner_id == request.user.id
        if isinstance(obj, WatchMetric):
            # Reload watch to ensure we have the owner reference
            obj.watch.reload()
            return obj.watch.owner_id == request.user.id
        if isinstance(obj, Alert):
            # Reload watch to ensure we have the owner reference
            obj.watch.reload()
            return obj.watch.owner_id == request.user.id
        return False


class SmartWatchViewSet(mongo_viewsets.ModelViewSet):
    serializer_class = SmartWatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SmartWatch.objects(owner_id=self.request.user.id)


class WatchMetricViewSet(mongo_viewsets.ModelViewSet):
    serializer_class = WatchMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Get all watches owned by the user, then get metrics for those watches
        user_watches = SmartWatch.objects(owner_id=self.request.user.id)
        watch_ids = [watch.id for watch in user_watches]
        return WatchMetric.objects(watch__in=watch_ids)

    def perform_create(self, serializer):
        watch = serializer.validated_data.get("watch")
        # Reload watch to ensure we have the owner reference
        watch.reload()
        if watch.owner_id != self.request.user.id:
            raise PermissionDenied("Cannot attach metrics to a watch you do not own.")
        serializer.save()


class AlertViewSet(mongo_viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for alerts. Users can only view their own alerts.
    Alerts are automatically created when heart rate thresholds are exceeded.
    """
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Get all watches owned by the user, then get alerts for those watches
        user_watches = SmartWatch.objects(owner_id=self.request.user.id)
        watch_ids = [watch.id for watch in user_watches]
        return Alert.objects(watch__in=watch_ids)


# Create your views here.
