from rest_framework import serializers
from .models import IrisObservation # Benim ana modelim

class IrisObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrisObservation
        fields = ['id', 'garden', 'sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']