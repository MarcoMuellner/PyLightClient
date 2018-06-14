from django.urls import path

from . import views

path('', views.handleRequests, name='postHardware'),