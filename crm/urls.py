from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from . import views
from .views import RegisterView, EmployeeViewSet, ClientViewSet, SalesPipelineStageViewSet, ProfileView, DashboardView, \
    ClientManagerDashboardView, ProductViewSet, SaleViewSet, chat_api

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'stages', SalesPipelineStageViewSet)
router.register(r'products', ProductViewSet, basename="product")
router.register(r'sales', SaleViewSet, basename="sale")


urlpatterns = [
    path('api/chat/', chat_api, name='chat_api'),
    path('clients/cleanup/', views.cleanup_old_clients, name='cleanup_old_clients'),
    path('', include(router.urls)),  # Автоматическая регистрация маршрутов через DefaultRouter
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/client-manager/', ClientManagerDashboardView.as_view(), name='client_manager_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),


]
