from rest_framework.routers import DefaultRouter

from surveys.api import SurveyViewSet, SurveyTemplateViewSet

router = DefaultRouter()
router.register("surveys", SurveyViewSet, basename="survey")
router.register("templates", SurveyTemplateViewSet, basename="template")

urlpatterns = router.urls

