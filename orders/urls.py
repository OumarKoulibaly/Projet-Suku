from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    # URLs personnalisées pour les actions du panier (sans préfixe car déjà sous /orders/)
    path('carts/current/', CartViewSet.as_view({'get': 'current'}), name='cart-current'),
    path('carts/add_item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('carts/update_item/', CartViewSet.as_view({'post': 'update_item'}), name='cart-update-item'),
    path('carts/remove_item/', CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('carts/clear/', CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
    path('carts/summary/', CartViewSet.as_view({'get': 'summary'}), name='cart-summary'),
] 