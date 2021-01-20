from attr.filters import exclude
from rest_framework import serializers
from restapi.models.members import Member
from restapi.models.sober_bros import SoberBro
from django.contrib.auth.models import User
import re


class SoberBroSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoberBro
        fields = '__all__'

    def create(self, validated_data):
        pass

    def update(self, member_acct, new_data):
        pass

    def to_internal_value(self, data):
        super(SoberBroSerializer, self).to_internal_value(data)

    def create_user(self, data):
        pass