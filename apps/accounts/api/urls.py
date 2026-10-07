"""Organiza los endpoints oficiales y versionados de cuentas."""

from django.urls import path

from apps.accounts.api.views import LoginView, RecoverView, RegisterView, RenewView, ResetView

app_name = "accounts"

urlpatterns = [
    path("accounts/", RegisterView.as_view(), name="account-create"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/password/recovery/", RecoverView.as_view(), name="password-recovery"),
    path("auth/password/reset/", ResetView.as_view(), name="password-reset"),
    path("auth/session/renew/", RenewView.as_view(), name="session-renew"),
]
