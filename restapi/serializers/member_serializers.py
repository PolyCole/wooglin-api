from rest_framework import serializers
from restapi.models.members import Member
from django.contrib.auth.models import User
import re


class MemberSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Member
        # fields = '__all__'
        exclude = ('user',)

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

        if User.objects.filter(email=validated_data.get('email')).exists():
            raise serializers.ValidationError(
                {"email": "I'm sorry, it looks like there's already a user with that email."}
            )



        user = self.create_user(validated_data)

        member = Member.objects.create(
            user=user,
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
    def update(self, member_acct, new_data):
        for field in new_data:
            setattr(member_acct, field, new_data[field])

        member_acct.save()

        return member_acct

    def to_internal_value(self, data):
        if 'email' in data:
            email = data.get('email')
            if email:
                regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
                if not re.search(regex, email):
                    raise serializers.ValidationError({
                        'email': 'It would appear that you haven\'t entered a valid email address!'
                    })

        if 'phone' in data:
            phone = data.get('phone')
            if phone:
                regex = '^\d{3}\.\d{3}\.\d{4}$'
                if not re.search(regex, phone):
                    raise serializers.ValidationError({
                        'phone': 'Phone number is in an improper format. Please make sure the phone number is in the form '
                                 'xxx.xxx.xxxx'
                    })

        return super(MemberSerializerAdmin, self).to_internal_value(data)

    def create_user(self, data):
        """
        Helper method used to create a user.
        """

        username = data.get('name').lower().replace(" ", ".")
        email = data.get('email').strip()
        password = data.get('name').split(" ")[1] + str(data.get('rollnumber'))

        user = User.objects.create(username=username, email=email, password=password)
        # print("***Successfully created user.***")
        return user


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
