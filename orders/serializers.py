from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, OrderHistory
from .exceptions import (
    CartNotFoundException, CartEmptyException, InvalidPaymentMethodException,
    InvalidDeliveryAddressException
)
from products.serializers import ProductSerializer
from products.exceptions import InsufficientStockException

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['added_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0.")
        return value
    
    def validate(self, attrs):
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        # Vérifier que le produit existe et est disponible
        from products.models import Product
        try:
            product = Product.objects.get(id=product_id, is_available=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé ou indisponible.")
        
        # Vérifier le stock
        if quantity > product.stock:
            raise InsufficientStockException()
        
        attrs['product'] = product
        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price_with_tax = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'total_price_with_tax', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price']

class OrderHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = OrderHistory
        fields = ['id', 'status', 'status_display', 'comment', 'created_at', 'created_by_email']
        read_only_fields = ['created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'payment_method', 
            'payment_method_display', 'payment_status', 'delivery_address', 
            'delivery_city', 'delivery_postal_code', 'delivery_country', 
            'delivery_phone', 'subtotal', 'tax_amount', 'shipping_cost', 
            'total_amount', 'items_count', 'items', 'history', 'created_at', 
            'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'order_number', 'subtotal', 'tax_amount', 'total_amount', 
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'payment_method', 'delivery_address', 'delivery_city', 
            'delivery_postal_code', 'delivery_country', 'delivery_phone', 
            'shipping_cost', 'cart_id'
        ]
    
    def validate_cart_id(self, value):
        # Vérifier que le panier existe et appartient à l'utilisateur
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                print(f"DEBUG: Recherche du panier {value} pour l'utilisateur {request.user.id}")
                cart = Cart.objects.get(id=value, user=request.user, is_active=True)
                print(f"DEBUG: Panier trouvé: {cart.id}, actif: {cart.is_active}, items: {cart.items.count()}")
                if not cart.items.exists():
                    print("DEBUG: Panier vide!")
                    raise CartEmptyException()
            except Cart.DoesNotExist:
                print(f"DEBUG: Panier {value} non trouvé pour l'utilisateur {request.user.id}")
                raise CartNotFoundException()
        return value
    
    def validate_payment_method(self, value):
        valid_methods = ['card', 'paypal', 'cash', 'transfer']
        if value not in valid_methods:
            raise InvalidPaymentMethodException()
        return value
    
    def validate_delivery_address(self, value):
        if not value or len(value.strip()) < 10:
            raise InvalidDeliveryAddressException()
        return value.strip()
    
    def validate_delivery_city(self, value):
        if not value or len(value.strip()) < 2:
            raise InvalidDeliveryAddressException()
        return value.strip()
    
    def validate_delivery_postal_code(self, value):
        if not value or len(value.strip()) < 4:
            raise InvalidDeliveryAddressException()
        return value.strip()
    
    def validate_delivery_phone(self, value):
        if not value or len(value.strip()) < 8:
            raise InvalidDeliveryAddressException()
        return value.strip()
    
    def create(self, validated_data):
        cart_id = validated_data.pop('cart_id')
        request = self.context.get('request')
        
        # Récupérer le panier
        cart = Cart.objects.get(id=cart_id, user=request.user, is_active=True)
        
        # Calculer le sous-total
        subtotal = cart.total_price
        
        # Créer la commande
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            **validated_data
        )
        
        # Créer les articles de commande
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            
            # Mettre à jour le stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Désactiver le panier
        cart.is_active = False
        cart.save()
        
        # Créer l'historique
        OrderHistory.objects.create(
            order=order,
            status='pending',
            comment='Commande créée',
            created_by=request.user
        )
        
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # Mettre à jour la commande
        instance = super().update(instance, validated_data)
        
        # Mettre à jour les dates selon le statut
        if new_status == 'confirmed' and old_status != 'confirmed':
            from django.utils import timezone
            instance.confirmed_at = timezone.now()
        elif new_status == 'shipped' and old_status != 'shipped':
            from django.utils import timezone
            instance.shipped_at = timezone.now()
        elif new_status == 'delivered' and old_status != 'delivered':
            from django.utils import timezone
            instance.delivered_at = timezone.now()
        
        instance.save()
        
        # Créer l'historique
        request = self.context.get('request')
        OrderHistory.objects.create(
            order=instance,
            status=new_status,
            comment=f'Statut changé de {old_status} à {new_status}',
            created_by=request.user if request else None
        )
        
        return instance 