from random import choice
import requests
from requests.exceptions import RequestException

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from core import utils
from core.constants import GET_MONSTERS, MONSTERS, TIMEOUT
from .permissions import (
    IsAdventurer,
    IsTavernKeeper,
    IsTavernKeeperOrRedAdventurer
)
from .serializers import (
    GetTokenSerializer,
    QuestCancelledSerializer,
    QuestCompletedSerializer,
    QuestCreateSerializer,
    QuestReportSerializer,
    QuestSerializer,
    QuestTakeSerializer,
    QuestTypeSerializer,
    UserRegistrationSerializer,
    UserSerializer
)
from quests.models import Quest, QuestReport, QuestType, User


class UserViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет для обработки запросов с пользователями:
    - создание (POST);
    - получение данных (GET)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self, *args, **kwargs):
        """
        Возвращает сериализатор в зависимости от действия:
        - для создания (create) - UserRegistrationSerializer;
        - для получения данных - UserSerializer.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        else:
            return UserSerializer

    @action(
        detail=False,
        methods=utils.get_methods(),
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        user = request.user
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)


class QuestTypeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для обработки заспросов типов квеста:
    - стандартные операции CRUD.
    """
    queryset = QuestType.objects.all()
    serializer_class = QuestTypeSerializer
    permission_classes = (IsTavernKeeper,)


class QuestViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для обработки заспросов типов квеста:
    - стандартные операции CRUD;
    - дополнительные действия:
        * взять квест в работу (POST) - take;
        * завершить квест (PATCH) - completed;
        * отменить квест (PATCH) - cancelled.
    """

    queryset = Quest.objects.all()
    permission_classes = [IsTavernKeeperOrRedAdventurer]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'name', 'status', 'quest_type', 'min_level', 'adventurer'
    )
    serializer_class = QuestSerializer

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action == 'create':
            return QuestCreateSerializer
        elif self.action == 'cancelled':
            return QuestCancelledSerializer
        elif self.action == 'take':
            return QuestTakeSerializer
        elif self.action == 'completed':
            return QuestCompletedSerializer
        return QuestSerializer

    def perform_create(self, serializer):
        """Автоматически сохраняет случайного монстра при создании квеста."""
        serializer.save(monster=self.get_random_monster())

    @action(
        detail=True,
        methods=utils.patch_methods(),
        permission_classes=[IsTavernKeeper]
    )
    def cancelled(self, request, pk=None):
        """Отмена квеста (только для тавернщика)."""
        quest = get_object_or_404(Quest, pk=pk)
        serializer = self.get_serializer(
            data=request.data, context={'quest': quest}
        )
        if serializer.is_valid(raise_exception=True):
            quest.status = 'cancelled'
            quest.save()
            return Response(
                {'message': 'Квест отменён'}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=utils.patch_methods(),
        permission_classes=[IsAdventurer]
    )
    def take(self, request, pk=None):
        """Взять квест в работу (только для авантюриста)."""
        quest = get_object_or_404(Quest, pk=pk)
        serializer = self.get_serializer(
            data=request.data, context={'quest': quest, 'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            quest.adventurer = request.user
            quest.status = Quest.QuestStatus.IN_PROGRESS
            quest.save()
            return Response(
                {'message': f'Вы взяли квест {quest.name}'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=utils.post_methods(),
        permission_classes=[IsAdventurer]
    )
    def completed(self, request, pk=None):
        """
        Завершение квеста и автоматическое создание отчета (только для
        авантюриста).
        """
        quest = get_object_or_404(Quest, pk=pk)
        serializer = self.get_serializer(
            data=request.data, context={'quest': quest, 'request': request}
        )

        if serializer.is_valid(raise_exception=True):
            result = serializer.validated_data['result']
            comment = serializer.validated_data.get('comment', '')

            QuestReport.objects.create(
                quest=quest,
                adventurer=request.user,
                result=result,
                comment=comment
            )
            quest.status = 'completed' if result == 'success' else 'failed'
            quest.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_random_monster():
        """
        Возвращает случайного монстра. Обращается к внешнему API. При ошибке
        обращения возвращает случайного монстра из списка по умолчанию
        """

        try:
            response = requests.get(
                GET_MONSTERS,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            monsters = data['results']
            monster_names = [monster['name'] for monster in monsters]
            return choice(monster_names)

        except RequestException:
            monster_names = MONSTERS
            return choice(monster_names)


class QuestReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Обработка запросов по отчетам о квестах:
    - только чтение (GET);
    - доступно только трактильщикам.
    """

    queryset = QuestReport.objects.all()
    permission_classes = (IsTavernKeeper,)
    serializer_class = QuestReportSerializer


class GetTokenView(views.APIView):
    """
    Класс для получения токена по паролю. Доступ - для всех
    пользователей.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = GetTokenSerializer

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        self.token = str(AccessToken.for_user(user))
        return Response({'token': self.token}, status=status.HTTP_200_OK)
