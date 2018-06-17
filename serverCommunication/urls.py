from django.urls import path

from serverCommunication.views import ServerCommunication

urlpatterns = [
path('', ServerCommunication.as_view(), name='postHardware'),
        ]