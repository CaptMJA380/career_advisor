from django.urls import path
from . import views

urlpatterns = [
    path('', views.career_advice, name='career_advice'),
    
    
]

