from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from usuarios.views import UsuarioViewSet

# Router gera o API Root e os endpoints do ModelViewSet
router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")

api_urlpatterns = [
    # Router
    path("", include(router.urls)),
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # OpenAPI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/", include(api_urlpatterns)),
]
