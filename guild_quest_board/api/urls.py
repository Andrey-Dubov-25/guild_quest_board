from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    GetTokenView,
    QuestReportViewSet,
    QuestTypeViewSet,
    QuestViewSet,
    UserViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('quests', QuestViewSet, basename='quests')
router.register('quest-types', QuestTypeViewSet, basename='quest-types')
router.register('quest-reports', QuestReportViewSet, basename='quest-reports')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/token/',
        GetTokenView.as_view(),
        name='token'
    )
]
