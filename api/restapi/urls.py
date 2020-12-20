from django.urls import path, include
from rest_framework import routers
from restapi import views

router = routers.DefaultRouter()
router.register(r'member', views.MemberViewSet)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
]