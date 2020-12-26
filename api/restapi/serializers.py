from rest_framework import serializers
from .models.members import Member


class MemberSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

    # TODO: Ensure this operation triggers a re-calculation of membership scores for this entry.
    def create(self, validated_data):
        if not validated_data['phone']:
            raise serializers.ValidationError(
                {"phone": "A phone number is  required for a member account to be created."}
            )

        if Member.objects.filter(phone=validated_data['phone']):
            raise serializers.ValidationError(
                {"phone": "A member account with that phone number already exists."}
            )

        member = Member.objects.create(
            user=validated_data['user'],
            name=validated_data['name'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            legal_name=validated_data['legal_name'],
            address=validated_data['address'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            rollnumber=validated_data['rollnumber'],
            member_score=validated_data['member_score'],
            inactive_flag=validated_data['inactive_flag'] if 'inactive_flag' in validated_data else False,
            abroad_flag=validated_data['abroad_flag'] if 'abroad_flag' in validated_data else False,
            temp_password=validated_data['temp_password'] if 'temp_password' in validated_data else True,
            present=0,
            position=validated_data['position']
        )

        # print("***Successfully created member.***")

        return member

    # TODO: Ensure this triggers a re-calculation of membership scores for this entry.
    # TODO: Determine when a global membership_score update should occur.
    def update(self, validated_data):
        if validated_data.get('member_score'):
            raise serializers.ValidationError({
                'member_score': 'This field is auto-generated and cannot be updated manually during a PATCH.'
            })

        return None

    def to_internal_value(self, data):
        # TODO: Email regex check.

        # TODO: Phone number regex check.

        return super(MemberSerializerAdmin, self).to_internal_value(data)


# TODO Determine how these are different.
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
