# 🛒 Endpoints de Commande - API E-commerce Fruits & Légumes

## Vue d'ensemble

Les endpoints de commande permettent aux utilisateurs de créer, gérer et suivre leurs commandes. Le processus complet inclut la création de commande à partir du panier, la confirmation, l'annulation et le suivi.

## 📋 Endpoints disponibles

### 1. Créer une nouvelle commande

**POST** `api/orders/orders/`

Crée une nouvelle commande à partir du panier actuel.

**Headers :**
```
Content-Type: application/json
Authorization: Bearer {{auth_token}}
```

**Corps de la requête :**
```json
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

**Paramètres requis :**
| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `cart_id` | `integer` | ID du panier à convertir en commande | `2` |
| `payment_method` | `string` | Méthode de paiement (`card`, `paypal`, `cash`, `transfer`) | `"card"` |
| `delivery_address` | `string` | Adresse de livraison (min 10 caractères) | `"123 Rue de la Paix"` |
| `delivery_city` | `string` | Ville de livraison (min 2 caractères) | `"Paris"` |
| `delivery_postal_code` | `string` | Code postal (min 4 caractères) | `"75001"` |
| `delivery_phone` | `string` | Téléphone (min 8 caractères) | `"0123456789"` |
| `shipping_cost` | `decimal` | Frais de livraison | `5.00` |

**Réponse (201 Created) :**
```json
{
  "message": "Commande créée avec succès",
  "data": {
    "id": 1,
    "order_number": "CMD20250629020000",
    "status": "pending",
    "status_display": "En attente",
    "payment_method": "card",
    "payment_method_display": "Carte bancaire",
    "payment_status": false,
    "delivery_address": "123 Rue de la Paix",
    "delivery_city": "Paris",
    "delivery_postal_code": "75001",
    "delivery_country": "France",
    "delivery_phone": "0123456789",
    "subtotal": "20.00",
    "tax_amount": "4.00",
    "shipping_cost": "5.00",
    "total_amount": "29.00",
    "items_count": 8,
    "items": [
      {
        "id": 1,
        "product": 3,
        "product_name": "Pomme Golden",
        "product_price": "2.50",
        "quantity": 8,
        "total_price": "20.00"
      }
    ],
    "history": [
      {
        "id": 1,
        "status": "pending",
        "status_display": "En attente",
        "comment": "Commande créée",
        "created_at": "2025-06-29T02:00:00Z",
        "created_by_email": "user@example.com"
      }
    ],
    "created_at": "2025-06-29T02:00:00Z",
    "updated_at": "2025-06-29T02:00:00Z"
  }
}
```

### 2. Lister toutes les commandes

**GET** `api/orders/orders/`

Récupère la liste de toutes les commandes de l'utilisateur.

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Paramètres de requête (optionnels) :**
| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `status` | `string` | Filtrer par statut | `pending`, `confirmed`, `shipped`, `delivered`, `cancelled` |
| `payment_method` | `string` | Filtrer par méthode de paiement | `card`, `paypal`, `cash`, `transfer` |
| `payment_status` | `boolean` | Filtrer par statut de paiement | `true`, `false` |
| `ordering` | `string` | Trier les résultats | `created_at`, `-created_at`, `total_amount`, `-total_amount` |
| `page` | `integer` | Numéro de page | `1`, `2`, `3` |
| `page_size` | `integer` | Taille de page | `10`, `20`, `50` |

**Réponse (200 OK) :**
```json
{
  "message": "Liste des commandes récupérée avec succès",
  "count": 1,
  "data": [
    {
      "id": 1,
      "order_number": "CMD20250629020000",
      "status": "pending",
      "status_display": "En attente",
      "payment_method": "card",
      "payment_method_display": "Carte bancaire",
      "payment_status": false,
      "delivery_address": "123 Rue de la Paix",
      "delivery_city": "Paris",
      "delivery_postal_code": "75001",
      "delivery_country": "France",
      "delivery_phone": "0123456789",
      "subtotal": "20.00",
      "tax_amount": "4.00",
      "shipping_cost": "5.00",
      "total_amount": "29.00",
      "items_count": 8,
      "created_at": "2025-06-29T02:00:00Z",
      "updated_at": "2025-06-29T02:00:00Z"
    }
  ]
}
```

### 3. Détails d'une commande

**GET** `api/orders/orders/{order_number}/`

Récupère les détails complets d'une commande spécifique.

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Paramètres d'URL :**
| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `order_number` | `string` | Numéro de commande unique | `CMD20250629020000` |

**Réponse (200 OK) :**
```json
{
  "message": "Détails de la commande récupérés avec succès",
  "data": {
    "id": 1,
    "order_number": "CMD20250629020000",
    "status": "pending",
    "status_display": "En attente",
    "payment_method": "card",
    "payment_method_display": "Carte bancaire",
    "payment_status": false,
    "delivery_address": "123 Rue de la Paix",
    "delivery_city": "Paris",
    "delivery_postal_code": "75001",
    "delivery_country": "France",
    "delivery_phone": "0123456789",
    "subtotal": "20.00",
    "tax_amount": "4.00",
    "shipping_cost": "5.00",
    "total_amount": "29.00",
    "items_count": 8,
    "items": [
      {
        "id": 1,
        "product": 3,
        "product_name": "Pomme Golden",
        "product_price": "2.50",
        "quantity": 8,
        "total_price": "20.00"
      }
    ],
    "history": [
      {
        "id": 1,
        "status": "pending",
        "status_display": "En attente",
        "comment": "Commande créée",
        "created_at": "2025-06-29T02:00:00Z",
        "created_by_email": "user@example.com"
      }
    ],
    "created_at": "2025-06-29T02:00:00Z",
    "updated_at": "2025-06-29T02:00:00Z",
    "confirmed_at": null,
    "shipped_at": null,
    "delivered_at": null
  }
}
```

### 4. Confirmer une commande

**POST** `api/orders/orders/{order_number}/confirm/`

Confirme une commande en attente.

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Paramètres d'URL :**
| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `order_number` | `string` | Numéro de commande unique | `CMD20250629020000` |

**Réponse (200 OK) :**
```json
{
  "message": "Commande confirmée avec succès",
  "data": {
    "id": 1,
    "order_number": "CMD20250629020000",
    "status": "confirmed",
    "status_display": "Confirmée",
    "confirmed_at": "2025-06-29T02:05:00Z",
    // ... autres détails de la commande
  }
}
```

### 5. Annuler une commande

**POST** `api/orders/orders/{order_number}/cancel/`

Annule une commande (seulement si elle n'est pas encore expédiée).

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Paramètres d'URL :**
| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `order_number` | `string` | Numéro de commande unique | `CMD20250629020000` |

**Réponse (200 OK) :**
```json
{
  "message": "Commande annulée avec succès",
  "data": {
    "id": 1,
    "order_number": "CMD20250629020000",
    "status": "cancelled",
    "status_display": "Annulée",
    // ... autres détails de la commande
  }
}
```

### 6. Commandes en attente

**GET** `api/orders/orders/pending/`

Récupère toutes les commandes en attente de l'utilisateur.

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Réponse (200 OK) :**
```json
{
  "message": "Commandes en attente récupérées avec succès",
  "count": 1,
  "data": [
    {
      "id": 1,
      "order_number": "CMD20250629020000",
      "status": "pending",
      "status_display": "En attente",
      // ... autres détails
    }
  ]
}
```

### 7. Commandes récentes

**GET** `api/orders/orders/recent/`

Récupère les commandes des 30 derniers jours.

**Headers :**
```
Authorization: Bearer {{auth_token}}
```

**Réponse (200 OK) :**
```json
{
  "message": "Commandes récentes récupérées avec succès",
  "count": 2,
  "data": [
    // ... commandes des 30 derniers jours
  ]
}
```

## 🔄 Statuts de commande

| Statut | Description | Actions possibles |
|--------|-------------|-------------------|
| `pending` | En attente | Confirmer, Annuler |
| `confirmed` | Confirmée | Annuler (si pas expédiée) |
| `processing` | En cours de traitement | Aucune |
| `shipped` | Expédiée | Aucune |
| `delivered` | Livrée | Aucune |
| `cancelled` | Annulée | Aucune |

## 💳 Méthodes de paiement

| Méthode | Description |
|---------|-------------|
| `card` | Carte bancaire |
| `paypal` | PayPal |
| `cash` | Espèces à la livraison |
| `transfer` | Virement bancaire |

## ⚠️ Gestion des erreurs

### Erreurs communes

**400 - Données invalides :**
```json
{
  "error": "Données invalides",
  "message": "Les données fournies sont invalides.",
  "details": {
    "cart_id": ["Ce champ est requis."],
    "delivery_address": ["L'adresse doit contenir au moins 10 caractères."]
  },
  "status_code": 400
}
```

**404 - Commande non trouvée :**
```json
{
  "error": "Commande non trouvée",
  "message": "La commande spécifiée n'existe pas.",
  "status_code": 404
}
```

**409 - Commande déjà confirmée :**
```json
{
  "error": "Commande déjà confirmée",
  "message": "Cette commande a déjà été confirmée.",
  "status_code": 409
}
```

**400 - Commande ne peut pas être annulée :**
```json
{
  "error": "Commande ne peut pas être annulée",
  "message": "Cette commande ne peut plus être annulée.",
  "status_code": 400
}
```

## 📝 Workflow complet de commande

### 1. Préparer le panier
```bash
# Ajouter des articles au panier
POST api/orders/carts/add_item/
{
  "product_id": 3,
  "quantity": 8
}

# Vérifier le panier
GET api/orders/carts/current/
```

### 2. Créer la commande
```bash
POST api/orders/orders/
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

### 3. Confirmer la commande
```bash
POST api/orders/orders/CMD20250629020000/confirm/
```

### 4. Suivre la commande
```bash
# Détails de la commande
GET api/orders/orders/CMD20250629020000/

# Historique des commandes
GET api/orders/orders/
```

## 🎯 Tests Postman

### Tests pour créer une commande
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Order was created successfully", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Commande créée avec succès");
    pm.expect(jsonData.data).to.have.property('order_number');
    pm.expect(jsonData.data.status).to.eql("pending");
});

pm.test("Cart was deactivated", function () {
    const jsonData = pm.response.json();
    // Le panier devrait être désactivé après création de commande
    pm.expect(jsonData.data.items).to.be.an('array').that.is.not.empty;
});
```

### Tests pour confirmer une commande
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Order was confirmed", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Commande confirmée avec succès");
    pm.expect(jsonData.data.status).to.eql("confirmed");
    pm.expect(jsonData.data.confirmed_at).to.not.be.null;
});
```

## 📊 Statistiques

- **Pagination automatique** : 10 commandes par page par défaut
- **Tri par défaut** : Plus récentes en premier (`-created_at`)
- **Filtres disponibles** : Statut, méthode de paiement, statut de paiement
- **Historique complet** : Tous les changements de statut sont enregistrés
- **Restauration de stock** : Le stock est restauré lors de l'annulation

---

**Collection Postman complète** : Tous les endpoints de commande sont documentés dans la collection "Suku E-commerce API" 📦✨ 