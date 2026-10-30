# HAAM: Human-Agent Agile Methodology

[English](README.md) · **Español** · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Nederlands](README.nl.md) · [Português](README.pt.md)

**Las personas deciden. Los agentes ejecutan. Todo vive en Git y en tu tracker.**

HAAM es una metodología abierta y un kit para crear software con agentes de programación de IA, de la idea a producción, sin perder el control. Da a todos los agentes las mismas reglas, los mismos comandos y las mismas puertas, sea cual sea la herramienta en la que se ejecuten: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI o GitHub Copilot**. El trabajo se sigue en un tablero de **GitHub Projects** (gratis) o en **Linear**, como prefieras. Varias personas, cada una con su propio agente y su propia cuenta, pueden trabajar en paralelo en el mismo producto.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## Qué incluye

- **Un ciclo de vida con cinco puertas humanas**: decidir la idea, aprobar la especificación, comprobaciones automáticas con revisión independiente de IA, prueba de aceptación humana y aprobación de producción. Cualquier puerta se puede anular en una emergencia, y cada anulación queda registrada y tiene seguimiento.
- **Tres flujos de trabajo** de los que tiran los agentes: bugs, features listas e ideas por evaluar. El tracker (GitHub Projects o Linear) guarda el backlog, las prioridades y el estado.
- **20 skills compartidas** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), en el formato abierto Agent Skills.
- **Tus ajustes, tus compromisos:** `/haam-settings` permite al product owner elegir cuándo se ejecutan la CI y las revisiones de IA (en cada PR, en local, solo en áreas protegidas o nunca), qué prueba personalmente, cómo se agrupa el trabajo (por issue, por epic o en una única PR de release), si los despliegues esperan aprobación y los límites, cada uno con su compromiso y las cifras del propio proyecto.
- **Probar con una sola palabra, antes de gastar minutos de CI**: escribe `/test`, prueba el cambio del agente en tu máquina y responde `pass` (solo entonces se abre la pull request y se comprueba, una vez, exactamente sobre lo que probaste) y luego `ship` (el agente la fusiona, la despliega y la cierra), o simplemente di qué falla (vuelve directamente a los agentes y regresa a ti cuando está arreglado). `/test all` recoge todo lo pendiente en una sola sesión, y `ship --all` lo despliega con una sola aprobación.
- **Un carril sin UAT** para los cambios que no puedes probar de forma útil (configuración, actualizaciones de dependencias, refactorizaciones invisibles): marca el issue con `uat:skip` una vez, y su PR se fusiona sola cuando pasan la CI y las dos revisiones de IA.
- **Epics con un agente que hace las preguntas adecuadas**: `/triage group` convierte un montón de issues sueltos en epics (uno por feature); `/epic` lee cada uno, escribe una ficha breve, te hace unas pocas preguntas concretas y después ordena los issues: duplicados, huecos, divisiones, orden.
- **Margen para que los agentes construyan piezas grandes rápido, con una protección:**
  - `/spike` construye un prototipo funcional desechable para que lo pruebes antes de decidir;
  - el modo de construcción de epic deja que un agente construya una feature entera, porción a porción, con puntos de control, una sola prueba y una sola release;
  - todo cambio que se fusiona cumple todas las puertas, y los prototipos nunca se fusionan.
- **Una guía de decisiones** ([DECISIONS.md](template/i18n/es/docs/setup/DECISIONS.md)): cada elección que hace un equipo al adoptar HAAM, con una recomendación para cada una. Cubre las cuentas de GitHub y el plan que necesitas, GitHub Projects o Linear, los ajustes, cómo dimensionar los límites según tu tiempo para probar y qué proteger. `/haam-setup` te guía por ella.
- **Una guía para el product manager** ([PRODUCT-MANAGER.md](template/i18n/es/docs/process/PRODUCT-MANAGER.md)): ritmo diario y semanal, cómo hacer triaje, reglas de prioridad con una matriz de impacto × alcance para bugs y tamaños de cola sanos, con un agente (`/triage`) o directamente en GitHub Projects o Linear.
- **Agentes en paralelo sin colisiones**: abre una nueva ventana de chat, escribe `/work bugs`, y el agente obtiene su propia copia del proyecto (un git worktree), elige el bug más prioritario y lo lleva hasta tu prueba. Ejecuta tantos como quieras, en una máquina o en varias.
- **Revisión de código en la que nadie se corrige sus propios deberes**: un escaneo de secretos antes de cada commit y en la CI, una auditoría de dependencias y dos revisores de IA independientes (especificación/calidad y seguridad) que nunca vieron escribir el código. Las personas revisan las áreas protegidas y pueden imponer su criterio.
- **Puertas que impone GitHub**, no la confianza: reglas de rama, comprobaciones obligatorias, una puerta por etiqueta de UAT y aprobaciones de despliegue, de modo que se cumplen sea cual sea el agente o la persona que hace push.
- **Documentación en siete idiomas:** inglés, español, francés, alemán, italiano, neerlandés y portugués. Elige uno al instalar (`install --language es`) y los agentes también escriben en él las especificaciones, los issues, los planes de UAT y los mensajes; los comandos, las etiquetas y el código siguen en inglés.
- **Una herramienta de configuración** (`haam.py`, Python 3, sin dependencias) que instala el kit en un repositorio existente sin sobrescribir nada, configura GitHub y el tracker (GitHub Projects o Linear), da a los agentes un único conjunto de comandos para el tablero, incorpora a los desarrolladores, comprueba la configuración y actualiza los proyectos a nuevas versiones del kit.

## Inicio rápido

### Adopta HAAM en tu proyecto (administrador del proyecto, una media jornada)

1. Consigue una versión publicada del kit:
   ```bash
   git clone --depth 1 --branch v1.18.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (o descarga el zip desde [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Abre tu agente de programación **en la carpeta raíz de tu proyecto** y dile:
   > Lee `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` y síguelo para configurar HAAM en este repositorio. El kit está en `~/haam-kit/template`.

El agente instala el kit en una rama, te hace unas pocas preguntas, rellena el conocimiento del proyecto a partir de tu código y te guía por GitHub y por tu tracker. Te enseña cada cambio antes de hacerlo. Todo lo que implique una contraseña o una clave de API lo haces tú, en tu propia terminal, nunca a través del chat del agente.

¿Prefieres hacerlo a mano? Sigue [la guía de adopción](template/i18n/es/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Únete a un proyecto que ya usa HAAM (desarrollador, una hora aproximadamente)

Clona el proyecto, abre tu agente en él y ejecuta `/haam-onboard` (Codex: `$haam-onboard`; otras herramientas: *"sigue `.agents/skills/haam-onboard/SKILL.md`"*).

### Actualiza un proyecto a una nueva versión del kit

Consigue la nueva versión del kit y luego, en tu proyecto, ejecuta `/haam-update`, o bien:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Los archivos que nunca cambiaste se actualizan; los que personalizaste se conservan, y cuando han cambiado los dos lados, la nueva versión se deja aparte para que tu agente la fusione. No se borra nada.

## La herramienta de configuración

| Comando | Quién | Qué hace |
|---|---|---|
| `install --target DIR` | admin | Copia el kit en un repositorio. Nunca sobrescribe; fusiona los archivos de ajustes de los agentes; aparca los conflictos en `.haam/incoming/`; registra la versión en `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Actualiza un proyecto a esta versión del kit, conservando las personalizaciones |
| `config` | admin | Nombre del producto, clave del equipo de Linear, repositorio, aprobadores → `haam.config.json`; los aplica a todos los archivos de HAAM |
| `agents [--apply]` | admin | Conecta las skills y Linear para Claude Code, Cursor, Codex, Grok, Gemini y Copilot |
| `github [--apply]` | admin | Etiquetas, conjunto de reglas de rama con comprobaciones obligatorias, aprobación de producción, funciones de seguridad |
| `github-project [--apply]` | admin | Tablero de GitHub Projects: 12 estados, campo Priority, etiquetas, vínculo con el repositorio |
| `linear [--apply]` | admin, en su propia terminal | Equipo de Linear, triaje, 12 estados, 14 etiquetas |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agentes | Trabajar con el tablero de GitHub Projects desde cualquier herramienta de agente |
| `exclusive "<who>" -- <command>` | agentes | Ejecutar una tanda de pruebas pesada (una que usa un recurso común a toda la máquina) cuando no hay otra en marcha en esta máquina |
| `capacity` | agentes | Frenar el trabajo nuevo cuando hay demasiadas PR abiertas o esperando tu prueba (límites en `haam.config.json`) |
| `ci-usage [--days 7]` | admin | En qué se fueron los minutos de GitHub Actions, por workflow, job, disparador y día |
| `metrics [--days 30] [--save]` | owner | Cómo fluye el trabajo: tiempo hasta Done, tiempo en cada cola (decisión, spec, construcción, tu prueba, envío), repeticiones, defectos encontrados en UAT frente a los encontrados después, reverts. `--save` guarda los números en `docs/metrics/` |
| `settings [--explain] [--set key=value] [--apply]` | owner/admin | Tus elecciones: cuándo se ejecutan la CI y las revisiones de IA, qué pruebas tú, agrupación, paso a producción, límites (`/haam-settings` te guía por ellas) |
| `local-ci ISSUE` | owner | Con `ci: local`: ejecuta `make check` aquí sobre el commit de la PR y publica el resultado (ship lo hace por ti) |
| `review ISSUE` | agentes | Las dos revisiones de IA en sesiones locales nuevas, publicadas como estados de la PR (cuando las revisiones son locales) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Poner un cambio en esta máquina para probarlo; tras `pass` + `ship`: fusionar, aprobar el despliegue (uno para varios), esperar, cerrar |
| `worktree status\|new\|prep\|list\|clean` | agentes, cualquiera | Un worktree por chat de agente; copia los archivos locales desde `.worktreeinclude`; limpia los terminados |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Invitar a un desarrollador (escritura en GitHub, no admin; acceso al tablero o al equipo de Linear) |
| `dev [--apply] [--run-checks]` | desarrollador | Comprobación de la máquina, hook de commit, `.env` a partir del ejemplo, comprobaciones del proyecto |
| `doctor [--role admin] [--check-updates]` | cualquiera | Qué está hecho, qué falta y quién tiene que hacerlo |
| `version [--check]` | cualquiera | Versiones de la herramienta, del proyecto y del último kit publicado |

Todos los comandos muestran primero un plan y solo cambian algo con `--apply`. Añade `--json` para obtener una salida legible por máquina.

## Ejecutar varios agentes a la vez

Cada chat de agente tiene su propia carpeta, así que los chats nunca sobrescriben el trabajo de otros:

1. Abre una nueva ventana de chat (Claude Code en VS Code: Cmd/Ctrl+Shift+Esc).
2. Escribe `/work bugs` (o `/work features`, `/work specs`, `/work ideas`, o simplemente `/work`; Codex: `$work`).
3. El agente se mueve a su propio git worktree, copia los archivos locales como `.env`, reserva el elemento más prioritario del tablero, lo construye y lo prueba, abre la PR y te entrega un plan de prueba.

Repite con tantos agentes como quieras, en cualquier máquina que tenga el proyecto clonado. La reserva en el tablero impide que dos agentes tomen el mismo issue, ya sea para construirlo, evaluarlo o escribir su especificación. Tu propio chat se queda en la carpeta principal para ideas, decisiones, pruebas y releases.

## Elegir un tracker

| | GitHub Projects | Linear |
|---|---|---|
| Coste | Gratis en todos los planes de GitHub | Plan gratuito con límites; de pago por usuario |
| Dónde | Junto a tu código, un solo inicio de sesión | Aplicación aparte |
| Uso por los agentes | `haam.py issue …` (cualquier agente) | El servidor MCP de Linear |
| Ideal para | Personas solas y equipos pequeños, que quieren todo en GitHub | Backlogs con más actividad, varios equipos, planificación más rica |

El mismo ciclo de vida, las mismas puertas y las mismas skills en ambos casos, y puedes cambiar más adelante. Consulta [TRACKER.md](template/i18n/es/docs/process/TRACKER.md).

## Compatibilidad con agentes

| | Reglas | Skills | Llamar a una skill | Linear (si se usa) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | comprobar en la primera ejecución | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` mediante `.gemini/settings.json` | por archivo | por archivo | por usuario |
| GitHub Copilot | `AGENTS.md` | por archivo | por archivo | por usuario |

En GitHub Projects todos los agentes usan los mismos comandos `haam.py issue`, así que no hay nada que conectar por herramienta. Detalles y ajustes seguros recomendados para cada herramienta: [AGENTS-SETUP.md](template/i18n/es/docs/setup/AGENTS-SETUP.md).

## Requisitos

- Un repositorio de GitHub. Los repositorios públicos lo tienen todo en el plan gratuito. En los **privados**, las reglas de rama necesitan GitHub Pro o Team, y exigir un aprobador para los despliegues a producción necesita GitHub Enterprise Cloud (sin él, tu `ship` es la decisión de release). [DECISIONS.md](template/i18n/es/docs/setup/DECISIONS.md) tiene los detalles.
- Un tracker: un tablero de GitHub Projects (gratis, en cualquier plan de GitHub) o un espacio de trabajo de Linear (cualquier plan)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Un secreto de Claude para los agentes revisores de la CI: un token de un plan de Claude (`claude setup-token`) o una clave de API de Anthropic (pago por uso; fija un límite de gasto)
- Cualquier agente de programación compatible

## Estructura del repositorio

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  i18n/          The same docs in other languages
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Versionado

HAAM sigue el [versionado semántico](https://semver.org):
- **Patch** (1.0.x): correcciones y redacción; `update` se aplica sin conflictos.
- **Minor** (1.x.0): nuevas skills, comprobaciones o documentos; compatible con versiones anteriores.
- **Major** (x.0.0): cambios que necesitan un paso de migración (p. ej., estados de Linear o comprobaciones obligatorias renombrados). El [CHANGELOG](CHANGELOG.md) enumera los pasos.

Instala siempre desde una etiqueta o una release, no desde `main`.

## Contribuir

Las ideas, los informes de bugs y las pull requests son bienvenidos. Consulta [CONTRIBUTING.md](CONTRIBUTING.md). Problemas de seguridad: consulta [SECURITY.md](SECURITY.md).

## Licencia

[MIT](LICENSE) © 2026 Jorge del Prado
