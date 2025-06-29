from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Cart(models.Model):
    """Panier d'achat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Panier de {self.user.email} - {self.created_at.strftime('%d/%m/%Y')}"

    @property
    def total_items(self):
        """Nombre total d'articles dans le panier"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Prix total du panier"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_price_with_tax(self):
        """Prix total avec taxes (TVA 20%)"""
        return self.total_price * Decimal('1.20')

class CartItem(models.Model):
    """Article dans le panier"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Prix total pour cet article"""
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        # Vérifier que le stock est suffisant
        if self.quantity > self.product.stock:
            raise ValueError(f"Stock insuffisant. Disponible: {self.product.stock}")
        super().save(*args, **kwargs)

class Order(models.Model):
    """Commande"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En cours de traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces à la livraison'),
        ('transfer', 'Virement bancaire'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    payment_status = models.BooleanField(default=False)
    
    # Adresse de livraison
    delivery_address = models.TextField(default='')
    delivery_city = models.CharField(max_length=100, default='')
    delivery_postal_code = models.CharField(max_length=10, default='')
    delivery_country = models.CharField(max_length=100, default='France')
    delivery_phone = models.CharField(max_length=20, default='')
    
    # Prix
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Commande {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Générer un numéro de commande unique
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"CMD{timestamp}"
        
        # Calculer les taxes et le total
        if not self.tax_amount:
            self.tax_amount = self.subtotal * Decimal('0.20')  # TVA 20%
        if not self.total_amount:
            self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
        
        super().save(*args, **kwargs)

    @property
    def items_count(self):
        """Nombre d'articles dans la commande"""
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    """Article dans la commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=250)  # Sauvegarder le nom au moment de la commande
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Sauvegarder le prix
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)

class OrderHistory(models.Model):
    """Historique des changements de statut de commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Historique des commandes"
