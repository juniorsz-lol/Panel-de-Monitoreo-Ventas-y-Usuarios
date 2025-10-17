from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartItemViewSet, OrderViewSet, register_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('cart', CartItemViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register_view),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('order/', OrderViewSet.as_view({'post':'create'}), name='order-create'),
    path('order/<int:pk>/qr/', OrderViewSet.as_view({'get':'qr'}), name='order-qr'),
]