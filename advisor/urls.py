from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("get_careers/", views.get_careers, name="get_careers"),
]
