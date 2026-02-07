from rest_framework import viewsets, generics
from rest_framework  import viewsets

from academy.models import Lesson, Course
from academy.serializers import LessonSerializer, CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
