from rest_framework.routers import DefaultRouter
from .views import SmartWatchViewSet, WatchMetricViewSet, AlertViewSet


router = DefaultRouter()
router.register(r"watches", SmartWatchViewSet, basename="watch")
router.register(r"watch-metrics", WatchMetricViewSet, basename="watch-metric")
router.register(r"alerts", AlertViewSet, basename="alert")

urlpatterns = router.urls


