from rest_framework import serializers
from .models import Category, Product
from .exceptions import (
    ProductAlreadyExistsException, CategoryAlreadyExistsException,
    InvalidPriceException, InvalidStockException
)

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Le nom de la catégorie doit contenir au moins 2 caractères.")
        return value.strip()
    
    def validate_slug(self, value):
        if value:
            if Category.objects.filter(slug=value).exists():
                raise CategoryAlreadyExistsException()
        return value

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    origin_display = serializers.CharField(source='get_origin_display', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 
            'image', 'image_url', 'category', 'category_name', 'category_slug',
            'origin', 'origin_display', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description']

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'stock', 'image', 'category', 'origin', 'is_available']
    
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom du produit doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("La description doit contenir au moins 10 caractères.")
        return value.strip()
    
    def validate_price(self, value):
        if value <= 0:
            raise InvalidPriceException()
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise InvalidStockException()
        return value
    
    def validate_slug(self, value):
        if value:
            if Product.objects.filter(slug=value).exists():
                raise ProductAlreadyExistsException()
        return value
    
    def validate_category(self, value):
        # Vérifier que la catégorie existe et est valide
        if not value:
            raise serializers.ValidationError("Une catégorie doit être sélectionnée.")
        return value 