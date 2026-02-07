from rest_framework.routers import DefaultRouter

from academy.apps import AcademyConfig
from academy.views import CourseViewSet

app_name = AcademyConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
urlpatterns = [

] + router.urls