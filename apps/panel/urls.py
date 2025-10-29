# apps/panel/urls.py

from django.urls import path
from .views import PanelAPIView  # <-- PanelAPIView 임포트

urlpatterns = [
    path('send/', PanelAPIView.as_view(), name='panel-send'),
]