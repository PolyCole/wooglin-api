import datetime
import dateutil.parser
from json import loads, dumps

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

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
from restapi.models.members import Member
from restapi.mixins import CustomPaginationMixin


class SoberBroShiftViewSet(ViewSet, CustomPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def list(self, request):
        """
        Lists the Sober Bro shifts in the database.
        """
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = self.add_one_month(datetime.datetime.combine(datetime.date.today(), datetime.time.max))

        try:
            data = SoberBroShift.objects.get(date__range=(today_min, today_max))
        except ObjectDoesNotExist:
            return Response(
                {
                    "no_shifts": "There are no shifts found in the next month"
                },
                status=status.HTTP_200_OK
            )

        serializer = SoberBroShiftSerializer(data)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Gets a specific sober bro shift from the DB.
        """

        queryset = SoberBroShift.objects.all()

        shift = get_object_or_404(queryset, id=pk)
        serializer = SoberBroShiftSerializer(shift)

        return Response(serializer.data)

    # This is the cleanest way I could think of to support editing and removing the brothers assigned to a shift.
    @action(methods=['post', 'get', 'delete'], detail=True, permission_classes=[IsAuthenticated],
            url_path="brothers", url_name='manage_brothers')
    def manage_brothers(self, request, pk=None):
        if request.method == 'GET':
            return self.get_sober_brothers(pk)

        if 'member' not in request.data.copy():
            return Response(
                {
                    'member': 'A member id is required to add or remove a member from a shift'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if the user isn't staff, we only want them to be able to add or remove themselves from shifts.
        if not request.user.is_staff:
            member_request_id = request.data.get('member')
            current_member = Member.objects.get(email=request.user.email)
            if member_request_id != current_member.id:
                return Response(
                    {
                        'operation': 'You are trying to either drop or add a sober bro who is not yourself. You do '
                                     'not have permission to do this.'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        if request.method == 'DELETE':
            return self.delete_sober_brother(pk, request)
        if request.method == 'POST':
            return self.add_sober_brother(pk, request)

    def get_sober_brothers(self, shift_pk):
        data = SoberBro.objects.filter(shift=shift_pk)
        serializer = SoberBroSerializer(data, many=True)

        return_list = self.trim_data(serializer.data)
        return Response(return_list, status=status.HTTP_200_OK)

    def delete_sober_brother(self, shift_pk, request):
        validated_data = self.ensure_shift_exists(shift_pk, request.data.copy())

        shift = SoberBro.objects.filter(shift=shift_pk, member=validated_data['member'])

        if shift.count() == 0:
            return Response(
                {
                    "member": "The member you're trying to delete is not currenly a part of this shift."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        member = Member.objects.get(id=validated_data['member'])
        title = shift[0].shift.title
        date = shift[0].shift.date
        shift.delete()

        return_string = 'Successfully removed ' + \
                        str(member.name) + \
                        ' from the Sober Bro shift titled ' + \
                        str(title) + \
                        ' on ' + \
                        str(date)

        return Response(
            {"delete": return_string},
            status=status.HTTP_200_OK
        )

    def add_sober_brother(self, shift_pk, request):
        validated_data = self.ensure_shift_exists(shift_pk, request.data.copy())

        shift = SoberBroShift.objects.get(pk=shift_pk)
        brothers = SoberBro.objects.filter(shift=shift_pk)

        if brothers.count() == shift.capacity:
            return Response({
                'shift': 'Shift is currently full. Unable to add another brother.'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = SoberBroSerializer(data=validated_data)
            if serializer.is_valid():
                serializer.save()
                return Response(self.trim_data(serializer.data), status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        validated_data = request.data.copy()

        if 'capacity' not in validated_data:
            validated_data['capacity'] = 5

        serializer = SoberBroShiftSerializer(data=validated_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Handles PUT requests. Essentially, maps to either create or partial_update depending on the request.
        """

        # If the pk doesn't exist, it should be created.
        if SoberBroShift.objects.filter(id=pk).count() == 0:
            return self.create(request)

        # If the pk exists, the data in it should be updated.
        # However, there currently aren't any use cases in which we would want to allow the user to
        # update the entirety of a SoberBroShift record. Especially if PATCH supports multi-field updates already.
        return self.partial_update(request, pk)

    def partial_update(self, request, pk=None):
        queryset = SoberBroShift.objects.all()
        shift = get_object_or_404(queryset, id=pk)

        serializer = SoberBroShiftSerializer(shift, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = SoberBroShift.objects.all()
        shift = get_object_or_404(queryset, id=pk)

        if shift:
            shift.delete()
            return Response(
                {'delete': 'The Sober Bro Shift delete operation has completed successfully.'},
                status=status.HTTP_200_OK
            )

    # TODO: Remove this. It's a crutch because I'm not fully an expert with nested serializers yet.
    def trim_data(self, serializer_data):
        return_list = []
        data = loads(dumps(serializer_data))

        if type(data) is list:
            for objects in data:
                shift = objects.pop('shift')
                member = objects.pop('member')

                stripped_shift = {'id': shift['id'], 'title': shift['title']}
                stripped_member = {'id': member['id'], 'name': member['name']}

                return_list.append({'shift': stripped_shift, 'member': stripped_member})
        elif type(data) is dict:
            shift = data.pop('shift')
            member = data.pop('member')

            stripped_shift = {'id': shift['id'], 'title': shift['title']}
            stripped_member = {'id': member['id'], 'name': member['name']}

            return_list.append({'shift': stripped_shift, 'member': stripped_member})

        return return_list

    def ensure_shift_exists(self, shift_pk, validated_data):
        if 'shift' not in validated_data:
            validated_data['shift'] = shift_pk

        return validated_data

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
