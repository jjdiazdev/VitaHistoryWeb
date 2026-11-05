# Auditoría UI/UX — VitaHistory

- **Fecha:** 2026-11-05
- **Alcance:** interfaz completa (vistas públicas, vistas autenticadas y páginas de error) en móvil, tablet y escritorio.
- **Rama auditada:** `main` (commit `00448c2`).
- **Tipo de entrega:** solo diagnóstico. No se modificó código, CSS ni plantillas.

---

## 1. Resumen ejecutivo

La aplicación tiene una identidad visual reconocible (verde/azul, tarjetas redondeadas, imágenes hero) y funciona razonablemente en **móvil (375 px)** y **escritorio (≥1440 px)**. Los problemas principales son de estructura y se repiten en todos los módulos:

| # | Hallazgo | Severidad |
|---|---|---|
| 1 | **Interfaz en dos idiomas.** Hay más de 40 textos visibles en inglés (mensajes flash, errores de formulario, títulos de pestaña y valores por defecto como "Specialty" o "Uncategorized") mezclados con una interfaz en español. El inventario completo está en el §7. | 🔴 Alta |
| 2 | **Tablet roto (720–1100 px).** Hay un solo breakpoint (`720px`) que pasa directamente a anchos fijos de escritorio (imágenes de 584–638 px, padding de 120 px). En 768 px el **formulario de login queda cortado fuera de pantalla** y el logo y los textos de la home se desbordan. | 🔴 Alta |
| 3 | **Accesibilidad básica ausente:** zoom deshabilitado (`user-scalable=no`), sin `lang`, sin `alt` en imágenes, `outline: none` en los inputs sin estilo de foco alternativo, menú móvil inaccesible por teclado y enlaces de iconos sin nombre accesible. | 🔴 Alta |
| 4 | **HTML inválido sistemático:** `<a>` dentro de `<button>` en todos los CTA y el bloque `header` renderizado **fuera de `<body>`**. | 🟠 Media |
| 5 | **Duplicación de componentes:** la cabecera de perfil se repite en 9 plantillas y los botones están duplicados en el DOM (`-btn-one` / `-btn-two`) para móvil y escritorio. Todo el CSS vive en un `main.css` de 1922 líneas, más estilos inline en `base.html`. | 🟠 Media |

> **Nota sobre las vistas simuladas:** durante la auditoría no fue posible crear pacientes por un error de base de datos en el campo de teléfono. Está documentado al final, en el §10, porque no es un problema de interfaz. Por eso los listados de pacientes e historias se auditaron **inyectando el markup exacto de sus plantillas** sobre las páginas reales (mismo CSS y mismas fuentes). Los hallazgos de esas vistas están marcados como *(simulado)*.

---

## 2. Metodología

- **Navegador:** Chrome (extensión Claude in Chrome) contra `http://127.0.0.1:5500`.
- **Viewports:** móvil **375×780**, tablet **768×780** y escritorio **1440×900**, renderizados en iframes de tamaño exacto. El gestor de ventanas no permitía redimensionar la ventana real.
- **Medición automática en cada vista:** desbordamiento horizontal (`scrollWidth` frente a `innerWidth` y elementos que salen del viewport), objetivos táctiles menores de 44×44 px, imágenes sin `alt` y mensajes flash.
- **Revisión estática:** las 22 plantillas Jinja, `base.html`, `snippets/*`, `main.css` y las rutas de los blueprints.
- **Contraste:** cálculo WCAG 2.1 sobre los pares de colores del CSS.
- **Usuario:** cuenta de prueba facilitada por el equipo. Las credenciales no se incluyen en este informe.

### Vistas auditadas

| Módulo | Ruta | Plantilla | Estado |
|---|---|---|---|
| Landing | `/index/home` | `index/home.html` | En vivo |
| Auth | `/auth/login` | `auth/login.html` | En vivo |
| Auth | `/auth/register` | `auth/register.html` | En vivo |
| Auth | `/auth/reset_request` | `auth/reset_request.html` | En vivo |
| Auth | `/auth/reset_final/<token>` | `auth/reset_final.html` | Estático |
| Dashboard | `/index/start` | `index/start.html` | En vivo |
| Cuenta | `/index/account` | `index/account.html` | En vivo |
| Pacientes | `/person/persons` | `person/persons.html` | En vivo (vacío) + simulado (poblado) |
| Pacientes | `/person/create` | `person/create_person.html` | En vivo |
| Pacientes | `/person/edit_person/<id>` | `person/edit_person.html` | Estático (requiere un paciente) |
| Pacientes | `/person/delete/<id>` | `person/delete_person.html` | Estático |
| Categorías | `/person/show/categories` | `person/show_categories.html` | En vivo |
| Categorías | `/person/create/category` | `person/create_category.html` | En vivo |
| Categorías | `/person/delete/category/<id>` | `person/delete_category.html` | En vivo (sin confirmar) |
| Historias | `/history/histories/<id>` | `history/show_histories.html` | Simulado |
| Historias | create / edit / delete | `history/*.html` | Estático |
| Errores | 404 / 403 / 500 | `error/*.html` | 404 en vivo; el resto estático |

---

## 3. Hallazgos globales

### 3.1 Documento base (`templates/base.html`)

| Sev. | Ubicación | Problema | Recomendación |
|---|---|---|---|
| 🔴 | `base.html:13` | `maximum-scale=1.0, user-scalable=no` **impide hacer zoom** en móvil (WCAG 1.4.4). Es especialmente grave en una app de salud con usuarios de cualquier edad. | Usar `<meta name="viewport" content="width=device-width, initial-scale=1">`. |
| 🔴 | `base.html:2` | `<html>` sin `lang`. Los lectores de pantalla leen el español con la fonética por defecto. | `<html lang="es">`. |
| 🟠 | `base.html:108` | `{% block header %}` está **entre `</head>` y `<body>`**. El navbar queda fuera del body (HTML inválido) y el navegador lo recoloca. | Mover el bloque dentro de `<body>`. |
| 🟠 | `base.html:3-13` | Falta `<meta charset="utf-8">`. Además, el `<meta viewport>` va después de 3 hojas de estilo. | Poner `charset` y `viewport` como primeras etiquetas del `<head>`. |
| 🟠 | `base.html:15-103` | 90 líneas de CSS inline repetidas en **cada página**, y no se cachean. Solo hacen falta por las URLs de `url_for()`. | Mover las reglas a CSS con rutas relativas (`url('../image/…')`) o con variables CSS que se inyecten una vez (ver §6). |
| 🟡 | `base.html:9` | Se cargan 3 familias de Google Fonts (EB Garamond, Inter e Istok Web). **EB Garamond no se usa** en `main.css`. | Quitar EB Garamond y limitar los pesos de Inter (ahora pide el rango 100–900 en itálica y normal). |
| 🟡 | `base.html:11` | Font Awesome 5.15.3 completo (unos 60 KB de CSS y las webfonts) para 6 iconos. | Usar SVG inline o un subset. |

### 3.2 Navbar (`snippets/navbar.html`, `main.css:35-142`, `342-411`)

| Sev. | Ubicación | Problema | Recomendación |
|---|---|---|---|
| 🔴 | `navbar.html:122-126` | El menú móvil usa el "checkbox hack" con `#check { display:none }`. **No se puede abrir con teclado** y no expone estado (`aria-expanded`). | Usar un `<button aria-controls aria-expanded>` con unas líneas de JS, o mantener el checkbox visualmente oculto (`.sr-only`) en lugar de `display:none`. |
| 🟠 | `main.css:60-77` | El menú cerrado se esconde con `position:absolute; right:-100vw`. Sigue en el layout y genera **desbordamiento horizontal**: en 375 px, `scrollWidth` es de 735 px. Lo tapa `overflow-x:hidden` en `body`, que no es fiable en iOS Safari. | Usar `transform: translateX(100%)` más `visibility:hidden`, o `display:none` cuando está cerrado. |
| 🟠 | `navbar.html:120` | El logo no tiene `alt` ni enlace a inicio. | `<a href="…home"><img alt="VitaHistory – inicio"></a>`. |
| 🟡 | captura móvil | Con el menú abierto, el overlay tapa el logo y solo queda un botón negro "X" de 60 px que no encaja con la paleta. | Mantener el logo visible y usar un icono de cierre en el color de marca. |
| 🟡 | `main.css:91-101` vs `382-396` | El navbar móvil usa *Istok Web* a 2rem y el de escritorio *Inter* a 1rem: cambia la tipografía según el breakpoint. | Unificar la familia tipográfica del navbar. |
| 🟡 | — | No se indica la página activa (`aria-current="page"`). | Añadir una clase o atributo de estado activo. |

### 3.3 Tipografía, color y contraste

| Sev. | Par de colores | Contraste | Uso | Veredicto |
|---|---|---|---|---|
| 🟠 | `#1D884D` sobre `#EBEBEB` | **3.76:1** | Enlaces del navbar, paginación, "Volver a inicio" | ❌ No cumple AA en texto normal (4.5:1) |
| 🟠 | `#FFFFFF` sobre `#26A0DA` | **2.95:1** | Parte inferior del degradado de `.global-btn` | ❌ La mitad inferior del texto del botón no cumple |
| 🟠 | `#FF0000` sobre `#FCEDED` | **3.52:1** | Botón "Eliminar" (`.cancel-btn`) | ❌ |
| ✅ | `#32CB1E` sobre `#00394A` | 5.76:1 | `.special-text` en la home | OK |
| ✅ | `#4A4A4A` sobre `#EBEBEB` | 7.43:1 | Texto de los inputs | OK |

Otros puntos:
- 🟡 Hay 20 colores hex distintos sin variables. `#EBEBEB` aparece 16 veces, `#1D884D` 13, `#C9C9C9` 11 y `#1B1B1B` 11. Conviene definir *design tokens* en `:root` (ver §6).
- 🟡 Las clases tienen nombres con errores o en dos idiomas: `secundary-title`, `hided-message`, `relleno`, `last_visit` (snake_case mezclado con kebab-case).
- 🟡 Los tamaños de fuente están en `rem` (bien), pero alturas y anchos están en `px` fijos (96 declaraciones `width/height: Npx`). Esa es la causa raíz de los problemas en tablet.

### 3.4 Accesibilidad transversal

| Sev. | Ubicación | Problema |
|---|---|---|
| 🔴 | `main.css:606`, `main.css:1668` | `outline: none` en `form input, form select` y en el textarea, **sin `:focus` alternativo**. En todo el CSS no hay ni un solo `:focus` o `:focus-visible`. |
| 🔴 | todas las plantillas | Ninguna `<img>` tiene `alt`. En la home hay 5 imágenes, 5 sin alt. |
| 🔴 | `persons.html:42-44`, `show_histories.html:50-51`, `show_categories.html:37` | Los enlaces de solo icono (ver, editar, eliminar) no tienen texto ni `aria-label`. Un lector de pantalla los anuncia como "enlace" vacío. |
| 🟠 | `home.html:27,50,60`, `persons.html:12,25` y todos los `.simple-btn` | `<button><a href>…</a></button>`: contenido interactivo anidado (HTML inválido). La zona clicable es solo el `<a>`, no el botón entero, y el foco de teclado pasa dos veces por el mismo control. | 
| 🟠 | `create_history.html:45,54`, `create_category.html:31` | `<select>`, `<textarea>` y el input de categoría **sin `<label>`**. Solo hay un placeholder o nada. |
| 🟠 | — | Objetivos táctiles por debajo de 44×44 px: iconos de acción de 18–23 × 24 px, paginación de **8×34 px**, botón "Eliminar" de 292×**22** px, link del footer de 85×17 px. |
| 🟡 | `home.html:16,59`; `persons.html:34` | Jerarquía de headings incoherente: dos `<h1>` en la home y un `<h1>` por cada tarjeta de paciente o historia. |

### 3.5 Contenido, idioma y microcopy

| Sev. | Problema | Ejemplos |
|---|---|---|
| 🔴 | **Textos en inglés en una interfaz en español** (flashes, errores, `<title>`, valores por defecto). | Ver el inventario completo y la traducción propuesta en el **§7**. |
| 🟡 | Ortografía: faltan signos de apertura y tildes. | `home.html:26` "Todavía no tienes…?" → "¿…?"; `:27` "Registrate" → "Regístrate"; `:28` "ES GRATIS!" → "¡ES GRATIS!"; `:59` "Que esperas" → "¿Qué esperas…?"; `login.html:38` "Nuevo usuario?" → "¿Nuevo usuario?"; `person/__init__.py:217` "digitos" → "dígitos". |
| 🟡 | `capitalize()` pasa a minúsculas el resto del nombre de la categoría. | Al introducir "[UI-AUDIT] Control" se guardó "[ui-audit] control". "VIH" se guardaría como "Vih" (`person/__init__.py:138`). |

---

## 4. Hallazgos por módulo

### 4.1 Landing — `/index/home`

| Sev. | Viewport | Ubicación | Problema | Recomendación |
|---|---|---|---|---|
| 🔴 | Tablet | `main.css:413-419`, `457-460` | A ≥720 px el título pasa a `6rem` y la imagen hero a 584 px fijos. En 768 px **el logo y "VitaHistory" se cortan** (el contenido llega a 921 px). | Usar `clamp()` en el título (`font-size: clamp(3rem, 8vw, 6rem)`), `max-width:100%; height:auto` en las imágenes y un breakpoint intermedio a 1024 px para el layout en fila. |
| 🔴 | Tablet | `main.css:495-498` | Hero 3: imagen de 638 px fijos y texto en fila. En 768 px **el texto queda cortado por la derecha** ("VitaHisto…", "profesiona…"). | Igual que el anterior: apilar en columna hasta unos 1024 px. |
| 🟠 | Tablet | hero-five | El botón "Registrarse hoy" se comprime y parte su texto en dos líneas dentro del botón. | `white-space:nowrap` y `flex-shrink:0` en el CTA, o apilar. |
| 🟠 | Móvil | `main.css:224-229`, `297-302` | Las imágenes de hero 2 y hero 4 se "ocultan" moviéndolas a `right:-100vw` con 20×20 px. **Se descargan igual** y añaden desbordamiento horizontal. | `display:none` en móvil, o mejor `<picture>`/`srcset` con `media`. |
| 🟠 | Móvil | `main.css:186-194`, `221`, `278`, `332` | Cada sección mide `100vh` o `calc(100vh - 120px)`. En móvil `100vh` no descuenta la barra del navegador, así que el contenido queda bajo el pliegue y aparecen grandes bloques vacíos (hero 2 en negro con mucho espacio). | Usar `min-height: 100svh` (o `dvh`) y dejar que el contenido defina la altura. |
| 🟡 | Todos | `home.html:50` | Botón "Nuestros servicios" con `display-none` y `href="#"`: es código muerto. | Eliminarlo o implementarlo. |
| 🟡 | Todos | `home.html:68` | El enlace de autor apunta a `#`. | Enlazar a un perfil real o quitar el enlace. |
| 🟡 | Escritorio | hero-four | Gran espacio vacío entre la tarjeta de texto y la imagen vertical, y una franja de la imagen de fondo de hero-five asoma por debajo. | Revisar alturas y alinear con un `gap`. |

### 4.2 Autenticación — login, registro y reset

| Sev. | Viewport | Ubicación | Problema | Recomendación |
|---|---|---|---|---|
| 🔴 | **Tablet** | `main.css:719-744` | `.container-login-logo` con `padding: 0 120px` y logo de 478 px: **el formulario de login queda fuera de la pantalla** (llega a 985 px en un viewport de 768). El usuario no puede iniciar sesión sin hacer scroll horizontal. | Quitar el padding fijo, usar `gap` y apilar logo y formulario por debajo de unos 1024 px. |
| 🟠 | Móvil | `login.html:10,38,43` | El CTA de registro aparece **3 veces** con textos distintos ("Registrarse gratis", "Crear una cuenta" y el párrafo inferior). | Dejar uno solo. |
| 🟠 | Todos | `login.html`, `register.html` vs `reset_request.html` | Login y registro no tienen navbar (usan `.link-header` propio), pero reset sí. Es una navegación incoherente dentro del mismo flujo de autenticación. | Elegir un patrón (recomendado: layout "auth" sin navbar, con logo y "Volver") y aplicarlo a las 4 vistas. |
| 🟠 | Móvil | `main.css:811-824` | Registro: `.left-field/.right-field` con `width: 36vw` y `.mid-field` con `60vw`. Los inputs Nombre y Apellido **se tocan sin separación**. "Repetir contraseña" queda más estrecho que el resto y desalineado. | Usar CSS Grid: `grid-template-columns: 1fr 1fr; gap: 12px`. |
| 🟠 | Todos | `register.html:43,57`, `main.css:841-870` | Los tooltips "?" son `<span>` que solo responden a `:hover`/`:active`. **No son accesibles por teclado** y en táctil son poco fiables. El tooltip tiene `position:absolute; right:80px` sin un contenedor `relative`. | Mostrar la ayuda como texto fijo bajo el campo (`aria-describedby`); es más útil para los requisitos de contraseña. |
| 🟡 | Todos | `register.html:68` | `<select … type="text">` (atributo inválido). El género solo ofrece dos opciones, sin "Prefiero no decirlo". | Quitar `type` y revisar si el dato es necesario. |
| 🟡 | Todos | login | Falta el botón para mostrar u ocultar la contraseña, y `autocomplete="username"` / `current-password`. | Añadirlos. |
| 🟡 | Escritorio | login | Los textos de 0.875rem (14 px) en el formulario se ven pequeños en pantallas grandes. | 1rem mínimo. |

### 4.3 Dashboard — `/index/start`

| Sev. | Viewport | Problema | Recomendación |
|---|---|---|---|
| 🟠 | Tablet | Las 3 tarjetas (356 px fijos, `main.css:931-935`) se comprimen en fila y el texto queda pegado al borde izquierdo, sin padding ("Pacientes registrados" parte palabras al borde). | `padding` interno en `.menu-image a` y grid `repeat(auto-fit, minmax(220px,1fr))`. |
| 🟠 | Todos | "Citas pendientes" y "Pagos por cuotas" llevan a `/start/development` y solo muestran el flash "Módulo en proceso de desarrollo". Parecen funcionales y no lo son. | Marcarlas visualmente como "Próximamente" (badge, opacidad) o no enlazarlas. |
| 🟡 | Móvil | La tercera tarjeta queda cortada bajo el pliegue y no hay indicador de scroll. | Reducir la altura de las tarjetas en móvil. |
| 🟡 | Todos | `.menu-image a:active { font-size:1.5rem }` provoca un salto del layout al pulsar. `.menu-image:hover { bottom:10px }` mueve la caja con `position` en lugar de `transform`. | Usar `transform: translateY(-4px)` y `scale` para el feedback. |

### 4.4 Cuenta — `/index/account`

| Sev. | Viewport | Problema | Recomendación |
|---|---|---|---|
| 🟠 | Móvil | Los inputs Nombre y Apellido se tocan sin gap. Los botones "Subir foto" y "Actualizar" están **pegados** y tienen alturas distintas. | Grid con `gap` y altura común para los botones. |
| 🟠 | Todos | "Subir foto" es un `<input type=file>` con `opacity:0` encima de un `<div>` (`main.css:1021-1048`). No hay foco visible ni feedback del archivo elegido ni preview. | `<label for="picture" class="btn">` más el input con `.sr-only`, y mostrar nombre o preview. |
| 🟡 | Todos | "Nombre de usuario" usa `.mid-field` y queda más estrecho que los demás campos sin motivo. | Ancho uniforme. |
| 🟡 | Todos | No hay forma de cambiar el email ni la contraseña desde la cuenta. | Evaluar si se añade una sección de seguridad. |

### 4.5 Pacientes — listado, crear, editar y eliminar

| Sev. | Viewport | Ubicación | Problema | Recomendación |
|---|---|---|---|---|
| 🟠 | Móvil *(simulado)* | `main.css:1169-1173` | `.person-container { height:110px }` fijo. Con nombres largos ("María Fernanda Rodríguez de los Santos") **el texto se sale de la tarjeta** y se solapa con la siguiente. | `min-height` en lugar de `height`. |
| 🟠 | Todos *(simulado)* | `main.css:1253-1261` | Paginación: `.pag-btn { padding:5px 0 }` sin padding horizontal. El número activo queda en un **rectángulo de 8 px de ancho**, casi ilegible. Los "…" son texto suelto. No hay botones anterior y siguiente. | `min-width:40px; padding:8px 12px; text-align:center`, más `aria-current="page"` y anterior/siguiente. |
| 🟠 | Todos | `person/__init__.py:31` | `per_page=3`: con 30 pacientes salen 10 páginas. Tampoco hay buscador ni filtro por categoría. | 10–20 por página y un buscador por nombre. |
| 🟠 | Todos | `persons.html:28-50` | **No hay estado vacío.** Con 0 pacientes solo se ve la cabecera, sin mensaje ni CTA central. | `{% else %}` en el `for` con un mensaje y el botón "Crear primer paciente". |
| 🟠 | Móvil | `create_person.html:42`, `:60` | Los selects de prefijo y categoría quedan **truncados** ("041", "Sin categor"). | Ancho mínimo, o el prefijo dentro del mismo campo (`input-group`). |
| 🟠 | Todos | `create_person.html:52`, `edit_person.html:49` | Teléfono con `type="number"`: muestra flechas de incremento, no acepta guiones aunque el placeholder sugiere "000-0000" y puede quitar ceros a la izquierda. `create_person.html:42` tiene `<select type="number">` (inválido). | `type="tel" inputmode="numeric" pattern="[0-9]{7}"`. |
| 🟡 | Todos | `edit_person.html:55-59` | La categoría actual se añade como una `<option>` más al final: **sale duplicada** en el desplegable. | Marcar `selected` dentro del bucle. |
| 🟠 | Todos | `delete_person.html:29-38` | La pantalla de confirmación de borrado no tiene **"Cancelar"**, no explica que el borrado es irreversible ni si borra las historias asociadas, y el botón mide 22 px de alto. | Diálogo de confirmación con texto de consecuencias, "Cancelar" como acción secundaria y "Eliminar" con altura ≥44 px. |
| 🟡 | Todos | `persons.html:12,25` | Los botones "Crear nuevo" están duplicados en el DOM (uno para móvil y otro para escritorio) y se alternan con `display:none`. Pasa en 8 plantillas. | Un solo botón reubicado con CSS (grid areas u `order`). |
| 🟡 | Todos | `persons.html:36` | "Última visita: 05/11" sin año. En realidad es la fecha de alta (`date_in`), no de la última visita. | Corregir la etiqueta o el dato e incluir el año. |

### 4.6 Categorías

| Sev. | Problema | Recomendación |
|---|---|---|
| 🟠 | La cabecera muestra "Nro. de pacientes" dentro de la gestión de categorías, sin contexto. | Mostrar el número de categorías o el número de pacientes por categoría. |
| 🟠 | En `create_category.html` el input no tiene label y el CTA "Crear categoría" aparece **dos veces** (botón superior y botón del formulario). En escritorio el input y el botón quedan separados por un hueco grande. | Un solo CTA junto al input, con su `<label>`. |
| 🟠 | El borrado no avisa de que los pacientes de esa categoría pasarán a "Uncategorized", no tiene "Cancelar" y el botón "Eliminar" mide 22 px. | Igual que en el borrado de pacientes. |
| 🟡 | En tablet el nombre de la categoría se muestra como `<h1>` gigante; en móvil es pequeño. | Tamaño coherente (`h2`/`h3`, unos 1.25rem). |
| 🟡 | No hay estado vacío ni opción de renombrar. | Añadir ambos. |

### 4.7 Historias *(simulado)*

| Sev. | Problema | Recomendación |
|---|---|---|
| 🟠 | La vista muestra **dos bloques de perfil seguidos**: el del profesional (cabecera genérica) y el del paciente. El que importa (el paciente) queda en segundo plano. | En vistas de paciente, quitar la cabecera del profesional y hacer del paciente el encabezado principal. |
| 🟠 | `create_history.html:45,54`: el select de tipo y el textarea no tienen label. El textarea usa `onInput` inline. | Labels visibles y JS fuera de la plantilla, o `field-sizing: content` en CSS cuando el soporte lo permita. |
| 🟡 | El contenido largo de la historia se muestra completo. Con muchas historias la página se hace muy larga, sin orden ni filtros por tipo (Diagnóstico, Tratamiento…). | Truncar con "ver más" y añadir filtros y orden por fecha. |
| 🟡 | El borrado se confirma con un flash "Are you sure…?" en inglés, de tipo warning, en lugar de una UI de confirmación. | Confirmación consistente con la de pacientes. |

### 4.8 Páginas de error

| Sev. | Problema | Recomendación |
|---|---|---|
| 🟠 | `static/image/404-error-bk.webp` **muestra "400' Not Found"**, no 404. | Reemplazar la ilustración. |
| 🟡 | El texto queda encima de la ilustración y no hay CTA ("Volver al inicio"). | Añadir un botón de vuelta. |
| 🟡 | Durante la auditoría, un error 500 mostró el **depurador de Werkzeug** (`debug=True` en `run.py:28`). En desarrollo es normal, pero hay que garantizar `debug=False` en despliegue. | Configurarlo por variable de entorno. |

---

## 5. Matriz de responsive

✅ correcto · ⚠️ defectos menores · ❌ roto o inutilizable

| Vista | Móvil 375 | Tablet 768 | Escritorio 1440 |
|---|---|---|---|
| Home | ⚠️ desbordamiento oculto, secciones de 100vh con mucho vacío | ❌ logo y textos cortados | ✅ |
| Login | ⚠️ CTA triplicado | ❌ **formulario fuera de pantalla** | ✅ |
| Registro | ⚠️ inputs sin gap, anchos irregulares | ✅ | ✅ |
| Reset | ✅ | ✅ | ✅ |
| Dashboard | ⚠️ tercera tarjeta bajo el pliegue | ⚠️ texto pegado al borde | ✅ |
| Cuenta | ⚠️ botones pegados | ✅ | ✅ |
| Pacientes (listado) | ❌ texto desborda la tarjeta *(sim.)* | ⚠️ paginación ilegible *(sim.)* | ⚠️ paginación *(sim.)* |
| Crear paciente | ⚠️ selects truncados | ✅ | ✅ |
| Categorías | ✅ | ⚠️ h1 desproporcionado | ✅ |
| Historias | ✅ *(sim.)* | ⚠️ doble cabecera *(sim.)* | ⚠️ doble cabecera *(sim.)* |
| 404 | ⚠️ ilustración "400" | ⚠️ | ⚠️ |

**Causa raíz común:** `main.css` tiene **un único breakpoint (`min-width: 720px`)**, repetido en 16 bloques `@media`. Pasa de un layout móvil a medidas fijas de escritorio (px) sin estados intermedios. Se recomienda:

```css
/* Breakpoints sugeridos (mobile-first) */
@media (min-width: 640px)  { /* móvil grande / tablet vertical */ }
@media (min-width: 1024px) { /* tablet horizontal / layouts en fila */ }
@media (min-width: 1280px) { /* escritorio amplio */ }
```

Y sustituir los anchos fijos por `max-width: 100%`, `clamp()`, `min()` y CSS Grid con `auto-fit/minmax`.

---

## 6. Propuesta: modularizar los estilos CSS

### 6.1 Situación actual

- **Un solo archivo**, `vitahistory/static/style/main.css`, de **1922 líneas**, organizado por comentarios `/*inicio … */ /*fin … */`.
- **90 líneas de CSS inline** en `templates/base.html:15-103`, enviadas en cada respuesta HTML.
- Hay estilos **compartidos dentro de secciones de módulos concretos**, por lo que su ubicación es difícil de adivinar:
  - Los estilos globales de formulario (`form label`, `form input`, `form button`, `.text-form`, `.link`) están en la sección de **login** (`main.css:575-618`).
  - `.field-double`, `.left-field` y `.right-field` (usados en cuenta, crear paciente y editar paciente) están en **registro** (`main.css:797-813`).
  - `.update-btn` y `.photo-btn` (usados en cuenta, crear y editar paciente) están en **cuenta** (`main.css:1021-1048`).
  - `.display-none` y `.person-name` están dentro de la sección **footer** (`main.css:1845-1851`).
  - La sección de la landing se llama "página start" (`main.css:144`), aunque `start` es el dashboard.
- No hay variables CSS: 20 colores hex repetidos a mano.

### 6.2 Estructura recomendada para los archivos de estilos

Se toma como referencia el patrón que el equipo ya usa en **NexusAccessFlask** (`nexus/static/css/main.css`). Ahí `main.css` no contiene los estilos de los módulos: es el **punto de entrada** y el lugar donde vive lo global. Se organiza en secciones fijas y siempre en el mismo orden:

| # | Sección de `main.css` | Qué contiene | En Nexus |
|---|---|---|---|
| 1 | **Importaciones** | Un `@import` por módulo o componente. Va **siempre al principio**: el navegador ignora un `@import` que aparezca después de cualquier regla. | `main.css:1-16` (16 módulos) |
| 2 | **Reset global** | `*`, `html`, normalización de márgenes, `box-sizing` y foco accesible (`:focus-visible`). | `main.css:19-71` |
| 3 | **Variables CSS (`:root`)** | Colores de marca, fondos, textos, estados (flashes), escala tipográfica (`--fs-*`, `--fw-*`, `--lh-*`), espaciados (`--space-*`) y alias semánticos (`--bg-primary`, `--text-muted`…). Todos los módulos los consumen. | `main.css:73-216` |
| 4 | **Convención de breakpoints** | Documentada en un comentario dentro de `:root`, porque las variables CSS no funcionan dentro de `@media`. Fija los únicos anchos permitidos. | `main.css:172-183` |
| 5 | **Elementos base** | `body`, `main`, `button`, inputs: las propiedades que se repetirían en todos los módulos se declaran **una sola vez** aquí. | `main.css:254-288` |

El principio es el mismo que propone el equipo: **una definición global para las propiedades que se repiten**, para escribir menos código y cambiar el aspecto desde un solo sitio. En VitaHistory el beneficio es medible, porque hoy `main.css` repite a mano:

| Declaración repetida | Veces | Pasaría a ser |
|---|---|---|
| `display: flex` | 70 | Utilidades `.flex`, `.flex-center` o reglas base |
| `justify-content: center` | 31 | `.flex-center` |
| `font-family: "Inter", sans-serif` | 28 | Una vez en `body { font-family: var(--font-sans) }` |
| `#EBEBEB` | 16 | `var(--color-bg)` |
| `border-radius: 7px` | 15 | `var(--radius-sm)` |
| `#1D884D` | 13 | `var(--color-primary)` |
| `1px solid #C9C9C9` | 11 | `var(--border)` |

> **Qué no conviene copiar de Nexus:**
> - Su `main.css` también incluye un componente completo (el modal, `main.css:290-424`). En VitaHistory, `main.css` debería quedarse solo con las 5 secciones anteriores y cada componente en su propio archivo. Así `main.css` no vuelve a crecer.
> - El tema claro/oscuro (`.light-theme`) no aplica hoy a VitaHistory. Si algún día se añade, iría en una sección 3b justo después de `:root`, como en Nexus.

### 6.3 Árbol propuesto para VitaHistory

Se sigue la convención de Nexus: **un archivo por módulo o componente, todos al mismo nivel** en `static/style/`. Al lado de cada archivo se indica de qué líneas del `main.css` actual sale su contenido.

```
vitahistory/static/style/
├── main.css            ← 1) @imports  2) reset  3) :root variables  4) breakpoints  5) elementos base
│
│   ── Componentes compartidos (los usan varios módulos) ──
├── navbar.css          ← menú móvil + escritorio           (main.css:35-142, 342-411)
├── footer.css          ← pie de la landing                 (main.css:1804-1844, 1853-1861)
├── buttons.css         ← .global-btn, .simple-btn, .cancel-btn, .pag-btn
├── forms.css           ← form label/input/select, .text-form, .field-double,
│                         .update-btn/.photo-btn, .grow-wrap (hoy dispersos en login,
│                         registro, cuenta e historias: 575-618, 797-813, 1021-1048, 1631-1672)
├── profile_header.css  ← .header-section, .profile-section, .user-info (cabecera repetida en 9 vistas)
├── cards.css           ← .person-container, .history-container, .category-container
├── flashes.css         ← mensajes flash                    (main.css:1735-1790)
├── utilities.css       ← .display-none, .display-flex, .round-picture, .flex-center
│
│   ── Módulos (uno por blueprint/sección de la app) ──
├── home.css            ← landing y heroes                  (main.css:144-539)
├── auth.css            ← login, registro y reset           (main.css:541-914)
├── dashboard.css       ← menú principal (index/start)       (main.css:917-967)
├── account.css         ← cuenta                            (main.css:970-1085)
├── persons.css         ← listado, crear, editar y eliminar (main.css:1087-1536)
├── categories.css      ← categorías                        (main.css:1864-1922)
├── histories.css       ← historias                         (main.css:1538-1733)
└── errors.css          ← 403/404/500 + fondos que hoy están en base.html:83-102
```

Cada archivo **lleva sus propias `@media`** (por ejemplo, `navbar.css` contiene sus reglas para ≥768 px). Así un módulo se entiende y se modifica sin abrir ningún otro archivo.

### 6.4 Cómo quedaría `main.css`

```css
/* =====================================================================
   1. IMPORTACIONES — siempre al principio del archivo.
   Orden: componentes compartidos → módulos → utilidades (al final,
   para que puedan sobrescribir).
   ===================================================================== */
@import url("navbar.css");
@import url("footer.css");
@import url("buttons.css");
@import url("forms.css");
@import url("profile_header.css");
@import url("cards.css");
@import url("flashes.css");

@import url("home.css");
@import url("auth.css");
@import url("dashboard.css");
@import url("account.css");
@import url("persons.css");
@import url("categories.css");
@import url("histories.css");
@import url("errors.css");

@import url("utilities.css");

/* =====================================================================
   2. RESET GLOBAL
   ===================================================================== */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html { height: 100%; }

/* Foco visible solo con teclado (corrige el outline: none actual, §3.4) */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* =====================================================================
   3. VARIABLES CSS — única fuente de verdad para colores, tipografía,
   espaciado y radios. Los módulos solo usan var(--…), nunca hex sueltos.
   ===================================================================== */
:root {
  /* Marca */
  --color-primary:       #1D884D;   /* verde VitaHistory (13 usos hoy)        */
  --color-primary-dark:  #09562D;
  --color-accent:        #32CB1E;   /* .special-text                          */
  --color-blue:          #26A0DA;
  --color-navy:          #314755;
  --color-teal-dark:     #00394A;   /* fondo hero 3                           */

  /* Fondos y superficies */
  --color-bg:            #EBEBEB;   /* 16 usos hoy                            */
  --color-surface:       #E5E5E5;   /* tarjetas de formulario                 */
  --color-white:         #FFFFFF;

  /* Texto */
  --color-text:          #1B1B1B;
  --color-text-muted:    #4A4A4A;

  /* Bordes */
  --color-border:        #C9C9C9;
  --border:              1px solid var(--color-border);

  /* Estados (flashes y acciones destructivas) */
  --color-success-bg:    #8AE882;  --color-success-text: #09562D;
  --color-info-bg:       #9AE0FB;  --color-info-text:    #0449A1;
  --color-warning-bg:    #FFEE99;  --color-warning-text: #936600;
  --color-danger-bg:     #FCEDED;  --color-danger:       #FF0000;

  /* Gradiente de los botones principales */
  --gradient-btn:        linear-gradient(to bottom, var(--color-navy), var(--color-blue));
  --gradient-btn-hover:  linear-gradient(to bottom, var(--color-blue), var(--color-navy));

  /* Tipografía */
  --font-sans:     "Inter", sans-serif;      /* 28 declaraciones hoy */
  --font-display:  "Istok Web", sans-serif;
  --fs-sm:   0.875rem;
  --fs-base: 1rem;
  --fs-md:   1.125rem;
  --fs-lg:   1.5rem;
  --fs-xl:   2rem;
  --fs-2xl:  clamp(2rem, 5vw, 3rem);       /* títulos fluidos: evitan cortes en tablet */
  --fs-3xl:  clamp(3rem, 8vw, 6rem);
  --fw-regular:  400;
  --fw-semibold: 600;
  --fw-bold:     700;

  /* Espaciado */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;   /* el "24px" que hoy se repite 11 veces */
  --space-xl: 2rem;

  /* Radios */
  --radius-sm: 7px;     /* 15 usos hoy */
  --radius-md: 10px;
  --radius-lg: 20px;

  /* Layout */
  --header-h:  97px;
  --max-width: 1370px;
  --tap-min:   44px;    /* tamaño mínimo de objetivo táctil (§3.4) */
}

/* =====================================================================
   4. BREAKPOINTS CANÓNICOS — convención, no variables (las custom
   properties no funcionan dentro de @media). Mobile-first:
     móvil  (por defecto, sin media query): 0–639px
     sm : (min-width: 640px)   móvil grande / tablet vertical
     md : (min-width: 768px)   tablet
     lg : (min-width: 1024px)  escritorio / layouts en fila
     xl : (min-width: 1280px)  escritorio amplio
   No introducir otros valores (hoy todo usa 720px, causa del §5).
   ===================================================================== */

/* =====================================================================
   5. ELEMENTOS BASE — lo que hoy se repite en cada módulo se declara
   aquí una sola vez.
   ===================================================================== */
body {
  font-family: var(--font-sans);
  font-size: var(--fs-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  min-height: 100%;
}

a { color: var(--color-primary); text-decoration: none; }
ul { list-style: none; }
img { max-width: 100%; height: auto; }   /* evita los desbordes de imágenes fijas */

button { font: inherit; cursor: pointer; }

input, select, textarea {
  font: inherit;
  border: var(--border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg);
  color: var(--color-text-muted);
  min-height: var(--tap-min);
  padding: 0 var(--space-sm);
}
```

Con esto, un módulo como `flashes.css` deja de repetir valores y solo describe lo que le es propio:

```css
/* flashes.css */
.flashes p {
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-weight: var(--fw-semibold);
}
.alert-success { background: var(--color-success-bg); color: var(--color-success-text); }
.alert-info    { background: var(--color-info-bg);    color: var(--color-info-text); }
.alert-warning { background: var(--color-warning-bg); color: var(--color-warning-text); }

@media (min-width: 768px) {
  .flashes p { max-width: 550px; }
}
```

Y un ajuste de marca o de contraste (por ejemplo, oscurecer `--color-primary` para cumplir AA, §3.3) se hace en **una sola línea** de `main.css`.

### 6.5 Sacar el CSS inline de `base.html`

Las reglas de `base.html:15-103` solo están inline porque usan `url_for()`. Como las imágenes están en `static/image/` y los CSS en `static/style/`, se pueden referenciar con una ruta relativa desde el propio archivo CSS:

```css
/* dashboard.css */
.image-container-one {
  background-image: linear-gradient(rgba(0,0,0,.5), rgba(0,0,0,.5)),
                    url("../image/fondo-personas-registradas.webp");
  background-size: cover;
  background-position: center;
}
```

> Las rutas en `url()` son relativas **al archivo CSS que las contiene**: desde `static/style/` es `../image/…`.

Así `base.html` queda limpio y esas reglas se cachean con el resto del CSS.

### 6.6 Consideraciones técnicas

| Opción | Ventajas | Inconvenientes |
|---|---|---|
| **A. `@import` nativo en `main.css`** (lo que propone el equipo) | Cero dependencias y organización clara. `base.html` sigue con un solo `<link>`. | El navegador descubre cada `@import` **solo después** de descargar `main.css`, así que hay peticiones encadenadas (unas 20). Con HTTP/1.1 y sin caché se nota en la primera carga. |
| **B. Varios `<link>` en `base.html`** | Descarga en paralelo. | `base.html` más largo y el orden de cascada se define en la plantilla. |
| **C. `@import` en desarrollo y un bundle en producción** (*recomendada*) | Organización de la opción A con el rendimiento de un solo archivo. Por ejemplo, `lightningcss --bundle main.css -o main.min.css`, `postcss-import` o `Flask-Assets`. | Añade un paso de build. |
| **D. CSS por página con `{% block styles %}`** | Cada plantilla carga solo lo que necesita. | Más gestión manual y riesgo de olvidar un archivo. |

**Recomendación:** adoptar ya la **estructura con `@import` (opción A, la misma que usa Nexus)**: aporta la mayor parte del beneficio en mantenibilidad. Cuando se prepare el despliegue, añadir el **bundling (opción C)** sin tocar la estructura. Mientras tanto, `@import` debe ir **siempre al principio** de `main.css`, antes de cualquier regla, o el navegador lo ignora.

### 6.7 Plan de migración sugerido (sin cambios visuales)

1. Reescribir `main.css` con sus 5 secciones (§6.4): primero `:root` con las variables y el reset. Sustituir los hex por `var(--…)` y comparar visualmente antes y después.
2. Extraer `utilities.css` y declarar los elementos base (`body`, `input`, `button`), eliminando las repeticiones de cada módulo.
3. Extraer los componentes compartidos (forms, buttons, profile-header, cards, flashes), que hoy están dispersos en secciones de módulos.
4. Mover cada sección de módulo a su archivo, llevando sus `@media`.
5. Sacar el CSS inline de `base.html`.
6. Verificar con capturas en los 3 viewports que no hay regresiones visuales y eliminar las reglas muertas (por ejemplo, `.display-none` del botón "Nuestros servicios").

---

## 7. Unificación del idioma: todo en español

**Objetivo:** que **ningún texto visible para el usuario esté en inglés**: mensajes flash, errores de validación, títulos de pestaña, valores por defecto guardados en la base de datos que se muestran en pantalla, y cualquier etiqueta o botón. Hoy conviven ambos idiomas, a veces en la misma pantalla. Por ejemplo, tras iniciar sesión aparece "You have successfully logged in" sobre un menú en español.

### 7.1 Mensajes flash y errores de formulario

| Archivo:línea | Texto actual (inglés) | Propuesta en español |
|---|---|---|
| `vitahistory/__init__.py:34` | Please log in to access this page | Inicia sesión para acceder a esta página |
| `auth/__init__.py:56` | You have successfully logged in | Has iniciado sesión correctamente |
| `auth/__init__.py:63` | Invalid username/email or password, please try again | Usuario, correo o contraseña incorrectos. Inténtalo de nuevo |
| `auth/__init__.py:93` | Username already exists, please try another one | Ese nombre de usuario ya existe, elige otro |
| `auth/__init__.py:98` | Email is already registered with another user | Ese correo ya está registrado por otro usuario |
| `auth/__init__.py:101` | Passwords do not match, please try again | Las contraseñas no coinciden. Inténtalo de nuevo |
| `auth/__init__.py:112` | User {username} has been registered successfully | El usuario {username} se registró correctamente |
| `auth/__init__.py:148` | User is not registered in the database, please try again | No existe ningún usuario registrado con ese correo |
| `auth/__init__.py:151` | An email has been sent to reset your password | Te enviamos un correo para restablecer tu contraseña |
| `auth/__init__.py:158` | To reset your password, please enter your email address | Para restablecer tu contraseña, escribe tu correo electrónico |
| `auth/__init__.py:171` | The provided token is invalid or has expired | El enlace no es válido o ha caducado |
| `auth/__init__.py:181` | Passwords do not match, please try again | Las contraseñas no coinciden. Inténtalo de nuevo |
| `auth/__init__.py:188` | Your password has been updated successfully | Tu contraseña se actualizó correctamente |
| `auth/__init__.py:197` | Please enter your new password | Escribe tu nueva contraseña |
| `person/__init__.py:56` | Phone number exceeds the maximum number of digits | El número telefónico tiene más dígitos de los permitidos |
| `person/__init__.py:60` | Phone number does not meet the required number of digits | Al número telefónico le faltan dígitos |
| `person/__init__.py:78` | Email already exists | Ese correo ya está registrado |
| `person/__init__.py:83` | Phone number already exists | Ese número telefónico ya está registrado |
| `person/__init__.py:145` | This category is already registered in your account | Ya tienes una categoría con ese nombre |
| `history/__init__.py:95` | History edited successfully | Historia actualizada correctamente |
| `history/__init__.py:123` | History deleted successfully | Historia eliminada correctamente |
| `history/__init__.py:134` | Are you sure you want to delete this history? | ¿Seguro que quieres eliminar esta historia? Esta acción no se puede deshacer |

Corregir también los mensajes que ya están en español pero tienen erratas: `person/__init__.py:217` y `:222` dicen "digitos", que debe ser **"dígitos"**.

### 7.2 Valores por defecto que se muestran en la interfaz

| Archivo:línea | Valor actual | Dónde se ve | Propuesta |
|---|---|---|---|
| `models.py:37` | `default='Specialty'` | Cabecera de perfil en todas las vistas internas y en el campo "Especialidad" de la cuenta | `'Sin especialidad'`, o mejor dejarlo vacío y que la UI muestre "Añade tu especialidad" como placeholder |
| `models.py:101` | `default='Uncategorized'` | Categoría de los pacientes | `'Sin categoría'` (es el valor que ya usa `create_person.html:62`) |
| `person/__init__.py:182` | `person.category = "Uncategorized"` al borrar una categoría | Tarjeta del paciente | `"Sin categoría"` |

> Los registros que ya existen con "Specialty" o "Uncategorized" en la base de datos necesitan una **migración de datos** (`UPDATE … SET … = 'Sin categoría' WHERE … = 'Uncategorized'`). Si no, los usuarios actuales seguirán viendo los textos en inglés.

### 7.3 Títulos de pestaña (`{% block title %}`)

| Plantilla | Actual | Propuesta |
|---|---|---|
| `index/home.html` | Home | Inicio |
| `index/start.html` | Dashboard | Menú principal |
| `index/account.html` | Account | Mi cuenta |
| `auth/login.html` | Login | Iniciar sesión |
| `auth/register.html` | Sign Up | Registrarse |
| `auth/reset_request.html` | Reset | Recuperar contraseña |
| `auth/reset_final.html` | Reset | Nueva contraseña |
| `person/persons.html` | Show Patients | Pacientes |
| `person/create_person.html` | Create Patient | Nuevo paciente |
| `person/edit_person.html` | Edit Patient | Editar paciente |
| `person/delete_person.html` | Delete Patient | Eliminar paciente |
| `person/show_categories.html` | Show Categories | Categorías |
| `person/create_category.html` | Create Category | Nueva categoría |
| `person/delete_category.html` | Delete Category | Eliminar categoría |
| `history/show_histories.html` | Show Histories | Historias clínicas |
| `history/create_history.html` | Create History | Nueva historia |
| `history/edit_history.html` | Edit History | Editar historia |
| `history/delete_history.html` | Delete History | Eliminar historia |
| `error/403.html`, `404.html`, `500.html` | Error 403/404/500 | Acceso denegado / Página no encontrada / Error del servidor |

### 7.4 Otros textos en inglés

- **Ilustración de la página 404** (`static/image/404-error-bk.webp`): muestra "400' Not Found". Hay que reemplazarla por una sin texto o con el texto en español ("Página no encontrada").
- **Formato de fecha nativo** del `<input type="date">` en el registro: aparece como `mm/dd/yyyy` porque el documento no declara idioma. Al añadir `<html lang="es">` (§3.1), el navegador mostrará `dd/mm/aaaa`.
- **Texto alternativo e `aria-label`** que se añadan (§3.4) deben redactarse en español.

### 7.5 Recomendación para que no vuelva a pasar

- **Centralizar los textos** en un módulo (por ejemplo, `vitahistory/messages.py` con constantes como `MSG_LOGIN_OK`), o adoptar **Flask-Babel** si en el futuro se quiere soportar varios idiomas. Así un texto en inglés queda en un solo sitio, fácil de revisar.
- Añadir a la checklist de PR: *"todos los textos visibles están en español"*.

---

## 8. Backlog priorizado (interfaz de usuario)

| Prioridad | Tarea | Esfuerzo |
|---|---|---|
| P0 | Traducir al español todos los textos visibles en inglés (§7): flashes, `<title>`, valores por defecto y migración de datos existentes | S |
| P0 | Login en tablet: el formulario queda fuera de pantalla | S |
| P0 | Quitar `user-scalable=no` / `maximum-scale`, añadir `lang="es"` y `<meta charset>` | XS |
| P1 | Estilos `:focus-visible` globales; `alt` en imágenes; `aria-label` en los iconos de acción | S |
| P1 | Sustituir `<button><a>` por `<a class="btn">` (o `<button>` en formularios) | M |
| P1 | Menú móvil accesible por teclado y sin desbordamiento horizontal | S |
| P1 | Breakpoints intermedios y medidas fluidas en home y login (tablet) | M |
| P1 | Tarjetas de paciente con `min-height`, paginación legible y estado vacío | S |
| P1 | Corregir la ortografía de la interfaz (signos de apertura, tildes: §3.5) | XS |
| P2 | Modularizar el CSS (§6) y crear design tokens | M |
| P2 | Extraer la cabecera de perfil a `snippets/profile_header.html` (se repite en 9 plantillas) | S |
| P2 | Eliminar los botones duplicados móvil/escritorio (`-btn-one/-btn-two`) | S |
| P2 | Confirmaciones de borrado con "Cancelar" y texto de consecuencias | S |
| P2 | Ajustar el contraste de `#1D884D` sobre `#EBEBEB` y del degradado de los botones | XS |
| P3 | Buscador y filtro de pacientes; `per_page` de 10–20 | M |
| P3 | Input de foto accesible, con preview | S |
| P3 | Reemplazar la ilustración 404 ("400") y añadir un CTA de vuelta | XS |
| P3 | Quitar la fuente EB Garamond sin uso y reducir Font Awesome | XS |

---

## 9. Datos de prueba creados durante la auditoría

| Entidad | Valor | Estado | Acción sugerida |
|---|---|---|---|
| Categoría (id 1) | `[ui-audit] control` | Creada en la cuenta de pruebas | Borrarla desde `/person/delete/category/1` |
| Paciente | `[UI-AUDIT] Paciente Demo` | **No creado** (falló con el error 500 del §10) | — |
| Historia | — | No creada (requiere un paciente) | — |

No se confirmó ningún borrado ni se modificaron los datos de la cuenta.

---

## 10. Anexo técnico (fuera del alcance de UI): el teléfono del paciente debe guardarse como texto

> Este punto no es de interfaz, pero **bloquea** el uso de los módulos de pacientes e historias. Se incluye para que se corrija junto con las mejoras anteriores.

### 10.1 Problema

| | Definición |
|---|---|
| Modelo (`vitahistory/models.py:76`) | `phonenumber = db.Column(db.String(20), unique=True, nullable=False)` |
| Migración aplicada (`migrations/versions/917a95d6b5a1_creando_tablas_iniciales.py:63`) | `sa.Column('phonenumber', sa.Integer(), nullable=False)` |

El modelo ya se cambió a `String(20)`, pero **no se generó la migración correspondiente**, así que la columna real en MySQL sigue siendo `INT` (máximo 2.147.483.647). Todos los prefijos que ofrece el formulario (0412, 0414, 0416, 0424 y 0426) forman números de 11 dígitos mayores que ese límite. Por eso **crear cualquier paciente falla siempre** con:

```
sqlalchemy.exc.DataError: (pymysql.err.DataError) (1264,
"Out of range value for column 'phonenumber' at row 1")
```

Aunque el valor cupiera, guardar un teléfono como entero **elimina el cero inicial** (`0412…` → `412…`). Los números de teléfono son identificadores, no cantidades: siempre deben guardarse como texto.

### 10.2 Corrección propuesta

1. Generar una nueva migración Alembic que cambie el tipo de la columna:

   ```python
   # migrations/versions/<nuevo>_phonenumber_to_string.py
   def upgrade():
       with op.batch_alter_table('person') as batch_op:
           batch_op.alter_column(
               'phonenumber',
               existing_type=sa.Integer(),
               type_=sa.String(length=20),
               existing_nullable=False,
           )

   def downgrade():
       with op.batch_alter_table('person') as batch_op:
           batch_op.alter_column(
               'phonenumber',
               existing_type=sa.String(length=20),
               type_=sa.Integer(),
               existing_nullable=False,
           )
   ```

   (Con `flask db migrate` Alembic puede no detectar el cambio de tipo si `compare_type` no está activo. Conviene revisar `migrations/env.py` o escribir la migración a mano como arriba.)

2. **Datos existentes:** si ya hay pacientes guardados con el teléfono como entero, el cero inicial se perdió. Añadir en la misma migración un paso que lo restaure, por ejemplo `UPDATE person SET phonenumber = CONCAT('0', phonenumber) WHERE LENGTH(phonenumber) = 10`.

3. **En la interfaz** (relacionado con el §4.5): cambiar los inputs de teléfono de `type="number"` a `type="tel" inputmode="numeric"` en `create_person.html:52` y `edit_person.html:49`. Así el navegador nunca convierte el valor a número y no se pierden ceros al editar.

4. **Verificación:** crear un paciente con prefijo 0412, comprobar que se guarda `04121234567` (con el cero), editarlo sin tocar el teléfono y confirmar que no aparece el error "no cumple la cantidad de dígitos".
