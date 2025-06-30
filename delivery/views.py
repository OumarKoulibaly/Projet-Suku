from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from orders.models import Order
from .models import Delivery
from .serializers import DeliverySerializer, DeliveryStatusUpdateSerializer
from notifications.models import Notification
from notifications.services import NotificationService

class DeliveryViewSet(viewsets.ModelViewSet):
    """Gestion des livraisons avec suivi en temps réel"""
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Récupère les livraisons de l'utilisateur connecté"""
        return Delivery.objects.filter(order__user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Liste toutes les livraisons de l'utilisateur"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': 'Livraisons récupérées avec succès',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Détails d'une livraison spécifique"""
        delivery = self.get_object()
        serializer = self.get_serializer(delivery)
        
        return Response({
            'message': 'Détails de la livraison récupérés avec succès',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut de livraison (pour les administrateurs)"""
        delivery = self.get_object()
        serializer = DeliveryStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            old_status = delivery.status
            new_status = serializer.validated_data['status']
            
            # Mettre à jour le statut
            delivery.status = new_status
            delivery.updated_at = timezone.now()
            delivery.save()
            
            # Créer une notification pour l'utilisateur
            NotificationService.notify_delivery_update(delivery, new_status)
            
            # Mettre à jour le statut de la commande si nécessaire
            self._update_order_status(delivery, new_status)
            
            return Response({
                'message': f'Statut de livraison mis à jour vers "{delivery.get_status_display()}"',
                'data': DeliverySerializer(delivery).data
            })
        
        return Response({
            'error': 'Données invalides',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Récupérer les livraisons actives (en préparation ou en cours)"""
        active_deliveries = self.get_queryset().exclude(status='delivered')
        serializer = self.get_serializer(active_deliveries, many=True)
        
        return Response({
            'message': 'Livraisons actives récupérées avec succès',
            'count': active_deliveries.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Récupérer les livraisons récentes (7 derniers jours)"""
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=7)
        recent_deliveries = self.get_queryset().filter(updated_at__gte=recent_date)
        serializer = self.get_serializer(recent_deliveries, many=True)
        
        return Response({
            'message': 'Livraisons récentes récupérées avec succès',
            'count': recent_deliveries.count(),
            'data': serializer.data
        })
    
    def _create_delivery_notification(self, delivery, old_status, new_status):
        """Créer une notification pour l'utilisateur"""
        status_messages = {
            'preparation': 'Votre commande est en cours de préparation',
            'on_the_way': 'Votre commande est en route vers vous !',
            'delivered': 'Votre commande a été livrée avec succès !'
        }
        
        if new_status in status_messages:
            Notification.objects.create(
                user=delivery.order.user,
                title=f"Livraison - {delivery.get_status_display()}",
                message=status_messages[new_status]
            )
    
    def _update_order_status(self, delivery, delivery_status):
        """Mettre à jour le statut de la commande en fonction de la livraison"""
        order = delivery.order
        
        if delivery_status == 'on_the_way' and order.status == 'confirmed':
            order.status = 'processing'
            order.save()
        elif delivery_status == 'delivered' and order.status in ['processing', 'shipped']:
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
