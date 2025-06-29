from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderHistory
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, 
    OrderCreateSerializer, OrderUpdateSerializer, OrderHistorySerializer
)
from .exceptions import (
    CartNotFoundException, CartItemNotFoundException, CartEmptyException,
    OrderNotFoundException, OrderAlreadyConfirmedException, OrderCannotBeCancelledException,
    InvalidPaymentMethodException, InvalidDeliveryAddressException,
    OrderStatusTransitionException, CartAlreadyExistsException,
    ProductNotAvailableForOrderException
)
from products.exceptions import InsufficientStockException

class CartViewSet(viewsets.ModelViewSet):
    """Gestion du panier d'achat"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        # Vérifier qu'il n'y a pas déjà un panier actif
        if Cart.objects.filter(user=self.request.user, is_active=True).exists():
            raise CartAlreadyExistsException()
        serializer.save(user=self.request.user)
    
    def get_object(self):
        try:
            return super().get_object()
        except Cart.DoesNotExist:
            raise CartNotFoundException()
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Ajouter un article au panier"""
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            # Vérifier que le produit est disponible
            if not product.is_available:
                raise ProductNotAvailableForOrderException()
            
            # Vérifier si l'article existe déjà dans le panier
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Mettre à jour la quantité
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    raise InsufficientStockException()
                cart_item.quantity = new_quantity
                cart_item.save()
            
            return Response({
                'message': 'Article ajouté au panier avec succès',
                'data': CartItemSerializer(cart_item).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Données invalides',
            'message': 'Les données fournies sont invalides.',
            'details': serializer.errors,
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_item(self, request, pk=None):
        """Modifier la quantité d'un article"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response({
                'error': 'Données manquantes',
                'message': 'item_id et quantity sont requis.',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response({
                'message': 'Quantité mise à jour avec succès',
                'data': CartItemSerializer(cart_item).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            raise CartItemNotFoundException()
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Supprimer un article du panier"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response({
                'error': 'Données manquantes',
                'message': 'item_id est requis.',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            return Response({
                'message': 'Article supprimé du panier avec succès'
            }, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            raise CartItemNotFoundException()
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Vider le panier"""
        cart = self.get_object()
        
        if not cart.items.exists():
            raise CartEmptyException()
        
        cart.items.all().delete()
        
        return Response({
            'message': 'Panier vidé avec succès'
        }, status=status.HTTP_200_OK)

class OrderViewSet(viewsets.ModelViewSet):
    """Gestion des commandes"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'payment_status']
    ordering_fields = ['created_at', 'total_amount', 'order_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_object(self):
        try:
            return super().get_object()
        except Order.DoesNotExist:
            raise OrderNotFoundException()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle commande"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response({
            'message': 'Commande créée avec succès',
            'data': OrderSerializer(order, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """Liste des commandes de l'utilisateur"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'message': 'Liste des commandes récupérée avec succès',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Liste des commandes récupérée avec succès',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Détails d'une commande"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Détails de la commande récupérés avec succès',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmer une commande"""
        order = self.get_object()
        
        if order.status != 'pending':
            raise OrderAlreadyConfirmedException()
        
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        
        # Créer l'historique
        OrderHistory.objects.create(
            order=order,
            status='confirmed',
            comment='Commande confirmée par l\'utilisateur',
            created_by=request.user
        )
        
        return Response({
            'message': 'Commande confirmée avec succès',
            'data': OrderSerializer(order, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une commande"""
        order = self.get_object()
        
        if order.status in ['shipped', 'delivered']:
            raise OrderCannotBeCancelledException()
        
        order.status = 'cancelled'
        order.save()
        
        # Restaurer le stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        
        # Créer l'historique
        OrderHistory.objects.create(
            order=order,
            status='cancelled',
            comment='Commande annulée par l\'utilisateur',
            created_by=request.user
        )
        
        return Response({
            'message': 'Commande annulée avec succès',
            'data': OrderSerializer(order, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Commandes en attente"""
        orders = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(orders, many=True)
        return Response({
            'message': 'Commandes en attente récupérées avec succès',
            'count': orders.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Commandes récentes (derniers 30 jours)"""
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        orders = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        serializer = self.get_serializer(orders, many=True)
        return Response({
            'message': 'Commandes récentes récupérées avec succès',
            'count': orders.count(),
            'data': serializer.data
        })
