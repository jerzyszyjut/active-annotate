from rest_framework import serializers
from rest_framework.serializers import Serializer


class StartActiveLearningLoopSerializer(Serializer):
    dataset_id = serializers.IntegerField()
