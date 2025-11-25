from rest_framework.serializers import IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import ValidationError

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction


class ClassificationLabelSerializer(ModelSerializer):
    class Meta:
        model = ClassificationLabel
        fields = "__all__"


class ClassificationPredictionSerializer(ModelSerializer):
    predicted_label = ClassificationLabelSerializer(required=False, read_only=True)
    predicted_class_index = IntegerField(write_only=True, required=False)

    class Meta:
        model = ClassificationPrediction
        fields = "__all__"

    def create(self, validated_data):
        predicted_class_index = validated_data.pop("predicted_class_index", None)

        if predicted_class_index is not None:
            datapoint = validated_data.get("datapoint")
            try:
                label = ClassificationLabel.objects.get(
                    dataset=datapoint.dataset,
                    class_index=predicted_class_index,
                )
                validated_data["predicted_label"] = label
            except ClassificationLabel.DoesNotExist as err:
                error_msg = (
                    f"Label with class_index {predicted_class_index} "
                    f"not found in dataset {datapoint.dataset.id}"
                )
                raise ValidationError(error_msg) from err

        return super().create(validated_data)

    def update(self, instance, validated_data):
        predicted_class_index = validated_data.pop("predicted_class_index", None)

        if predicted_class_index is not None:
            datapoint = instance.datapoint
            try:
                label = ClassificationLabel.objects.get(
                    dataset=datapoint.dataset,
                    class_index=predicted_class_index,
                )
                validated_data["predicted_label"] = label
            except ClassificationLabel.DoesNotExist as err:
                error_msg = (
                    f"Label with class_index {predicted_class_index} "
                    f"not found in dataset {datapoint.dataset.id}"
                )
                raise ValidationError(error_msg) from err

        return super().update(instance, validated_data)


class ClassificationDatapointSerializer(ModelSerializer):
    file_url = SerializerMethodField(read_only=True)
    predictions = ClassificationPredictionSerializer(many=True, read_only=True)
    label = ClassificationLabelSerializer(required=False, read_only=True)
    class_index = IntegerField(write_only=True, required=False)

    class Meta:
        model = ClassificationDatapoint
        fields = "__all__"
        extra_kwargs = {
            "file": {"write_only": True, "required": False},
        }

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def create(self, validated_data):
        class_index = validated_data.pop("class_index", None)

        if class_index is not None:
            dataset = validated_data.get("dataset")
            try:
                label = ClassificationLabel.objects.get(
                    dataset=dataset,
                    class_index=class_index,
                )
                validated_data["label"] = label
            except ClassificationLabel.DoesNotExist as err:
                error_msg = (
                    f"Label with class_index {class_index} "
                    f"not found in dataset {dataset.id}"
                )
                raise ValidationError(error_msg) from err

        return super().create(validated_data)

    def update(self, instance, validated_data):
        class_index = validated_data.pop("class_index", None)

        if class_index is not None:
            dataset = instance.dataset
            try:
                label = ClassificationLabel.objects.get(
                    dataset=dataset,
                    class_index=class_index,
                )
                validated_data["label"] = label
            except ClassificationLabel.DoesNotExist as err:
                error_msg = (
                    f"Label with class_index {class_index} "
                    f"not found in dataset {dataset.id}"
                )
                raise ValidationError(error_msg) from err

        return super().update(instance, validated_data)


class ClassificationDatasetSerializer(ModelSerializer):
    datapoints = ClassificationDatapointSerializer(many=True, read_only=True)
    labels = ClassificationLabelSerializer(many=True, read_only=True)

    class Meta:
        model = ClassificationDataset
        fields = "__all__"
        read_only_fields = ("epoch", "state")
