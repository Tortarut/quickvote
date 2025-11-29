"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import LandingPageView
from analytics.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("auth/", include(("users.urls", "users"), namespace="users")),
    path("surveys/", include(("surveys.urls", "surveys"), namespace="surveys")),
    path("responses/", include(("responses.urls", "responses"), namespace="responses")),
    path("analytics/", include(("analytics.urls", "analytics"), namespace="analytics")),
    path("notifications/", include(("notifications.urls", "notifications"), namespace="notifications")),
    path("api/", include("config.api_urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
