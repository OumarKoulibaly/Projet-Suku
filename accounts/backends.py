from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Backend d'authentification personnalisé pour permettre la connexion avec email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Essayer de trouver l'utilisateur par email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # Essayer de trouver l'utilisateur par nom d'utilisateur
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 