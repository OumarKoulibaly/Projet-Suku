from django.db import models
from orders.models import Order

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    status = models.CharField(max_length=50, choices=[
        ('preparation', 'En préparation'),
        ('on_the_way', 'En cours de livraison'),
        ('delivered', 'Livré')
    ], default='preparation')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Livraison de commande #{self.order.id} - {self.status}"
