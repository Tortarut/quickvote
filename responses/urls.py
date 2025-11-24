from django.urls import path

from .views import SubmitResponseAPIView, SurveyStatisticsAPIView, SurveyExportView, ThankYouView

app_name = "responses"

urlpatterns = [
    path("thank-you/", ThankYouView.as_view(), name="thank-you"),
    path("api/<slug:slug>/submit/", SubmitResponseAPIView.as_view(), name="api-submit"),
    path("api/<slug:slug>/stats/", SurveyStatisticsAPIView.as_view(), name="api-stats"),
    path("api/<slug:slug>/export/<str:fmt>/", SurveyExportView.as_view(), name="api-export"),
]

