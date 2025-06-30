from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService
from products.models import Product

class NotificationViewSet(viewsets.ModelViewSet):
    """Gestion des notifications utilisateur"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Récupère les notifications de l'utilisateur connecté"""
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Liste toutes les notifications de l'utilisateur"""
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        
        # Compter les notifications non lues
        unread_count = queryset.filter(is_read=False).count()
        
        return Response({
            'message': 'Notifications récupérées avec succès',
            'unread_count': unread_count,
            'count': queryset.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Récupérer seulement les notifications non lues"""
        unread_notifications = self.get_queryset().filter(is_read=False).order_by('-created_at')
        serializer = self.get_serializer(unread_notifications, many=True)
        
        return Response({
            'message': 'Notifications non lues récupérées avec succès',
            'count': unread_notifications.count(),
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marquée comme lue',
            'data': self.get_serializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues"""
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        
        return Response({
            'message': f'{updated_count} notifications marquées comme lues',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Récupérer les notifications récentes (7 derniers jours)"""
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=7)
        recent_notifications = self.get_queryset().filter(created_at__gte=recent_date).order_by('-created_at')
        serializer = self.get_serializer(recent_notifications, many=True)
        
        return Response({
            'message': 'Notifications récentes récupérées avec succès',
            'count': recent_notifications.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['delete'])
    def clear_read(self, request):
        """Supprimer toutes les notifications lues"""
        deleted_count = self.get_queryset().filter(is_read=True).delete()[0]
        
        return Response({
            'message': f'{deleted_count} notifications lues supprimées',
            'deleted_count': deleted_count
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def send_promotion(self, request):
        """Envoyer une notification de promotion (admin seulement)"""
        product_id = request.data.get('product_id')
        discount_percent = request.data.get('discount_percent')
        
        if not product_id or not discount_percent:
            return Response({
                'error': 'Données manquantes',
                'message': 'product_id et discount_percent sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
            NotificationService.notify_promotion(product, discount_percent)
            
            return Response({
                'message': f'Notification de promotion envoyée pour {product.name}',
                'product': product.name,
                'discount': f'{discount_percent}%'
            })
        except Product.DoesNotExist:
            return Response({
                'error': 'Produit non trouvé',
                'message': f'Le produit avec l\'ID {product_id} n\'existe pas'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def send_new_product(self, request):
        """Envoyer une notification de nouveau produit (admin seulement)"""
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({
                'error': 'Données manquantes',
                'message': 'product_id est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
            NotificationService.notify_new_product(product)
            
            return Response({
                'message': f'Notification de nouveau produit envoyée pour {product.name}',
                'product': product.name
            })
        except Product.DoesNotExist:
            return Response({
                'error': 'Produit non trouvé',
                'message': f'Le produit avec l\'ID {product_id} n\'existe pas'
            }, status=status.HTTP_404_NOT_FOUND)
