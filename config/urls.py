from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

from config.views import db_status


def home(request):
    return HttpResponse(
        "<h1>Hello from AWS EC2!</h1>"
        "<p>Deployed using GitHub</p>"
    )


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path('db-status/', db_status),
]