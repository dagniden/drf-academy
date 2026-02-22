from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from academy.models import Course, Lesson
from users.models import User


class LessonTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@mail.ru", password="test", username="admin"
        )
        # self.group_moder, _ = self.user.groups.get_or_create(name='Moderators')
        # self.user.groups.add(self.group_moder)
        # self.user.save()

        self.course = Course.objects.create(title="Тест курс", owner=self.user)
        self.lesson = Lesson.objects.create(
            title="Тест урок", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        url = reverse("academy:lesson-detail", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)

    def test_lesson_create(self):
        url = reverse("academy:lesson-create")
        data = {
            "title": "Тест урок 2",
            "course": self.course.id,
            "owner": self.user.id,
            "description": "Тест",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        url = reverse("academy:lesson-update", args=(self.lesson.pk,))
        response = self.client.patch(url, {"title": "Омега"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Омега")

    def test_lesson_delete(self):
        url = reverse("academy:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        url = reverse("academy:lesson-list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.id,
                    "title": "Тест урок",
                    "description": "",
                    "image": None,
                    "video_url": None,
                    "course": self.course.id,
                    "owner": self.user.id,
                }
            ],
        }
        self.assertEqual(data, result)

    def test_subscription(self):
        url = reverse("academy:subscription-toggle")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data=data)
        data = response.json()
        result = {"message": "Подписка оформлена"}
        self.assertEqual(data, result)
