from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions

from restapi import views

router = routers.DefaultRouter()
router.register(r'member', views.MemberViewSet, basename='member')
router.register(r'sober-bro-shift', views.SoberBroShiftViewSet, basename='sober-bro-shift')

schema_view = get_schema_view(
    openapi.Info(
        title="Wooglin API",
        default_version='v1',
        description="This is the API that allows access to the data collected and maintained by the Alpha Zeta "
                    "chapter of Beta Theta Pi",
        terms_of_service="",
        contact=openapi.Contact(email="colepolyak@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
