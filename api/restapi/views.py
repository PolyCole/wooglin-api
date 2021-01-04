import re

from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings


from restapi.models.members import Member
from django.contrib.auth.models import User

from .serializers import MemberSerializerAdmin
from .serializers import MemberSerializerNonAdmin

from restapi.mixins import CustomPaginationMixin

from .data_utilities import apply_search_filters, apply_ordering


class MemberViewSet(ViewSet, CustomPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    # TODO: I think there's room for optimization and code cleanup here.
    def list(self, request):
        """
        Lists the member records in the database.
        """
        data = Member.objects.all().order_by('id')
        data = apply_search_filters(data, request.query_params, request.user.is_staff)

        # Processing our orderby requess.
        if 'order_by' in request.query_params:
            operations = request.query_params['order_by'].split(",")

            for op in operations:
                # Ensuring the commands are in the format we expect.
                regex = '^([a-z_]+)\.(asc|desc)$'
                if re.search(regex, op) is None:
                    return Response({
                        "order_by": "One or more of your ordering parameters are formatted incorrectly. Please ensure "
                                    "they follow the format: ?order_by=name.asc,phone.desc "
                    }, status.HTTP_400_BAD_REQUEST)

            data = apply_ordering(data, request.query_params, request.user.is_staff)

            if type(data) is str:
                return Response({
                    "order_by": str(data)
                }, status.HTTP_403_FORBIDDEN)

        if request.user.is_staff:
            response_object = self.list_admin(request, data)
        else:
            response_object = self.list_nonadmin(request, data)

        return response_object

    def list_admin(self, request, data):
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = MemberSerializerAdmin(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = MemberSerializerAdmin(data, many=True)
            return serializer.data

    def list_nonadmin(self, request, data):
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = MemberSerializerNonAdmin(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = MemberSerializerNonAdmin(data, many=True)
            return serializer.data


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
