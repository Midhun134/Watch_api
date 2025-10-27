from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import SmartWatch, WatchMetric, Alert
from .serializers import SmartWatchSerializer, WatchMetricSerializer, AlertSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, SmartWatch):
            return obj.owner_id == request.user.id
        if isinstance(obj, WatchMetric):
            return obj.watch.owner_id == request.user.id
        if isinstance(obj, Alert):
            return obj.watch.owner_id == request.user.id
        return False


class SmartWatchViewSet(viewsets.ModelViewSet):
    serializer_class = SmartWatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SmartWatch.objects.filter(owner=self.request.user)


class WatchMetricViewSet(viewsets.ModelViewSet):
    serializer_class = WatchMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return WatchMetric.objects.filter(watch__owner=self.request.user)

    def perform_create(self, serializer):
        watch = serializer.validated_data.get("watch")
        if watch.owner_id != self.request.user.id:
            raise PermissionDenied("Cannot attach metrics to a watch you do not own.")
        serializer.save()


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for alerts. Users can only view their own alerts.
    Alerts are automatically created when heart rate thresholds are exceeded.
    """
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Alert.objects.filter(watch__owner=self.request.user)


# Create your views here.
