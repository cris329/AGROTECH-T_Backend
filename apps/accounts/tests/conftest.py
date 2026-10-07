"""Fixtures compartidas para pruebas."""
import base64

import pytest
from django.contrib.auth.hashers import make_password

from apps.accounts.models import User


@pytest.fixture(autouse=True)
def token_key(monkeypatch):
    """Configura claves deterministas exclusivamente para pruebas."""
    monkeypatch.setenv("JWT_ENCRYPTION_KEY", base64.b64encode(b"k" * 32).decode())
    monkeypatch.setenv("OTP_HMAC_KEY", "test-otp-key")


@pytest.fixture
def user(db) -> User:
    """Crea una cuenta válida reutilizable."""
    return User.objects.create(
        first_name="Ana",
        last_name="Pérez",
        identification="12345678",
        phone="3001234567",
        correo="ana@example.com",
        password_hash=make_password("Secure1!"),
    )
