# Prompt de replicación — Warhammer Store

Copiá y pegá el bloque de abajo completo a un asistente de IA (Claude Code, etc.) en un directorio vacío para reconstruir este proyecto desde cero. Está escrito para minimizar los errores que sí cometimos la primera vez (ver notas al final de cada bloque).

---

```
Quiero construir una tienda e-commerce de portfolio, temática Warhammer (miniaturas + impresión 3D custom), full-stack, con panel de administración y un módulo de logística con mapa.

STACK
- Backend: FastAPI + SQLAlchemy ORM + JWT (python-jose, passlib/bcrypt). Base de datos vía DATABASE_URL en .env, con fallback automático a SQLite local (sqlite:///./warhammer_store.db) si no está seteada — así puedo desarrollar sin depender de un servidor SQL Server externo.
- Frontend: Angular 17, arquitectura NgModule clásica (no standalone components), Angular Material 17 (MDC-based).
- Sin frameworks CSS externos (nada de Tailwind): CSS plano con variables custom.

MODELO DE DATOS (SQLAlchemy)
- users: email, hashed_password, full_name, is_admin
- categories: name, description, parent_id (auto-referencial)
- products: name, description, price, cost_price, sku (unique), stock_quantity, min_stock_level, category_id, manufacturer, material, scale, is_3d_print, print_time_hours, resin_type, image_urls (JSON list de strings), is_active
- cart_items: user_id, product_id, quantity
- orders: user_id, total_amount, status (enum pending/processing/shipped/delivered/cancelled), shipping_address (JSON), payment_method, tracking_number, notes, zone_id (FK a delivery_zones), shipping_cost
- order_items: order_id, product_id, quantity, unit_price, total_price
- sales: product_id, order_id, quantity, unit_price, total_amount, month_year (para reportes)
- delivery_zones: name, description, center_lat, center_lng, radius_km, shipping_cost, color
- vehicles: name, plate, driver_name, status (idle/delivering/returning), lat, lng, heading_lat, heading_lng

AUTENTICACIÓN — presta atención acá, es donde más nos equivocamos la primera vez:
- El JWT firmado en /auth/login DEBE incluir en el payload: sub (email), user_id, is_admin. Si el token no lleva is_admin, el frontend nunca podrá saber si el usuario es administrador (nos pasó: login "funcionaba" pero el navbar nunca mostraba las opciones de admin).
- La dependencia get_current_user del backend debe usar fastapi.security.OAuth2PasswordBearer para extraer el token del header Authorization — NO uses un Depends(lambda: None) ni nada que no lea el header real (error real que cometimos: eso hace que TODAS las rutas protegidas fallen siempre con 401/500).
- get_current_admin_user reutiliza get_current_user y exige is_admin=True. Se usa en: crear/editar/borrar producto, dashboard stats, listar todas las órdenes, listar vehículos de flota.
- En rutas con paths dinámicos tipo /orders/{order_id} y /orders/admin: declará SIEMPRE las rutas literales (/admin) ANTES que las rutas con parámetro ({order_id}) en el mismo router. FastAPI matchea en orden de declaración — si {order_id} va primero, una request a /admin la intenta parsear como order_id="admin" y explota con 422.

FRONTEND — AUTENTICACIÓN Y GUARDS
- AuthService decodifica el JWT client-side (atob del payload) para exponer isLoggedIn() e isAdmin() vía BehaviorSubject<User|null>.
- Crear un AdminGuard (CanActivate) que valida isLoggedIn() && isAdmin(), redirige a /home si falla. Aplicarlo a TODAS las rutas de administración (/dashboard, /admin/orders, /admin/products, /admin/fleet). Sin esto, cualquiera accede a esas vistas escribiendo la URL directo aunque el backend bloquee las mutaciones — la pantalla carga vacía/rota igual, mala UX y hueco de seguridad.
- Un interceptor HTTP (auth.interceptor.ts) agrega "Authorization: Bearer <token>" a cada request saliente.

RUTAS FRONTEND
/home /products /products/:id /cart /checkout /login /register (públicas)
/dashboard /admin/orders /admin/products /admin/fleet (con AdminGuard)

FEATURES CLIENTE
- Catálogo con filtro por categoría, búsqueda, paginación.
- Detalle de producto con galería, selector de cantidad, agregar a carrito.
- Carrito: tabla con cantidad editable, subtotal, ir a checkout.
- Checkout: formulario de envío + selector de ZONA DE ENVÍO (fetch a /api/fleet/zones, público) que suma un costo fijo por zona al total. Al confirmar, crea la orden con zone_id.

FEATURES ADMIN
- Dashboard: revenue, órdenes, productos activos, clientes, stock bajo, top productos, ventas mensuales.
- Gestión de productos: tabla + dialog de formulario (crear/editar) con TODOS los atributos del modelo (precio, costo, SKU, stock, categoría, imagen, atributos de impresión 3D en una sección "Advanced Options" colapsable). Borrar con confirmación.
- Gestión de órdenes: tabla con cambio de estado.
- Mapa de flota (/admin/fleet): usar Leaflet (librería gratis, sin API key) + tiles oscuros de CartoDB (https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png). Dibujar cada delivery_zone como círculo (radio en metros = radius_km * 1000) con su color y popup mostrando nombre + costo. Vehículos como markers con divIcon custom (no el ícono default de Leaflet, para evitar el bug clásico de paths de imagen rotos con bundlers). Polling cada 3 segundos a GET /api/fleet/vehicles para mover los markers (setLatLng), sin recrear el mapa.
- Simulación de movimiento: en el backend, una tarea asyncio lanzada en el evento startup de FastAPI, corre cada 3s, mueve cada vehículo con un "random walk con inercia" (mantiene una dirección heading_lat/heading_lng y ocasionalmente la cambia) para que se vea como movimiento real, no saltos aleatorios. Diseñar esto para que sea trivial de reemplazar por GPS real después (un endpoint que reciba lat/lng de un dispositivo y actualice la misma tabla vehicles).

DISEÑO VISUAL — "gótico/imperial 40K", NO genérico
- Paleta (variables CSS en :root): --primary-color:#8b0000 (rojo sangre), --gold-color:#d4af37 (oro), --dark-bg:#1a1a2e (navy oscuro), --card-bg:rgba(26,26,46,0.85), texto claro sobre fondo oscuro siempre.
- Tipografía: 'Cinzel' (Google Fonts, serif gótica/imperial) para TODOS los títulos/headers; Roboto para texto de cuerpo.
- Fondo de página: una imagen de ilustración temática fija (background-attachment:fixed) con un overlay oscuro encima (body::before, background rgba(15,15,26,0.8) aprox — necesita ser bastante oscuro, 0.6 de opacidad no alcanza para que el texto se lea bien sobre zonas claras de la imagen).
- Cualquier texto/título que NO esté ya dentro de una card con fondo propio necesita un "frosted panel": fondo oscuro semitransparente + backdrop-filter:blur(10px) + borde dorado sutil. Aplicar esto a headers de página sueltos, estados vacíos, etc. — si no, quedan ilegibles sobre la imagen de fondo.
- Esquinas doradas estilo HUD/relicario (4 divs absolutos en las esquinas, con border-left+border-top o combinaciones, sin border-radius en el borde que conecta) en cards de producto al hacer hover, y en cards de login/register siempre.
- Animaciones: fadeInUp para entrada de cards (stagger con animation-delay incremental), glow pulsante en títulos importantes, partículas ("ascuas") subiendo en el hero, barrido de brillo (shine) al pasar el mouse por botones primarios.
- Emblemas de producto: en vez de fotos de stock, diseñar un emblema SVG propio por facción (space marines/orks/eldar/chaos/tau/imperial guard/necrons/terreno/impresión 3D custom), estilo insignia circular con anillo ornamentado, ícono central geométrico, paleta de color propia por facción, nombre de la unidad/facción en Cinzel abajo. Guardarlos como archivos .svg estáticos en el frontend (src/assets/emblems/), NO como binarios en la base de datos — la base solo guarda el path.
- Botón de contacto (WhatsApp u otro) flotante: debe recolorearse acorde al tema (rojo/dorado), NUNCA dejar el verde default de WhatsApp, rompe la estética.

MATERIAL 17 — GOTCHA IMPORTANTE
Angular Material 17+ usa componentes MDC por default. El DOM real usa clases mat-mdc-* (mat-mdc-card, mat-mdc-form-field, mat-mdc-table, mat-mdc-dialog-container, etc.), NO las clases legacy sin el prefijo mdc (mat-card, mat-form-field-outline). Cualquier CSS de tema global tiene que apuntar a las clases mat-mdc-* reales — verificalo inspeccionando el DOM en el navegador antes de asumir el nombre de una clase, si no las reglas de tema simplemente no aplican y quedan pantallas con fondo blanco/texto invisible sobre fondo oscuro.

NOTIFICACIONES
No uses alert()/confirm() nativos del navegador en ninguna parte — se ven completamente fuera de tema. Crear un NotificationService que envuelva MatSnackBar con panelClass propio (fondo oscuro, borde dorado/rojo según sea éxito/error).

CATEGORÍAS DE PRODUCTO (seed inicial)
Warhammer 40K, Warhammer Age of Sigmar, Warhammer Space Marines, Warhammer Orks, Warhammer Eldar, Warhammer Tyranids, Warhammer Necrons, Warhammer Chaos, Warhammer Tau, Warhammer Imperial Guard, Custom 3D Prints, 3D Terrain.

ZONAS DE ENVÍO SEED (ejemplo Santiago, Chile — ajustar a tu ciudad real)
4 zonas circulares con centro/radio real de la ciudad, cada una con una tarifa fija distinta y un color distinto para el mapa.

Empezá por el backend (modelos → schemas → CRUD → routers → seed script), después el frontend (módulo + routing + servicios + guards), y dejá el rediseño visual gótico y el mapa de flota para el final una vez que el CRUD básico funcione end-to-end.
```

---

### Notas de uso

- Reemplazá la sección "ZONAS DE ENVÍO" con la ciudad real donde vas a operar.
- Si el asistente te pregunta por el proveedor de mapas, la respuesta es **Leaflet + tiles de CartoDB** (gratis, sin API key) — no Google Maps (requiere billing).
- Pedí explícitamente que verifique con Playwright (o el navegador) que el login realmente refleja `is_admin` en el navbar antes de dar por cerrado el tema de autenticación — es el bug que más tiempo nos tomó detectar porque el login "parecía" funcionar.
