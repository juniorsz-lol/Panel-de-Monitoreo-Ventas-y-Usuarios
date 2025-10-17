from rest_framework import serializers
from .models import CustomUser, Product, CartItem, Order, OrderItem, Activity
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = CustomUser
        fields = ('id','first_name','last_name','email','password','gender','role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    def create(self, validated_data):
        user = CustomUser(
            email = validated_data['email'],
            first_name = validated_data.get('first_name',''),
            last_name = validated_data.get('last_name',''),
            gender = validated_data.get('gender',None),
            role = validated_data.get('role','buyer')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta: model = Product; fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')
    class Meta:
        model = CartItem
        fields = ('id','user','product','product_id','quantity','added_at')
        read_only_fields = ('user','added_at')

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id','user','total','created_at','paid','items')
