import datetime
from datetime import timedelta
from json import loads, dumps

import re

from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings

from restapi.serializers import SoberBroShiftSerializer
from restapi.serializers import SoberBroSerializer

from restapi.models.sober_bro_shifts import SoberBroShift
from restapi.models.sober_bros import SoberBro
from restapi.mixins import CustomPaginationMixin


class SoberBroShiftViewSet(ViewSet, CustomPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def list(self, request):
        """
        Lists the Sober Bro shifts in the database.
        """
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = self.add_one_month(datetime.datetime.combine(datetime.date.today(), datetime.time.max))

        # data = SoberBroShift.objects.get(date__range=(today_min, today_max)).order_by('date')
        data = SoberBroShift.objects.all()

        serializer = SoberBroShiftSerializer(data, many=True)

        return Response(serializer.data)

    # def create(self, request):
    #     pass
    #

    def retrieve(self, request, pk=None):
        """
        Gets a single member record from the table.
        """

        queryset = SoberBroShift.objects.all()

        shift = get_object_or_404(queryset, id=pk)
        serializer = SoberBroShiftSerializer(shift)

        return Response(serializer.data)

    @action(methods=['post', 'get', 'delete'], detail=True, permission_classes=[IsAuthenticated],
            url_path="brothers", url_name='manage_brothers')
    def manage_brothers(self, request, pk=None):
        if request.method == 'DELETE':
            return self.delete_sober_brothers(pk)
        if request.method == 'GET':
            return self.get_sober_brothers(pk)
        if request.method == 'POST':
            return self.add_sober_brother(pk)

    def get_sober_brothers(self, pk):
        data = SoberBro.objects.filter(shift=pk)
        serializer = SoberBroSerializer(data, many=True)
        
        return_list = self.trim_data(serializer.data)
        return Response(return_list, status=status.HTTP_200_OK)

    def delete_sober_brother(self, pk):
        return Response({"Deleting": "Brother"}, status=status.HTTP_418_IM_A_TEAPOT)

    def add_sober_brother(self, pk):
        return Response({"Adding": "Brothers"}, status=status.HTTP_418_IM_A_TEAPOT)

    # def update(self, request, pk=None):
    #     pass
    #
    # def partial_update(self, request, pk=None):
    #     pass
    #
    # def destroy(self, request, pk=None):
    #     pass

    def trim_data(self, serializer_data):
        return_list = []
        data = loads(dumps(serializer_data))

        for objects in data:
            shift = objects.pop('shift')
            member = objects.pop('member')

            stripped_shift = {'id': shift['id'], 'title': shift['title']}
            stripped_member = {'id': member['id'], 'name': member['name']}

            return_list.append({'shift': stripped_shift, 'member': stripped_member})

        return return_list

    def add_one_month(self, dt0):
        use_date = dt0 + datetime.timedelta(days=+31)
        return use_date

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
