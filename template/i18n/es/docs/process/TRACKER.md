# El tracker: Linear o GitHub Projects

HAAM funciona igual con cualquiera de los dos trackers. `haam.config.json` → `"tracker"` indica cuál usa este proyecto:

- **`github`**: issues en este repositorio de GitHub, en un tablero de GitHub Projects. Gratis en todos los planes de GitHub. Los agentes usan `python3 tools/haam/haam.py issue …` (más abajo), que funciona desde cualquier herramienta de agente.
- **`linear`**: issues en un equipo de Linear. Los agentes usan la conexión con Linear (MCP).

Las skills dicen "en el tracker"; esta página explica cómo hacer cada operación en cada tracker. **Agentes: comprobar `tracker` en `haam.config.json` una vez por sesión y usar después la columna correspondiente.**

## Conceptos

| Concepto | GitHub Projects | Linear |
|---|---|---|
| ID del issue (escríbelo así) | `#123` | `APP-123` |
| Nombre de rama | `123-short-title` | `app-123-short-title` (el nombre de rama de Linear) |
| Mensaje de commit | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Título de la PR | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Vincular PR → issue | **`Refs #123`** en la descripción de la PR (no `Closes`: el issue se cierra en `/release`, tras el despliegue) | ID del issue en el título de la PR |
| Archivos del issue | `docs/specs/GH-123-slug.md` (igual para evaluaciones y UAT) | `docs/specs/APP-123-slug.md` |
| 12 estados | Campo **Status** del tablero | Estados del workflow del equipo |
| Prioridad | Campo **Priority** del tablero (Urgent/High/Medium/Low) | Prioridad integrada |
| Flujos, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Etiquetas del issue | Etiquetas del issue |
| Epic (agrupa los issues de una feature) | Issue con la etiqueta `epic`; sus issues son **sub-issues** de GitHub | Issue con la etiqueta `epic`; sus issues son **sub-issues** (con el padre fijado) |
| Quién está trabajando en él | Estado In Progress (construyendo) o etiqueta `claimed` (evaluando, escribiendo una especificación, construyendo un prototipo), más el comentario de reserva. La persona asignada no basta para distinguir dos chats de la misma persona | Igual |
| Cambios de estado al abrir o fusionar una PR | Workflow `tracker-sync.yml`: solo los issues que se están entregando (no los epics, ni las PR solo de documentación, ni los spikes) | La integración de Linear con GitHub |

## Operaciones

Los comandos de la columna de GitHub se ejecutan desde la raíz del repositorio. Añade `--json` para obtener una salida legible por máquina.

| Operación | GitHub Projects | Linear (mediante MCP) |
|---|---|---|
| **Buscar trabajo** (colas para `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (añade `--label agent-ready` para features, `--label stream:bug` para bugs) | Listar los issues del equipo por estado, etiqueta y persona asignada |
| **Leer un issue** | `haam.py issue view 123` | Obtener el issue |
| **Crear una idea** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (cae en Triage) | Crear un issue, estado Triage, etiqueta `stream:idea` |
| **Informar de un bug** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Crear un issue, estado Triage, etiqueta `stream:bug` |
| **Crear un epic** | `haam.py issue create --epic --stream idea --title "…"` | Crear un issue con la etiqueta `epic` |
| **Meter un issue en un epic** | `haam.py issue link 14 --parent 9` | Fijar el epic como padre del issue |
| **Crear un issue dentro de un epic** (p. ej., porciones de una especificación, huecos) | `haam.py issue create --stream feature --parent 9 --title "…"` | Crear un sub-issue del epic |
| **Los campos propios del tablero** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` los enumera con sus opciones. Se fijan con `--field NAME=VALUE` en `issue create` o `issue edit` (se puede repetir; un valor vacío borra uno; `Sprint=@current` es la iteración en curso hoy), y se filtra con `issue list --field Area=Billing`. Un nombre o un valor erróneo se rechaza antes de cambiar nada | Los campos propios del equipo, con la conexión con Linear |
| **Sacar un issue de un epic** | `haam.py issue unlink 14` | Quitar el padre del issue |
| **Reescribir un issue** (título, descripción) | `haam.py issue edit 14 --title "…" --body-file new.md` | Actualizar el issue |
| **Los issues de un epic** | `haam.py issue children 9` (con el progreso) | Listar los sub-issues del epic |
| **Issues que no están en ningún epic** | `haam.py issue list --open-only --no-parent --no-label epic` | Listar los issues sin padre |
| **Reservar** (antes de construir, evaluar o escribir una especificación) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (construcción: lo rechaza si ya está reservado o no está en Ready; `--force` para bugs que se corrigen directamente desde Triage, solo cuando la persona lo dijo). Para evaluar: añade `--for assess`; para escribir una especificación: `--for spec`. Imprime un id de reserva: guárdalo | Volver a obtenerlo; si está In Progress, tiene la etiqueta `claimed` o está asignado a otra persona, parar; si no, asignártelo, ponerlo en In Progress (construcción) o añadir la etiqueta `claimed` (evaluación, especificación), comentar con un id de reserva y volver a leer los comentarios (AGENTS.md §6) |
| **Construir un prototipo** (`/spike`) | `haam.py issue claim 123 --for spike` (ideas de Triage a Decision, features en Backlog) y, cuando esté subido: `issue label 123 --add spike-ready` e `issue release 123 --claim <id> --status Decision` (una feature en Backlog: sin `--status`) | Reservar como arriba (etiqueta `claimed`, un comentario de reserva que diga "to build a prototype"), etiqueta `spike-ready`, liberar |
| **Código de producción en un cambio** | `haam.py production` (los archivos que cambia una rama y que se ejecutan para los usuarios) | Igual |
| **Liberar una reserva** (evaluación o especificación subida; o el chat se detiene) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` en lugar del id solo en `/triage stale` o `/test`) | Quitar la asignación, quitar `claimed`, fijar el estado, comentar `🔓 Claim released` |
| **Cambiar el estado** | `haam.py issue status 123 "UAT"` | Actualizar el estado del issue |
| **Estado reservado a personas** (Done, Parked, Canceled, Decision→Backlog) | Igual, más `--human`, **solo** dentro de `/triage`, `/epic`, `/decide`, `/test`, `/release` u `/override` escritos por una persona | La misma regla |
| **Prioridad** | `haam.py issue priority 123 High` | Actualizar la prioridad |
| **Etiquetas** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` también necesita `--human`, después de que la persona apruebe la especificación) | Actualizar las etiquetas |
| **Comentar** | `haam.py issue comment 123 --body "…"` o `--body-file` | Crear un comentario |
| **Rechazar o marcar como duplicado** (en `/triage`, `/epic` o `/decide`) | `haam.py issue status 123 Canceled --human` (también cierra el issue como no planificado); comenta el motivo o el ID del original | Estado Canceled, comentario |
| **Probar un cambio** (persona, en `/test`) | `haam.py checkout-pr 123` y después `haam.py checkout-pr --back` | Igual (el código está en GitHub en ambos casos) |
| **Abrir la PR tras una aprobación** (test-first, la persona dijo `pass`) | `haam.py publish 123 --human`: sube el commit probado, abre la PR con la etiqueta `uat-passed` y mueve el issue a In Review | `haam.py publish APP-123 --human` (`--label human-review` si el issue la tiene) y después mover el issue a In Review y comentar, según lo que imprima |
| **Registrar una prueba suspendida** (la persona dijo que falló) | `haam.py test-failed 123 --human` y después etiqueta `uat-failed`, estado Ready, sin persona asignada | `haam.py test-failed APP-123 --human` y después lo mismo en Linear |
| **Llevar a producción tras una aprobación** (la persona dijo `ship`) | `haam.py ship 123 --human`: fusionar, aprobar el despliegue, esperar, cerrar | `haam.py ship APP-123 --human` y después poner Done en Linear |
| **Llevar a producción todo lo listo, un solo despliegue** | `haam.py ship --all --human` (o `ship 12 13 14 --human`): fusiona cada una, aprueba solo el despliegue más reciente, cierra todos | `haam.py ship APP-12 APP-13 --human` (enuméralos: `--all` no puede leer Linear) |
| **Ver o cambiar cómo funciona HAAM** (product owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (solo por decisión del product owner) | Igual |
| **Ejecutar la CI aquí** (ajuste `ci: local`) | `haam.py local-ci 123` (ship la ejecuta por ti) | Igual |
| **Sin UAT para este issue** (decisión del product owner) | `haam.py issue label 123 --add uat:skip --human` | Etiqueta `uat:skip` |
| **¿Hay hueco para trabajo nuevo?** (`/next` lo comprueba primero) | `haam.py capacity` (la cola de UAT y las PR listas frente a `max_in_uat`, `max_open_prs`, o el aumento de una ventana de lote; los borradores y las PR solo de documentación no cuentan) | El mismo comando, con `--in-uat <count>` |
| **¿Chocará el trabajo nuevo con lo que está esperando?** | `haam.py overlap --files src/auth/,src/api/users.py` (ramas en UAT que cambian los mismos archivos) | Igual, con `--branch <name>` para cada rama en UAT |
| **PR por lotes** (los bugs de un epic) | Título `#12 #13 #14: …`, una línea `Refs #n` por issue; `ship` los cierra todos | Título `APP-12 APP-13: …` |
| **Cerrar tras la release** | `haam.py issue close 123 --human` (pone Done y cierra; solo `/release`) | Estado Done |

## Reglas que se aplican a los dos

- Todo trabajo tiene un issue en el tracker; no se sigue nada en ningún otro sitio.
- Si no se puede acceder al tracker, para y avisa a la persona.
- El protocolo de reserva es lo que impide que dos chats de agente (o dos máquinas) construyan, evalúen o especifiquen lo mismo. No te lo saltes nunca.
- Los movimientos reservados a personas solo ocurren dentro de las skills reservadas a personas, y la herramienta pide `--human` en GitHub como recordatorio. Los agentes actúan con el propio inicio de sesión del product owner, así que GitHub no puede saber quién puso una etiqueta del product owner (`uat:skip`, `mode:prototype`, `mode:epic-build`): es una regla, que la herramienta comprueba en GitHub Projects y que nada comprueba en Linear. Un agente que la incumpliera con `gh` a secas podría, con `uat:skip`, hacer que un cambio fuera de las áreas protegidas se saltara tu prueba; la CI y las dos revisiones de IA se siguen ejecutando, y los despliegues siguen esperándote donde tu plan lo permite.

## Configuración de GitHub Projects (admin, una vez)

1. `gh auth refresh -s project` (permite que tu inicio de sesión de GitHub use Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plan) y después `--apply`: crea el tablero con el nombre del producto, vincula el repositorio, fija los 12 estados y el campo Priority, y crea las etiquetas.
4. **Token de automatización** (para `tracker-sync.yml` y para el auto-merge del carril sin UAT): crea un token clásico en github.com/settings/tokens con los permisos `project` y `repo` (`public_repo` basta para un repositorio público) y después `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Sin él todo funciona, pero las tarjetas no se mueven solas cuando se abren o se fusionan las PR, y el carril sin UAT no puede activar el auto-merge (la puerta usa este token, porque una fusión hecha con el propio token del workflow no iniciaría el despliegue). En los proyectos con Linear el carril nunca hace auto-merge, así que no hace falta el token para eso.
5. **En el navegador**, en el tablero: crea las vistas guardadas que indica la configuración (Board agrupado por Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics) y activa el workflow integrado del tablero **Auto-add to project** para este repositorio (tablero → Workflows). Pone en el tablero, sin coste, los issues creados en la web de GitHub; `haam.py issue create` añade los suyos. **Desactiva** el workflow integrado **Item closed → Status: Done**: sobrescribe `Canceled` después de que `issue status … Canceled` cierra el issue, y `ship` ya pone Done él mismo.
6. Cada desarrollador ejecuta `gh auth refresh -s project` una vez; `/haam-onboard` lo comprueba.

## Cambiar de tracker más adelante

Fija `"tracker"` con `haam.py config --tracker …`, ejecuta la configuración del nuevo tracker y pide después a tu agente que copie los issues abiertos (puede leer un tracker y escribir en el otro). Deja el tracker antiguo en solo lectura para conservar el historial.
