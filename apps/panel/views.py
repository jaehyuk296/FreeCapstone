# apps/panel/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PanelSerializer  # <-- PanelSerializer 임포트

class PanelAPIView(APIView):  # <-- View 이름 변경
    """
    간단한 텍스트를 받고 텍스트로 응답하는 API 뷰
    """
    def post(self, request):
        # 1. 입력 데이터 검증
        serializer = PanelSerializer(data=request.data)
        
        if serializer.is_valid():
            # 2. 유효한 데이터 추출
            message = serializer.validated_data['message']
            
            # 3. (임시) 간단한 비즈니스 로직: "메아리"
            # TODO: 나중에 이 부분을 Service Layer(services.py)로 대체합니다.
            bot_response = f"패널 서버가 '{message}'(을)를 잘 받았습니다!" # <-- 응답 메시지 변경
            
            # 4. JSON 응답 반환
            return Response({'response': bot_response}, status=status.HTTP_200_OK)
        
        # 5. 유효하지 않은 데이터 처리
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.
