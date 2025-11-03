from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from active_annotate.integrations.api.views import LabelStudioIntegrationViewSet

app_name = "integrations"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register(r"label-studio", LabelStudioIntegrationViewSet, basename="label-studio")
urlpatterns = router.urls
