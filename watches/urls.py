from rest_framework.routers import DefaultRouter
from .views import SmartWatchViewSet, WatchMetricViewSet, AlertViewSet, BestBPViewSet


router = DefaultRouter()
router.register(r"watches", SmartWatchViewSet, basename="watch")
router.register(r"watch-metrics", WatchMetricViewSet, basename="watch-metric")
router.register(r"alerts", AlertViewSet, basename="alert")
router.register(r"best-bp", BestBPViewSet, basename="best-bp")

urlpatterns = router.urls


