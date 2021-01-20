import re

from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings


from restapi.models.members import Member
from django.contrib.auth.models import User

from restapi.serializers import MemberSerializerAdmin
from restapi.serializers import MemberSerializerNonAdmin

from restapi.mixins import CustomPaginationMixin
from restapi.data_utilities import apply_search_filters, apply_ordering


class SoberBroViewSet(ViewSet, CustomPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    calculated_fields = ['member_score', 'present']

    # TODO: I think there's room for optimization and code cleanup here.
    def list(self, request):
        pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

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
