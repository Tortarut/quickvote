from django.urls import path

from .views import NotificationCenterView, ComplaintListView

app_name = "notifications"

urlpatterns = [
    path("", NotificationCenterView.as_view(), name="center"),
    path("complaints/", ComplaintListView.as_view(), name="complaints"),
]

