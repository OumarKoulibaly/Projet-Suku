from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .models import User

# Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour obtenir les tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    """Vue personnalisée pour rafraîchir les tokens JWT"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            return Response({
                'message': 'Token rafraîchi avec succès',
                'access': str(serializer.validated_data['access']),
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Token invalide',
            'message': 'Le token de rafraîchissement est invalide ou expiré.',
            'details': serializer.errors,
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Vue de connexion personnalisée"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Connexion réussie',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Données invalides',
        'message': 'Les données fournies sont invalides.',
        'details': serializer.errors,
        'status_code': 400
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Vue d'inscription personnalisée"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Inscription réussie',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'error': 'Données invalides',
        'message': 'Les données fournies sont invalides.',
        'details': serializer.errors,
        'status_code': 400
    }, status=status.HTTP_400_BAD_REQUEST)
