# Decisiones que tomar al adoptar HAAM

Las toma el product owner, junto con el administrador del proyecto. `/haam-setup` las recorre en este orden, con una recomendación para cada una, y `/haam-settings` las cambia más adelante. Empieza con la opción recomendada y revísala después de la primera semana con mucho trabajo. Para entonces, `haam.py ci-usage` muestra en qué se fueron los minutos de Actions y `haam.py capacity` muestra lo que te está esperando.

**Algunas palabras que se usan aquí:**
- **PR** (pull request): un cambio propuesto, a la espera de fusionarse en `main`.
- **CI:** las comprobaciones automáticas (lint, tipos, pruebas, build) que se ejecutan en GitHub para una PR. Gastan minutos de Actions.
- **UAT** (prueba de aceptación de usuario): tu propia prueba de un cambio, en tu máquina, antes de que llegue a producción.
- **El carril sin UAT:** los cambios que marcas con `uat:skip` (actualizaciones de dependencias, configuración, refactorizaciones invisibles). Se saltan tu prueba y van directamente a las comprobaciones.
- **Puerta de release:** la comprobación que impide que una PR se fusione hasta que tu prueba se haya superado, o hasta que hayas elegido el carril sin UAT.
- **Worktree:** una copia aparte de la carpeta del proyecto para un chat de agente, para que los chats no se sobrescriban entre sí.

## De un vistazo

| Decisión | Empieza con | Cámbiala cuando | Ver |
|---|---|---|---|
| Cuenta y plan de GitHub | Una organización. Repositorio público: Free. Privado: Team | El repositorio es privado y necesitas un aprobador en los despliegues: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | El equipo ya trabaja en Linear a diario | §2 |
| Quién es quién | Un product owner, una persona aprobadora suplente | Varios productos o varios product owners | §3 |
| Idioma (`language`) | El idioma en el que escribe tu equipo | El equipo cambia | §3 |
| Orden de las pruebas (`flow`) | `test-first` | Pruebas en un entorno de staging compartido y no en local | §4 |
| Qué pruebas tú (`uat`) | `owner-decides` | Producto regulado: `always`. Muchas correcciones pequeñas y bien probadas: `bugs-skip` | §4 |
| Agrupación (`grouping`) | `per-issue` | Epics formados por elementos pequeños: `per-epic`. Los minutos de Actions escasean: `release` | §4 |
| Comprobaciones (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | Los minutos de Actions no llegan | §4 |
| Paso a producción (`deploy`, `deploy_approval`) | `github`, `each` | Despliegas de otra forma, o tu plan no puede retener los despliegues hasta su aprobación | §4 |
| Límites | `settings --recommend` | Cambia tu tiempo para probar o el número de agentes | §5 |
| Áreas protegidas | Las predeterminadas, más tu código sensible | Cambia la arquitectura | §6 |
| Recursos de prueba compartidos (`heavy_runs`) | Ninguno | Las pruebas comparten una base de datos local, un simulador o un dispositivo | §7 |
| Cuánta libertad tienen los agentes | Prototipos y modo de construcción de epic cuando los pidas; el código de producción es todo salvo prototipos, pruebas y documentación | Quieres que los agentes exploren más, o tu código de producción vive en unas pocas carpetas | §8 |

## 1. Cuenta de GitHub, organización y plan

### Cuentas
Cada persona crea y conserva su propia cuenta; nunca compartas un inicio de sesión.

1. **Cada persona** se registra en [github.com/signup](https://github.com/signup) con su correo del trabajo y activa la autenticación en dos fases (Settings → Password and authentication).
2. **Un administrador** crea una organización ([github.com/organizations/plan](https://github.com/organizations/plan)) e invita al equipo. El plan gratuito basta para un repositorio público; uno privado necesita Team (ver la tabla de abajo). La organización es la propietaria de los repositorios, así que nada depende de la cuenta de una persona. Haz propietarias a dos personas.
3. **El repositorio** vive en la organización: créalo ahí, o transfiere uno existente (Settings del repositorio → General → Transfer ownership).
4. **En cada máquina**, instala la GitHub CLI ([cli.github.com](https://cli.github.com)) y ejecuta `gh auth login`. Con GitHub Projects como tracker, ejecuta también `gh auth refresh -s project`.
5. **Sin cuentas aparte para los agentes.** Los agentes actúan con la cuenta de la persona que ha iniciado sesión. Las puertas dan por hecho que la persona que está al teclado responde de lo que hacen sus agentes.

### Qué plan necesitas

| Lo que usa HAAM | Repositorio público, cualquier plan | Privado, Free | Privado, Pro | Privado, Team | Privado, Enterprise Cloud |
|---|---|---|---|---|---|
| Reglas de rama y comprobaciones obligatorias ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Sí | No | Sí | Sí | Sí |
| Un aprobador en los despliegues a producción ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Sí | No | No | No | Sí |
| El escaneo de secretos y la protección de push propios de GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Sí | No | No | Complemento de pago | Complemento de pago |
| Tablero de GitHub Projects | Sí | Sí | Sí | Sí | Sí |
| Minutos de Actions | Gratis en los runners estándar | Una asignación mensual | Una asignación mayor | Una asignación mayor | Una asignación mayor |

Pro es para una cuenta personal; Team y Enterprise Cloud son para organizaciones.

Qué significa cada pieza que falta:
- **Sin reglas de rama** (repositorio privado en Free): GitHub no impide una fusión en `main` sin las comprobaciones. A los agentes se les sigue diciendo que nunca fusionen, y `ship` sigue ejecutando todas las puertas, pero nada lo impone. Para cualquier producto privado, usa Team (organización) o Pro (cuenta personal).
- **Sin aprobador de despliegues** (repositorio privado por debajo de Enterprise Cloud): los despliegues empiezan cuando se fusiona una PR. Tu `ship`, que hace la fusión, pasa a ser entonces la decisión de release. Pon `deploy_approval: automatic` para que HAAM no espere una aprobación que no puede llegar, y deja `uat` en `owner-decides` o `always` (§4).
- **Sin el escaneo de secretos de GitHub:** no pasa nada. La comprobación `secrets` del propio kit y el hook pre-commit funcionan en todos los planes.

Los planes y las asignaciones cambian, así que consulta [github.com/pricing](https://github.com/pricing) antes de elegir.

### El acceso de los revisores a Claude
Las dos revisiones de IA se ejecutan con un único secreto del repositorio, que el product owner añade en su propia terminal y que nunca se pega en un chat:
- `CLAUDE_CODE_OAUTH_TOKEN` (de `claude setup-token`): las revisiones se descuentan del plan de Claude de esa persona.
- `ANTHROPIC_API_KEY`: se factura por revisión, aparte de la suscripción de nadie. Fija un límite de gasto mensual en la consola de Anthropic.

## 2. El tracker: GitHub Projects o Linear

| | GitHub Projects | Linear |
|---|---|---|
| Coste | Gratis en todos los planes de GitHub | Gratis hasta 250 issues activos (no archivados) y 2 equipos; los planes de pago por usuario quitan el tope. Consulta [linear.app/pricing](https://linear.app/pricing) |
| Cómo lo usan los agentes | `haam.py issue …` desde cualquier herramienta de agente, con el inicio de sesión de `gh` de la persona | La conexión con Linear (MCP) configurada en cada herramienta de agente |
| Lo que se hace por ti | Reservas que impiden que dos chats tomen la misma tarea; la cola de UAT contada para los límites; los campos propios del tablero (`--field`); el carril sin UAT fusionándose solo; `ship` cerrando los issues | Los agentes hacen los movimientos a través de la conexión y cuentan la cola de UAT para `capacity --in-uat N`. El carril sin UAT no se fusiona solo: esas PR las llevas tú a producción |
| Configuración | `haam.py github-project --apply` | `haam.py linear --apply` con la clave de API del product owner, más los pasos en el navegador de `LINEAR-SETUP.md` |
| Ideal para | La mayoría de los equipos: todo en un solo sitio | Equipos que ya viven en Linear |

**Recomendación:** GitHub Projects, salvo que el equipo ya use Linear a diario. El triaje y los agentes crean issues rápido, así que el tope gratuito de Linear se puede alcanzar en semanas.

## 3. Quién es quién
- **Product owner:** una persona, que decide, prueba y lleva a producción. Solo ella ejecuta las skills reservadas a personas: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` y `/haam-settings`.
- **Aprobadores suplentes:** una o dos personas que pueden aprobar despliegues cuando el product owner no está (`config --backup-approvers a,b`). Necesita un aprobador en los despliegues, así que no tiene efecto en un repositorio privado por debajo de Enterprise Cloud.
- **Constructores:** todas las personas que ejecutan chats de agente. Cada una necesita su propia cuenta de GitHub con acceso de escritura y su propia herramienta de agente. El administrador ejecuta `haam.py invite --github USER` para ver el plan, y después lo mismo con `--apply`. Luego, cada constructor ejecuta `/haam-onboard`.
- **Administrador:** configura GitHub, el tracker y los secretos. A menudo es el product owner.
- **En cuanto dos personas trabajen en el código,** exige una aprobación en las reglas de rama (`GITHUB-SETUP.md` §2).
- **Idioma:** la documentación del kit está en inglés, español, francés, alemán, italiano, neerlandés y portugués (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Los agentes escriben las especificaciones, los issues, los planes de UAT y los mensajes en el idioma que elijas; los comandos, las etiquetas, los estados y el código siguen en inglés. Elígelo al instalar (`install --language es`). Para cambiarlo más adelante: `haam.py config --language fr`, y después el `update --target . --apply` del kit cambia los documentos que no hayas editado.

## 4. Cómo fluye el trabajo: los ajustes
`python3 tools/haam/haam.py settings --explain` imprime todas las opciones con su compromiso. Las elecciones que importan:

| Ajuste | Empieza con | Elige otra cosa cuando | Lo que cuesta o arriesga |
|---|---|---|---|
| `flow` | `test-first`: pruebas la rama del agente y después la PR y las comprobaciones se ejecutan una vez | `checks-first`: solo quieres probar código que haya pasado las comprobaciones, o pruebas en un entorno de staging compartido | Cada ronda de retoques vuelve a ejecutar las comprobaciones |
| `uat` | `owner-decides`: lo pruebas todo salvo lo que marques con `uat:skip` | `always`: productos regulados o críticos para la seguridad. `bugs-skip`: muchas correcciones pequeñas con buenas pruebas | `bugs-skip`: una corrección errónea puede llegar a producción sin que la veas |
| `grouping` | `per-issue`: una PR por issue | `per-epic`: epics formados por elementos pequeños. `release` (solo test-first): pocos minutos y releases por lotes | Un elemento que falla retiene todo el lote |
| `ci` | `every-pr`, en GitHub | `local`: se acaban los minutos y tu máquina compila todo. `off`: solo prototipos de una persona | `local` no es a prueba de manipulaciones |
| `review` | `github`: dos revisiones de IA independientes por PR | `protected-only`: ahorra la mayor parte del coste de revisión. `local`: ahorra minutos | Menos comprobaciones independientes |
| `nightly` | `on` | `off`: cuando los minutos escasean mucho | Descubres más tarde las roturas y las vulnerabilidades nuevas |
| `runner` | `github` | `self-hosted`: un repositorio privado con builds pesados y una máquina siempre encendida | Mantenimiento. Nunca para repositorios públicos |
| `deploy` | `github`: `deploy.yml` despliega al fusionar | `manual`: despliegas de otra forma | `ship` espera a que digas "live" |
| `deploy_approval` | `each`: cada despliegue espera tu aprobación | `automatic`: tu plan no puede retener los despliegues (§1), o elegiste `uat: always` | Un cambio fusionado sale a producción sin un último vistazo |
| `worktree_cleanup` | `after-ship` | `manual`: prefieres ordenar tú los worktrees | Espacio en disco |

El carril sin UAT solo se fusiona solo en GitHub Projects, con el secreto `HAAM_PROJECT_TOKEN`, `ci: every-pr` y `review: github`. Si no, esas PR las llevas tú a producción.

Evita estas parejas, porque juntas eliminan la última comprobación:
- `ci: off` con `review: off`: nada comprueba el código antes de tu prueba.
- `deploy_approval: automatic` con `uat: bugs-skip`: una corrección de un bug puede llegar a producción sin que ninguna persona la mire. Los despliegues son automáticos en un repositorio privado por debajo de Enterprise Cloud, así que no elijas ahí `bugs-skip`.

## 5. Límites: cuánto trabajo puede esperar
Los límites impiden que los agentes produzcan más de lo que puedes probar, y más PR de las que cubre tu presupuesto de CI. Cuando se alcanza un límite, los agentes dejan de empezar construcciones nuevas. Siguen corrigiendo retoques, escribiendo especificaciones y evaluando ideas.

| Límite | Qué cuenta | Cómo dimensionarlo |
|---|---|---|
| `max_in_uat` | Cambios que esperan tu prueba. El límite principal en test-first | Lo que puedes probar en una sesión: minutos por sesión ÷ minutos por prueba (una prueba suele llevar de 5 a 10 minutos). Una hora al día a unos 6 minutos por prueba son 10 |
| `max_open_prs` | PR listas. Los borradores, las PR solo de documentación y las PR de bots (Dependabot) no cuentan | Test-first: las PR viven poco (desde tu aprobación hasta `ship`), así que con el doble de los chats de agente en marcha a la vez sobra. Checks-first: cada cambio que espera tu prueba es una PR lista, así que ponlo al menos en `max_in_uat` más los chats en marcha a la vez |
| `max_review_rounds` | Rondas fallidas de revisión de IA antes de que un agente se detenga y te pregunte | 2. Súbelo a 3 en áreas difíciles |
| `max_pr_lines` | Tamaño objetivo de una PR, en líneas cambiadas | 400. Las PR más pequeñas reciben mejores revisiones y pruebas |

Calcúlalo para tu equipo:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
Imprime los límites sugeridos y avisa cuando los agentes pueden producir más de lo que puedes probar. Después da el comando que los aplica. Supone unos 6 minutos por prueba y 2 cambios por chat al día; pasa `--minutes-per-test` y `--changes-per-chat` con tus propias cifras. Lee `flow` de los ajustes del proyecto, o lo toma de `--flow`.

Si los agentes producen más de lo que tú pruebas:
- la cola se llena y los agentes pausan las construcciones nuevas, que es el límite haciendo su trabajo;
- `/test all` con "pass all verified" despacha los cambios que los propios agentes demostraron;
- `uat: bugs-skip` envía las correcciones pequeñas de bugs directamente a las comprobaciones;
- o ejecuta menos chats de agente.

Para un fin de semana de trabajo de agentes que se prueba en una sola sesión, abre una **ventana de lote**: un aumento que termina solo después de su último día, p. ej. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. Qué proteger
**La regla:** protege el código en el que un cambio erróneo podría perjudicar a los usuarios, hacer perder dinero o datos, incumplir la ley o debilitar las propias puertas de HAAM. Cada cambio protegido necesita tu revisión de código y tu prueba, y nunca va por el carril sin UAT. Así que protege lo que importa, no todo.

| Área | Proteger | Rutas típicas (ejemplos) |
|---|---|---|
| Inicio de sesión, sesiones, permisos, roles | Siempre | `src/auth/**`, `**/permissions/**`, *el middleware de autenticación* |
| Pagos, facturación, reembolsos, precios | Siempre | `src/billing/**`, `src/payments/**` |
| Datos personales: almacenamiento, conservación, borrado, exportaciones | Siempre que tengas datos personales | `src/users/**`, `**/privacy/**` |
| Registros que podrían capturar datos personales | Siempre que tengas datos personales | *la configuración de registros y los módulos de auditoría* |
| Decisiones sobre usuarios: elegibilidad, verificación, aprobaciones, puntuaciones | Cuando un resultado erróneo perjudica a alguien | `src/verification/**`, `src/decisions/**` |
| Proveedores externos que actúan en nombre de los usuarios o reciben sus datos | Sí | `src/integrations/**` |
| Migraciones de base de datos | Siempre | `db/migrations/**`, `**/migrations/**` |
| Configuración de seguridad: criptografía, CORS, CSP, gestión de secretos | Sí | `**/security/**`, `**/crypto/**` |
| Infraestructura como código | Sí | `infra/**`, `terraform/**` |
| Configuración de firma y de release de móvil | Si publicas aplicaciones | *archivos de entitlements, de firma y de build de release* |
| CI, despliegue y scripts de build | Protegido por defecto | `.github/**`, `Makefile`, `scripts/**` |
| HAAM y la configuración de los agentes | Protegido por defecto | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json` y más: `haam.py settings` los enumera |

Las rutas en cursiva describen qué buscar; conviértelas en patrones reales para tu código.

Cómo configurarlo:
1. `/haam-setup` propone rutas reales de tu código para cada área que aplique. Tú las confirmas.
2. `config --protected "src/auth/**,db/migrations/**" --human` añade patrones, y `config --unprotected "…" --human` quita uno. `**` significa cualquier número de carpetas y `*` significa dentro de una sola carpeta. Un nombre de carpeta sin más cubre todo lo que contiene.
3. `haam.py protected` en cualquier rama enumera los archivos protegidos que cambia.
4. La puerta de release decide a partir de los archivos que cambia una PR. Lee la lista desde `main`, así que un agente no puede quitar una protección en su propia PR.

Revisa la lista cada vez que cambie `docs/product/ARCHITECTURE.md`.

## 7. Recursos de prueba compartidos
Algunas pruebas usan algo que comparte toda la máquina, como una base de datos local que clonan las pruebas, un simulador de teléfono o un dispositivo conectado. Dos chats de agente que las ejecutan a la vez se rompen mutuamente, y el fallo parece un cambio roto. Enumera esos comandos como patrones: `config --heavy-run "make (check|test-integration)"`. Los agentes los ejecutan entonces de uno en uno mediante `haam.py exclusive`. Deja la lista vacía cuando tus pruebas sean autónomas.

## 8. Cuánta libertad tienen los agentes
Los agentes pueden construir piezas grandes rápido, como cuando la gente hace "vibe coding" con IA, allí donde un error sale barato de tirar. Todo lo que se ejecuta para usuarios reales sigue detrás de las puertas.

**Algunas palabras que se usan aquí:**
- **Prototipo** (o **spike**): una versión funcional rápida y desechable de una idea, construida para probarla, nunca para llevarla a producción tal cual.
- **Porción:** una pieza de un epic que se puede llevar a producción, con su propio issue y su propia especificación.
- **Agente principal:** el único chat de agente que construye un epic entero. Puede pasar porciones independientes a agentes auxiliares (**subagentes**).
- **Feature flag:** un interruptor en el código que mantiene oculta una feature nueva hasta que alguien la activa.
- **Código de producción:** el código que se ejecuta para usuarios reales.

Tres elecciones:

| Elección | Qué hace | Cuándo usarla |
|---|---|---|
| **Prototipo primero.** Escribe `/spike`, o elige `prototype` en `/triage` | Un agente construye un prototipo en una rama `spike/`, sin especificación, sin PR y sin límite de tamaño. Lo pruebas con `/test`. Después dices `discard`, `change: <what>`, `rebuild` (especificarlo y construirlo desde cero) o `keep` (especificarlo y construir a partir de ese código) | Cuando probar la idea te dice más que leer sobre ella: una pantalla nueva, un flujo, una integración que te genera dudas |
| **Modo de construcción de epic.** Pon la etiqueta `mode:epic-build` a un epic aprobado; `/decide` y `/triage backlog` lo ofrecen | Un agente principal construye todas las porciones del epic en una sola rama, con un punto de control después de cada porción. Pruebas y llevas a producción la feature entera una sola vez | Una feature cuyas porciones solo tienen sentido juntas, o que prefieres juzgar en conjunto |
| **Qué cuenta como código de producción** (`production_paths`, `non_production_paths`) | Indica a los agentes y a ti qué se ejecuta para los usuarios, de modo que las notas de un prototipo y `haam.py production` muestran lo que tocaría un cambio. Por defecto, los prototipos, las pruebas y la documentación quedan fuera | Acótalo cuando tu producto viva en unas pocas carpetas: `config --production "src/**,api/**" --human`. Añade carpetas que nunca se ejecutan para usuarios con `config --not-production "…" --human`. Si tu documentación es lo que ven los usuarios, sácala de la lista con `config --remove-not-production "docs/**" --human` |

Sea cual sea el modo, todo cambio que se fusiona cumple todas las puertas. La protección que hay detrás:
- un prototipo nunca se fusiona: la puerta de release rechaza las ramas `spike/` y todo lo que haya en `prototypes/`, y `publish` rechaza los spikes;
- el código de un prototipo que se conserva solo llega a los usuarios mediante `/spec`, una rama normal y tu prueba, detrás de una feature flag desactivada por defecto. Nunca va por el carril sin UAT: la puerta ve sus commits `spike:`;
- el código de producción nunca importa nada de `prototypes/`, y el revisor de IA lo bloquea si lo hace;
- un prototipo nunca cambia áreas protegidas, y `/test` te muestra los archivos protegidos que cambia y sus dependencias nuevas antes de ejecutar nada;
- las áreas protegidas siempre reciben tu revisión de código;
- ningún agente toca sistemas ni datos de producción, en ningún modo.

## Fuentes
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (planes que los incluyen) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (revisores obligatorios en repositorios privados) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
