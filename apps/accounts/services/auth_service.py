"""Ejecuta los casos de uso de registro, acceso y recuperación."""
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.exceptions import AppError
from apps.accounts.models import Session, User
from apps.accounts.services import otp_service, token_service


def register(data: dict) -> None:
    """Crea una cuenta y almacena únicamente el hash de contraseña."""
    password = data.pop("password")
    try:
        User.objects.create(password_hash=make_password(password), **data)
    except IntegrityError as exc:
        raise AppError("esa identificacion ya esta registrada", 409) from exc


def login(identification: str, password: str) -> str:
    """Valida credenciales y abre una sesión única."""
    user = User.objects.filter(identification=identification).first()
    if not user or not check_password(password, user.password_hash):
        raise AppError("credenciales invalidas", 401)
    token = token_service.issue(user.pk)
    Session.objects.update_or_create(
        user=user,
        defaults={"last_seen": timezone.now(), "token": token},
    )
    return token


def recover(identification: str, method: str) -> int:
    """Solicita un OTP sin revelar cuentas inexistentes."""
    user = User.objects.filter(identification=identification).first()
    unavailable = not user or (method == "whatsapp" and not user.phone) or (
        method == "correo" and not user.correo
    )
    if unavailable:
        raise AppError("no se pudo enviar el codigo")
    return otp_service.request_code(user, method)


def reset_password(identification: str, code: str, password: str) -> None:
    """Consume un OTP y guarda una contraseña nueva."""
    user = User.objects.filter(identification=identification).first()
    if not user:
        raise AppError("codigo invalido", 401)
    otp_service.verify_code(user, code)
    user.password_hash = make_password(password)
    user.save(update_fields=["password_hash"])
    Session.objects.filter(user=user).delete()


def renew(authorization: str) -> str:
    """Rota el token de una sesión que permanece activa."""
    current = _bearer(authorization)
    user_id = token_service.read(current)
    threshold = timezone.now() - token_service.ttl()
    session = Session.objects.filter(
        user_id=user_id,
        token=current,
        last_seen__gt=threshold,
    ).first()
    if not session:
        raise AppError("la sesion vencio", 401)
    next_token = token_service.issue(user_id)
    session.token = next_token
    session.last_seen = timezone.now()
    session.save(update_fields=["token", "last_seen"])
    return next_token


def _bearer(header: str) -> str:
    """Extrae un token del esquema HTTP Bearer."""
    scheme, separator, token = header.strip().partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise AppError("la sesion vencio", 401)
    return token.strip()
