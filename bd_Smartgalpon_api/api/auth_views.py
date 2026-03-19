from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# Serializador para el registro de usuarios usando ya el auth de django 
class RegisterSerializer(serializers.Serializer):
    #el username minimo de 3 caracteres y maximo de 150 caracteres
    username = serializers.CharField(min_length=3, max_length=150)
    #el password minimo de 6 caracteres y solo se puede escribir (no se puede leer)
    password = serializers.CharField(min_length=6, write_only=True)
    #el email es requerido y no puede estar en blanco
    email = serializers.EmailField(required=True, allow_blank=False)

    #validando si el usuario si existe
    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya existe.")
        return value
    
    #validando que el email solo sea de gmail.com
    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if not email.endswith("@gmail.com"):
            raise serializers.ValidationError("Solo se permiten correos @gmail.com.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Ese correo ya está registrado.")
        return email

    #crear al usuario
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {"success": True, "id": user.id, "username": user.username},
        status=status.HTTP_201_CREATED,
    )
