from django.urls import path
from rest_framework.routers import DefaultRouter

from academy.apps import AcademyConfig
from academy.views import *

app_name = AcademyConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-detail"),
    path(
        "lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"
    ),
    path(
        "lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-delete"
    ),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
] + router.urls
