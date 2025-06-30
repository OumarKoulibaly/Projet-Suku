# 📦 Résumé des Endpoints de Commande

## 🎯 Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| **POST** | `/orders/orders/` | Créer une nouvelle commande |
| **GET** | `/orders/orders/` | Lister toutes les commandes |
| **GET** | `/orders/orders/{order_number}/` | Détails d'une commande |
| **POST** | `/orders/orders/{order_number}/confirm/` | Confirmer une commande |
| **POST** | `/orders/orders/{order_number}/cancel/` | Annuler une commande |
| **GET** | `/orders/orders/pending/` | Commandes en attente |
| **GET** | `/orders/orders/recent/` | Commandes récentes (30 jours) |

## 🔄 Workflow de commande

1. **Préparer le panier** → `POST /orders/carts/add_item/`
2. **Créer la commande** → `POST /orders/orders/`
3. **Confirmer** → `POST /orders/orders/{order_number}/confirm/`
4. **Suivre** → `GET /orders/orders/{order_number}/`

## 📊 Statuts de commande

- `pending` → En attente
- `confirmed` → Confirmée  
- `processing` → En cours de traitement
- `shipped` → Expédiée
- `delivered` → Livrée
- `cancelled` → Annulée

## 💳 Méthodes de paiement

- `card` → Carte bancaire
- `paypal` → PayPal
- `cash` → Espèces à la livraison
- `transfer` → Virement bancaire

## ⚡ Fonctionnalités

✅ **Création automatique** du numéro de commande  
✅ **Calcul automatique** des taxes (TVA 20%)  
✅ **Désactivation du panier** après création  
✅ **Historique complet** des changements de statut  
✅ **Restauration du stock** lors de l'annulation  
✅ **Filtrage et tri** des commandes  
✅ **Pagination** automatique  
✅ **Validation complète** des données  
✅ **URLs sécurisées** avec order_number comme slug  

## 🎯 Exemple de création de commande

```bash
POST /orders/orders/
{
  "cart_id": 2,
  "payment_method": "card",
  "delivery_address": "123 Rue de la Paix",
  "delivery_city": "Paris", 
  "delivery_postal_code": "75001",
  "delivery_country": "France",
  "delivery_phone": "0123456789",
  "shipping_cost": 5.00
}
```

## 🔐 URLs sécurisées avec order_number

```bash
# Détails de la commande
GET /orders/orders/CMD20250629020000/

# Confirmer la commande
POST /orders/orders/CMD20250629020000/confirm/

# Annuler la commande
POST /orders/orders/CMD20250629020000/cancel/
```

## 📝 Documentation complète

Voir `orders/README_ORDER_ENDPOINTS.md` pour la documentation détaillée Postman. 