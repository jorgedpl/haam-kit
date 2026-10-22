# Incorporación de desarrolladores

Te damos la bienvenida. Este repositorio lo construyen personas y agentes de programación que trabajan juntos con la **Human-Agent Agile Methodology (HAAM)**. Puedes usar la herramienta de agente que prefieras: Claude Code, Cursor, Codex, Grok, Gemini o Copilot. Esta guía te lleva de cero a tu primer issue en una hora aproximadamente.

## La forma rápida: deja que tu agente te incorpore

1. Clona el repositorio y abre tu herramienta de agente en su carpeta raíz:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Dile a tu agente:
   - Claude Code, Cursor o Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Cualquier otra herramienta: *"Lee `.agents/skills/haam-onboard/SKILL.md` y síguelo."*

Comprueba tu máquina, tus accesos y la conexión con el tracker, configura tus hooks locales y tu `.env`, ejecuta las comprobaciones del proyecto, te explica cómo trabajamos y te sugiere un primer issue. Los pasos que necesitan tu contraseña o tus claves los haces tú, en tu propia terminal o editor. Nunca pegas secretos en el chat.

¿Prefieres hacerlo a mano? Las secciones siguientes cubren lo mismo.

---

## 1. Lee primero (15 minutos)
1. `AGENTS.md`: las reglas que sigue cada agente, sea cual sea la herramienta. También se aplican a ti.
2. `docs/process/LIFECYCLE.md`: flujos, estados, puertas, quién hace qué.
3. `docs/process/GATES.md`: listas de comprobación, revisión de código y anulaciones.
4. `docs/product/PRODUCT.md` y `docs/product/ARCHITECTURE.md`: qué estamos construyendo y cómo está estructurado.

## 2. Cuentas que necesitas
| Cuenta | Para qué | Qué pedir |
|---|---|---|
| GitHub | Código, PR, CI | Acceso de escritura al repositorio |
| Tracker | Backlog y estado | **GitHub Projects:** acceso al tablero (viene con la invitación al repositorio). **Linear:** pertenecer al equipo **APP** |
| Tu herramienta de agente | Agente de programación | Tu **propia** cuenta (Claude, Cursor, OpenAI, xAI…). Nunca compartas cuentas |
| Servicios de prueba | Ejecutar en local | Solo credenciales de prueba, que te da el product owner |

El administrador del proyecto te invita con un solo comando: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. **No** recibirás credenciales de producción; los despliegues pasan por GitHub con aprobación.

## 3. Instala las herramientas
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (obligatorio; sin él se bloquean los commits): en macOS `brew install gitleaks`; en otros sistemas: https://github.com/gitleaks/gitleaks/releases
- Entorno de ejecución del lenguaje de este repositorio: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Tu herramienta de agente

Compruébalo todo con: `python3 tools/haam/haam.py dev`

## 4. Pon el código en marcha
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Conecta con el tracker
Mira `"tracker"` en `haam.config.json`:
- **GitHub Projects:** ejecuta `gh auth refresh -s project` una vez y después prueba: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** sigue la sección de tu herramienta en `docs/setup/AGENTS-SETUP.md` (un solo inicio de sesión) y después pide a tu agente: *"Enumera los issues en Ready del equipo APP de Linear."*

## 6. Tus ajustes personales (no compartidos)
Las notas y preferencias personales van en archivos ignorados por git: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, o los ajustes de usuario de tu herramienta. Nunca pongas ahí reglas compartidas. Si algo debería aplicarse a todo el mundo, propón un cambio en `AGENTS.md` mediante una PR.

## 7. El flujo de trabajo diario
Más abajo los comandos se escriben `/name`; en Codex usa `$name`.

| Quieres… | Haz esto |
|---|---|
| Ver lo que está esperando | La vista del tracker **Agent queue** (para construir) o **Waiting on me** |
| Arrancar un agente en una nueva ventana de chat | `/work` (o `/work bugs`) |
| Empezar a trabajar en este chat | `/next`, o `/build APP-123` |
| Hacer triaje y priorizar (product owner) | `/triage`, `/triage group`, `/epic` y `docs/process/PRODUCT-MANAGER.md` |
| Registrar una idea | `/idea …` |
| Informar de un bug | `/bug …` |
| Convertir una idea aprobada en una especificación | `/spec APP-123` |
| Probar un cambio (product owner) | `/test` y después `pass` → `ship`, o di qué falla |
| Probar el cambio de otra persona (desarrollador) | Sigue `docs/uat/APP-123-*.md` y después avisa al product owner |
| Comprobar tu configuración | `python3 tools/haam/haam.py doctor` |

### Ejecutar agentes en paralelo
Abre una nueva ventana de chat por agente y escribe `/work` (o `/work bugs`, `/work features`, `/work specs`, `/work ideas`; Codex: `$work`). El agente obtiene su propia copia del proyecto (un git worktree en `.claude/worktrees/`), copia los archivos locales que aparecen en `.worktreeinclude` (como `.env`), elige el elemento más prioritario y lo lleva hasta el traspaso. Mantén tu propio chat en la carpeta principal para ideas, decisiones y pruebas.

- **Claude Code en VS Code:** nueva pestaña de chat con Cmd+Shift+Esc (Mac) o Ctrl+Shift+Esc (Windows/Linux). En una terminal: `claude --worktree`.
- **Otras herramientas:** si la herramienta tiene su propia opción de worktree o de agentes en paralelo, úsala; si no, `/work` crea el worktree y te dice qué carpeta abrir en una nueva ventana.
- **Otra máquina:** lo mismo. La reserva en el tracker impide que dos agentes tomen el mismo issue; pon nombre a la máquina cuando te lo pida, para que el comentario de reserva muestre dónde se está ejecutando.
- **Limpia** de vez en cuando los worktrees terminados: `python3 tools/haam/haam.py worktree clean` (plan) y después `--apply`.
- **Probar la rama de un agente:** el plan de UAT usa `git switch --detach origin/<branch>`, que funciona mientras el worktree del agente siga teniendo la rama.

### Ejecutar agentes de forma semiautónoma
- **Con supervisión:** escribe `/next`, revisa lo que elige y déjalo trabajar. Tu herramienta debería preguntar antes de hacer push o abrir PR (consulta los ajustes seguros en `docs/setup/AGENTS-SETUP.md`).
- **Sin supervisión:** una tarea programada o un cron ejecuta tu agente sin interfaz con el prompt `/next` (Codex: `$next`). Solo toma trabajo que ha pasado su puerta, y se detiene en UAT para que pruebe una persona.
- Los agentes se detienen en cada puerta humana por diseño. Tu trabajo es mantener corta la vista **Waiting on me**.

## 8. Cómo se revisa tu trabajo
Cada PR la comprueban pruebas, un escaneo de secretos, una auditoría de dependencias y dos revisores de IA independientes (especificación/calidad y seguridad) que nunca vieron escribir el código. Corrige sus hallazgos **Blocking**; si crees que alguno es erróneo, responde en la PR y pregunta al product owner, que puede imponerse con la etiqueta `ai-review-overruled`. Las áreas protegidas reciben además una revisión humana. Detalles: `docs/process/GATES.md` § Cómo funciona la revisión de código.

**Si alguna vez haces commit de un secreto real:** avisa al product owner de inmediato. Hay que revocarlo y rotarlo, aunque lo borres en el siguiente commit.

## 9. Reglas que vale la pena repetir
- Los agentes no hacen push a `main`, ni fusionan, ni despliegan.
- Ni secretos ni datos personales reales en el código, las pruebas, los fixtures, el tracker o el chat. Los datos personales están protegidos por ley (p. ej., el RGPD).
- Un issue → una rama → una PR, lo bastante pequeña para revisarla en 15 minutos.
- Rellena **Hecho con (Built with)** en cada PR (tu herramienta y tu modelo).
- Si no está en Git o en el tracker, no existe para la siguiente persona.

## 10. Pedir ayuda
- Preguntas sobre el proceso: pregunta a tu agente *"según LIFECYCLE.md, ¿qué debería pasar cuando…?"*
- Accesos y credenciales: el product owner.
- Mejorar el proceso: abre un `/idea` con la etiqueta `area:process`. Los cambios en `AGENTS.md`, `.agents/`, las carpetas de configuración de los agentes y `.github/` necesitan la revisión del product owner.
