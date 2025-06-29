# Endpoints de Panier - API E-commerce Fruits & Légumes

## Vue d'ensemble

Les endpoints de panier permettent aux utilisateurs de gérer leur panier d'achat. Chaque utilisateur connecté peut avoir un seul panier actif à la fois.

## Endpoints disponibles

### 1. Récupérer le panier actuel

**GET** `api/orders/carts/current/`

Récupère le panier actuel de l'utilisateur connecté.

**Réponse :**
```json
{
    "message": "Panier actuel récupéré avec succès",
    "data": {
        "id": 1,
        "items": [
            {
                "id": 1,
                "product": {
                    "id": 1,
                    "name": "Pommes Golden",
                    "price": "2.50",
                    "image": "http://...",
                    "stock": 100
                },
                "quantity": 3,
                "total_price": "7.50",
                "added_at": "2024-01-15T10:30:00Z"
            }
        ],
        "total_items": 3,
        "total_price": "7.50",
        "total_price_with_tax": "9.00",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

### 2. Ajouter un article au panier

**POST** `api/orders/carts/add_item/`

Ajoute un article au panier actuel. Si le produit existe déjà, la quantité est ajoutée.

**Corps de la requête :**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

**Réponse :**
```json
{
    "message": "Article ajouté au panier avec succès",
    "item": {
        "id": 1,
        "product": {...},
        "quantity": 5,
        "total_price": "12.50",
        "added_at": "2024-01-15T10:30:00Z"
    },
    "cart": {
        "id": 1,
        "items": [...],
        "total_items": 5,
        "total_price": "12.50",
        "total_price_with_tax": "15.00"
    }
}
```

### 3. Modifier la quantité d'un article

**PUT** `api/orders/carts/update_item/`

Modifie la quantité d'un article spécifique dans le panier.

**Corps de la requête :**
```json
{
    "item_id": 1,
    "quantity": 4
}
```

**Réponse :**
```json
{
    "message": "Quantité mise à jour avec succès",
    "item": {
        "id": 1,
        "product": {...},
        "quantity": 4,
        "total_price": "10.00"
    },
    "cart": {
        "total_items": 4,
        "total_price": "10.00",
        "total_price_with_tax": "12.00"
    }
}
```

### 4. Supprimer un article du panier

**DELETE** `api/orders/carts/remove_item/`

Supprime un article spécifique du panier.

**Corps de la requête :**
```json
{
    "item_id": 1
}
```

**Réponse :**
```json
{
    "message": "Article supprimé du panier avec succès",
    "cart": {
        "total_items": 0,
        "total_price": "0.00",
        "total_price_with_tax": "0.00"
    }
}
```

### 5. Vider le panier

**POST** `api/orders/carts/clear/`

Supprime tous les articles du panier actuel.

**Réponse :**
```json
{
    "message": "Panier vidé avec succès",
    "cart": {
        "items": [],
        "total_items": 0,
        "total_price": "0.00",
        "total_price_with_tax": "0.00"
    }
}
```

### 6. Résumé du panier

**GET** `api/orders/carts/summary/`

Récupère un résumé rapide du panier (nombre d'articles, prix total).

**Réponse :**
```json
{
    "message": "Résumé du panier récupéré avec succès",
    "data": {
        "total_items": 5,
        "total_price": "12.50",
        "total_price_with_tax": "15.00",
        "items_count": 3
    }
}
```

## Gestion des erreurs

### Erreurs communes

**400 - Données invalides :**
```json
{
    "error": "Données invalides",
    "message": "Les données fournies sont invalides.",
    "details": {
        "product_id": ["Ce champ est requis."],
        "quantity": ["La quantité doit être supérieure à 0."]
    },
    "status_code": 400
}
```

**404 - Panier non trouvé :**
```json
{
    "error": "Panier non trouvé",
    "message": "Aucun panier actif trouvé pour cet utilisateur.",
    "status_code": 404
}
```

**400 - Stock insuffisant :**
```json
{
    "error": "Stock insuffisant",
    "message": "Stock insuffisant pour cette opération.",
    "status_code": 400
}
```

**400 - Produit indisponible :**
```json
{
    "error": "Produit indisponible",
    "message": "Ce produit n'est pas disponible pour la commande.",
    "status_code": 400
}
```

## Authentification

Tous les endpoints de panier nécessitent une authentification. Incluez le token JWT dans l'en-tête :

```
Authorization: Bearer <votre_token_jwt>
```

## Exemples d'utilisation

### Workflow complet d'utilisation du panier

1. **Récupérer le panier actuel :**
   ```bash
   GET api/orders/carts/current/
   ```

2. **Ajouter des articles :**
   ```bash
   POST api/orders/carts/add_item/
   {
       "product_id": 1,
       "quantity": 2
   }
   ```

3. **Vérifier le résumé :**
   ```bash
   GET api/orders/carts/summary/
   ```

4. **Modifier une quantité :**
   ```bash
   PUT api/orders/carts/update_item/
   {
       "item_id": 1,
       "quantity": 3
   }
   ```

5. **Supprimer un article :**
   ```bash
   DELETE api/orders/carts/remove_item/
   {
       "item_id": 1
   }
   ```

6. **Vider le panier :**
   ```bash
   POST api/orders/carts/clear/
   ```

## Notes importantes

- Chaque utilisateur ne peut avoir qu'un seul panier actif à la fois
- Les prix sont calculés automatiquement avec la TVA (20%)
- Le stock est vérifié à chaque ajout/modification
- Les articles avec quantité 0 sont automatiquement supprimés
- Le panier est automatiquement créé lors du premier ajout d'article 