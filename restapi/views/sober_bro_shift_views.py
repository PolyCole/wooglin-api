import re
import datetime
from datetime import timedelta
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings

from restapi.models.sober_bro_shifts import SoberBroShift

from restapi.serializers import SoberBroShiftSerializer

from restapi.mixins import CustomPaginationMixin
from restapi.data_utilities import apply_search_filters, apply_ordering


class SoberBroShiftViewSet(ViewSet, CustomPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def list(self, request):
        """
        Lists the Sober Bro shifts in the database.
        """
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = self.add_one_month(datetime.datetime.combine(datetime.date.today(), datetime.time.max))

        data = SoberBroShift.objects.get(date__range=(today_min, today_max)).order_by('date')

        serializer =


    # def create(self, request):
    #     pass
    #
    # def retrieve(self, request, pk=None):
    #     pass
    #
    # def update(self, request, pk=None):
    #     pass
    #
    # def partial_update(self, request, pk=None):
    #     pass
    #
    # def destroy(self, request, pk=None):
    #     pass

    def add_one_month(self, dt0):
        dt1 = dt0.replace(days=1)
        dt2 = dt1 + timedelta(days=32)
        dt3 = dt2.replace(days=1)
        return dt3

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
