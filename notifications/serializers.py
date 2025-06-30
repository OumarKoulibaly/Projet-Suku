from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'is_read', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une nouvelle notification"""
    
    class Meta:
        model = Notification
        fields = ['user', 'title', 'message'] 