from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, mixins

from restapi.models.members import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet, mixins.UpdateModelMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Member.objects.all().order_by('user_id')
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]


