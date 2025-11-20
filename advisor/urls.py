from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
   # path("get_careers/", views.get_careers, name="get_careers"),
]
