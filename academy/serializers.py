from rest_framework import serializers

from academy.models import Lesson, Course


class CourseSerializer(serializers.ModelSerializer):
    number_of_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_number_of_lessons(self, instance):
        return instance.lessons.count()

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
