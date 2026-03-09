from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_information_about_subscription(recipients):

    send_mail(
        'Course update message',
        'This is a test email sent from a Django application.',
        settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False
    )

