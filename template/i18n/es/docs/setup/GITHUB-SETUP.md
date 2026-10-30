# Configuración de GitHub (una vez, unos 30 minutos, administrador del repositorio)

Esto convierte las puertas G3–G5 de convenciones en reglas que impone GitHub.

> **Automatizado:** las etiquetas (§1), las reglas de rama (§2), el entorno de producción (§4) y las funciones de seguridad (§3b–c) las hace `python3 tools/haam/haam.py github --apply` (antes, mira el plan sin `--apply`). Esta página es el equivalente manual, más los pasos que GitHub solo ofrece en el navegador. El secreto del revisor lo añades siempre tú: `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (token de `claude setup-token`, tu plan de Claude) o `gh secret set ANTHROPIC_API_KEY -R owner/repo` (clave de API, se factura por revisión). Cualquiera de los dos ejecuta las dos revisiones.

## 1. Etiquetas
Crea estas etiquetas del repositorio (Issues → Labels), o ejecuta:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Protección de la rama `main`
Settings → **Rules → Rulesets** → New branch ruleset (o la protección de rama clásica, Branch protection), con destino `main`:

- ✅ Restringir los borrados; bloquear los force push
- ✅ Exigir una pull request antes de fusionar
  - Aprobaciones obligatorias: **1** cuando haya una segunda persona; **0** mientras no haya nadie más (la etiqueta de UAT es tu aprobación)
  - ✅ Descartar las aprobaciones antiguas cuando se suban commits nuevos
- ✅ Exigir que pasen las comprobaciones de estado (deja desactivado "require branches to be up to date": vuelve a ejecutar la CI en cada PR abierta tras cada fusión)
  - Comprobaciones obligatorias: **`ci`** (o **`ci-local`** cuando `ci` es `local`; omítelo cuando `ci` es `off`), **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** y **`release-gate`** (aparecen en la lista cuando los workflows se han ejecutado una vez en una PR). `haam.py settings --apply` / `github --apply` añade las comprobaciones que piden los ajustes y quita las de HAAM que ya no piden (p. ej. `ci` cuando pasas a `off`)
- ✅ Exigir un historial lineal (opcional, mantiene limpio el historial)
- **Lista de excepciones (bypass list):** solo los administradores del repositorio, **solo para pull requests** (nunca "always": los agentes trabajan con el inicio de sesión de una persona, a menudo de un administrador, y si no podrían hacer push directamente a `main`). Es el bypass de emergencia de nivel 2 de `docs/process/GATES.md`.

**Auto-merge** (Settings → General → Pull Requests → *Allow auto-merge*; `haam.py github --apply` lo activa): solo lo usa el carril sin UAT, para las PR cuyos issues marcaste con `uat:skip`. La puerta lo activa para esas PR con el secreto `HAAM_PROJECT_TOKEN` (`docs/process/TRACKER.md`), y GitHub solo fusiona cuando pasan todas las comprobaciones obligatorias. Si exiges aprobaciones, el carril también espera una.

## 3. Revisión de código y seguridad

### 3a. Un secreto de Claude para los agentes revisores
Los revisores independientes (`.github/workflows/review.yml`) ejecutan Claude en GitHub Actions. Un único secreto del repositorio ejecuta las dos revisiones (Settings → **Secrets and variables → Actions** → New repository secret). Elige uno de estos:
- **`CLAUDE_CODE_OAUTH_TOKEN`:** ejecuta `claude setup-token` y usa el token que imprime. Las revisiones se descuentan entonces de ese plan de Claude.
- **`ANTHROPIC_API_KEY`:** una clave de API dedicada a este repositorio, de console.anthropic.com, con un límite de gasto mensual. Se factura por revisión, aparte de la suscripción de Claude de nadie. Con ella, la revisión de seguridad usa la acción de revisión de seguridad de Anthropic.

Las PR en borrador y las PR solo de documentación no llaman a Claude. Las instrucciones de revisión están en `.github/review/REVIEWER.md` y `SECURITY-REVIEWER.md`, y siempre se leen desde `main`. Ajústalas a medida que aprendas.

### 3b. Escaneo de secretos y protección de push
Settings → **Security** (Code security / Advanced Security, según tu plan):
- ✅ **Secret scanning**, ✅ **Push protection**: GitHub rechaza los push que contienen formatos de secretos conocidos.
- Gratis para repositorios públicos. Para repositorios privados puede requerir el complemento de seguridad de pago de GitHub; si no lo tienes, la comprobación `secrets` del propio kit (gitleaks) y los hooks locales te siguen cubriendo.

### 3c. Alertas de dependencias
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Después, quita el comentario de tu ecosistema en `.github/dependabot.yml`. Las PR de Dependabot pasan por las mismas puertas.

### 3d. Pull requests desde forks
Settings → **Actions → General** → *Fork pull request workflows*: exige aprobación para todos los colaboradores externos. (Las PR desde forks no reciben los secretos del repositorio, así que las revisiones de IA no pueden ejecutarse en ellas; una persona revisa y se impone si hace falta.)

## 4. Entorno de producción (puerta G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** el product owner (+ una persona suplente si la tienes)
- ✅ Prevent self-review: déjalo **desactivado** mientras no haya otra persona que apruebe; actívalo más adelante
- **Deployment branches and tags:** ramas seleccionadas → solo `main`
- **Environment secrets:** las credenciales de despliegue a producción van aquí y en ningún otro sitio
- **Environment variables:** `PRODUCTION_URL` (la usa la prueba de humo)

A partir de ahora, cada fusión en `main` ejecuta `deploy.yml`, que se detiene en *deploy-production* hasta que un aprobador hace clic en **Review deployments → Approve**. GitHub avisa a los aprobadores por correo o con una notificación.

Los revisores obligatorios funcionan en los repositorios públicos con cualquier plan, pero en los privados solo con GitHub Enterprise Cloud. Sin ellos, los despliegues empiezan al fusionar, y tu `ship` es la decisión de release: pon `deploy_approval: automatic` con `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (opcional, pero recomendado cuando haya dos personas)
`.github/CODEOWNERS`:
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Después activa "Require review from Code Owners" en el conjunto de reglas.

## 6. Rellenar el contrato de comandos
Edita el `Makefile` (incluido `audit`) y los pasos de preparación del entorno de ejecución en `.github/workflows/ci.yml`, `security.yml` y `deploy.yml` (busca `TODO(setup)`). Abre una PR. La comprobación `ci` tiene que ponerse en verde en esa PR antes de activar las comprobaciones obligatorias.

## 7. Opcional: la aplicación de GitHub de Claude
Si quieres mencionar a un agente en una PR para un arreglo rápido (p. ej., la aplicación de GitHub de Claude mediante `/install-github-app` en Claude Code, o la integración con GitHub de tu otra herramienta), instálala. Cualquier aplicación de ese tipo está sujeta a las mismas protecciones de rama y comprobaciones, así que no puede saltarse las puertas.

## 8. Ahorrar minutos de Actions

Los repositorios privados reciben una asignación mensual de minutos de Actions; los agentes que abren muchas PR la gastan rápido. Lo que ya hace el kit: por defecto (test-first) los agentes suben ramas sin abrir PR, y una PR solo se abre después de que hayas probado y aprobado el cambio, así que las comprobaciones se ejecutan una vez sobre código probado (proyectos checks-first: las PR en borrador no ejecutan nada, y los agentes marcan una PR como lista una sola vez, cuando está completa); las PR solo de documentación se saltan las comprobaciones; `main` se comprueba cada noche en lugar de después de cada fusión; las etiquetas, los comentarios y los issues nuevos no arrancan runners; los agentes frenan el trabajo nuevo con 10 PR abiertas o 10 cambios esperando tu prueba (`max_open_prs`, `max_in_uat`).

Averigua en qué se van los minutos: `python3 tools/haam/haam.py ci-usage` (últimos 7 días, por workflow, job, disparador y día).

Dos ajustes de la tabla de abajo ahorran minutos con poco compromiso. Cámbialos con `/haam-settings`, o con `python3 tools/haam/haam.py settings --set … --apply --human`; se convierten en variables del repositorio que leen los workflows. Los demás (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) ahorran más: consulta `settings --explain`. Con `ci: off`, las reglas de rama dejan de exigir la comprobación `ci`; mantén el escaneo de secretos, las revisiones de IA y release-gate, y ejecuta una comprobación completa al publicar (tu script de despliegue o el workflow de CI sobre el commit que envías) para seguir detectando los fallos que solo aparecen en Linux.

| Opción | Qué cambia | Compromiso |
|---|---|---|
| `--review local` | Las dos revisiones de IA se ejecutan en tu máquina en sesiones nuevas de Claude (`haam.py review`), con tu plan de Claude en lugar de minutos de Actions. Las PR con la etiqueta `human-review` se siguen revisando en GitHub | El resultado deja de ser a prueba de manipulaciones: el agente que construye inicia la revisión (sesiones nuevas de solo lectura, instrucciones de `main`), y cualquier cosa que use tu inicio de sesión podría publicar un resultado favorable. Ejecuta `haam.py review` desde tu propio chat para tener más separación |
| `--runner self-hosted` | Todos los jobs salvo el despliegue se ejecutan en tu propia máquina (registrada en Settings → Actions → Runners) en lugar de en las de GitHub | La máquina tiene que estar encendida, con git, make, Python 3, curl, gitleaks y las herramientas de tu proyecto; solo repositorios privados. Consulta los precios actuales de GitHub para los runners autoalojados |

También conviene revisar: los jobs en runners de macOS cuentan 10 minutos por cada minuto que se ejecutan (Windows: 2). Ejecuta los builds de móvil solo cuando haya cambiado el código móvil (`make check` recibe los archivos cambiados en `$CI_CHANGED_FILES`), o cada noche.

## 9. Comprobar que funciona
1. Abre una PR de prueba diminuta (p. ej., corregir una errata en el código). Se ejecutan `ci`, `secrets` y `dependencies`; el agente revisor publica un comentario y `ai-review` / `security-review` informan del resultado; `release-gate` muestra **failure: waiting for UAT**.
   - **Prueba de secretos:** en una rama desechable, haz commit de una clave falsa con formato de AWS, como `AKIA` seguido de 16 letras mayúsculas o dígitos, en un archivo de código. El hook local debería bloquear el commit; si te lo saltas con `--no-verify`, la comprobación `secrets` debería fallar. Borra la rama después.
2. Añade la etiqueta `uat-passed` → `release-gate` se pone en verde → se permite fusionar.
3. Tras la fusión, Actions → Deploy muestra **Waiting for review** en `deploy-production`.
4. Abre una PR solo de documentación → `release-gate` se supera automáticamente.
