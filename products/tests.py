from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateSerializer

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")

    def test_category_creation(self):
        """Test de création d'une catégorie"""
        self.assertEqual(self.category.name, "Fruits")
        self.assertEqual(self.category.slug, "fruits")
        self.assertTrue(self.category.created_at)
        self.assertTrue(self.category.updated_at)

    def test_category_str(self):
        """Test de la méthode __str__"""
        self.assertEqual(str(self.category), "Fruits")

    def test_category_slug_auto_generation(self):
        """Test de la génération automatique du slug"""
        category = Category.objects.create(name="Légumes Bio")
        self.assertEqual(category.slug, "legumes-bio")

    def test_category_meta(self):
        """Test des métadonnées de la catégorie"""
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")
        self.assertEqual(Category._meta.ordering, ['name'])

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")
        self.product = Product.objects.create(
            name="Pomme Golden",
            description="Pomme sucrée et croquante",
            price=Decimal('2.50'),
            stock=100,
            category=self.category,
            origin='local'
        )

    def test_product_creation(self):
        """Test de création d'un produit"""
        self.assertEqual(self.product.name, "Pomme Golden")
        self.assertEqual(self.product.slug, "pomme-golden")
        self.assertEqual(self.product.price, Decimal('2.50'))
        self.assertEqual(self.product.stock, 100)
        self.assertEqual(self.product.origin, 'local')
        self.assertTrue(self.product.is_available)
        self.assertEqual(self.product.category, self.category)

    def test_product_str(self):
        """Test de la méthode __str__"""
        self.assertEqual(str(self.product), "Pomme Golden")

    def test_product_slug_auto_generation(self):
        """Test de la génération automatique du slug"""
        product = Product.objects.create(
            name="Banane Cavendish",
            description="Banane douce et crémeuse",
            price=Decimal('1.80'),
            stock=50,
            category=self.category
        )
        self.assertEqual(product.slug, "banane-cavendish")

    def test_product_origin_choices(self):
        """Test des choix d'origine"""
        origins = [choice[0] for choice in Product.ORIGIN_CHOICES]
        expected_origins = ['local', 'imported', 'organic', 'conventional', 'fair_trade']
        self.assertEqual(origins, expected_origins)

    def test_product_meta(self):
        """Test des métadonnées du produit"""
        self.assertEqual(Product._meta.ordering, ['-created_at'])

class CategorySerializerTest(APITestCase):
    def setUp(self):
        self.category_data = {'name': 'Fruits'}
        self.category = Category.objects.create(name="Fruits")

    def test_category_serializer_valid_data(self):
        """Test du sérialiseur avec des données valides"""
        serializer = CategorySerializer(data=self.category_data)
        self.assertTrue(serializer.is_valid())

    def test_category_serializer_invalid_name(self):
        """Test du sérialiseur avec un nom invalide"""
        invalid_data = {'name': 'A'}
        serializer = CategorySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_category_serializer_product_count(self):
        """Test du champ product_count"""
        Product.objects.create(
            name="Pomme",
            description="Pomme rouge",
            price=Decimal('2.00'),
            stock=50,
            category=self.category
        )
        serializer = CategorySerializer(self.category)
        self.assertEqual(serializer.data['product_count'], 1)

class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")
        self.product = Product.objects.create(
            name="Pomme Golden",
            description="Pomme sucrée et croquante",
            price=Decimal('2.50'),
            stock=100,
            category=self.category,
            origin='local'
        )

    def test_product_serializer_fields(self):
        """Test des champs du sérialiseur"""
        serializer = ProductSerializer(self.product)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('slug', data)
        self.assertIn('price', data)
        self.assertIn('stock', data)
        self.assertIn('category_name', data)
        self.assertIn('origin', data)
        self.assertIn('origin_display', data)

    def test_product_serializer_category_info(self):
        """Test des informations de catégorie"""
        serializer = ProductSerializer(self.product)
        self.assertEqual(serializer.data['category_name'], 'Fruits')
        self.assertEqual(serializer.data['category_slug'], 'fruits')

    def test_product_serializer_origin_display(self):
        """Test de l'affichage de l'origine"""
        serializer = ProductSerializer(self.product)
        self.assertEqual(serializer.data['origin_display'], 'Local')

class ProductCreateSerializerTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")
        self.valid_data = {
            'name': 'Pomme Golden',
            'description': 'Pomme sucrée et croquante de qualité supérieure',
            'price': '2.50',
            'stock': 100,
            'category': self.category.id,
            'origin': 'local',
            'is_available': True
        }

    def test_product_create_serializer_valid_data(self):
        """Test du sérialiseur de création avec des données valides"""
        serializer = ProductCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_product_create_serializer_invalid_price(self):
        """Test avec un prix invalide"""
        invalid_data = self.valid_data.copy()
        invalid_data['price'] = '-1.00'
        serializer = ProductCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_product_create_serializer_invalid_stock(self):
        """Test avec un stock invalide"""
        invalid_data = self.valid_data.copy()
        invalid_data['stock'] = -10
        serializer = ProductCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock', serializer.errors)

    def test_product_create_serializer_short_description(self):
        """Test avec une description trop courte"""
        invalid_data = self.valid_data.copy()
        invalid_data['description'] = 'Court'
        serializer = ProductCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Fruits")

    def test_list_categories(self):
        """Test de la liste des catégories"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_create_category(self):
        """Test de création d'une catégorie"""
        url = reverse('category-list')
        data = {'name': 'Légumes'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_retrieve_category(self):
        """Test de récupération d'une catégorie"""
        url = reverse('category-detail', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_category(self):
        """Test de mise à jour d'une catégorie"""
        url = reverse('category-detail', kwargs={'slug': self.category.slug})
        data = {'name': 'Fruits Bio'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_delete_category(self):
        """Test de suppression d'une catégorie"""
        url = reverse('category-detail', kwargs={'slug': self.category.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_category_products(self):
        """Test de récupération des produits d'une catégorie"""
        Product.objects.create(
            name="Pomme",
            description="Pomme rouge",
            price=Decimal('2.00'),
            stock=50,
            category=self.category
        )
        url = reverse('category-products', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Fruits")
        self.product = Product.objects.create(
            name="Pomme Golden",
            description="Pomme sucrée et croquante",
            price=Decimal('2.50'),
            stock=100,
            category=self.category,
            origin='local'
        )

    def test_list_products(self):
        """Test de la liste des produits"""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_create_product(self):
        """Test de création d'un produit"""
        url = reverse('product-list')
        data = {
            'name': 'Banane',
            'description': 'Banane douce et crémeuse de qualité supérieure',
            'price': '1.80',
            'stock': 50,
            'category': self.category.id,
            'origin': 'imported'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_retrieve_product(self):
        """Test de récupération d'un produit"""
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_products_by_category(self):
        """Test de filtrage par catégorie"""
        url = reverse('product-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_products_by_origin(self):
        """Test de filtrage par origine"""
        url = reverse('product-list')
        response = self.client.get(url, {'origin': 'local'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_products_by_price_range(self):
        """Test de filtrage par plage de prix"""
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': '1.00', 'max_price': '3.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_products(self):
        """Test de recherche de produits"""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Pomme'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available_products(self):
        """Test de récupération des produits disponibles"""
        url = reverse('product-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_low_stock_products(self):
        """Test de récupération des produits en stock faible"""
        url = reverse('product-low-stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_stock(self):
        """Test de mise à jour du stock"""
        url = reverse('product-update-stock', kwargs={'slug': self.product.slug})
        data = {'quantity': 75}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_toggle_availability(self):
        """Test de basculement de la disponibilité"""
        url = reverse('product-toggle-availability', kwargs={'slug': self.product.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ExceptionTest(TestCase):
    def test_product_not_found_exception(self):
        """Test de l'exception produit non trouvé"""
        from .exceptions import ProductNotFoundException
        exception = ProductNotFoundException()
        self.assertEqual(exception.status_code, 404)
        self.assertEqual(exception.default_code, 'product_not_found')

    def test_invalid_price_exception(self):
        """Test de l'exception prix invalide"""
        from .exceptions import InvalidPriceException
        exception = InvalidPriceException()
        self.assertEqual(exception.status_code, 400)
        self.assertEqual(exception.default_code, 'invalid_price')
