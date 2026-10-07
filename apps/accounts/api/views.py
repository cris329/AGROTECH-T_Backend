"""Gestiona las solicitudes HTTP del dominio de cuentas."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    LoginSerializer,
    RecoverSerializer,
    RecoveryResponseSerializer,
    RegisterSerializer,
    ResetSerializer,
    SuccessResponseSerializer,
    TokenResponseSerializer,
)
from apps.accounts.services import auth_service


class RegisterView(APIView):
    """Crea cuentas nuevas."""

    authentication_classes = []

    @extend_schema(request=RegisterSerializer, responses={201: SuccessResponseSerializer})
    def post(self, request: Request) -> Response:
        """Registra una cuenta validada."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_service.register(serializer.validated_data.copy())
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Autentica cuentas."""

    authentication_classes = []

    @extend_schema(request=LoginSerializer, responses={200: TokenResponseSerializer})
    def post(self, request: Request) -> Response:
        """Entrega un JWT cifrado."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return _token_response(auth_service.login(**serializer.validated_data))


class RecoverView(APIView):
    """Inicia la recuperación de contraseña."""

    authentication_classes = []

    @extend_schema(request=RecoverSerializer, responses={200: RecoveryResponseSerializer})
    def post(self, request: Request) -> Response:
        """Envía un OTP por el canal solicitado."""
        serializer = RecoverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wait = auth_service.recover(**serializer.validated_data)
        response = Response({"ok": True, "wait": wait})
        response["Cache-Control"] = "no-store"
        return response


class ResetView(APIView):
    """Finaliza la recuperación de contraseña."""

    authentication_classes = []

    @extend_schema(request=ResetSerializer, responses={200: SuccessResponseSerializer})
    def post(self, request: Request) -> Response:
        """Cambia la contraseña después de verificar el OTP."""
        serializer = ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_service.reset_password(**serializer.validated_data)
        return Response({"ok": True})


class RenewView(APIView):
    """Renueva una sesión activa."""

    authentication_classes = []

    @extend_schema(request=None, responses={200: TokenResponseSerializer})
    def post(self, request: Request) -> Response:
        """Rota el token Bearer presentado."""
        token = auth_service.renew(request.headers.get("Authorization", ""))
        return _token_response(token)


def _token_response(token: str) -> Response:
    """Crea una respuesta privada con un token."""
    response = Response({"token": token})
    response["Cache-Control"] = "no-store"
    return response
