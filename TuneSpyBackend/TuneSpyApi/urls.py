from django.urls import path
from .views import recognize_audio

urlpatterns = [
    path('recognize/', recognize_audio, name='recognize_audio'),  # Make sure this matches the endpoint in Flutter
]
