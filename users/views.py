from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import CustomTokenObtainPairSerializer, UserSerializer


@extend_schema(
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя. Доступно без авторизации.",
)
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


@extend_schema(
    summary="Получить JWT-токен",
    description=(
        "Аутентификация по email и паролю. "
        "Возвращает пару токенов: `access` и `refresh`."
    ),
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
        description="Возвращает список всех пользователей. Требует авторизации.",
    ),
    create=extend_schema(
        summary="Создать пользователя",
        description="Создаёт нового пользователя. Доступно без авторизации.",
    ),
    retrieve=extend_schema(
        summary="Профиль пользователя",
        description="Возвращает данные конкретного пользователя. Требует авторизации.",
    ),
    update=extend_schema(
        summary="Обновить пользователя",
        description="Полное обновление данных пользователя. Требует авторизации.",
    ),
    partial_update=extend_schema(
        summary="Частично обновить пользователя",
        description="Частичное обновление данных пользователя. Требует авторизации.",
    ),
    destroy=extend_schema(
        summary="Удалить пользователя",
        description="Удаляет пользователя. Требует авторизации.",
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            # Создание пользователя доступно всем (регистрация)
            self.permission_classes = [AllowAny]
        else:
            # Все остальные операции требуют авторизации
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
