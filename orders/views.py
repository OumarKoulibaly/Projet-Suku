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
    
    def list(self, request, *args, **kwargs):
        """Liste des paniers actifs de l'utilisateur"""
        queryset = self.get_queryset()
        
        # Normalement, un utilisateur n'a qu'un seul panier actif
        if queryset.exists():
            cart = queryset.first()
            serializer = self.get_serializer(cart)
            return Response({
                'message': 'Panier récupéré avec succès',
                'data': serializer.data
            })
        else:
            return Response({
                'message': 'Aucun panier actif trouvé',
                'data': None
            })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Récupérer le panier actuel de l'utilisateur"""
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            serializer = self.get_serializer(cart)
            return Response({
                'message': 'Panier actuel récupéré avec succès',
                'data': serializer.data
            })
        except Cart.DoesNotExist:
            return Response({
                'message': 'Aucun panier actif trouvé',
                'data': None
            })
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Ajouter un article au panier actuel"""
        # Récupérer ou créer le panier actuel
        cart, created = Cart.objects.get_or_create(
            user=request.user, 
            is_active=True,
            defaults={'user': request.user}
        )
        
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
            
            # Récupérer le panier mis à jour
            cart.refresh_from_db()
            cart_serializer = self.get_serializer(cart)
            
            return Response({
                'message': 'Article ajouté au panier avec succès',
                'item': CartItemSerializer(cart_item).data,
                'cart': cart_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Données invalides',
            'message': 'Les données fournies sont invalides.',
            'details': serializer.errors,
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Modifier la quantité d'un article dans le panier actuel"""
        print(f"DEBUG: update_item appelé avec data: {request.data}")
        
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            print(f"DEBUG: Panier trouvé: {cart.id}")
        except Cart.DoesNotExist:
            print("DEBUG: Panier non trouvé")
            raise CartNotFoundException()
        
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        print(f"DEBUG: item_id={item_id}, quantity={quantity}")
        
        if not item_id or quantity is None:
            return Response({
                'error': 'Données manquantes',
                'message': 'item_id et quantity sont requis.',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0:
            return Response({
                'error': 'Quantité invalide',
                'message': 'La quantité doit être supérieure à 0.',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            print(f"DEBUG: CartItem trouvé: {cart_item.id}, produit: {cart_item.product.name}")
            
            # Vérifier le stock
            if quantity > cart_item.product.stock:
                raise InsufficientStockException()
            
            cart_item.quantity = quantity
            cart_item.save()
            
            # Récupérer le panier mis à jour
            cart.refresh_from_db()
            cart_serializer = self.get_serializer(cart)
            
            return Response({
                'message': 'Quantité mise à jour avec succès',
                'item': CartItemSerializer(cart_item).data,
                'cart': cart_serializer.data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            print(f"DEBUG: CartItem {item_id} non trouvé dans le panier {cart.id}")
            raise CartItemNotFoundException()
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Supprimer un article du panier actuel"""
        print(f"DEBUG: remove_item appelé avec data: {request.data}")
        
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            print(f"DEBUG: Panier trouvé: {cart.id}")
        except Cart.DoesNotExist:
            print("DEBUG: Panier non trouvé")
            raise CartNotFoundException()
        
        item_id = request.data.get('item_id')
        print(f"DEBUG: item_id={item_id}")
        
        if not item_id:
            return Response({
                'error': 'Données manquantes',
                'message': 'item_id est requis.',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            print(f"DEBUG: CartItem trouvé: {cart_item.id}, produit: {cart_item.product.name}")
            cart_item.delete()
            
            # Récupérer le panier mis à jour
            cart.refresh_from_db()
            cart_serializer = self.get_serializer(cart)
            
            return Response({
                'message': 'Article supprimé du panier avec succès',
                'cart': cart_serializer.data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            print(f"DEBUG: CartItem {item_id} non trouvé dans le panier {cart.id}")
            raise CartItemNotFoundException()
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Vider le panier actuel"""
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
        except Cart.DoesNotExist:
            raise CartNotFoundException()
        
        if not cart.items.exists():
            raise CartEmptyException()
        
        cart.items.all().delete()
        
        # Récupérer le panier mis à jour
        cart.refresh_from_db()
        cart_serializer = self.get_serializer(cart)
        
        return Response({
            'message': 'Panier vidé avec succès',
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé du panier actuel (nombre d'articles, prix total)"""
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            return Response({
                'message': 'Résumé du panier récupéré avec succès',
                'data': {
                    'total_items': cart.total_items,
                    'total_price': cart.total_price,
                    'total_price_with_tax': cart.total_price_with_tax,
                    'items_count': cart.items.count()
                }
            })
        except Cart.DoesNotExist:
            return Response({
                'message': 'Aucun panier actif trouvé',
                'data': {
                    'total_items': 0,
                    'total_price': 0,
                    'total_price_with_tax': 0,
                    'items_count': 0
                }
            })

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
