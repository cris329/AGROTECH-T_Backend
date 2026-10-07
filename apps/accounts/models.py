"""Modelos persistentes de usuario, código y sesión."""
from django.db import models


class User(models.Model):
    """Representa una cuenta identificada por documento."""

    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    identification = models.CharField(max_length=15, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(max_length=254, blank=True)
    password_hash = models.CharField(max_length=255)

    class Meta:
        db_table = "users"


class LoginCode(models.Model):
    """Conserva una sola huella OTP activa por usuario."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    channel = models.CharField(max_length=10)
    sent_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "login_codes"


class Session(models.Model):
    """Conserva el token vigente y su última actividad."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    last_seen = models.DateTimeField()
    token = models.TextField()

    class Meta:
        db_table = "sessions"
