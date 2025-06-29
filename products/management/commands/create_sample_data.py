from django.core.management.base import BaseCommand
from products.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crée des données d\'exemple pour les produits'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')
        
        # Créer des catégories
        categories_data = [
            {'name': 'Fruits'},
            {'name': 'Légumes'},
            {'name': 'Fruits Bio'},
            {'name': 'Légumes Bio'},
            {'name': 'Fruits Importés'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'name': cat_data['name']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')
            else:
                self.stdout.write(f'Catégorie existante: {category.name}')
        
        # Créer des produits
        products_data = [
            {
                'name': 'Pomme Golden',
                'description': 'Pomme sucrée et croquante, parfaite pour les desserts et la consommation fraîche.',
                'price': Decimal('2.50'),
                'stock': 100,
                'category': categories[0],  # Fruits
                'origin': 'local'
            },
            {
                'name': 'Banane Cavendish',
                'description': 'Banane douce et crémeuse, riche en potassium et énergisante.',
                'price': Decimal('1.80'),
                'stock': 150,
                'category': categories[0],  # Fruits
                'origin': 'imported'
            },
            {
                'name': 'Tomate Cerise Bio',
                'description': 'Tomates cerises biologiques, cultivées sans pesticides, goût intense et naturel.',
                'price': Decimal('3.20'),
                'stock': 80,
                'category': categories[2],  # Fruits Bio
                'origin': 'organic'
            },
            {
                'name': 'Carotte Orange',
                'description': 'Carottes fraîches et croquantes, riches en bêta-carotène et vitamines.',
                'price': Decimal('1.50'),
                'stock': 120,
                'category': categories[1],  # Légumes
                'origin': 'local'
            },
            {
                'name': 'Avocat Hass',
                'description': 'Avocat crémeux et délicieux, parfait pour les salades et le guacamole.',
                'price': Decimal('2.80'),
                'stock': 60,
                'category': categories[4],  # Fruits Importés
                'origin': 'imported'
            },
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'Produit créé: {product.name} - {product.price}€')
            else:
                self.stdout.write(f'Produit existant: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Données d\'exemple créées avec succès!')
        ) 