from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from rest_framework_mongoengine import viewsets as mongo_viewsets
from .models import SmartWatch, WatchMetric, Alert, BPRecommendation
from .serializers import SmartWatchSerializer, WatchMetricSerializer, AlertSerializer, BestBPSerializer, BPRecommendationSerializer
from time import time
from mongoengine.errors import NotUniqueError

#this is the api logic for the watches app
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, SmartWatch):
            # For mongoengine, compare owner ObjectId with user id
            return str(obj.owner.id) == str(request.user.id)
        if isinstance(obj, WatchMetric):
            # Reload watch to ensure we have the owner reference
            obj.watch.reload()
            return str(obj.watch.owner.id) == str(request.user.id)
        if isinstance(obj, Alert):
            # Reload watch to ensure we have the owner reference
            obj.watch.reload()
            return str(obj.watch.owner.id) == str(request.user.id)
        return False


class SmartWatchViewSet(mongo_viewsets.ModelViewSet):
    serializer_class = SmartWatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SmartWatch.objects(owner=self.request.user)


class WatchMetricViewSet(mongo_viewsets.ModelViewSet):
    serializer_class = WatchMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Get all watches owned by the user, then get metrics for those watches
        user_watches = SmartWatch.objects(owner=self.request.user)
        watch_ids = [watch.id for watch in user_watches]
        return WatchMetric.objects(watch__in=watch_ids)

    def perform_create(self, serializer):
        watch = serializer.validated_data.get("watch")
        # Reload watch to ensure we have the owner reference
        watch.reload()
        if str(watch.owner.id) != str(self.request.user.id):
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
        user_watches = SmartWatch.objects(owner=self.request.user)
        watch_ids = [watch.id for watch in user_watches]
        return Alert.objects(watch__in=watch_ids)

class BestBPViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def list(self, request):
        # compute-only, do NOT persist on GET
        data = request.query_params if request.query_params else request.data
        serializer = BestBPSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        age = serializer.validated_data["age"]
        systolic, diastolic = BestBPSerializer.compute_bp(age)
        return Response({
            "age": age,
            "recommended_systolic": systolic,
            "recommended_diastolic": diastolic,
            "recommended_bp": f"{systolic}/{diastolic}"
        }, status=status.HTTP_200_OK)

    def create(self, request):
        # persist on POST
        serializer = BestBPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        age = serializer.validated_data["age"]
        systolic, diastolic = BestBPSerializer.compute_bp(age)

        if BPRecommendation.objects(user=request.user).first():
            raise DRFValidationError({"age": "A person can have only one age"})
        rec = BPRecommendation(
            user=request.user,
            age=age,
            systolic=systolic,
            diastolic=diastolic,
            recommended_bp=f"{systolic}/{diastolic}",
            timestamp=int(time())
        )
        try:
            rec.save()
        except NotUniqueError:
            # race-condition / DB-level uniqueness hit
            raise DRFValidationError({"age": "A person can have only one age"})
        out = BPRecommendationSerializer(rec, context={'request': request}).data
        return Response(out, status=status.HTTP_201_CREATED)