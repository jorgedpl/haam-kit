# Human-Agent Agile Methodology (HAAM)
## Guía de adopción para el administrador del proyecto

HAAM es una forma de crear software en la que **las personas deciden y los agentes ejecutan**. Todo trabajo va de la idea a producción por las mismas etapas, con puertas humanas en los puntos que importan. Todo vive en **Git** (conocimiento y código) y en el **tracker** (trabajo y estado): un tablero de **GitHub Projects** (gratis) o **Linear**. Las personas pueden usar distintos agentes de programación (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) con sus propias cuentas y aun así trabajar en paralelo.

Esta guía aplica HAAM a un repositorio existente en **seis fases, una media jornada en total**. Puedes detenerte después de cualquier fase y seguir teniendo algo útil.

---

## Conseguir el kit

El kit es la carpeta `template/` de https://github.com/jorgedpl/haam-kit. Usa siempre una versión publicada:
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
o descarga el zip desde la página de Releases. A partir de aquí, `<path-to-kit>` significa esa carpeta `template/`.

## El camino rápido: deja que lo haga tu agente

Pon el kit en algún sitio fuera de tu proyecto, abre tu agente de programación **en la carpeta raíz de tu proyecto** y dile:

> Lee `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` y síguelo para configurar HAAM en este repositorio. El kit está en `<path-to-kit>`.

El agente maneja la herramienta de configuración (`tools/haam/haam.py`) en todas las fases que siguen. Te hace unas pocas preguntas, te enseña cada cambio antes de hacerlo y te pasa los pocos pasos que necesitan tus contraseñas o claves para que los ejecutes en tu propia terminal. Usa el resto de esta guía para entender lo que está haciendo, o para hacerlo a mano.

### Quién hace qué durante la configuración

| Marcado como | Significa |
|---|---|
| `[agent]` | Lo hace tu agente de programación (o tú, si lo haces a mano) |
| `[YOU, in your terminal]` | Ejecutas tú el comando: implica un secreto (clave de API, inicio de sesión) que nunca debe pasar por el chat de un agente |
| `[YOU, in the browser]` | Un ajuste que GitHub o Linear solo ofrecen en su aplicación web |

---

## Qué incluye

```
START-HERE.md                 Kit entry point (not copied into your repo)
AGENTS.md                     Rules every agent reads, whatever the tool
CLAUDE.md                     Pointer to AGENTS.md for Claude Code
haam.config.json              Project settings for the setup tool (created by `config`; no secrets)
haam.lock.json                Installed kit version and file fingerprints (used by `update`)
docs/changes/                 One release note per shipped change (added by /uat)
Makefile                      Command contract: setup, hooks, dev, test, check, audit, secrets, smoke, deploy
tools/haam/haam.py            Setup tool: install, config, agents, github, github-project, linear, issue, worktree, invite, dev, doctor
scripts/scan-secrets.sh       Secret scan (gitleaks) shared by all commit hooks
.githooks/pre-commit          Blocks commits containing secrets (any human, any agent using git)
.agents/skills/               One skill per stage, shared by all agent tools
.worktreeinclude              Local files (like .env) to copy into each agent's worktree
.claude/                      Claude Code: settings (guard-rails), hooks, skills link
.cursor/mcp.json              Cursor: Linear connection (Linear projects)
.grok/skills                  Grok Build: skills link
.gemini/settings.json         Gemini CLI: read AGENTS.md
.mcp.json                     Linear connection (Claude Code, Grok; Linear projects)
.github/
  pull_request_template.md    Includes "Built with" (agent tool and model)
  workflows/ci.yml            Gate G3: tests on every PR
  workflows/security.yml      Gate G3: secret scan of every commit + dependency audit
  workflows/review.yml        Gate G3: independent AI reviewers (spec/quality + security)
  workflows/tracker-sync.yml    Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/              Idea and bug forms (GitHub Projects)
  workflows/gates.yml         Gate G4: blocks merge until UAT passed or overridden
  workflows/deploy.yml        Gate G5: production deploy waits for human approval
  review/REVIEWER.md          Instructions for the reviewer agent
  dependabot.yml              Dependency update PRs
docs/
  process/LIFECYCLE.md        The methodology: streams, stages, statuses, roles
  process/GATES.md            Gate checklists, code review, overrides
  process/TRACKER.md          How each tracker operation works on GitHub Projects and on Linear
  product/PRODUCT.md          Your product context (you confirm it)
  product/ARCHITECTURE.md     Map of your codebase (the agent drafts it)
  setup/HAAM-ADOPTION-GUIDE.md  This guide
  setup/DECISIONS.md          Every choice to make (accounts and plan, tracker, settings, limits, what to protect), with recommendations
  setup/AGENTS-SETUP.md       Per-tool setup: Claude Code, Cursor, Codex, Grok, Gemini, Copilot
  setup/LINEAR-SETUP.md       Linear configuration in detail
  setup/GITHUB-SETUP.md       GitHub configuration in detail
  ONBOARDING.md               Guide for new developers
  templates/                  idea, bug, assessment, feature-spec, uat-plan, adr
  decisions/0001-adopt-haam.md
  assessments/ specs/ uat/    Filled in automatically as work flows
```

### El ciclo de vida en una imagen

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### Los comandos

Aquí se escriben `/name` (Claude Code, Cursor, Grok). En Codex usa `$name`. En cualquier otra herramienta: *"sigue `.agents/skills/<name>/SKILL.md`"*.

| Comando | Etapa | Quién |
|---|---|---|
| `/idea <text>` | Capturar una idea | Cualquiera |
| `/bug <text>` | Informar de un problema | Cualquiera |
| `/assess APP-12` | Evaluar valor, esfuerzo, riesgo y viabilidad | Agente |
| `/triage` | Hacer el triaje de la bandeja, agrupar issues en epics (`group`), reordenar (`backlog`), perseguir el trabajo atascado (`stale`) | Solo personas |
| `/epic APP-9` | Dar forma a un epic: ficha, preguntas para ti, limpieza de sus issues | Solo personas |
| `/decide APP-12 approve` | Puerta G1 | Solo personas |
| `/spec APP-12` | Escribir una especificación lista para construir | Agente |
| `/work bugs` | Arrancar un agente en una nueva ventana de chat: su propio worktree y después `/next` | Cualquiera |
| `/next` | Elegir el siguiente elemento entre bugs, features e ideas | Agente |
| `/build APP-12` | Implementar con pruebas unitarias y abrir una PR | Agente |
| `/uat APP-12` | Escribir tu plan de prueba en local | Agente |
| `/test` | Probar un cambio y después `pass` → `ship`, o decir qué falla (G4 y G5) | Solo personas |
| `/uat-result APP-12 pass` | Registrar solo el resultado de una prueba (G4) | Solo personas |
| `/override APP-12 "reason"` | Saltarse la UAT en una emergencia | Solo personas |
| `/release APP-12` | Cerrar tras el despliegue | Solo personas |
| `/haam-setup` | Adoptar HAAM en un repositorio | Administrador del proyecto |
| `/haam-onboard` | Preparar a un desarrollador nuevo | Desarrollador nuevo |
| `/haam-update` | Actualizar a una nueva versión del kit | Administrador del proyecto |

### Cómo funciona la revisión de código

Ningún agente revisa nunca su propio trabajo, y los secretos los detecta un escáner, no el criterio de nadie. Todo cambio pasa por seis capas:

| Capa | Cuándo | Qué comprueba | Quién lo hace |
|---|---|---|---|
| 1. Guarda local de secretos | Antes de cada commit | Claves, tokens y contraseñas en los cambios; si los encuentra, bloquea el commit | gitleaks mediante el hook de git (todo el mundo), más hooks de la herramienta del agente donde se admiten |
| 2. Autocomprobación | Antes de abrir una PR | Las pruebas pasan; autorrevisión de seguridad de su propio diff | El agente que lo construyó |
| 3. CI automática | Cada actualización de una PR | Pruebas, lint, tipos (`ci`); secretos en cada commit (`secrets`); bibliotecas vulnerables (`dependencies`) | GitHub Actions |
| 4. Revisión independiente de IA | Cada actualización de una PR (no borradores ni PR solo de documentación) | ¿Cumple la especificación? ¿Las pruebas son honestas? Bugs, ampliaciones del alcance, incumplimientos de las reglas (`ai-review`). Vulnerabilidades de seguridad (`security-review`) | Un Claude aparte en GitHub Actions que nunca vio escribir el código (de otro modelo, cuando el código salió de otra herramienta) |
| 5. Revisión de código humana | PR que tocan áreas protegidas | Lógica central, autenticación, pagos, datos personales, migraciones, infraestructura, configuración de los agentes | El product owner o un desarrollador designado |
| 6. Aceptación humana | Cada PR de código | Funciona de verdad (puerta G4, UAT) | Product owner |

- El revisor publica un comentario con **Blocking / Should fix / Nits**. Los hallazgos bloqueantes impiden la fusión.
- El agente que construye corrige los elementos Blocking y hace push; las revisiones se vuelven a ejecutar automáticamente. Si no está de acuerdo, responde en la PR y pregunta a una persona. Tras **dos** rondas fallidas, se detiene y pasa el testigo.
- Los revisores de IA pueden bloquear, pero nunca aprobar ni fusionar. Solo una persona puede imponerse a ellos, con la etiqueta de PR `ai-review-overruled`.
- Si un secreto real llega alguna vez a GitHub: revócalo y rótalo de inmediato, y después pide a un administrador que reescriba el historial de la rama. No basta con borrarlo en un commit nuevo.

Todas las reglas: `docs/process/GATES.md`. Instrucciones del revisor que puedes ajustar: `.github/review/REVIEWER.md`.

---

## Antes de empezar

Necesitas:
- [ ] Acceso de administrador al repositorio de GitHub. Si es privado, las reglas de rama necesitan GitHub Pro o Team, y exigir un aprobador en los despliegues a producción necesita Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Un tracker: **GitHub Projects** (nada adicional; gratis en todos los planes) o acceso de administrador a un espacio de trabajo de **Linear**
- [ ] Un agente de programación instalado y con la sesión iniciada, con tu propia cuenta
- [ ] Python 3, Git, Make y la GitHub CLI con la sesión iniciada (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, o desde su página de releases en GitHub)
- [ ] Un secreto de Claude para los agentes revisores: un token de un plan de Claude (`claude setup-token`) o una clave de API de Anthropic con un límite de gasto mensual (console.anthropic.com)
- [ ] Que tu proyecto funcione hoy en local

Decide ahora:
1. **Tracker:** GitHub Projects (gratis, todo en GitHub) o Linear (más agradable de usar, plan gratuito limitado). Puedes cambiar más adelante.
2. **Clave del producto:** un código corto, p. ej. `ACM`, `SHOP`, `CRM` (la clave del equipo de Linear si usas Linear). El kit usa `APP` como marcador de posición hasta que `config` lo sustituye en todas partes.
3. **Product owner:** la única persona que aprueba ideas, especificaciones, UAT y despliegues (más, opcionalmente, alguien que apruebe en su lugar).
4. **Herramientas de agente** que usará tu equipo.

Comprueba tu máquina cuando quieras con: `python3 <kit>/tools/haam/haam.py dev`

---

## Fase 1: Instalar el kit (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

La documentación está en inglés salvo que añadas `--language es` (o `fr`, `de`, `it`, `nl`, `pt`) a los dos comandos. Los agentes también escriben entonces en ese idioma las especificaciones, los issues, los planes de UAT y los mensajes; los comandos, las etiquetas y el código siguen en inglés. Cámbialo más adelante con `haam.py config --language <code>` y después el `update --target . --apply` del kit.

El instalador **nunca sobrescribe** tus archivos:
- Los archivos nuevos se añaden.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` y `.claude/settings.json` se **fusionan** automáticamente.
- A `.gitignore` se le añade una vez un bloque de HAAM al final.
- Cualquier otro archivo que ya tengas se deja tal cual, y la versión del kit se guarda en `.haam/incoming/` para que la fusiones tú (o el agente).

Cómo fusionar los conflictos habituales:

| Si tu repositorio ya tiene… | Haz esto |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Mueve el conocimiento propio del proyecto (convenciones, trampas, comandos) a `docs/product/ARCHITECTURE.md` o a una sección "Project specifics" al final de `AGENTS.md`. Después usa el `AGENTS.md` y el `CLAUDE.md` del kit. Conserva las reglas `.mdc` de Cursor solo para detalles acotados por glob |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` mueve tus skills a `.agents/skills/` y enlaza la carpeta. Antes, cambia el nombre de las que choquen con nombres de skills de HAAM |
| `Makefile` | Añade los targets del kit a los tuyos |
| `.github/workflows/` con CI | Conserva tu CI, pero asegúrate de que un job llamado **`ci`** ejecuta tu batería completa de pruebas en las PR. Añade `gates.yml`, `security.yml`, `review.yml`. Compara tu despliegue con `deploy.yml` (fase 4) |
| `.github/pull_request_template.md` | Incorpora "Hecho con (Built with)", "Criterios de aceptación → pruebas" y "Lista de comprobación (G3)" |
| `.pre-commit-config.yaml` o Husky | Consérvalo y llama desde él a `scripts/scan-secrets.sh` en lugar de usar `.githooks/` |
| `CHANGELOG.md`, `.github/dependabot.yml` | Conserva los tuyos (añade el ecosistema `github-actions` a Dependabot si falta) |

Borra `.haam/incoming/` cuando termines.

---

## Fase 2: Configurarlo y enseñarle tu proyecto (45 min)

1. **Ajustes del proyecto** `[agent]` (con tus respuestas):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Esto escribe `haam.config.json` y sustituye el marcador `APP` y el nombre del producto en todos los archivos de HAAM.

2. **Herramientas de agente** `[agent]`: `python3 tools/haam/haam.py agents --apply`. Enlaza las skills compartidas para Claude Code y Grok, comprueba los archivos de Cursor, Codex, Gemini y Copilot, y enumera los pasos que tiene que dar cada persona. Detalles: `docs/setup/AGENTS-SETUP.md`.

3. **Contrato de comandos** `[agent]`: rellena cada `TODO(setup)` del `Makefile` (setup, dev, test, lint, typecheck, build, audit) y los pasos de entorno de ejecución de los workflows, a partir de los comandos reales de tu proyecto. Después, `make check` tiene que pasar con el código actual. Si ya hay pruebas que fallan en `main`, corrígelas o márcalas primero: HAAM depende de que verde signifique verde. Si `make audit` informa de vulnerabilidades antiguas altas o críticas, corrígelas o regístralas como bugs y sube el umbral temporalmente.

4. **Mapa de la arquitectura** `[agent]`: rellena `docs/product/ARCHITECTURE.md` a partir del código (menos de 150 líneas) y propón rutas reales para las áreas protegidas en `AGENTS.md` §4. Tú lo revisas.

5. **Contexto del producto** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: qué es, usuarios, recorridos que nunca deben romperse, innegociables, prioridades actuales. Es lo que lee cada agente para tomar decisiones de criterio.

6. **Documento de incorporación** `[agent]`: rellena los elementos `TODO(setup)` de `docs/ONBOARDING.md` (URL para clonar, entorno de ejecución, URL local).

7. **Higiene de secretos** `[agent]`: `make hooks` y después escanea el historial una vez: `gitleaks git --redact -v .` Todo lo que sea real hay que **revocarlo y rotarlo** con el proveedor: ya está expuesto a cualquiera con acceso al repositorio. Tú apruebas las huellas de falsos positivos que se añadan a `.gitleaksignore`.

8. **Chats en paralelo** `[agent]`: enumera en `.worktreeinclude` los archivos solo locales que necesita la aplicación (como `.env`), excluye `.claude/worktrees/` de cualquier herramienta que escanee toda la carpeta (ejecutor de pruebas, linter, watcher) y prueba un worktree nuevo: `python3 tools/haam/haam.py worktree new setup-check`, después `make setup && make check` dentro de él y luego `git worktree remove .claude/worktrees/setup-check`. A partir de entonces, cada chat de agente nuevo empieza con `/work`.

9. **Comprobación:** `python3 tools/haam/haam.py doctor` muestra lo que queda.

---

## Fase 3: Abrir la PR de adopción (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Esto hace que las comprobaciones existan en GitHub para poder exigirlas. El primer comentario de revisión de IA aparecerá en esta PR.

---

## Fase 4: Puertas de GitHub (20 min)

1. **Planificar y después aplicar** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Crea las etiquetas, un conjunto de reglas en la rama predeterminada (PR obligatoria, las seis comprobaciones obligatorias, sin force push; los administradores pueden saltárselo solo al fusionar una PR, para emergencias, nunca haciendo push a main; "up to date before merging" desactivado, para ahorrar ejecuciones de CI). Si el conjunto de reglas ya existe, solo añade lo que falta y conserva tus ajustes (`--reset` lo sustituye). También crea el entorno `production` con tus aprobadores y la variable `PRODUCTION_URL`, y activa el escaneo de secretos, la protección de push y Dependabot donde tu plan lo permite.
2. **Clave del revisor** `[YOU, in your terminal]`: un solo secreto ejecuta las dos revisiones. O bien `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` con el token de `claude setup-token` (usa tu plan de Claude), o bien `gh secret set ANTHROPIC_API_KEY -R owner/repo` con una clave de API dedicada (se factura por revisión; con ella, la revisión de seguridad usa la acción de revisión de seguridad de Anthropic). Cualquiera de los dos comandos pide el valor sin mostrarlo.
3. **PR desde forks** `[YOU, in the browser]`: Settings → Actions → General → exigir aprobación para colaboradores externos.
4. **Despliegues:**
   - *¿Ya despliegas desde GitHub Actions?* Añade `environment: production` a tu job de despliegue: solo con eso tienes la puerta G5. Borra el `deploy.yml` del kit o consérvalo como referencia.
   - *¿Despliegas de otra forma* (la integración con Git de una plataforma de hosting, a mano)? O bien llevas los despliegues a `deploy.yml` (rellena `make deploy`), o bien conservas tu método y tratas G5 como un paso manual: el product owner despliega tras la fusión y después ejecuta `/release`. Desactiva el despliegue automático al hacer push si se saltara la aprobación.
5. **Repositorios privados:** las reglas de rama necesitan GitHub Pro o Team, y exigir un aprobador en los despliegues a producción necesita Enterprise Cloud; la herramienta te dice lo que permite tu plan. Sin aprobador, tu `ship` es la decisión de release: pon `deploy_approval: automatic` (`docs/setup/DECISIONS.md` §1).

Detalles y equivalentes manuales: `docs/setup/GITHUB-SETUP.md`.

---

## Fase 5: El tracker (20 min)

### Opción A: GitHub Projects (gratis)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (permite que tu inicio de sesión de GitHub use Projects).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` token de automatización, para que las tarjetas se muevan cuando se abren y se fusionan las PR: crea un token clásico en github.com/settings/tokens con el permiso `project` (más `repo` si el repositorio es privado) y después `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` en el tablero, crea las vistas que enumera la herramienta: Board agrupado por Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Prueba: `python3 tools/haam/haam.py issue list`.

Los agentes usan `python3 tools/haam/haam.py issue …` para todas las operaciones del tablero (`docs/process/TRACKER.md`), así que funciona igual desde Claude Code, Cursor, Codex, Grok o cualquier otra herramienta.

### Opción B: Linear
1. **Estados, etiquetas, equipo** `[YOU, in your terminal]` (necesita tu clave de API personal de Linear, que nunca pasa por un agente):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Crea el equipo si hace falta, activa Triage, crea los 12 estados (cambiando el nombre del "Todo" predeterminado de Linear a "Ready") y las 9 etiquetas. Nunca borra nada; enumera los estados sobrantes para que los archives.
2. **Ajustes solo del navegador** `[YOU, in the browser]`: conecta GitHub, las automatizaciones de PR (PR en borrador → In Progress, PR lista para revisión → In Review, fusionada → Deploying), el formato de nombre de rama `{issue-identifier}-{issue-title}` y las vistas guardadas. Consulta `docs/setup/LINEAR-SETUP.md`.
3. **Conecta tu agente** a Linear (`docs/setup/AGENTS-SETUP.md`) y prueba: *"Enumera los issues del equipo ACM de Linear."*

**¿Ya tienes un backlog?** Pide a tu agente que lo traiga al tracker (los issues de GitHub se pueden añadir sin más al tablero). Ponlo todo en **Triage**, haz el triaje una vez (`stream:bug`, `stream:idea`, o `stream:feature` + Backlog) y especifica solo los cinco primeros.

---

## Fase 6: Fusión, ciclo de prueba y personas

### Fusionar la PR de adopción
Cuando las comprobaciones estén en verde, añade tú `uat-passed` (la puerta ya está activa, así que hasta esta PR pasa por ella) y fusiona. Si los agentes revisores se ponen quisquillosos con el propio kit, imponte con `ai-review-overruled`. Ejecuta `python3 tools/haam/haam.py doctor --role admin` para una comprobación final.

### Haz un ciclo completo (45–60 min)
Elige algo pequeño y real. Llévalo una vez por todas las etapas:

| Paso | Escribes | Qué debería pasar |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Issue nuevo en Triage, etiqueta `stream:idea` (en GitHub: `#1`; en Linear: `ACM-1`) |
| 2 | `/assess #1` | Evaluación con commit en la rama del issue (sin PR); el issue pasa a Decision |
| 3 | `/decide #1 approve medium` | El issue pasa a Backlog, la etiqueta pasa a ser `stream:feature` |
| 4 | `/spec #1` | Especificación con criterios de aceptación, en la misma rama |
| 5 | Lee la especificación (enlace en el issue) y dile al agente "spec approved" | El issue recibe `agent-ready` y pasa a Ready |
| 6 | `/build #1` | Lo reserva, crea la rama, programa, escribe las pruebas, se autorrevisa, escribe el plan de UAT y sube la rama. Todavía sin PR (test-first, el predeterminado) |
| 7 | `/uat #1` (`/build` lo ejecuta) | El issue pasa a UAT; recibes un aviso |
| 8 | `/test #1` | El agente pone el cambio en tu máquina, arranca la aplicación y te da una lista breve |
| 9 | Pruébalo y responde `pass` | El agente abre la PR con la etiqueta `uat-passed`; `ci`, `secrets`, `dependencies` y los agentes revisores se ejecutan una vez; `release-gate` se pone en verde; el agente pregunta "¿Lo llevamos a producción?" |
| 10 | Responde `ship` | El agente fusiona, aprueba por ti el despliegue a producción, espera y cierra el issue: Done |
| 11 | (pruébalo una vez) `/test` sobre un cambio, pero describiendo un problema | Vuelve a los agentes con tus notas (`uat-failed`) y regresa a ti cuando está arreglado |

(En Linear los IDs tienen la forma `ACM-1`.)

Después prueba una vez los casos límite: pide al agente que haga commit de una clave falsa en una rama desechable (`AKIA` + 16 letras mayúsculas o dígitos): el commit tiene que quedar bloqueado. Luego suspende una UAT y usa una anulación. Ajusta las skills de `.agents/skills/` o el proceso de `docs/process/LIFECYCLE.md` donde algo no te haya convencido.

**Prueba también una segunda herramienta de agente en el ciclo de prueba** (p. ej., Cursor o Codex para el paso 6). Así confirmas que las reglas y las skills compartidas funcionan más allá de tu herramienta principal.

### Añadir desarrolladores
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: acceso de escritura en GitHub (no de administrador), acceso al tablero de GitHub Projects o una invitación a Linear.
2. Envíale el enlace del repositorio y las credenciales de prueba (gestor de contraseñas o enlace de un solo uso, nunca por chat ni por correo).
3. La persona abre su propio agente en el repositorio y ejecuta `/haam-onboard` (Codex: `$haam-onboard`).
4. En cuanto haya dos personas o más: la herramienta pone "1 approval required" cuando añades aprobadores suplentes (`config --backup-approvers` y después `github --apply`), y puedes añadir `.github/CODEOWNERS` para las áreas protegidas.

### Dejar que los agentes trabajen de forma semiautónoma

| Nivel | Cómo | Cuándo |
|---|---|---|
| **1. Supervisado** | Escribes `/next` o `/build` y apruebas cada push y cada PR | Las primeras 2–3 semanas |
| **2. Por lotes** | 2–3 ventanas de chat (cualquier combinación de herramientas y máquinas), cada una arrancada con `/work`, que le da su propio worktree; revisas las PR por lotes | Cuando las especificaciones salen bien de forma fiable |
| **3. Programado** | Una tarea programada ejecuta un agente sin interfaz con `/next` y se detiene en UAT | Cuando confías en las puertas |

En todos los niveles, los agentes se detienen en las puertas humanas.

### Costes de funcionamiento
Además de GitHub, Linear (si lo usas) y la suscripción de agente de cada persona, el único coste por uso son los agentes revisores: dos llamadas a Claude por cada push revisado a una PR, facturadas a `ANTHROPIC_API_KEY` o descontadas de tu plan de Claude (`CLAUDE_CODE_OAUTH_TOKEN`). Mantén activado el límite de gasto y las PR pequeñas.

### Mantenerse al día
Las nuevas versiones del kit se publican en https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` te avisa cuando sale una. Ejecuta `/haam-update` (Codex: `$haam-update`) en una rama: los archivos que nunca cambiaste se actualizan, tus personalizaciones se conservan y, donde han cambiado los dos, el agente los fusiona. El CHANGELOG enumera los pasos de migración que haya.

### Tu ritmo como product owner
A diario (10–15 min): prueba lo que está en **UAT**, vacía **Triage** (`/triage`). Cada semana (30–45 min): decide todo lo que está en **Decision**, reordena el backlog (`/triage backlog`), persigue el trabajo atascado (`/triage stale`), revisa **Parked** y cierra las **anulaciones**. La guía completa, con reglas de prioridad y listas de comprobación: `docs/process/PRODUCT-MANAGER.md`.

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| No sabes qué queda | – | `python3 tools/haam/haam.py doctor --role admin` |
| El agente no sigue las reglas | La herramienta no lee `AGENTS.md` | Comprobación de la primera ejecución en `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` dice que el inicio de sesión no puede usar Projects | Al inicio de sesión de gh le falta el permiso `project` | `gh auth refresh -s project` |
| Las tarjetas del tablero no se mueven al abrir o fusionar PR | Falta `HAAM_PROJECT_TOKEN`, o la PR no dice `Refs #123` | Añade el secreto (fase 5); revisa la descripción de la PR |
| El agente no ve Linear | MCP sin conectar o sin sesión iniciada | Pasos por herramienta en `docs/setup/AGENTS-SETUP.md` |
| Las skills aparecen dos veces en Cursor | Cursor lee tanto `.agents/skills` como `.claude/skills` | Desactiva la compatibilidad con las skills de Claude en los ajustes de Cursor |
| Faltan `.claude/skills` o `.grok/skills` tras clonar (Windows) | Enlaces simbólicos de Git desactivados | `git config core.symlinks true` y vuelve a clonar, o `haam.py agents --apply` (copia en lugar de enlazar) |
| `haam.py github` dice que los conjuntos de reglas o las aprobaciones no están disponibles | Repositorio privado en un plan gratuito | Mejora el plan, o protege a mano y confía en las comprobaciones |
| `haam.py linear` da error en un paso | Cambio en la API o permisos | Termina ese paso a mano con `docs/setup/LINEAR-SETUP.md` |
| Dos chats cambiaron los mismos archivos o la misma rama | Compartían una carpeta | Empieza cada chat de agente con `/work` (su propio worktree) |
| Las pruebas o el linter encuentran archivos duplicados en `.claude/worktrees/` | La herramienta escanea toda la carpeta | Excluye `.claude/worktrees/` en la configuración de esa herramienta |
| Un worktree no puede ejecutar la aplicación | Faltan archivos locales | Añádelos a `.worktreeinclude` y después `haam.py worktree prep` en el worktree |
| `/build` se niega a empezar | El issue no está en Ready, o le falta `agent-ready` | `/spec` y apruébala, o mueve tú el issue a Ready |
| Los estados de Linear no se mueven con los eventos de las PR | Integración con GitHub o automatizaciones sin configurar | Team settings → Workflow → PR automations; el título de la PR tiene que empezar por el ID del issue |
| `release-gate` sigue en rojo después de `uat-passed` | El workflow no se volvió a ejecutar | Quita la etiqueta y vuelve a añadirla |
| Falta una comprobación obligatoria en la lista | Todavía no se ha ejecutado | Abre primero cualquier PR |
| Commits bloqueados: "gitleaks is not installed" | Falta gitleaks en esa máquina | Instálalo y después `make hooks` |
| Commit bloqueado por un secreto que no lo es | Falso positivo | Una persona añade la huella a `.gitleaksignore` en un commit revisado |
| `ai-review` o `security-review` pendiente o con error | Sin secreto del revisor (`CLAUDE_CODE_OAUTH_TOKEN` o `ANTHROPIC_API_KEY`), PR desde un fork, o se quedó sin turnos | Añade el secreto; vuelve a ejecutarlo; sube `--max-turns`; o `ai-review-overruled` |
| Revisor demasiado estricto | Instrucciones sin ajustar | Edita `.github/review/REVIEWER.md` |
| `dependencies` falla en todas las PR | Vulnerabilidades antiguas | Corrígelas, o sube el umbral temporalmente y síguelas como bugs |
| Especificaciones demasiado vagas, las construcciones salen mal | G2 demasiado laxa | Endurece la Definition of Ready en `docs/process/GATES.md` |

---

## Principios

1. **Las personas deciden, los agentes ejecutan.**
2. **Si no está en Git o en el tracker, no existe** para la siguiente persona o el siguiente agente.
3. **Porciones pequeñas:** un issue, una rama, una PR, revisable en 15 minutos.
4. **Las puertas son baratas de pasar y caras de saltar.** Las anulaciones están permitidas, siempre se registran y siempre tienen seguimiento.
5. **Verde significa verde.** Nunca debilites una prueba para pasar una puerta.
6. **Nadie se corrige sus propios deberes.** El agente que escribe el código nunca lo revisa; los secretos los detectan herramientas, no el criterio de nadie.
7. **Cualquier agente, las mismas reglas.** Las herramientas son intercambiables; el proceso y las puertas, no.
