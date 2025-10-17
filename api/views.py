from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import Product, CartItem, Order, OrderItem, Activity, CustomUser
from .serializers import ProductSerializer, CartItemSerializer, OrderSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.db import transaction
import qrcode, io
from django.http import HttpResponse

# ✅ PRODUCT VIEWSET
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get('category')
        if cat:
            qs = qs.filter(category=cat)
        return qs

# ✅ CART ITEM VIEWSET  
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ✅ ORDER VIEWSET (CORREGIDO)
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        user = request.user
        items = CartItem.objects.filter(user=user)
        if not items.exists():
            return Response({'detail':'Carrito vacío'}, status=400)
        total = sum([it.product.price * it.quantity for it in items])
        order = Order.objects.create(user=user, total=total, paid=False)
        for it in items:
            OrderItem.objects.create(order=order, product=it.product, quantity=it.quantity, price=it.product.price)
            # disminuir stock
            if it.product.stock >= it.quantity:
                it.product.stock -= it.quantity
                it.product.save()
        items.delete()
        Activity.objects.create(user=user, action=f'Order created #{order.id}')
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        # generar QR con info simple
        data = f"ORDER:{order.id}|USER:{order.user.email}|TOTAL:{order.total}|DATE:{order.created_at.isoformat()}"
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

# ✅ REGISTER VIEW
# CAMBIA ESTO:
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])  # ← ESTA LÍNEA ESTÁ CAUSANDO EL PROBLEMA

# POR ESTO:
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # ← PERMITE ACCESO PÚBLICO
def register_view(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=201)