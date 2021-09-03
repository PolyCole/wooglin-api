import datetime
import pytz
from json import loads, dumps

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ViewSet

from restapi.mixins import CustomPaginationMixin
from restapi.models.members import Member
from restapi.models.sober_bro_shifts import SoberBroShift
from restapi.models.sober_bros import SoberBro
from restapi.serializers import SoberBroSerializer
from restapi.serializers import SoberBroShiftSerializer
from restapi.serializers import UpcomingSoberBroSerializer


class NextShiftViewSet(ViewSet, CustomPaginationMixin):

    def list(self, request):
        """
        Returns a list of shifts beginning in the next 15 minutes, and their associated sober bros.
        """
        tz = pytz.timezone('America/Denver')
        now = datetime.datetime.now(tz)
        max_start = now + datetime.timedelta(minutes=15)

        try:
            data = SoberBroShift.objects.filter(
                date=now.date(),
                time_start__gte=now,
                time_start__lt=max_start,
                time_end__gt=now
            )
        except Exception as e:
            print(str(e))
            return Response(
                {
                    "error": "Encountered an unexpected error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if len(data) == 0:
            return Response(
                {
                    "no_shifts": "There are no shifts beginning in the next 15 minutes."
                },
                status=status.HTTP_200_OK
            )

        serializer = SoberBroShiftSerializer(data, many=True)

        for current_shift in serializer.data:
            assigned_brothers = SoberBro.objects.filter(shift=current_shift["id"])

            brothers_list = []

            for brother in assigned_brothers:
                brothers_list.append(UpcomingSoberBroSerializer(brother.member).data)

            current_shift["brothers"] = brothers_list

        return Response(serializer.data)
