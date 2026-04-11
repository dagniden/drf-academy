from rest_framework import serializers

from academy.models import Course, Lesson, Subscription
from academy.services import StripeService
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
        fields = [
            "id",
            "payment_date",
            "payment_method",
            "amount",
            "user",
            "course",
            "lesson",
            "payment_url",
        ]
        read_only_fields = ["id", "payment_date", "payment_url", "user"]

    def validate(self, attrs):
        course = attrs.get("course")
        lesson = attrs.get("lesson")

        if not course and not lesson:
            raise serializers.ValidationError("Укажите курс или урок")
        if course and lesson:
            raise serializers.ValidationError("Нельзя указать одновременно курс и урок")

        return attrs

    def create(self, validated_data):
        paid_item = validated_data.get("course") or validated_data.get("lesson")
        amount_in_cents = int(validated_data["amount"] * 100)

        product = StripeService.create_product(
            product_name=paid_item.title,
            product_description=getattr(paid_item, "description", "") or paid_item.title,
        )
        price = StripeService.create_price(product=product, product_price=amount_in_cents)
        payment_url = StripeService.create_checkout_session(price=price)

        validated_data["payment_url"] = payment_url
        return super().create(validated_data)


