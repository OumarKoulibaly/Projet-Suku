from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Nombre de produits'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'is_available', 'image_preview']
    list_filter = ['category', 'is_available', 'price', 'created_at']
    search_fields = ['name', 'description', 'slug']
    list_editable = ['price', 'stock', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-created_at']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Prix et stock', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "Aucune image"
    image_preview.short_description = 'Aperçu'
    image_preview.allow_tags = True