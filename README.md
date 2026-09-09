# Plataforma de gestion para negocio de postres

Aplicacion web Django para administrar autenticacion, usuarios y las fases futuras de catalogo, inventario, compras, produccion, ventas, finanzas y dashboard.

## Requisitos

- Python 3.12+
- PostgreSQL
- Git

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tus valores locales. No subas secretos reales al repositorio.

## Base de datos

Para PostgreSQL, crea la base de datos y ajusta estas variables:

```env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=postres
DATABASE_USER=postres_user
DATABASE_PASSWORD=postres_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Tambien puedes usar:

```env
DATABASE_URL=postgres://postres_user:postres_password@localhost:5432/postres
```

Si no configuras PostgreSQL, el proyecto usa sqlite por defecto para facilitar pruebas locales.

## Migraciones

```bash
python manage.py migrate
```

Las migraciones iniciales crean el modelo `usuarios.Usuario` y los grupos:

- ADMINISTRADOR
- VENTAS
- COMPRAS
- PRODUCCION
- SOCIO

## Superusuario

```bash
python manage.py createsuperuser
```

El identificador principal es el correo electronico. El telefono es opcional y, si existe, debe ser unico.

## Servidor local

```bash
python manage.py runserver
```

Rutas principales:

- `/` dashboard protegido
- `/usuarios/login/`
- `/usuarios/logout/`
- `/usuarios/password-reset/`
- `/usuarios/password-change/`
- `/admin/`

## Tests

```bash
python manage.py test
```

## Alcance de la Fase 1

- Usuario personalizado desde el inicio.
- Login por correo y opcionalmente por telefono.
- Logout.
- Recuperacion de contrasena con backend de correo configurable.
- Cambio de contrasena para usuarios autenticados.
- Rutas protegidas y redireccion al login.
- Navbar/base layout mostrando el usuario autenticado.
- Grupos iniciales de roles.
