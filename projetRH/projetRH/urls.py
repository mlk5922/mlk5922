#projetRH\urls.py
"""
URL configuration for projetRH project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    
Add an import:  from my_app import views
Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    
Add an import:  from other_app.views import Home
Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    
Import the include() function: from django.urls import include, path
Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# projetRH/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.views import login_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="HR Management API",
        default_version='v1',
        description="API documentation for HR Management System",
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login, name='root'),  # Redirige vers la page de login
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),  # Inclure les URL de core
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('api/', include('core.urls')),  # Les routes API sont sous /api/
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Pour obtenir un jeton
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Pour rafraîchir un jeton
    path('login/', login_view, name='login'),  # Page de connexion à part
]

# Ajouter la configuration pour les médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)