from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductSerializer, 
    ProductDetailSerializer, ProductCreateSerializer
)
from .exceptions import (
    ProductNotFoundException, CategoryNotFoundException,
    InsufficientStockException, ProductNotAvailableException
)

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'Catégorie créée avec succès',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'message': 'Catégorie mise à jour avec succès',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Catégorie supprimée avec succès'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Récupérer tous les produits d'une catégorie"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response({
            'message': f'Produits de la catégorie {category.name}',
            'count': products.count(),
            'data': serializer.data
        })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'price', 'created_at', 'stock']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        # Filtrer par prix min/max
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtrer par stock disponible
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'Produit créé avec succès',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'message': 'Produit mis à jour avec succès',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Produit supprimé avec succès'
        }, status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'message': 'Liste des produits récupérée avec succès',
                'data': serializer.data
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Liste des produits récupérée avec succès',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Détails du produit récupérés avec succès',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Récupérer seulement les produits disponibles"""
        products = self.get_queryset().filter(is_available=True, stock__gt=0)
        serializer = self.get_serializer(products, many=True)
        return Response({
            'message': 'Produits disponibles récupérés avec succès',
            'count': products.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Récupérer les produits en stock faible"""
        threshold = int(self.request.query_params.get('threshold', 10))
        products = self.get_queryset().filter(stock__lte=threshold)
        serializer = self.get_serializer(products, many=True)
        return Response({
            'message': f'Produits en stock faible (≤{threshold}) récupérés avec succès',
            'count': products.count(),
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, slug=None):
        """Mettre à jour le stock d'un produit"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if quantity < 0:
            raise InvalidStockException()
        
        product.stock = quantity
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            'message': f'Stock mis à jour avec succès ({quantity} unités)',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, slug=None):
        """Activer/désactiver la disponibilité d'un produit"""
        product = self.get_object()
        product.is_available = not product.is_available
        product.save()
        
        status_text = "activé" if product.is_available else "désactivé"
        serializer = self.get_serializer(product)
        return Response({
            'message': f'Produit {status_text} avec succès',
            'data': serializer.data
        })
