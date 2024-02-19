from django.urls import path
from . import views

urlpatterns = [
    path('index/',view=views.index , name="index"),
    path('try/',view=views.try_ , name="try"),
]