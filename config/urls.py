"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# config/urls.py

from django.contrib import admin
from django.urls import path, include  # 'include'가 임포트 되어 있는지 확인

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 'panel/'으로 시작하는 모든 주소는 apps.panel.urls가 처리하도록 변경
    path('panel/', include('apps.panel.urls')),

]