from django.utils import timezone
from .models import Notification
from products.models import Product
from accounts.models import User

class NotificationService:
    """Service pour gérer les notifications automatiques"""
    
    @staticmethod
    def notify_new_product(product):
        """Notifier tous les utilisateurs d'un nouveau produit"""
        users = User.objects.filter(is_active=True)
        
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title="Nouveau produit disponible !",
                    message=f"Découvrez notre nouveau produit : {product.name} - {product.price}€"
                )
            )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def notify_promotion(product, discount_percent):
        """Notifier d'une promotion sur un produit"""
        users = User.objects.filter(is_active=True)
        
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title="Promotion spéciale !",
                    message=f"{discount_percent}% de réduction sur {product.name} !"
                )
            )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def notify_stock_alert(product):
        """Notifier quand un produit est en rupture de stock"""
        # Notifier les utilisateurs qui ont ce produit dans leur panier
        from orders.models import CartItem
        
        cart_items = CartItem.objects.filter(product=product)
        users_to_notify = set(item.cart.user for item in cart_items)
        
        notifications = []
        for user in users_to_notify:
            notifications.append(
                Notification(
                    user=user,
                    title="Produit en rupture de stock",
                    message=f"Le produit {product.name} est temporairement indisponible."
                )
            )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def notify_order_status_change(order, new_status):
        """Notifier du changement de statut de commande"""
        status_messages = {
            'confirmed': f"Votre commande {order.order_number} a été confirmée !",
            'processing': f"Votre commande {order.order_number} est en cours de traitement.",
            'shipped': f"Votre commande {order.order_number} a été expédiée !",
            'delivered': f"Votre commande {order.order_number} a été livrée avec succès !",
            'cancelled': f"Votre commande {order.order_number} a été annulée."
        }
        
        if new_status in status_messages:
            Notification.objects.create(
                user=order.user,
                title=f"Commande {order.order_number} - {order.get_status_display()}",
                message=status_messages[new_status]
            )
    
    @staticmethod
    def notify_delivery_update(delivery, new_status):
        """Notifier de la mise à jour de livraison"""
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