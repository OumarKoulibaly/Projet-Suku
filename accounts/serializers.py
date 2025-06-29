from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User as CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Sérialiseur JWT personnalisé pour l'authentification par email"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authentification avec email
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Connexion impossible avec les informations fournies.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte utilisateur est désactivé.')
            
            # Ajouter l'utilisateur aux attributs validés
            attrs['user'] = user
            
            # Générer les tokens
            refresh = self.get_token(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
            return data
        else:
            raise serializers.ValidationError('Veuillez fournir un email et un mot de passe.')

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authentification avec email
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Connexion impossible avec les informations fournies.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte utilisateur est désactivé.')
        else:
            raise serializers.ValidationError('Veuillez fournir un email et un mot de passe.')

        attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id'] 