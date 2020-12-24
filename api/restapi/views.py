from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from restapi.models.members import Member

from .serializers import MemberSerializerAdmin
from .serializers import MemberSerializerNonAdmin


class MemberViewSet(ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def list(self, request):
        data = Member.objects.all().order_by('rollnumber')

        if request.user.is_staff:
            serializer = MemberSerializerAdmin(data, many=True)
        else:
            serializer = MemberSerializerNonAdmin(data, many=True)

        return Response(serializer.data)

    # def create(self, request):
    #     pass

    def retrieve(self, request, pk=None):
        queryset = Member.objects.all()
        member = get_object_or_404(queryset, user_id=pk)
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
        admin_only = ['update', 'partial_update', 'destroy']

        if self.action in admin_only:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


    def select_serializer(request):
        if request.user.is_staff:
            return True
        else:
            return False





