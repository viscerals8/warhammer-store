# Warhammer Store

Tienda online full-stack para figuras de Warhammer e impresiones 3D personalizadas, con panel de administración y seguimiento de flota de reparto. Proyecto de portfolio: cubre de punta a punta el ciclo típico de un e-commerce (catálogo → carrito → checkout → gestión admin) más una capa de logística con mapa en tiempo real.

## Qué problema resuelve

Un negocio chico que vende piezas físicas y bajo pedido (impresiones 3D custom) necesita, como mínimo:

- Un catálogo con control de inventario y alertas de stock bajo.
- Un flujo de compra completo (carrito → checkout → pedido) sin depender de una plataforma de terceros.
- Un panel de administración con visibilidad real de ventas (qué se vende, cuánto entra, tendencia mensual) y gestión de pedidos.
- Visibilidad de la logística de entrega: zonas de cobertura, tarifas por zona y estado de los vehículos de reparto.

Este proyecto implementa esas cuatro piezas como una aplicación única, con autenticación por roles (cliente vs. administrador) para separar lo que ve un comprador de lo que ve quien opera el negocio.

## Cómo se resolvió

- **Backend** (FastAPI + SQLAlchemy): expone una API REST con autenticación JWT. El JWT lleva el id de usuario y un flag `is_admin` en el payload, y cada endpoint de administración depende de una validación de ese flag en el servidor (el frontend nunca es la única barrera de seguridad).
- **Catálogo e inventario**: cada producto tiene stock, nivel mínimo de stock y metadatos propios de impresión 3D (tiempo de impresión, tipo de resina) además de los atributos típicos de un producto de retail.
- **Checkout con zonas de envío**: en vez de una tarifa de envío fija, el checkout consulta zonas de entrega (radio geográfico + tarifa + color) y suma el costo correspondiente al total del pedido.
- **Dashboard**: agregaciones sobre pedidos y ventas (revenue total, top productos, ventas por mes, productos con stock bajo) para la vista de administrador.
- **Mapa de flota**: un mapa (Leaflet + tiles de CartoDB, sin API key) muestra las zonas de entrega y la posición de los vehículos. La posición se actualiza cada 3 segundos vía polling desde una tarea en segundo plano del backend que simula el movimiento — la arquitectura está pensada para poder reemplazar esa simulación por GPS real sin tocar el frontend.
- **Imágenes de producto**: sin acceso a fotografía oficial de producto, se optó por emblemas SVG propios (uno por facción/categoría) en vez de imágenes de stock genéricas.

## Estado del proyecto (honesto, por módulo)

| Módulo | Estado | Detalle |
|---|---|---|
| Autenticación (JWT, roles cliente/admin) | ✅ Completo | Login, registro, guard de rutas en Angular + validación real en cada endpoint del backend |
| Catálogo de productos (CRUD, filtros, categorías) | ✅ Completo | Incluye atributos específicos de impresión 3D |
| Carrito de compras | ✅ Completo | |
| Checkout + zonas de envío | ✅ Completo | Tras confirmar el pedido redirige a `/home` (no existe todavía una página de detalle de pedido post-compra) |
| Historial de pedidos (cliente) | 🟡 Parcial | La tabla de administración de pedidos muestra "Customer: N/A" — la respuesta de la API no incluye aún el nombre/email del dueño del pedido |
| Gestión de pedidos (admin) | ✅ Completo | Cambio de estado del pedido |
| Dashboard de analytics | ✅ Completo | Revenue, top productos, ventas mensuales, alertas de stock bajo |
| Mapa de flota + simulación de vehículos | ✅ Completo | Simulación por backend (no GPS real todavía); diseñado para aceptarlo a futuro |
| Notificaciones de UI | 🟡 Parcial | Reemplazadas por Material Snackbar en checkout; quedan `alert()`/`confirm()` nativos del navegador en `admin-products`, `product-detail` y `register` |
| Pasarela de pago real | ⛔ Pendiente | No implementada (no hay integración con Stripe/PayPal/etc.) |
| Tests automatizados | 🟡 Parcial | 12 tests de backend (pytest) sobre `auth.py`/`crud.py` y 8 de frontend (Jasmine/Karma) sobre `AuthService`/`AdminGuard`. Cubre lo más crítico (login, JWT, stock, checkout), no hay cobertura completa |
| CI/CD | ⛔ Pendiente | No configurado |

## Stack técnico

**Backend**
- FastAPI + SQLAlchemy (ORM)
- Autenticación JWT (`python-jose` + `passlib`/bcrypt)
- SQL Server en producción vía `DATABASE_URL`, con fallback automático a SQLite si no está configurada (útil para desarrollo local sin depender de un servidor externo)

**Frontend**
- Angular 17 (NgModules clásicos, no standalone components)
- Angular Material 17 (componentes MDC)
- Leaflet + tiles de CartoDB para el mapa de flota

## Cómo correrlo localmente

### Requisitos
- Python 3.9+
- Node.js 18+ y Angular CLI (`npm install -g @angular/cli`)
- SQL Server (opcional — sin él, cae automáticamente a SQLite local)

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate       # Linux/Mac

pip install -r requirements.txt

# Copiar el archivo de ejemplo y completar tus propios valores
cp .env.example .env
```

Editar `.env` con tus propios datos (nunca subir este archivo — ya está en `.gitignore`):

```
DATABASE_URL=mssql+pyodbc://usuario:contraseña@localhost:1433/warhammer_store?driver=ODBC+Driver+17+for+SQL+Server
SECRET_KEY=generá-una-clave-propia-larga-y-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Si no configurás `DATABASE_URL`, el proyecto usa automáticamente `sqlite:///./warhammer_store.db`.

```bash
python init_db.py       # crea tablas + categorías + productos de ejemplo + usuario admin
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API en `http://localhost:8000` — documentación interactiva en `http://localhost:8000/docs`.

**Credencial de administrador (solo para este entorno de desarrollo/demo, no usar en producción):** `admin@warhammer.store` / `admin123`.

### Frontend

```bash
cd frontend
npm install
ng serve --open
```

Aplicación en `http://localhost:4200`.

### Tests

```bash
# Backend (desde backend/, con el venv activado)
pip install -r requirements-dev.txt
pytest

# Frontend (desde frontend/)
npm test
```

### Scripts de arranque rápido (Windows)

`start-backend.bat`, `start-frontend.bat` y `start-all.bat` en la raíz automatizan los pasos de arriba.

## Estructura del proyecto

```
trasin/
├── backend/            # API FastAPI
│   ├── main.py, database.py, models.py, schemas.py, crud.py, auth.py, init_db.py
│   └── routers/         # auth, products, categories, cart, orders, dashboard, fleet
├── frontend/            # Aplicación Angular
│   └── src/app/
│       ├── components/  # una carpeta por vista
│       ├── services/    # un servicio HTTP por dominio
│       ├── guards/       # AdminGuard
│       ├── interceptors/ # inyecta el JWT en cada request
│       └── assets/emblems/ # emblemas SVG propios por facción
└── docs/                # documentación técnica extendida y notas de desarrollo
```

Documentación más detallada (modelo de datos completo, decisiones de diseño, bugs conocidos ya corregidos) en [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md).

## Licencia

Proyecto educativo / de portfolio.
