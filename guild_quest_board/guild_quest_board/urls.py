from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from api import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urls))
]


schema_view = get_schema_view(
    openapi.Info(
        title="GQB API",
        default_version='',
        description="Документация для проекта GQB",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns += [
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    )
]
