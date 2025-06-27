from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class ProductNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Produit non trouvé.')
    default_code = 'product_not_found'

class CategoryNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Catégorie non trouvée.')
    default_code = 'category_not_found'

class ProductAlreadyExistsException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Un produit avec ce nom ou slug existe déjà.')
    default_code = 'product_already_exists'

class CategoryAlreadyExistsException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Une catégorie avec ce nom ou slug existe déjà.')
    default_code = 'category_already_exists'

class InvalidPriceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Le prix doit être supérieur à 0.')
    default_code = 'invalid_price'

class InvalidStockException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Le stock ne peut pas être négatif.')
    default_code = 'invalid_stock'

class InsufficientStockException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Stock insuffisant pour cette opération.')
    default_code = 'insufficient_stock'

class ProductNotAvailableException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Ce produit n\'est pas disponible.')
    default_code = 'product_not_available'

def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions personnalisé"""
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personnaliser les messages d'erreur
        if response.status_code == 404:
            response.data = {
                'error': 'Ressource non trouvée',
                'message': 'La ressource demandée n\'existe pas.',
                'status_code': 404
            }
        elif response.status_code == 400:
            response.data = {
                'error': 'Données invalides',
                'message': 'Les données fournies sont invalides.',
                'details': response.data,
                'status_code': 400
            }
        elif response.status_code == 401:
            response.data = {
                'error': 'Non autorisé',
                'message': 'Vous devez être connecté pour effectuer cette action.',
                'status_code': 401
            }
        elif response.status_code == 403:
            response.data = {
                'error': 'Accès interdit',
                'message': 'Vous n\'avez pas les permissions nécessaires.',
                'status_code': 403
            }
        elif response.status_code == 500:
            response.data = {
                'error': 'Erreur serveur',
                'message': 'Une erreur interne s\'est produite.',
                'status_code': 500
            }
    
    return response 