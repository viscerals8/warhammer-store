# Warhammer Store - Tienda Online de Figuras

Aplicación completa para tienda online de figuras de Warhammer e impresiones 3D, con carrito de compras, gestión de inventario y dashboard de ventas.

## Tecnologías

- **Backend**: FastAPI (Python)
- **Base de datos**: SQL Server
- **Frontend**: Angular 17+ con TypeScript
- **UI Framework**: Angular Material

## Estructura del Proyecto

```
trasin/
├── backend/          # API FastAPI
│   ├── main.py               # Aplicación principal
│   ├── database.py           # Conexión a SQL Server
│   ├── models.py             # Modelos SQLAlchemy
│   ├── schemas.py            # Esquemas Pydantic
│   ├── crud.py               # Operaciones de base de datos
│   ├── auth.py               # Autenticación JWT
│   ├── init_db.py            # Inicialización de datos
│   ├── requirements.txt      # Dependencias Python
│   └── routers/              # Endpoints API
│       ├── auth.py
│       ├── products.py
│       ├── categories.py
│       ├── cart.py
│       ├── orders.py
│       └── dashboard.py
│
└── frontend/         # Aplicación Angular
    ├── src/
    │   ├── app/
    │   │   ├── components/
    │   │   │   ├── navbar/
    │   │   │   ├── home/
    │   │   │   ├── product-list/
    │   │   │   ├── product-detail/
    │   │   │   ├── cart/
    │   │   │   ├── checkout/
    │   │   │   ├── login/
    │   │   │   ├── register/
    │   │   │   └── dashboard/
    │   │   ├── services/
    │   │   ├── models/
    │   │   ├── interceptors/
    │   │   ├── app.module.ts
    │   │   └── app-routing.module.ts
    │   └── environments/
    ├── angular.json
    ├── package.json
    └── tsconfig.json
```

## Características

### Backend
- ✅ Autenticación con JWT (login/registro)
- ✅ Gestión de productos (CRUD completo)
- ✅ Categorías de productos
- ✅ Carrito de compras
- ✅ Sistema de pedidos
- ✅ Dashboard de ventas y analytics
- ✅ Control de inventario
- ✅ Alertas de stock bajo

### Frontend
- ✅ Catálogo de productos con filtros
- ✅ Vista detallada de productos
- ✅ Carrito de compras en tiempo real
- ✅ Proceso de checkout
- ✅ Dashboard administrativo:
  - Ingresos totales
  - Número de pedidos
  - Productos más vendidos
  - Tendencia de ventas mensuales
  - Alertas de stock bajo
- ✅ Diseño responsive con Angular Material

## Configuración

### Requisitos Previos

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **SQL Server** (o SQL Server Express/LocalDB)
   - Asegúrate de tener SQL Server instalado y configurado

3. **Node.js 18+ y Angular CLI**
   ```bash
   node --version
   npm --version
   npm install -g @angular/cli
   ```

### 1. Configuración del Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# o
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales de SQL Server:
# DATABASE_URL=mssql+pyodbc://usuario:contraseña@localhost:1433/warhammer_store?driver=ODBC+Driver+17+for+SQL+Server
```

#### Configurar SQL Server

1. **Crear la base de datos**:
   ```sql
   CREATE DATABASE warhammer_store;
   GO
   ```

2. **Habilitar usuario** (si es necesario):
   ```sql
   CREATE LOGIN warhammer_user WITH PASSWORD = 'tu_password';
   CREATE USER warhammer_user FOR LOGIN warhammer_user;
   ALTER ROLE db_owner ADD MEMBER warhammer_user;
   ```

3. **Instalar driver ODBC** si es necesario:
   - Descargar "ODBC Driver 17 for SQL Server" desde Microsoft

#### Inicializar Base de Datos

```bash
python init_db.py
```

Esto creará:
- Tablas de la base de datos
- Usuario administrador: `admin@warhammer.store` / `admin123`
- Categorías predefinidas
- Productos de ejemplo

#### Ejecutar el Servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en: **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

### 2. Configuración del Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
ng serve --open
```

Aplicación disponible en: **http://localhost:4200**

#### Build de Producción

```bash
ng build --configuration production
```

## Uso de la Aplicación

### Roles de Usuario

1. **Usuario Normal** (cliente)
   - Navegar productos
   - Agregar al carrito
   - Realizar pedidos
   - Ver historial de pedidos

2. **Administrador**
   - Todas las funcionalidades de usuario
   - Acceso a dashboard de analytics
   - Gestionar productos (crear/editar/eliminar)
   - Gestionar pedidos y estados
   - Ver alertas de stock

### Credenciales de Prueba

- **Admin**: `admin@warhammer.store` / `admin123`
- **Cliente**: Registrarse desde la aplicación

## API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuario actual

### Productos
- `GET /api/products/` - Listar productos
- `GET /api/products/{id}` - Detalle de producto
- `POST /api/products/` - Crear producto (admin)
- `PUT /api/products/{id}` - Actualizar producto (admin)
- `DELETE /api/products/{id}` - Eliminar producto (admin)

### Carrito
- `GET /api/cart/` - Ver carrito
- `POST /api/cart/` - Agregar al carrito
- `PUT /api/cart/{id}` - Actualizar cantidad
- `DELETE /api/cart/{id}` - Eliminar item
- `DELETE /api/cart/` - Vaciar carrito

### Pedidos
- `POST /api/orders/` - Crear pedido
- `GET /api/orders/` - Mis pedidos
- `GET /api/orders/{id}` - Detalle de pedido
- `PUT /api/orders/{id}/status` - Actualizar estado (admin)

### Dashboard
- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/dashboard/top-products` - Productos más vendidos
- `GET /api/dashboard/monthly-sales` - Ventas mensuales

## Base de Datos - Schema

### Tablas Principales

- **users** - Usuarios del sistema
- **categories** - Categorías de productos
- **products** - Catálogo de productos
- **cart_items** - Carrito de compras
- **orders** - Pedidos realizados
- **order_items** - Items de cada pedido
- **sales** - Registro de ventas (para analytics)

### Categorías

El sistema incluye categorías predefinidas para Warhammer y 3D prints:

- Warhammer 40K
- Warhammer Age of Sigmar
- Warhammer Space Marines, Orks, Eldar, etc.
- Custom 3D Prints
- 3D Terrain

## Dashboard de Ventas

El dashboard administrativo muestra:

1. **Métricas Clave**
   - Ingresos totales
   - Total de pedidos
   - Productos activos
   - Clientes totales

2. **Productos Más Vendidos**
   - Lista de top 10 productos
   - Cantidad vendida y revenue

3. **Tendencia de Ventas**
   - Gráfico mensual de ventas
   - Número de pedidos por mes

4. **Estado del Inventario**
   - Productos con stock bajo
   - Alertas de reabastecimiento

## Personalización

### Cambiar Tema de Angular Material

Editar `src/styles.css` para cambiar el tema predefinido.

### Configurar Email (Opcional)

Para envío de emails de confirmación, extender backend con configuración SMTP.

### Agregar Pasarela de Pago

Integrar Stripe/PayPal modificando:
- Backend: Agregar endpoint de pago
- Frontend: Página de pago con API del proveedor

## Despliegue en Producción

### Backend

1. **Configurar SQL Server en producción**
2. **Actualizar variables de entorno** en `.env`
3. **Usar Gunicorn** (recomendado):
   ```bash
   pip install gunicorn
   gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. **Configurar Nginx** como proxy reverso
5. **Usar HTTPS** con certificado SSL

### Frontend

```bash
ng build --configuration production
# Los archivos están en dist/warhammer-store/
```

Servir los archivos estáticos con cualquier servidor web (Nginx, Apache, etc.)

## Troubleshooting

### Error de conexión a SQL Server
- Verificar que el driver ODBC esté instalado
- Confirmar que SQL Server esté corriendo
- Revisar credenciales en `.env`

### Error "No module named X"
- Asegurar activación del entorno virtual
- Ejecutar `pip install -r requirements.txt`

### CORS errors en frontend
- Verificar que el backend esté en `http://localhost:8000`
- Revisar configuración CORS en `main.py`

### Angular no compila
- Verificar Node.js version (>= 18)
- Eliminar `node_modules` y reinstalar
- Limpiar cache: `ng cache clean`

## Desarrollo Futuro

- [ ] Pasarela de pago integrada (Stripe/PayPal)
- [ ] Sistema de reseñas y valoraciones
- [ ] Recomendaciones de productos
- [ ] Historial de precios
- [ ] Reportes avanzados
- [ ] API GraphQL
- [ ] Aplicación móvil

## Licencia

Proyecto educativo - U libre.

## Soporte

Para reportar problemas o sugerir mejoras, contactar al equipo de desarrollo.

---

**Store Version**: 1.0.0
**Backend**: FastAPI + SQL Server
**Frontend**: Angular 17 + Material
