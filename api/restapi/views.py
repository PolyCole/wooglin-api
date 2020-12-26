from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from restapi.models.members import Member
from django.contrib.auth.models import User

from .serializers import MemberSerializerAdmin
from .serializers import MemberSerializerNonAdmin


class MemberViewSet(ViewSet):
    def list(self, request):
        """
        Lists the member records in the database.
        """

        data = Member.objects.all().order_by('rollnumber')

        if request.user.is_staff:
            serializer = MemberSerializerAdmin(data, many=True)
        else:
            serializer = MemberSerializerNonAdmin(data, many=True)

        return Response(serializer.data)

    def create(self, request):
        """
        Creates Members and an attached User based on a request.
        """

        # Ensuring there's no monkey-business with the member_score value. It's to be auto-generated.
        validated_data = request.data.copy()
        validated_data['member_score'] = -1
        validated_data['present'] = 0

        # Each time we create a member, we're going to have to create a user, and set a temp password.
        validated_data['temp_password'] = True

        if User.objects.filter(email=validated_data.get('email')).exists():
            return Response({"Unable to create": "I'm sorry, it looks like there's already a user with that email."},
                            status.HTTP_400_BAD_REQUEST)

        user_id = self.create_user(validated_data)
        validated_data['user'] = user_id

        serializer = MemberSerializerAdmin(data=validated_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Gets a single member record from the table.
        """

        queryset = Member.objects.all()
        member = get_object_or_404(queryset, id=pk)
        if request.user.is_staff:
            serializer = MemberSerializerAdmin(member)
        else:
            serializer = MemberSerializerNonAdmin(member)

        return Response(serializer.data)

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass

    def create_user(self, data):
        """
        Helper method used to create a user.
        """

        username = data.get('name').lower().replace(" ", ".")
        email = data.get('email').strip()
        password = data.get('name').split(" ")[1] + str(data.get('rollnumber'))

        user = User.objects.create(username=username, email=email, password=password)
        # print("***Successfully created user.***")
        return user.id


    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        admin_only = ['update', 'partial_update', 'destroy', 'create']

        if self.action in admin_only:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
