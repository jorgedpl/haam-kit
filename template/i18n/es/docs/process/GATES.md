# Puertas y anulaciones

Entre una idea y producción hay cinco puertas. Cada una tiene un responsable claro, una lista de comprobación y, cuando es posible, un punto de control automático, para que la regla no dependa de que alguien se acuerde.

| Puerta | Entre | Responsable | La impone |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Persona (PO) | Estado del tracker: solo las personas ejecutan `/decide` |
| **G2 Ready** | Backlog → Ready | Una persona aprueba la especificación | Etiqueta `agent-ready`; los agentes solo construyen issues `agent-ready` |
| **G3 Verified** | In Progress → UAT | Comprobaciones automáticas + agente revisor independiente (+ persona en las áreas protegidas) | Comprobaciones obligatorias `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → fusión | Persona que prueba | Comprobación obligatoria `release-gate` (necesita la etiqueta de PR `uat-passed` o `gate-override`) |
| **G5 Released** | fusión → producción | Persona (PO) | Entorno de GitHub `production` con revisor obligatorio |

---

## Lista de comprobación de G1 Decision

La evaluación (o, para una idea construida como prototipo, las notas del prototipo de `/spike`) debe contener:
- [ ] Planteamiento del problema y para quién es
- [ ] Estimación del valor con pruebas (o un "todavía no hay pruebas" explícito)
- [ ] Tamaño del esfuerzo razonado a partir del código
- [ ] Riesgos: seguridad, protección de datos (p. ej., RGPD), normativa, operaciones
- [ ] Al menos dos opciones más "no hacer nada"
- [ ] Una recomendación

La persona responde con una de estas: **aprobar** (con prioridad), **aparcar** (con lo que hará que se revise), **rechazar** (con un motivo). Si es un prototipo, primero lo prueba (`/test`), así que la decisión se basa en usarlo y no en leer sobre él.

## G2 Definition of Ready

Un issue solo puede recibir `agent-ready` cuando:
- [ ] La especificación existe en `docs/specs/` y está enlazada desde el issue
- [ ] Los criterios de aceptación están escritos como Given / When / Then y cada uno se puede probar
- [ ] El alcance y lo que queda **fuera del alcance** están explícitos
- [ ] Se enumeran los archivos o módulos que probablemente se tocan
- [ ] Se indica el impacto en datos, migraciones y configuración (o "ninguno")
- [ ] Se incluyen el plan de pruebas unitarias y un esbozo de la UAT
- [ ] Tamaño ≤ 1 día de trabajo de agente (unas 400 líneas cambiadas); si no, se divide en sub-issues
- [ ] Se señalan las áreas protegidas afectadas (añadida la etiqueta `human-review`)
- [ ] Prioridad fijada
- [ ] Una persona aprobó la especificación

## G3 Verified (Definition of Done para el código)

- [ ] Cada criterio de aceptación tiene al menos una prueba automática
- [ ] `make check` pasa en local y en la CI (lint, tipos, pruebas unitarias, build)
- [ ] No hay cambios ajenos en el diff
- [ ] La documentación afectada por el cambio está actualizada (`ARCHITECTURE.md`, documentación de la API, lista de variables de entorno)
- [ ] Ni secretos ni datos personales reales en el código, las pruebas o los fixtures
- [ ] La descripción de la PR sigue la plantilla y enlaza el issue (`Refs #123` en GitHub Projects, el ID en el título en Linear)
- [ ] Comprobación `secrets` en verde: ni claves, ni tokens, ni contraseñas en ningún commit de la PR
- [ ] Comprobación `dependencies` en verde: ninguna vulnerabilidad conocida alta o crítica
- [ ] `ai-review` en verde: el agente revisor independiente no encontró problemas bloqueantes
- [ ] `security-review` en verde: la revisión de seguridad de Claude no encontró vulnerabilidades
- [ ] Revisión de código humana hecha si está la etiqueta `human-review`

### Cómo funciona la revisión de código

La revisión va por capas, de modo que **ningún agente revisa nunca su propio trabajo** y **los secretos los detectan herramientas deterministas, no el criterio de nadie**.

| Capa | Cuándo | Qué | Quién o qué la hace |
|---|---|---|---|
| 1. Guarda local de secretos | Antes de cada commit | Bloquea los commits que contienen claves o tokens | gitleaks mediante el hook pre-commit de git (todo el mundo, cualquier herramienta), más hooks de la herramienta del agente donde se admiten (Claude Code; Grok) |
| 2. Autocomprobación | Antes de abrir una PR | `make check` + `/security-review` sobre los cambios propios | El agente que construye |
| 3. CI determinista | Cada push a una PR | Pruebas, lint, tipos, escaneo de secretos de cada commit, auditoría de dependencias | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Revisión independiente de IA | Cada push a una PR (no borradores ni PR solo de documentación) | Conformidad con la especificación, pruebas honestas, corrección, reglas del proyecto; vulnerabilidades de seguridad | Un Claude aparte en GitHub Actions que nunca vio escribir el código (`ai-review`, `security-review`) |
| 5. Revisión humana | PR con la etiqueta `human-review` | Áreas protegidas: lógica central, autenticación, pagos, datos personales, migraciones, infraestructura | El product owner o un desarrollador designado |
| 6. Aceptación humana | Cada PR de código | El comportamiento funciona de verdad (G4 UAT) | Product owner |

**Reglas del ciclo de revisión**
- El agente que construye lee el comentario del revisor, corrige cada elemento **Blocking** y hace push; las revisiones se vuelven a ejecutar automáticamente.
- Si el agente que construye cree que un hallazgo es erróneo, responde en la PR explicando por qué y pregunta a la persona. Nunca discute en círculos: **tras dos rondas de revisión** que siguen fallando, se detiene y pasa el testigo a la persona.
- Solo una persona puede imponerse a una revisión de IA, con la etiqueta de PR `ai-review-overruled`. Esto queda registrado en la PR.
- Los revisores de IA no pueden aprobar ni fusionar. Solo pueden bloquear.

### Si un secreto llega alguna vez a GitHub
1. **Revócalo y rótalo de inmediato** con el proveedor. Da por hecho que está comprometido; quitarlo del código no deshace la fuga.
2. Quítalo del código; usa una variable de entorno documentada en `.env.example`.
3. Un administrador del repositorio reescribe el historial de la rama antes de fusionar (no basta con un commit nuevo).
4. Registra un `/bug` con prioridad Urgent para dejar constancia de lo que pasó y de lo que se rotó (nunca incluyas el propio secreto).

**Los ajustes del product owner cambian cómo se ejecuta G3, no quién decide** (`/haam-settings`):
- `ci`: en cada PR, en local (`ci-local`, publicado por `haam.py local-ci` en la máquina del product owner) o desactivada.
- `review`: en GitHub, en local, solo en áreas protegidas o desactivada.
- `nightly`.

Las comprobaciones obligatorias siguen a los ajustes (`settings --apply`). El escaneo de secretos se ejecuta siempre.

## G4 Accepted (UAT)

En el flujo predeterminado test-first, G4 va antes que G3: el product owner prueba la rama que subió el agente antes de que exista una PR, y después G3 comprueba exactamente el commit que aprobó (`haam.py publish` y luego `ship`, que rechaza cualquier otra cosa).

**Carril sin UAT:** en este caso G4 se decide de antemano. Cuando el product owner marca un issue con `uat:skip` (en `/triage`, o con "spec approved, no UAT"), el agente abre la PR con la misma etiqueta y `release-gate` se supera cuando todos los issues a los que corresponde la PR la llevan (GitHub Projects: la puerta lee los issues; Linear: se fía de la etiqueta de la PR). Nunca cuando la PR cambia un área protegida: la puerta compara los archivos cambiados con `protected_paths` en `haam.config.json` en `main` (por defecto, la configuración de los agentes y de la CI, más las del propio proyecto), añade `human-review` y mantiene el carril cerrado, digan lo que digan las etiquetas. Por eso una actualización del kit nunca va por el carril: cambia la configuración de los agentes, y la revisas y la llevas a producción tú. G3 se sigue aplicando entera, y el auto-merge (necesita `HAAM_PROJECT_TOKEN`) solo fusiona cuando pasan todas las comprobaciones obligatorias. No hay auto-merge en Linear, ni tampoco a menos que la CI y las dos revisiones de IA se ejecuten en GitHub (ajustes `ci: every-pr` y `review: github`): los resultados locales no son a prueba de manipulaciones y unas comprobaciones reducidas no bastan por sí solas, así que esas PR del carril las lleva a producción el product owner (`ship`), lo que sigue siendo una decisión para muchas. Solo la decisión de una persona añade `uat:skip` a un issue (`issue create` e `issue label` lo rechazan sin `--human`).

- [ ] El plan de UAT existe en `docs/uat/` con pasos numerados y resultados esperados
- [ ] Una persona lo ejecutó en local sobre la rama (test-first: la rama que subió el agente, antes de cualquier PR; checks-first: la rama de la PR)
- [ ] Todos los pasos se superan, o los fallos quedan registrados y aceptados como issues de seguimiento
- [ ] La aprobación de la persona (`/test` o `/uat-result <ID> pass`) añade la etiqueta `uat-passed` a la PR (test-first: `publish` también la registra en el commit probado como el estado `uat`)
- [ ] La aprobación cubre el código que se fusiona: un push posterior quita `uat-passed` (`gates.yml`), salvo que el nuevo head sea el commit probado; `ship` solo fusiona ese commit

## G5 Released

- [ ] PR fusionada en `main` por una persona, o por `haam.py ship --human` después de que la persona dijera `ship`
- [ ] Despliegue a producción aprobado (entorno `production`): en GitHub, o por `ship` con la palabra de la persona
- [ ] Prueba de humo posterior al despliegue superada (`make smoke`, si está definida)
- [ ] El issue está marcado como Done (`ship`, o `/release` para los cambios fusionados de otra forma); la nota de versión en `docs/changes/` viajó con él

---

## Anulaciones

A veces producción está ardiendo o un plazo no puede esperar. Las anulaciones existen para eso y son **solo para personas**.

### Nivel 1: saltarse la UAT (el más habitual)
Úsalo cuando la corrección es urgente y está verificada por pruebas, pero no hay tiempo para un ciclo completo de UAT.

1. La persona ejecuta `/override <ID> "<reason>"` (para una PR sin issue: `/override PR <number> "<reason>"`), o comenta a mano `OVERRIDE: <reason>` en la PR (el comentario debe empezar por `OVERRIDE:`) y añade la etiqueta de PR `gate-override`.
2. La comprobación `release-gate` se supera gracias a la etiqueta de anulación.
3. La CI (comprobación `ci`) **tiene que pasar igualmente**.
4. Cuando la PR tiene un issue, el agente crea un issue de seguimiento en el tracker: `Post-override UAT for <ID>` (prioridad High, etiqueta `stream:bug`, `override-followup`), para que la verificación que se saltó se haga igualmente a posteriori.

### Nivel 2: bypass de emergencia (poco frecuente)
Úsalo solo cuando la propia CI está rota o bloquea una corrección en producción.

1. Un administrador del repositorio fusiona con "bypass branch protections" en GitHub.
2. El administrador comenta `EMERGENCY BYPASS: <reason>` en la PR.
3. Se crea un issue de seguimiento como el anterior, más un segundo para arreglar lo que bloqueó la CI.

### Reglas de las anulaciones
- Los agentes **nunca** añaden `gate-override`, nunca se saltan las protecciones y nunca sugieren anular una puerta salvo que la persona lo plantee primero.
- Toda anulación debe tener un motivo escrito en la PR.
- Las anulaciones se revisan en la revisión semanal del backlog: filtra el tracker por la etiqueta `override-followup`.
