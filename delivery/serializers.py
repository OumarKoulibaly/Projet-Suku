from rest_framework import serializers
from .models import Delivery
from orders.serializers import OrderSerializer

class DeliverySerializer(serializers.ModelSerializer):
    """Serializer pour les livraisons"""
    order = OrderSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'status', 'status_display', 
            'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

class DeliveryStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour du statut de livraison"""
    STATUS_CHOICES = [
        ('preparation', 'En préparation'),
        ('on_the_way', 'En cours de livraison'),
        ('delivered', 'Livré')
    ]
    
    status = serializers.ChoiceField(
        choices=STATUS_CHOICES,
        help_text="Nouveau statut de la livraison"
    )
    comment = serializers.CharField(
        max_length=500, 
        required=False, 
        help_text="Commentaire optionnel sur le changement de statut"
    )

class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une nouvelle livraison"""
    
    class Meta:
        model = Delivery
        fields = ['order', 'status']
        read_only_fields = ['status']  # Le statut par défaut est 'preparation' 