from attr.filters import exclude
from rest_framework import serializers
from restapi.models.members import Member
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift
from django.contrib.auth.models import User
import re


class SoberBroShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoberBroShift
        fields = '__all__'

    # def create(self, validated_data):
    #     pass
    #
    # def update(self, member_acct, new_data):
    #     pass
    #
    # def to_internal_value(self, data):
    #     super(SoberBroShiftSerializer, self).to_internal_value(data)
    #
    # def create_user(self, data):
    #     pass