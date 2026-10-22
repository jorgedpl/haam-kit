# Configuración de Linear (una vez, unos 30 minutos, administrador del espacio de trabajo)

> **Solo si tu tracker es Linear** (`"tracker": "linear"` en `haam.config.json`). ¿Usas GitHub Projects? Ejecuta en su lugar `python3 tools/haam/haam.py github-project` y consulta `docs/process/TRACKER.md`.

Esto configura Linear para que coincida con `docs/process/LIFECYCLE.md`. Hazlo una vez; a partir de ahí, todos los desarrolladores y agentes usan la misma estructura.

> **Automatizado:** las secciones 1–4 las hace `python3 tools/haam/haam.py linear --apply`, que ejecutas tú en tu propia terminal (pide tu clave de API personal de Linear de forma segura y nunca la guarda). Esta página es el equivalente manual, más las secciones 5–9, que solo existen en la aplicación web de Linear.

## 1. Equipo
- Crea (o reutiliza) un equipo con el nombre de tu producto y un identificador corto (los ejemplos usan **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` sustituye `APP` en todos los archivos de HAAM.
- Invita a cada persona que contribuya, con su propia cuenta de Linear. Los agentes actúan como la persona que los ejecuta, así que no hacen falta licencias aparte para los agentes.

## 2. Estados del workflow
Team settings → **Workflow**. Crea estos estados, en este orden y en la categoría indicada:

| Estado | Categoría | Notas |
|---|---|---|
| Triage | Triage | Activa Triage para el equipo |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Márcalo como predeterminado para los issues nuevos que no pasan por triaje |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Borra o cambia el nombre de los estados predeterminados de Linear (`Todo`, `Duplicate`, etc.) para que solo queden estos. Los nombres tienen que coincidir exactamente; las skills se refieren a ellos por su nombre.

## 3. Etiquetas
Team settings → **Labels**. Crea estas etiquetas (etiquetas simples, sin grupo):
- `stream:idea`
- `stream:feature`
- `stream:bug`

Y estas etiquetas independientes:

| Etiqueta | Significado | Quién la aplica |
|---|---|---|
| `agent-ready` | Ha pasado G2; los agentes pueden construirlo | El agente, solo después de que una persona apruebe la especificación |
| `human-review` | Toca un área protegida; se necesita revisión de código humana | Agente o persona |
| `human-only` | Los agentes no deben tomarlo | Persona |
| `override-followup` | Creado tras anular una puerta | `/override` |
| `epic` | Issue padre que agrupa los sub-issues de una feature | `/triage group`, `/epic` o una persona |
| `uat-failed` | Ha suspendido la prueba humana; los agentes lo retocan antes que nada | `/test`, `/uat-result` |
| `uat:skip` | Decisión del product owner: no lo va a probar | `/triage`, o "spec approved, no UAT" |
| `claimed` | Un chat de agente lo está evaluando, escribiendo su especificación o construyendo un prototipo | El agente, mientras trabaja |
| `mode:prototype` | Decisión del product owner: construir primero un prototipo desechable (`/spike`) | `/triage` |
| `mode:epic-build` | Decisión del product owner: un agente principal construye todo este epic | `/decide` |
| `spike-ready` | Hay un prototipo listo para que lo pruebe el product owner | `/spike` |

Opcional: etiquetas de área (`area:onboarding`, `area:billing`, `area:checkout`…) para filtrar el tablero.

## 4. Prioridades
Usa la prioridad integrada de Linear (Urgent / High / Medium / Low / No priority). No hacen falta campos personalizados.

## 5. Plantillas de issue
Team settings → **Templates** → crea tres plantillas de issue, pegando el cuerpo desde:
- **Idea**: `docs/templates/idea.md` · etiqueta predeterminada `stream:idea` · estado Triage
- **Bug**: `docs/templates/bug.md` · etiqueta predeterminada `stream:bug` · estado Triage
- **Feature**: un cuerpo breve con un enlace a la especificación · etiqueta predeterminada `stream:feature` · estado Backlog

Los agentes las rellenan ellos mismos con `/idea` y `/bug`; las plantillas son para las personas que crean issues en la aplicación de Linear.

## 6. Integración con GitHub
Settings → **Integrations → GitHub** → conecta la organización o el repositorio.

Después, en los ajustes del equipo → **Workflow → Pull request automations** (el texto puede variar ligeramente):

| Evento de GitHub | Mover el issue a |
|---|---|
| Rama creada / PR en borrador abierta | In Progress |
| PR lista para revisión (los agentes abren borradores y los marcan como listos cuando están completos) | In Review |
| PR lista para fusionar | *(sin cambio, los agentes lo mueven a UAT)* |
| PR fusionada | Deploying |

**Formato del nombre de rama:** `{issue-identifier}-{issue-title}` (en minúsculas), p. ej. `app-123-bulk-invite-users`. Quita el prefijo del nombre de usuario para que las ramas sean iguales las cree quien las cree.

Activa **"link PRs by issue ID in title"** para que los títulos de PR del tipo `APP-123: ...` se vinculen automáticamente.

## 7. Vistas (filtros guardados)
Crea estas vistas de equipo para que las personas vean lo que las necesita:

| Vista | Filtro |
|---|---|
| **Triage** | La bandeja Triage integrada de Linear (la bandeja diaria del product owner; ver `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Estado en (Decision, UAT), más los issues de Backlog con un comentario `📝 Spec ready for review` |
| **Agent queue** | Estado = Ready, etiqueta `agent-ready` o `stream:bug`, sin asignar |
| **Ideas inbox** | Estado en (Triage, Discovery), etiqueta `stream:idea` |
| **Bugs** | Etiqueta `stream:bug`, no Done/Canceled, ordenados por prioridad |
| **Epics** | Etiqueta `epic`, no Done/Canceled (muestra el progreso de los sub-issues) |
| **Overrides to close** | Etiqueta `override-followup`, no Done |

## 8. Notificaciones
Cada persona: Settings → Notifications → asegúrate de recibir avisos de las **menciones** y de los **issues que te asignan**. `/uat` menciona al product owner cuando hay algo listo para probar.

## 9. Conectar a Linear la herramienta de agente de cada persona
Cada persona inicia sesión una vez desde su propia herramienta (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Pasos por herramienta: `docs/setup/AGENTS-SETUP.md`.
Prueba: pide al agente *"enumera mis issues abiertos de Linear en el equipo APP"*.

Si también usas una aplicación de chat (Claude, ChatGPT…) con un conector de Linear, conéctala también para poder capturar ideas desde el móvil.
