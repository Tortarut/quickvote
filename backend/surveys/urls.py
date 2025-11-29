from django.urls import path

from .views import (
    SurveyListView,
    SurveyBuilderView,
    SurveyDetailView,
    SurveyEditView,
    SurveyDeleteView,
    SurveyPublicView,
    SurveyTemplatesView,
)

app_name = "surveys"

urlpatterns = [
    path("", SurveyListView.as_view(), name="list"),
    path("create/", SurveyBuilderView.as_view(), name="create"),
    path("templates/", SurveyTemplatesView.as_view(), name="templates"),
    path("public/<slug:slug>/", SurveyPublicView.as_view(), name="public"),
    path("<slug:slug>/", SurveyDetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", SurveyEditView.as_view(), name="edit"),
    path("<slug:slug>/delete/", SurveyDeleteView.as_view(), name="delete"),
]

