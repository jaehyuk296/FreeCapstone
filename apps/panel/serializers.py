# apps/panel/serializers.py

from rest_framework import serializers

class PanelSerializer(serializers.Serializer):
    """
    사용자가 보낼 메시지(데이터)의 형식을 정의합니다.
    """
    message = serializers.CharField(max_length=1000, help_text="사용자의 메시지")