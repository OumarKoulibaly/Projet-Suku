from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'status', 'updated_at']
    list_filter = ['status', 'updated_at']
    search_fields = ['order__order_number', 'order__user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order', 'status')
        }),
        ('Dates', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'order__user')
