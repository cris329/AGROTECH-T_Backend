"""Configura la aplicación de cuentas."""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Declara el dominio de cuentas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
