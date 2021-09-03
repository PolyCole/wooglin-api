from rest_framework import serializers

from restapi.models.members import Member


class UpcomingSoberBroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', "phone"]
        depth = 1
