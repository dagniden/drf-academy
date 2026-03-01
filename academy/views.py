from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academy.models import Course, Lesson, Subscription
from academy.paginators import LessonCoursePagination
from academy.serializers import (CourseSerializer, LessonSerializer,
                                 PaymentSerializer)
from users.models import Payment
from users.permissions import IsModerator, IsOwner


@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Возвращает постраничный список всех курсов с количеством уроков и статусом подписки.",
    ),
    create=extend_schema(
        summary="Создать курс",
        description="Создаёт новый курс. Недоступно модераторам. Владелец устанавливается автоматически.",
    ),
    retrieve=extend_schema(
        summary="Детали курса",
        description="Возвращает полную информацию о курсе: описание, список уроков и статус подписки текущего пользователя.",
    ),
    update=extend_schema(
        summary="Обновить курс",
        description="Полное обновление курса. Доступно только владельцу или модератору.",
    ),
    partial_update=extend_schema(
        summary="Частично обновить курс",
        description="Частичное обновление полей курса. Доступно только владельцу или модератору.",
    ),
    destroy=extend_schema(
        summary="Удалить курс",
        description="Удаляет курс. Доступно только владельцу, модераторы удалять не могут.",
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    """Управление курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = LessonCoursePagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ["update", "retrieve", "list", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]

        return super().get_permissions()


@extend_schema(
    summary="Создать урок",
    description="Создаёт новый урок. Недоступно модераторам. Владелец устанавливается автоматически.",
)
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [~IsModerator, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    summary="Список уроков",
    description="Возвращает постраничный список всех уроков. Доступно авторизованным пользователям.",
)
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonCoursePagination


@extend_schema(
    summary="Детали урока",
    description="Возвращает полную информацию об уроке. Доступно владельцу или модератору.",
)
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


@extend_schema(
    summary="Обновить урок",
    description="Полное или частичное обновление урока. Доступно владельцу или модератору.",
)
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


@extend_schema(
    summary="Удалить урок",
    description="Удаляет урок. Доступно владельцу. Модераторы удалять не могут.",
)
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator | IsOwner]


@extend_schema(
    summary="Список платежей",
    description=(
            "Возвращает список платежей текущего пользователя. "
            "Поддерживает фильтрацию по курсу, уроку и способу оплаты, "
            "а также сортировку по дате платежа."
    ),
)
class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [~IsModerator, IsAuthenticated]

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = [
        "payment_date",
    ]


class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


@extend_schema_view(
    post=extend_schema(
        summary="Переключить подписку на курс",
        description=(
                "Подписывает текущего пользователя на курс или отменяет подписку, если она уже активна. "
                "В теле запроса передаётся `course_id`."
        ),
        responses={
            200: OpenApiResponse(
                description='`{"message": "Подписка оформлена"}` или `{"message": "Подписка отменена"}`'),
        },
    ),
)
class SubscriptionToggleAPIView(APIView):
    """Управление подпиской на курс."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка отменена"
        else:
            Subscription.objects.create(user=user, course_id=course_id)
            message = "Подписка оформлена"

        return Response({"message": message}, status=200)
