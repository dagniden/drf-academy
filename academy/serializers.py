from rest_framework import serializers

from academy.models import Course, Lesson, Subscription
from academy.validators import URLValidator
from users.models import Payment


class LessonSerializer(serializers.ModelSerializer):
    """Урок: базовые поля + валидация ссылки на YouTube-видео."""

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [URLValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    """Полное представление курса с вложенными уроками и статусом подписки."""
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "lessons_count",
            "lessons",
            "owner",
            "is_subscribed",
        ]

    def get_lessons_count(self, instance):
        return instance.lessons.count()

    def get_is_subscribed(self, instance):
        user = self.context["request"].user
        return Subscription.objects.filter(user=user, course=instance).exists()


class PaymentSerializer(serializers.ModelSerializer):
    """Платёж: содержит пользователя, курс или урок, сумму и способ оплаты."""

    class Meta:
        model = Payment
        fields = "__all__"
