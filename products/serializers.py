from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 
            'image', 'image_url', 'category', 'category_name', 'category_slug',
            'is_available', 'created_at', 'updated_at'
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
        fields = ['name', 'slug', 'description', 'price', 'stock', 'image', 'category', 'is_available']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Le stock ne peut pas être négatif")
        return value
    
    def validate_slug(self, value):
        if value:
            # Vérifier que le slug est unique
            if Product.objects.filter(slug=value).exists():
                raise serializers.ValidationError("Ce slug existe déjà")
        return value 