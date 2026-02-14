from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from users.models import User, Payment
from academy.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполняет таблицу платежей тестовыми данными'

    def handle(self, *args, **options):
        # Получаем существующие объекты
        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR('Нет пользователей в базе данных. Создайте хотя бы одного пользователя.'))
            return

        if not courses.exists() and not lessons.exists():
            self.stdout.write(self.style.ERROR('Нет курсов и уроков в базе данных. Создайте хотя бы один курс или урок.'))
            return

        # Удаляем старые платежи (опционально)
        Payment.objects.all().delete()
        self.stdout.write(self.style.WARNING('Все существующие платежи удалены'))

        # Создаем 10 платежей
        payments_created = 0
        payment_methods = [Payment.PaymentMethod.CASH, Payment.PaymentMethod.TRANSFER]

        for i in range(10):
            user = random.choice(users)
            payment_method = random.choice(payment_methods)
            amount = Decimal(random.randint(1000, 50000))

            # Случайно выбираем: платеж за курс или за урок
            is_course_payment = random.choice([True, False])

            if is_course_payment and courses.exists():
                # Платеж за курс
                course = random.choice(courses)
                payment = Payment.objects.create(
                    user=user,
                    course=course,
                    amount=amount,
                    payment_method=payment_method
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан платеж #{payment.id}: {user.email} оплатил курс "{course.title}" - {amount} руб. ({payment.get_payment_method_display()})'
                    )
                )
            elif lessons.exists():
                # Платеж за урок
                lesson = random.choice(lessons)
                payment = Payment.objects.create(
                    user=user,
                    lesson=lesson,
                    amount=amount,
                    payment_method=payment_method
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан платеж #{payment.id}: {user.email} оплатил урок "{lesson.title}" - {amount} руб. ({payment.get_payment_method_display()})'
                    )
                )
            else:
                # Если нет уроков, создаем платеж за курс
                course = random.choice(courses)
                payment = Payment.objects.create(
                    user=user,
                    course=course,
                    amount=amount,
                    payment_method=payment_method
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан платеж #{payment.id}: {user.email} оплатил курс "{course.title}" - {amount} руб. ({payment.get_payment_method_display()})'
                    )
                )

            payments_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Успешно создано {payments_created} платежей')
        )
