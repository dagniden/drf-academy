from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError

from academy.models import Course, Lesson


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0.0)])
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)

    def clean(self):
        super().clean()
        if not self.course and not self.lesson:
            raise ValidationError("Должен быть указан либо курс, либо урок")
        if self.course and self.lesson:
            raise ValidationError("Нельзя указать одновременно курс и урок")

    def __str__(self):
        paid_for = self.course if self.course else self.lesson
        return f"#{self.id}. Payment: {self.user} for {paid_for}. Amount: {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
