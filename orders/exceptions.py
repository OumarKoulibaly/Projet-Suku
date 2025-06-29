from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class CartNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Panier non trouvé.')
    default_code = 'cart_not_found'

class CartItemNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Article du panier non trouvé.')
    default_code = 'cart_item_not_found'

class CartEmptyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Le panier est vide.')
    default_code = 'cart_empty'

class OrderNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Commande non trouvée.')
    default_code = 'order_not_found'

class OrderAlreadyConfirmedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cette commande est déjà confirmée.')
    default_code = 'order_already_confirmed'

class OrderCannotBeCancelledException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cette commande ne peut pas être annulée.')
    default_code = 'order_cannot_be_cancelled'

class InvalidPaymentMethodException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Méthode de paiement invalide.')
    default_code = 'invalid_payment_method'

class InvalidDeliveryAddressException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Adresse de livraison invalide.')
    default_code = 'invalid_delivery_address'

class OrderStatusTransitionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Transition de statut non autorisée.')
    default_code = 'order_status_transition_invalid'

class CartAlreadyExistsException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Un panier actif existe déjà.')
    default_code = 'cart_already_exists'

class ProductNotAvailableForOrderException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Ce produit n\'est pas disponible pour la commande.')
    default_code = 'product_not_available_for_order' 