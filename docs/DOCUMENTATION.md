# Warhammer Store — Documentación Técnica

Última actualización: reflejada al estado del proyecto tras la sesión de rediseño + fusión con SQL Server + módulo de flota.

## 1. Qué es este proyecto

Tienda e-commerce temática de Warhammer (miniaturas oficiales + impresiones 3D custom), pensada como pieza de portfolio. Full-stack:

- **Frontend**: Angular 17 (NgModule, no standalone) + Angular Material 17 (MDC).
- **Backend**: FastAPI + SQLAlchemy ORM + JWT auth.
- **Base de datos**: SQL Server (host configurable vía `DATABASE_URL`, base `trasin`). SQLite queda disponible como fallback local si `DATABASE_URL` no está seteada.

## 2. Estructura de carpetas

```
trasin/
├── README.md
├── start-all.bat / start-backend.bat / start-frontend.bat
├── backend/
│   ├── main.py              # entrypoint FastAPI, CORS, static /media, routers, tarea de simulación de flota
│   ├── database.py          # engine SQLAlchemy, Settings (lee .env)
│   ├── models.py            # modelos ORM (fuente de verdad del esquema)
│   ├── schemas.py           # esquemas Pydantic (request/response)
│   ├── crud.py               # lógica de acceso a datos
│   ├── auth.py                # JWT: hash de password, creación/validación de token
│   ├── init_db.py            # script de siembra (categorías + productos + admin)
│   ├── routers/
│   │   ├── auth.py            # /api/auth (register, login, me)
│   │   ├── products.py        # /api/products (CRUD)
│   │   ├── categories.py      # /api/categories
│   │   ├── cart.py            # /api/cart (requiere login)
│   │   ├── orders.py          # /api/orders (checkout, historial, admin)
│   │   ├── dashboard.py       # /api/dashboard (stats, solo admin)
│   │   └── fleet.py           # /api/fleet (zonas de envío, vehículos)
│   ├── media/products/        # imágenes legacy (ya no usadas por el catálogo activo)
│   └── .env                   # DATABASE_URL, SECRET_KEY, etc. (no versionar)
├── frontend/
│   └── src/app/
│       ├── components/        # un folder por vista (ver sección 5)
│       ├── services/          # un servicio HTTP por dominio
│       ├── guards/            # admin.guard.ts
│       ├── interceptors/      # auth.interceptor.ts (agrega Bearer token)
│       ├── models/            # interface.model.ts (tipos TS)
│       ├── utils/              # warhammer-images.ts (fallback de imágenes)
│       └── assets/emblems/     # emblemas SVG propios por facción
└── scripts/                    # utilidades sueltas (scraper de imágenes, no usado en runtime)
```

## 3. Modelo de datos (SQLAlchemy — `backend/models.py`)

| Tabla | Campos clave | Notas |
|---|---|---|
| `users` | email, hashed_password, is_admin | `is_admin` decide acceso a rutas de administración |
| `categories` | name, parent_id | auto-referencial (subcategorías) |
| `products` | price, cost_price, sku (unique), stock_quantity, min_stock_level, category_id, image_urls (JSON), is_3d_print, print_time_hours, resin_type | `image_urls` guarda **paths**, no binarios (ver sección 7) |
| `cart_items` | user_id, product_id, quantity | uno por usuario+producto |
| `orders` | total_amount, status (enum), shipping_address (JSON), zone_id, shipping_cost | `zone_id` referencia `delivery_zones` |
| `order_items` | order_id, product_id, quantity, unit_price, total_price | snapshot de precio al momento de compra |
| `sales` | product_id, order_id, month_year | usado por el dashboard para reportes mensuales |
| `delivery_zones` | name, center_lat, center_lng, radius_km, shipping_cost, color | zonas de cobertura de envío (Santiago) |
| `vehicles` | name, plate, driver_name, status, lat, lng, heading_lat/lng | posición simulada, se mueve sola cada 3s |

## 4. Backend — flujos clave

### 4.1 Autenticación
1. `POST /api/auth/login` valida credenciales y firma un JWT con `sub` (email), **`user_id`** y **`is_admin`** en el payload.
2. El frontend decodifica ese JWT client-side (`auth.service.ts::decodeToken`) para saber si el usuario es admin — **no vuelve a preguntarle al backend**.
3. Cada request subsecuente lleva `Authorization: Bearer <token>` (inyectado por `auth.interceptor.ts`).
4. `auth.py::get_current_user` usa `OAuth2PasswordBearer` para extraer el token del header y validarlo contra `SECRET_KEY`.
5. `get_current_admin_user` reutiliza lo anterior y además exige `is_admin=True` — usado en endpoints de products (create/update/delete), dashboard, fleet/vehicles y orders/admin.

⚠️ **Importante**: si alguna vez el login "funciona" pero el usuario admin no ve las opciones de administrador, el primer sospechoso es que el JWT no lleve `is_admin` en el payload (ya pasó una vez, ver sección 8).

### 4.2 Carrito → Checkout → Orden
1. Cliente agrega productos vía `POST /api/cart/` (requiere login).
2. En checkout, el frontend pide `GET /api/fleet/zones` (público) para mostrar las zonas de envío y sus tarifas.
3. Al confirmar, `POST /api/orders/` recibe `zone_id` además de la dirección; `crud.create_order` busca la zona, suma `shipping_cost` al total, y limpia el carrito.
4. Cada item de la orden genera también una fila en `sales` (para las métricas del dashboard).

### 4.3 Simulación de flota
- `main.py` lanza una tarea `asyncio` en el evento `startup` que cada 3 segundos llama a `crud.simulate_vehicle_tick`, moviendo cada vehículo un poco (random walk con inercia de dirección).
- `GET /api/fleet/vehicles` (solo admin) devuelve la posición actual — el frontend hace polling cada 3s para reflejar el movimiento en el mapa.
- Arquitectura pensada para aceptar GPS real en el futuro: bastaría con reemplazar `simulate_vehicle_tick` por un endpoint que reciba coordenadas reales desde un dispositivo/app y las escriba en `vehicles`.

## 5. Frontend — rutas y componentes

| Ruta | Componente | Acceso |
|---|---|---|
| `/home` | HomeComponent | público |
| `/products`, `/products/:id` | ProductListComponent, ProductDetailComponent | público |
| `/cart` | CartComponent | requiere login (a nivel de API) |
| `/checkout` | CheckoutComponent | requiere login |
| `/login`, `/register` | LoginComponent, RegisterComponent | público |
| `/dashboard` | DashboardComponent | **AdminGuard** |
| `/admin/orders` | OrdersComponent | **AdminGuard** |
| `/admin/products` | AdminProductsComponent (+ ProductFormComponent en dialog) | **AdminGuard** |
| `/admin/fleet` | FleetMapComponent | **AdminGuard** |

`AdminGuard` (`guards/admin.guard.ts`) valida `authService.isLoggedIn() && authService.isAdmin()`; si falla, redirige a `/home`. Sin esto, cualquiera podía acceder a las vistas de administración escribiendo la URL directamente (el backend igual bloqueaba las mutaciones, pero la pantalla cargaba vacía/rota).

### Servicios (`services/`)
- `auth.service.ts` — login/registro/logout, decodifica el JWT, expone `isLoggedIn()`/`isAdmin()` vía `BehaviorSubject`.
- `product.service.ts`, `cart.service.ts`, `order.service.ts`, `dashboard.service.ts`, `fleet.service.ts` — un wrapper HTTP por dominio, todos leyendo `environment.apiUrl`.
- `notification.service.ts` — reemplaza los `alert()`/`confirm()` nativos por `MatSnackBar` con estilo propio (`wh-snackbar`).

## 6. Sistema de diseño (gótico/imperial)

Definido casi enteramente en `frontend/src/styles.css` vía variables CSS:

```css
--primary-color: #8b0000;   /* rojo sangre */
--gold-color: #d4af37;      /* oro */
--dark-bg: #1a1a2e;         /* navy oscuro */
--card-bg: rgba(26,26,46,0.85);
--font-display: 'Cinzel', serif;   /* títulos */
--font-body: 'Roboto', sans-serif; /* texto */
```

Elementos reutilizables (clases globales):
- `.reveal` — animación de entrada (fadeInUp).
- `.frame-corner` (+ `.tl/.tr/.bl/.br`) — esquinas doradas estilo HUD/relicario.
- `.frosted-panel` — panel de vidrio esmerilado (fondo oscuro translúcido + blur) para texto que de otra forma quedaría directo sobre la imagen de fondo.
- `.auth-glyph` / `.dialog-glyph` — cruz gótica animada sobre títulos de card/diálogo.

**Gotcha de Angular Material 17**: el proyecto usa componentes MDC (`mat-mdc-*`), no las clases legacy (`mat-form-field-*`, `mat-card` sin prefijo). Cualquier override de tema debe apuntar a las clases `mat-mdc-*` reales — confirmalo siempre inspeccionando el DOM, no asumas por el nombre del componente.

## 7. Imágenes de producto

No hay fotos reales de producto ni API gratuita de Games Workshop para conseguirlas (protegen su IP de cerca). Solución adoptada: **emblemas SVG propios**, uno por facción, en `frontend/src/assets/emblems/*.svg` (space-marines, orks, eldar, chaos, tau, imperial-guard, necrons, terrain, custom-print). La tabla `products.image_urls` solo guarda el path (`/assets/emblems/xxx.svg`); el archivo real vive en el bundle del frontend, no en la base de datos ni en el backend.

## 8. Bugs encontrados y corregidos durante el desarrollo

Documentados para no repetirlos si se reconstruye el proyecto:

1. **`auth.py::get_current_user` con `Depends(lambda: None)`** — el token nunca se leía del header, todas las rutas protegidas fallaban siempre. Fix: `Depends(OAuth2PasswordBearer(tokenUrl=...))`.
2. **JWT sin `is_admin`** — el login firmaba el token solo con `sub`, así que el frontend nunca detectaba usuarios admin. Fix: incluir `user_id` e `is_admin` en el payload.
3. **Rutas admin sin guard** — `/dashboard`, `/admin/*` eran accesibles por URL directa sin sesión. Fix: `AdminGuard` en `app-routing.module.ts`.
4. **`MatCheckboxModule` nunca importado** — los checkboxes del formulario de producto tiraban `Cannot read properties of null (reading 'writeValue')`.
5. **Orden de rutas en `orders.py`** — `/{order_id}` estaba declarada antes que `/admin`, así que `GET /orders/admin` matcheaba como `order_id="admin"` y fallaba con 422. Fix: declarar `/admin` antes que `/{order_id}`.
6. **`create_all()` no altera tablas existentes** — al migrar a SQL Server hubo que correr `ALTER TABLE orders ADD zone_id, shipping_cost` a mano; SQLAlchemy solo crea tablas nuevas, nunca modifica columnas de tablas ya existentes.
7. **Angular Material 17 es MDC-based** — varias reglas CSS globales apuntaban a clases legacy (`.mat-form-field-outline`, `.mat-card`) que ya no existen en el DOM; hubo que re-apuntar a `.mat-mdc-*`.

## 9. Cómo correr el proyecto

```powershell
# Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (otra terminal)
cd frontend
ng serve --open
```

Credenciales admin: `admin@warhammer.store` / `admin123`.

`backend/.env` controla la conexión a base de datos:
```
DATABASE_URL=mssql+pyodbc://<user>:<password>@<host>:1433/trasin?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
```
Si se borra o comenta esa línea, `database.py` cae automáticamente a `sqlite:///./warhammer_store.db` (útil para desarrollo sin acceso al SQL Server).

## 10. Pendientes conocidos (no bloqueantes)

- `checkout.component.ts` redirige a `/home` tras crear la orden (antes apuntaba a una ruta `/orders/:id` inexistente).
- `orders.component.html` muestra "Customer: N/A" — el `OrderResponse` no incluye el email/nombre del usuario dueño de la orden.
- Quedan `alert()`/`confirm()` nativos sin reemplazar en `admin-products.component.ts`, `product-detail.component.ts` y `register.component.ts` (ya reemplazado en `checkout.component.ts`).
- El panel "Advanced Options" del formulario de producto (dentro del dialog) no se verificó visualmente al 100% tras el último fix — revisar que el `mat-expansion-panel` despliegue correctamente el contenido dentro del scroll del dialog.
