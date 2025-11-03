from django.db import models


class LabelStudioIntegration(models.Model):
    url = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    ml_backend_url = models.URLField(blank=True)

    def __str__(self):
        return f"LabelStudio Integration - {self.url}"
