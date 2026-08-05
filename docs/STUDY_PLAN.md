# Plan de estudio — Entendiendo Warhammer Store

Objetivo: que puedas explicar de memoria cómo funciona este proyecto de punta a punta — no solo qué hace, sino por qué está armado así. Está pensado en fases progresivas; no pases a la siguiente hasta poder responder las preguntas de autoevaluación de la anterior.

No hace falta hacerlo todo en una sentada. Cada fase está pensada para 1-2 horas.

---

## Fase 0 — Correr el proyecto vos mismo

Antes de leer una sola línea de código, tenés que poder levantarlo y romperlo un poco.

**Hacé esto:**
1. Segui `docs/DOCUMENTATION.md` sección 9 y levantá backend + frontend.
2. Entrá como admin, agregá un producto, cambiale el precio, borralo.
3. Cerrá sesión, intentá entrar a `/admin/products` sin loguearte. ¿Qué pasa?
4. Abrí las DevTools del navegador (F12) → pestaña Network → filtrá por "Fetch/XHR" → hacé login de nuevo y mirá qué requests salen.

**Autoevaluación:**
- ¿Qué URL exacta pega el frontend cuando hacés login?
- ¿Qué pasa cuando entrás a una ruta de admin sin sesión — te bloquea, o carga vacío?

---

## Fase 1 — El panorama general (cliente-servidor)

**Idea central:** hay DOS programas corriendo, en dos puertos distintos, que no se conocen entre sí más que por HTTP.
- `localhost:4200` — Angular, le sirve HTML/CSS/JS a tu navegador. No toca la base de datos directamente, nunca.
- `localhost:8000` — FastAPI, la única cosa en todo el sistema que le habla a la base de datos.

**Leé:**
- `backend/main.py` completo (es corto). Fijate en `app.include_router(...)` — ahí es donde se "enchufan" todos los grupos de endpoints.
- `frontend/src/environments/environment.ts` — ahí está hardcodeado que el frontend le pega a `localhost:8000/api`.

**Autoevaluación:**
- Si apagás el backend pero dejás el frontend prendido, ¿qué se rompe y qué sigue andando?
- ¿Por qué existe CORS (`CORSMiddleware` en `main.py`)? ¿Qué pasaría si no estuviera?

---

## Fase 2 — Los datos: modelos y base de datos

**Leé, en este orden:**
1. `backend/models.py` completo — es la fuente de verdad de qué tablas existen y qué campos tiene cada una.
2. `backend/database.py` — cómo se arma la conexión (`DATABASE_URL` desde `.env`, con fallback a SQLite).
3. `backend/schemas.py` — fijate que hay clases parecidas a las de `models.py` pero **no son lo mismo**.

**La pregunta que tenés que poder responder:** ¿para qué existen `models.py` Y `schemas.py` si ambos describen un "Product"? (Pista: uno es la tabla real en SQL, el otro es el "contrato" de qué forma tiene el JSON que entra/sale de la API — nunca se expone el modelo de base de datos directo, porque si mañana agregás una columna sensible como `hashed_password` no querés que aparezca en una respuesta HTTP por accidente).

**Ejercicio práctico:** agregale un campo nuevo a `Product` (ej. `weight_grams`, un Float). Vas a necesitar tocar 3 archivos como mínimo — ¿cuáles? (Pista: `models.py`, `schemas.py`, y si la tabla ya existe en SQL Server, un `ALTER TABLE` a mano — ver sección 8 de `DOCUMENTATION.md`, punto "create_all() no altera tablas existentes").

---

## Fase 3 — La API: routers, CRUD y autenticación

**Leé:**
1. `backend/routers/products.py` — el router más simple y completo, patrón que se repite en todos los demás.
2. `backend/crud.py` — funciones puras que reciben una sesión de DB y hacen queries. Los routers casi no tienen lógica, solo llaman a estas funciones.
3. `backend/auth.py` completo, dos veces. Es el archivo más importante de todo el backend.

**La pregunta central de esta fase:** seguí el camino completo de un request `POST /api/cart/` con un token inválido. Empezá en `routers/cart.py`, seguí a `Depends(auth.get_current_user)`, entendé qué hace `OAuth2PasswordBearer`, y explicá en tus palabras en qué momento exacto se rechaza el request y con qué código HTTP.

**Autoevaluación:**
- ¿Dónde se firma el JWT? ¿Qué tres datos lleva adentro? (ver `routers/auth.py`, función `login`)
- ¿Por qué `get_current_admin_user` no reimplementa la validación del token, sino que "envuelve" a `get_current_user`?
- En `routers/orders.py`, ¿por qué el orden en que declarás las rutas `/admin` y `/{order_id}` importa? (esto fue un bug real que tuvimos — está documentado en `DOCUMENTATION.md` punto 8.5)

---

## Fase 4 — Frontend: la anatomía de un componente Angular

Angular (en este proyecto, versión "clásica" con NgModules) organiza todo en componentes. Cada uno son 3 archivos que trabajan juntos.

**Leé un componente completo, los 3 archivos:**
- `frontend/src/app/components/product-list/product-list.component.ts` (lógica)
- `...product-list.component.html` (template)
- `...product-list.component.css` (estilos, solo aplican a este componente)

**Después leé:**
- `frontend/src/app/app.module.ts` — la lista maestra de qué componentes/módulos existen en toda la app.
- `frontend/src/app/services/product.service.ts` — cómo un componente le pide datos al backend sin saber nada de HTTP directamente.

**La pregunta central:** ¿por qué el componente no llama a `HttpClient` directamente, sino que pasa por un "service"? ¿Qué ganás con esa capa extra?

**Autoevaluación:**
- ¿Qué es un `Observable` en `product.service.ts` y por qué el componente hace `.subscribe(...)` en vez de simplemente usar el valor de retorno?
- ¿Dónde se define qué componente se muestra en cada URL? (pista: `app-routing.module.ts`)

---

## Fase 5 — Frontend: sesión, guards e interceptors

**Leé:**
1. `frontend/src/app/services/auth.service.ts` completo.
2. `frontend/src/app/guards/admin.guard.ts`.
3. `frontend/src/app/interceptors/auth.interceptor.ts`.
4. `frontend/src/app/app-routing.module.ts` — fijate en `canActivate: [AdminGuard]`.

**La pregunta central:** el JWT vive en `localStorage`. Explicá el camino completo desde que hacés login hasta que el navbar te muestra el link "Dashboard": ¿quién decodifica el token? ¿quién guarda el resultado? ¿quién lo lee para decidir si mostrar el link?

**Autoevaluación:**
- ¿Qué pasa si editás manualmente el `localStorage` en DevTools y le ponés `is_admin: true` a mano? ¿Te deja entrar a `/admin/products`? ¿Te deja **borrar un producto**? (la respuesta a estas dos preguntas es distinta, y ahí está la clave de por qué la seguridad real vive en el backend, no en el frontend — el guard de Angular es solo una mejora de experiencia de usuario, no un candado real).

---

## Fase 6 — Seguir un flujo completo de punta a punta

Elegí **un** flujo y trazalo por todas las capas, escribiendo vos mismo (en un papel o doc aparte) cada paso:

**Flujo sugerido: "agregar un producto al carrito"**
1. Click en botón "Add to Cart" → ¿qué método del componente se dispara? (`product-list.component.ts`)
2. Ese método llama a un service → ¿cuál, y qué URL arma?
3. El interceptor agrega el header `Authorization` → ¿de dónde saca el token?
4. Llega al backend, a qué router/función.
5. Esa función tiene un `Depends(...)` → ¿qué valida antes de dejarte entrar?
6. Se llama a una función de `crud.py` → ¿qué hace exactamente con la sesión de SQLAlchemy?
7. La respuesta vuelve, ¿qué schema de Pydantic la valida antes de salir?
8. El componente recibe la respuesta en el `.subscribe(...)` → ¿qué hace con ella?

Si podés escribir estos 8 pasos sin mirar el código, entendiste la arquitectura.

---

## Fase 7 — El sistema de diseño

Este proyecto tiene un tema visual consistente ("gótico/imperial") armado casi todo desde `frontend/src/styles.css`.

**Leé:**
1. `frontend/src/styles.css` de punta a punta (es largo, pero es el corazón del look del sitio). Prestá atención a las variables `:root` y a las clases reutilizables (`.frosted-panel`, `.frame-corner`, `.reveal`).
2. Elegí un `.svg` de `frontend/src/assets/emblems/` y abrilo en el navegador o en un editor de texto — es solo XML, vas a poder leer la estructura (círculos, gradientes, paths).

**Autoevaluación:**
- ¿Por qué hay reglas CSS que apuntan a clases con el prefijo `mat-mdc-` en vez de `mat-` a secas? (ver `DOCUMENTATION.md` sección 6, "Gotcha de Angular Material 17")
- ¿Qué problema resuelve `.frosted-panel` que un simple `color: gold` no resuelve?

---

## Fase 8 — La feature más compleja: mapa de flota + simulación

Esta es la que más conecta backend y frontend en tiempo real.

**Leé, en este orden:**
1. `backend/models.py` — las clases `Vehicle` y `DeliveryZone`.
2. `backend/crud.py` — función `simulate_vehicle_tick`.
3. `backend/main.py` — la función `_vehicle_simulation_loop` y el `@app.on_event("startup")`.
4. `backend/routers/fleet.py`.
5. `frontend/src/app/services/fleet.service.ts`.
6. `frontend/src/app/components/fleet-map/fleet-map.component.ts` — el más largo de todos, tomate tu tiempo.

**La pregunta central:** el mapa no usa websockets ni nada "en tiempo real" de verdad — usa **polling** (pedir cada 3 segundos). Explicá por qué eso alcanza para este caso, y en qué situación dejaría de alcanzar (pista: pensá en cuántos usuarios mirando el mapa a la vez, y cuánto tráfico HTTP genera cada uno).

**Ejercicio práctico:** agregá un cuarto vehículo a la base y confirmá que aparece solo en el mapa la próxima vez que refresque, sin tocar el componente Angular. Si lo lograste, entendiste que el frontend no tiene "hardcodeado" nada de la flota — todo sale de la base.

---

## Fase 9 — Ejercicios de cierre

Si llegaste hasta acá y pudiste responder todo, ya podés defender este proyecto en una entrevista o explicárselo a otro dev. Como cierre, probá:

1. **Agregar un endpoint nuevo**: `GET /api/products/featured` que devuelva los 3 productos con más stock. Vas a tocar `crud.py`, `routers/products.py`, y opcionalmente un método nuevo en `product.service.ts`.
2. **Agregar una columna calculada**: mostrar "% de margen" (`(price - cost_price) / price`) en la tabla de admin de productos — esto es 100% frontend, sin tocar el backend (el dato ya viaja en la respuesta).
3. **Romper algo a propósito** y arreglarlo: comentá la línea que arma el header `Authorization` en `auth.interceptor.ts`, mirá qué se rompe, y explicá por qué justo eso y no otra cosa.

---

## Referencia rápida — mapa mental del proyecto

```
Navegador (Angular, :4200)
   │  HTTP + JWT en header Authorization
   ▼
FastAPI (:8000)
   │  Depends(get_current_user / get_current_admin_user)
   ▼
crud.py (funciones con SQLAlchemy Session)
   │
   ▼
SQL Server "trasin" (host desde DATABASE_URL)
```

Todo lo que ves en pantalla sale de ese camino. No hay datos hardcodeados en el frontend excepto las imágenes SVG de los emblemas (que son arte, no datos de negocio).
