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
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


