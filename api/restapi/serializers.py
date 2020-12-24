from rest_framework import serializers
from .models.members import Member


class MemberSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class MemberSerializerNonAdmin(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name',
                  'first_name',
                  'last_name',
                  'phone',
                  'email',
                  'rollnumber',
                  'abroad_flag',
                  'inactive_flag',
                  'position']
