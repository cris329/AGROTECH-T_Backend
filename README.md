# AGROTECH-T_Backend

Backend independiente de AGROTECH-T construido con:

- Python 3.13
- Django 5.2 LTS
- Django REST Framework
- MariaDB 11.8.8

No contiene frontend.

## Funciones

- Registro con identificación única.
- Contraseñas con Argon2.
- Inicio de sesión con JWT cifrado mediante JWE A256GCM.
- Recuperación por correo con Brevo/SMTP o por WhatsApp con Twilio Verify.
- OTP de correo almacenado como HMAC, con caducidad y máximo cinco intentos.
- Sesión única, vencimiento por inactividad y rotación de token.
- CORS restringido, HTTPS en producción y logs JSON.
- OpenAPI y Swagger.

## Inicio con Docker

1. Copia `.env.example` como `.env`.
2. Completa las contraseñas de MariaDB.
3. Genera las claves secretas:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
python -c "import base64,secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

Usa el primer valor para `DJANGO_SECRET_KEY` y `OTP_HMAC_KEY`. Usa el segundo
para `JWT_ENCRYPTION_KEY`.

4. Ejecuta:

```bash
docker compose up --build
```

API: `http://localhost:8080`  
Swagger: `http://localhost:8080/api/docs/`

## Endpoints

La especificación completa está en `docs/API.md`.

- `POST /api/v1/accounts/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/password/recovery/`
- `POST /api/v1/auth/password/reset/`
- `POST /api/v1/auth/session/renew/`

## Desarrollo

```bash
python -m venv .venv
pip install -r requirements-dev.txt
pytest
ruff check .
```

Las pruebas usan SQLite. Docker y producción usan MariaDB.

## Producción

Configura `DJANGO_DEBUG=false`, hosts explícitos, HTTPS, claves únicas y solo
los orígenes CORS autorizados. El contenedor aplica las migraciones antes de
iniciar Gunicorn.
