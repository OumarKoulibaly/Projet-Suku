# 🍏 E-commerce Fruits & Légumes – API Django

## 🎯 Objectif du Projet

Développer une plateforme e-commerce dédiée à la vente de fruits et légumes frais, avec une API RESTful modulaire, maintenable et évolutive.

---

## 🗂 Structure du Projet

Le projet est divisé en plusieurs **applications Django** indépendantes selon les fonctionnalités. Cela permet une meilleure séparation des responsabilités, facilitant le développement, les tests et la maintenance.


---

## 📦 Description des Applications

### 1. `accounts`
- 📌 Gère l'authentification (email/mot de passe)
- 📇 Informations personnelles (nom, téléphone, etc.)
- 🔐 Utilisation d’un `CustomUser` basé sur `AbstractUser`

### 2. `products`
- 📦 CRUD des fruits, légumes et produits bio
- 🗂 Catégorisation des produits
- 🔍 Recherche et filtres

### 3. `orders`
- 🛒 Panier d’achat
- 📑 Commandes passées
- 💳 Choix du mode de paiement (à implémenter)

### 4. `delivery`
- 🚚 Statut de livraison d’une commande
- 🕓 En préparation / En cours / Livrée

### 5. `notifications`
- 🔔 Notifications liées aux commandes, livraisons, promotions
- 📨 Notifications internes (par API)

---

## ⚙️ Installation

```bash
git clone lien du project
cd Projet-Suku-master
python -m venv env
source env/bin/activate sur windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


## 🧪 Tests des API

### 🔑 Authentication API Endpoints

#### 1. Inscription (Register)
```bash
curl -X POST http://localhost:8000/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password1": "StrongPass123!",
    "password2": "StrongPass123!"
  }'
```

#### 2. Connexion (Login)
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPass123!"
  }'
```

#### 3. Obtenir les Détails de l'Utilisateur
```bash
curl -X GET http://localhost:8000/auth/user/ \
  -H "Authorization: Bearer your_access_token"
```

#### 4. Rafraîchir le Token
```bash
curl -X POST http://localhost:8000/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token"
  }'
```

#### 5. Déconnexion (Logout)
```bash
curl -X POST http://localhost:8000/auth/logout/ \
  -H "Authorization: Bearer your_access_token"
```

### 📝 Notes Importantes

1. **Tokens JWT** :
   - Le token d'accès expire après 1 heure
   - Le token de rafraîchissement expire après 1 jour
   - Conservez ces tokens de manière sécurisée

2. **Headers Requis** :
   - Pour les requêtes authentifiées : `Authorization: Bearer your_access_token`
   - Pour toutes les requêtes : `Content-Type: application/json`

3. **Réponses** :
   - Succès : Code 200/201 avec les données
   - Erreur d'authentification : Code 401
   - Erreur de permission : Code 403
   - Ressource non trouvée : Code 404

### 🔧 Configuration Postman

1. Créez une nouvelle collection "Suku API"
2. Importez ces endpoints
3. Créez un environnement avec les variables :
   - `base_url`: http://localhost:8000
   - `access_token`: [à remplir après login]
   - `refresh_token`: [à remplir après login]


Teste des endpoinds de l'authentification
📋 ORDRE DE TEST RECOMMANDÉ :
Création de compte → Vérifiez le statut 201
Vérification email → Vérifiez le statut 200
Connexion → Récupérez les tokens
Profil utilisateur → Vérifiez les données
Modifier profil → Testez la modification
Refresh token → Testez le renouvellement
Changer mot de passe → Testez la modification
Déconnexion → Testez la déconnexion
