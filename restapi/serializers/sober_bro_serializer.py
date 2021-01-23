from restapi.models.sober_bros import SoberBro
from rest_framework import serializers


class SoberBroSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoberBro
        fields = '__all__'
        depth = 1
