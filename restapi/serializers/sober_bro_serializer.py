from restapi.models.members import Member
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift
from rest_framework import serializers


class SoberBroSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoberBro
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        """
        Assigns a member to a shift, based on the information passed in.
        """
        shift = SoberBroShift.objects.get(id=validated_data['shift'])
        member = Member.objects.get(id=validated_data['member'])

        sober_bro = SoberBro.objects.create(
            shift=shift,
            member=member
        )

        return sober_bro

    def to_internal_value(self, data):
        """
        Data validation.
        """

        if not Member.objects.filter(id=data.get('member')):
            raise serializers.ValidationError(
                {
                    "member": "The member you attempted to add to the shift does not exist."
                }
            )

        if SoberBro.objects.filter(shift=data['shift'], member=data['member']):
            raise serializers.ValidationError(
                {
                    "member": "The member you're attempting to assign is already signed up for this shift."
                }
            )

        return data

