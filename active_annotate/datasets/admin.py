from django.contrib import admin

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction

admin.site.register(ClassificationDataset)
admin.site.register(ClassificationLabel)
admin.site.register(ClassificationDatapoint)
admin.site.register(ClassificationPrediction)
