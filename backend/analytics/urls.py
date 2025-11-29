from django.urls import path

from .views import DashboardView, AdminMonitorView

app_name = "analytics"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("monitor/", AdminMonitorView.as_view(), name="admin-monitor"),
]

