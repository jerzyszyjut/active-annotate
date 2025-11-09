from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from active_annotate.datasets.api.views import ClassificationDatapointViewSet
from active_annotate.datasets.api.views import ClassificationDatasetViewSet
from active_annotate.datasets.api.views import ClassificationLabelViewSet
from active_annotate.datasets.api.views import ClassificationPredictionViewSet

app_name = "datasets"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register(r"datasets/classification", ClassificationDatasetViewSet)
router.register(r"labels/classification", ClassificationLabelViewSet)
router.register(r"datapoints/classification", ClassificationDatapointViewSet)
router.register(r"predictions/classification", ClassificationPredictionViewSet)

urlpatterns = router.urls
