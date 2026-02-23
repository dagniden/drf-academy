from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100, help_text='Название курса')
    description = models.TextField(help_text='Описание курса')
    image = models.ImageField(upload_to="avatars/", null=True, blank=True, help_text='Изображение курса')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Автор курса",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", help_text='Курс')
    title = models.CharField(max_length=100, help_text='Название урока')
    description = models.TextField(help_text='Описание урока')
    image = models.ImageField(upload_to="avatars/", null=True, blank=True, help_text='Изображение урока')
    video_url = models.TextField(blank=True, null=True, help_text='Ссылка на видео урока')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Автор урока",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="subscriptions", help_text='Курс'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions", help_text='Пользователь'
    )

    def __str__(self):
        return f"{self.user} - {self.course}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
