# Herramientas de agente: configuración por herramienta

HAAM funciona con cualquier agente de programación. Todas las herramientas leen las **mismas reglas** (`AGENTS.md`) y las **mismas skills** (`.agents/skills/`), y trabajan sobre el **mismo tracker**: un tablero de GitHub Projects (mediante `python3 tools/haam/haam.py issue …`, que cualquier agente puede ejecutar) o Linear (mediante su servidor MCP, `https://mcp.linear.app/mcp`). Solo cambia la fontanería.

Ejecuta `python3 tools/haam/haam.py agents` para ver qué está conectado en este repositorio, y `python3 tools/haam/haam.py dev` para comprobar tu máquina.

## Cómo adopta HAAM cada herramienta

| | Reglas | Skills | Llamar a una skill | MCP de Linear (solo proyectos con Linear) | Skills reservadas a personas |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importa `AGENTS.md` | `.claude/skills` (enlace a `.agents/skills`) | `/build APP-1` | `.mcp.json` (en el repositorio) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (en el repositorio) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | por usuario: `codex mcp add` | `agents/openai.yaml` en cada skill |
| **Grok Build** | comprobar en la primera ejecución (ver abajo) | `.grok/skills` (enlace a `.agents/skills`) | `/build APP-1` | lee `.mcp.json` | según el texto de la skill |
| **Gemini CLI** | `AGENTS.md` mediante `.gemini/settings.json` | seguir `SKILL.md` por nombre | "follow .agents/skills/build" | por usuario | según el texto de la skill |
| **GitHub Copilot** | `AGENTS.md` | seguir `SKILL.md` por nombre | "follow .agents/skills/build" | por usuario | según el texto de la skill |

Si una herramienta no carga las skills, dile: *"Abre `.agents/skills/<name>/SKILL.md` y síguelo."* Las skills son Markdown sin más.

## Conectar con el tracker (una vez por persona)

**GitHub Projects:** no hay nada que instalar en tu agente. Ejecuta `gh auth refresh -s project` una vez y prueba con `python3 tools/haam/haam.py issue list`. El resto de esta sección es para los proyectos con **Linear**.

Linear te hace iniciar sesión con tu propia cuenta (OAuth). Los agentes actúan como tú.

- **Claude Code:** abre `claude` en el repositorio → aprueba el servidor `linear` → `/mcp` → **linear** → inicia sesión.
- **Cursor:** Settings → MCP → `linear` aparece a partir de `.cursor/mcp.json` → actívalo → inicia sesión.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp` y después sigue la petición de inicio de sesión.
- **Grok Build:** lee `.mcp.json`; si no, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Inicia sesión cuando te lo pida.
- **Gemini CLI / Copilot / otros:** añade un servidor MCP remoto llamado `linear` con la URL `https://mcp.linear.app/mcp` en los ajustes de MCP de la herramienta.

**Prueba:** pide a tu agente *"Enumera los issues en Ready del equipo APP de Linear."*

## Ejecutar varios agentes a la vez

Cada chat de agente que cambia archivos necesita su propia carpeta (un git worktree); si no, los chats sobrescriben el trabajo de los demás. Empieza cada chat de agente con `/work` (Codex: `$work`): comprueba dónde está y prepara un worktree si hace falta. Tu propio chat se queda en la carpeta principal.

| Herramienta | Nuevo chat de agente |
|---|---|
| **Claude Code (VS Code)** | Nueva pestaña de chat: Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux), o Command Palette → "Claude Code: Open in New Tab". Escribe `/work`; Claude se mueve solo a un worktree. |
| **Claude Code (terminal)** | `claude --worktree` (o `-w <name>`) y después `/work`. |
| **Aplicación de escritorio de Claude** | Inicia una sesión con la opción **worktree** y después `/work`. |
| **Codex, Cursor y otros** | Usa la opción de worktree o de agentes en paralelo de la propia herramienta si la tiene, y después `/work`. Si no, escribe `/work` en la carpeta principal: crea un worktree con `haam.py worktree new` y te dice qué carpeta abrir en una nueva ventana. |

Los archivos locales que no están en Git (como `.env`) se copian en cada worktree nuevo a partir de la lista de `.worktreeinclude`. Limpia los worktrees terminados con `python3 tools/haam/haam.py worktree clean` (plan) y después `--apply`.

## Ajustes seguros por herramienta

Las barreras de seguridad fuertes viven en GitHub y en git, así que te protegen **haga lo que haga la herramienta**: nada de push a `main`, comprobaciones obligatorias, etiqueta de UAT, aprobación de despliegues, el hook de secretos en los commits (`make hooks`) y el escaneo de secretos de la CI. Los ajustes de la herramienta son una segunda capa que detiene los errores antes. Recomendado:

| Herramienta | Ajustes recomendados |
|---|---|
| **Claude Code** | Ya configurado en `.claude/settings.json`: pregunta antes de hacer push o abrir PR, bloquea fusiones, despliegues y lecturas de `.env`, y tiene un hook de escaneo de secretos antes de los commits. Consérvalo. |
| **Cursor** | Ejecución automática del agente: usa una lista de permitidos (targets de make, git status/diff/log, `gh pr view/checks`) y exige confirmación para `git push`, `gh pr create/edit/merge` y cualquier cosa con `deploy`. Añade `.env*` a la lista de ignorados de Cursor para que el agente no pueda leerlo. |
| **Codex** | Sandbox *workspace-write* y política de aprobación *on-request* (pregunta antes de acciones de red y de hacer push). Evita los modos de "acceso total" en este repositorio. |
| **Grok Build** | Usa sus reglas de permisos (se permiten a nivel de repositorio) para exigir aprobación en `git push`, `gh pr merge` y los comandos de despliegue; deniega la lectura de `.env*`. Admite hooks `PreToolUse`: puedes llamar a `bash scripts/scan-secrets.sh` antes de `git commit`, como hace el hook de Claude. Evita `--always-approve` fuera de la CI. |
| **Gemini CLI / Copilot** | Mantén activadas las confirmaciones para los comandos de shell; nunca apruebes automáticamente los push ni las fusiones. |

Nunca des a ninguna herramienta de agente tus credenciales de producción ni un token de GitHub con permisos de administrador.

## Comprobación de la primera ejecución para cada herramienta

Pregunta al agente, en el repositorio:
1. *"¿Cuáles son las reglas estrictas de este repositorio?"* Debería enumerar las reglas de `AGENTS.md` §3. Si no, dile que lea primero `AGENTS.md` y revisa en los ajustes de la herramienta el nombre del archivo de instrucciones.
2. *"¿Qué skills tienes para este proyecto?"* Debería enumerar idea, bug, assess, spec, next, work, build, uat… Si no, consulta la tabla de arriba.
3. *"Enumera los issues en Ready del equipo APP de Linear."* Esto comprueba la conexión con Linear.

## Registrar qué herramienta hizo el trabajo
El comentario de reserva en el issue y el campo **Hecho con (Built with)** de la PR registran la herramienta y el modelo. Al cabo de unas semanas puedes comparar los hallazgos de las revisiones y los fallos de UAT por herramienta.

## Revisión con otro modelo
Los agentes revisores de la CI usan Claude. Cuando el código se escribe con otra herramienta (Codex, Grok, Cursor con otro modelo), la revisión la hace además un modelo distinto, lo que es una comprobación extra útil.
