from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from users.models import User


@shared_task
def send_information_about_subscription(recipients):
    send_mail(
        'Course update message',
        'This is a test email sent from a Django application.',
        settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False
    )


@shared_task
def block_inactive_user():
    print("Старт задачи academy.tasks.block_inactive_user")
    now = timezone.now()
    one_month_ago = now - relativedelta(months=1)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_superuser=False, is_active=True)
    for user in inactive_users:
        user.is_active = False

        user.save()
        print(f"Заблокирован пользователь {user}")
    print("Завершение задачи academy.tasks.block_inactive_user")
