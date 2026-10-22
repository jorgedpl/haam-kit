# Trabajar como product manager

*Una guía para la persona que decide qué se construye. Los agentes no necesitan leerla; tú sí.*

En HAAM tú decides **qué** y **por qué**; los agentes averiguan **cómo** y lo hacen. Los agentes son rápidos, así que la velocidad de todo el sistema la marca lo rápido que tú hagas el triaje, decidas, apruebes y pruebes. Tu tarea principal es mantener corta la cola **Waiting on me** y la **Agent queue** apuntando a lo que importa.

Los ejemplos usan IDs de GitHub Projects (`#12`); en Linear el mismo elemento es `APP-12`. Los comandos se escriben `/name`; en Codex usa `$name`.

---

## 1. Tu trabajo en una página

| Lo que solo haces tú | Con qué frecuencia | Con IA | Directamente en el tracker |
|---|---|---|---|
| Mantener al día `docs/product/PRODUCT.md`: prioridades actuales, innegociables, recorridos principales | Mensual | "Actualiza PRODUCT.md: ahora nuestras prioridades son…" | Editar el archivo (mediante una PR) |
| Hacer triaje de las ideas y los bugs nuevos | Diaria | `/triage` | Vista Triage: prioridad, estado, etiquetas |
| Agrupar los issues relacionados en epics y responder las preguntas del agente sobre cada uno | Semanal | `/triage group` y después `/epic #9` | Issue de epic (etiqueta `epic`) con sub-issues |
| Fijar y cambiar prioridades | Diaria y semanal | `/triage`, `/triage backlog` | Campo Priority |
| Decidir sobre las ideas evaluadas (G1) | Semanal | `/decide #12 approve high` | Estado, etiquetas, comentario (§7–8) |
| Aprobar especificaciones (G2) | Según llegan | Lee la especificación (enlazada en el issue) y después "spec for #12 approved" | Comentario "spec approved"; Status Ready, etiqueta `agent-ready` |
| Probar los cambios (G4) y llevarlos a producción (G5) | Diaria | `/test` y después responde `pass` → `ship`, o di qué falla | GitHub: etiqueta `uat-passed`, fusionar, aprobar el despliegue |
| Cerrar los seguimientos de anulaciones | Semanal | "Muéstrame los seguimientos de anulaciones abiertos" | Vista: etiqueta `override-followup` |

Todo lo que decides va al tracker o a Git, nunca solo a un chat. Si no queda escrito ahí, el siguiente agente no lo sabe.

---

## 2. Tu ritmo

### Diario (10–15 minutos)
1. **Primero, probar.** Escribe `/test all`: el agente te guía por todos los cambios que te esperan, uno tras otro (§2a), y después lleva a producción todo lo aprobado con un solo despliegue. Los agentes no pueden terminar hasta que tú termines, y su contexto se queda viejo.
2. **Vacía la bandeja de Triage** (`/triage`, o la vista Triage). Nada debería quedarse ahí más de dos días laborables.
3. **Bugs urgentes:** si hay alguno, pon un agente con él ahora mismo: nueva ventana de chat, `/work bugs`.
4. Echa un vistazo a los comentarios de traspaso y de "bloqueado" de los agentes y responde a sus preguntas.

### 2a. Probar un cambio: el ciclo completo
1. Escribe **`/test`** (o `/test #12`). El agente pone el cambio en tu máquina, arranca la aplicación y te da el enlace y una lista breve: *haz esto → deberías ver aquello*.
2. Pruébalo. Después responde con una palabra o una frase:
   - **`pass`** → el agente abre la pull request (hasta ahora no había ninguna: probaste la rama del agente), las comprobaciones se ejecutan una vez exactamente sobre lo que probaste, y te pregunta *"¿Lo llevo a producción cuando pasen las comprobaciones?"* Responde **`ship`**: espera a que pasen, fusiona, aprueba el despliegue a producción por ti y cierra el issue. Recibes *"#12 ya está en producción."* Responde `later` para dejarlo en espera.
   - Si tu proyecto **despliega a mano** (`"deploy": "manual"`), el agente fusiona y después te pide que despliegues; responde **`live`** cuando esté fuera y cierra el issue.
   - Si después las comprobaciones o las revisiones encuentran un problema, vuelve a los agentes como una prueba suspendida, y regresa a ti cuando esté arreglado.
   - **Qué ha fallado** (*"paso 3: el botón de exportar sigue sin aparecer en el móvil"*) → el agente lo registra en el issue, le pone la etiqueta `uat-failed` y lo devuelve a los agentes, que lo arreglan antes que nada. Cuando está arreglado, vuelve a `/test`.
3. Eso es todo. No necesitas tocar ramas, etiquetas ni el tablero.

**Cómo funciona HAAM lo eliges tú.** Escribe `/haam-settings`: repasa cada ajuste con tus propias cifras (minutos de Actions, la cola de UAT), recomienda una opción y aplica lo que elijas:
- cuándo se ejecutan la CI y las revisiones de IA (en cada PR, en tu máquina, solo en áreas protegidas o nunca);
- qué pruebas personalmente (todo, lo que decidas por issue, o que los bugs se salten la prueba);
- cómo se agrupan los cambios (por issue, por epic, o una única PR de release para todo lo que aprobaste);
- si los despliegues esperan tu aprobación;
- los límites.

`python3 tools/haam/haam.py settings --explain` los enumera todos.

**Cambios que no puedes probar tú** (actualizaciones del kit o de la configuración, subidas de versión de dependencias, refactorizaciones que no notarías, la CI): márcalos con `uat:skip` al hacer su triaje, o di "spec approved, no UAT". Nunca llegan a `/test`: su PR se fusiona sola cuando pasan la CI y las dos revisiones de IA (GitHub Projects), y tu siguiente `ship` los despliega con todo lo demás y los cierra. Si pasas un tiempo sin llevar nada a producción, ejecuta `/test` y responde `ship` de todos modos, o `ship --all`: su despliegue espera tu aprobación. En Linear, llévalos a producción por su nombre (`ship APP-12 --human`). Resérvalo para cambios que ningún usuario notaría; nunca para áreas protegidas.

### Semanal (30–45 minutos)
1. **Agrupa** los issues sueltos en epics (`/triage group`) y da forma al epic más prioritario con el agente (`/epic #9`).
2. **Decide** todo lo que está en **Decision** (G1).
3. **Revisa las especificaciones** (enlazadas en cada issue) y apruébalas o coméntalas (G2).
4. **Reordena** Ready y Backlog según las prioridades actuales (`/triage backlog`).
5. **Busca el trabajo atascado:** `/triage stale` (reservado pero sin movimiento, UAT esperando demasiado, decisiones con retraso).
6. **Revisa los elementos Parked** cuyo "revisar cuando" ya se ha cumplido.
7. **Cierra los seguimientos de anulaciones** (etiqueta `override-followup`).
8. Mejora una cosa del proceso (un `/idea` con la etiqueta `area:process`).

### Mensual o trimestral (30 minutos)
1. Reescribe las **prioridades actuales** en `PRODUCT.md`: 3–5 resultados, por orden. Los agentes las usan para sugerir prioridades y deshacer empates, así que es lo más útil que puedes mantener al día.
2. **Poda:** todo lo que sea Low y lleve más de dos meses esperando → apárcalo con un "revisar cuando". Un backlog corto es un backlog que se puede usar.

---

## 3. Triaje: decidir qué es cada elemento nuevo

El estado **Triage** es tu bandeja de entrada. Las ideas y los bugs llegan ahí desde `/idea`, `/bug`, los formularios de issues, otras personas y los agentes. Intenta tener la bandeja vacía al final de cada día.

Si varios elementos parecen relacionados, o a la mayoría les falta contexto, **agrúpalos primero** (§4): hacer el triaje de una feature cada vez es más rápido y mejor que hacerlo de fragmentos.

Para cada elemento, responde cuatro preguntas:

1. **¿Está claro y es nuevo?** Duplicado → ciérralo y enlaza el original. No hay información suficiente → comenta con tu pregunta y déjalo en Triage.
2. **¿Qué es?** Un **bug** significa que algo no funciona como se pretendía. Una **idea** significa un comportamiento nuevo o cambiado. "Funciona como se diseñó, pero el usuario esperaba otra cosa" es una idea, no un bug. Corrige la etiqueta de flujo si está mal.
3. **¿Qué importancia tiene?** Fija la prioridad (§5).
4. **¿Qué pasa después?**

| Elemento | Tu decisión | Estado después | Lo que sigue |
|---|---|---|---|
| Bug con pasos claros para reproducirlo | **Ready** | Ready, con una prioridad | Un agente lo toma (`/work bugs`) |
| Bug sin información suficiente | **Falta información** | Se queda en Triage, con tu pregunta como comentario | Respondes tú o quien lo notificó, y se vuelve a hacer el triaje |
| Bug urgente | **Ready, empezar ya** | Ready, Urgent | Pon un agente ahora; tienes `/override` si el despliegue no puede esperar |
| Idea que merece explorarse | **Evaluar** | Discovery, con una prioridad | Un agente escribe la evaluación (`/work ideas` o `/assess #12`) |
| Idea que entenderías mejor probándola | **Prototipo** | Discovery, etiqueta `mode:prototype` | Un agente construye una versión funcional desechable (`/spike #12`); la pruebas con `/test` y decides |
| Buena idea, mal momento | **Aparcar** | Parked, con un comentario "revisar cuando…" | Vuelve en una revisión semanal |
| Idea que no harás | **Rechazar** | Canceled, con un motivo de una línea | Cerrado |
| Duplicado | **Duplicado** | Canceled, enlazado al original | Cerrado |

Las ideas pequeñas también pasan por la evaluación. Pide una rápida ("assess #12, que sea breve"). La evaluación es donde el agente revisa el código y los riesgos, y a ti te cuesta un minuto leerla.

---

## 4. Epics: agrupar issues en features

Los issues sueltos a menudo carecen de contexto. "Falta el botón de exportar en el móvil", "Exportar a CSV" e "Informes programados" son tres fragmentos de una misma feature y, si se hace el triaje de uno en uno, cada uno parece pequeño y poco claro. Un **epic** es un issue padre (etiqueta `epic`) que agrupa los issues de un mismo resultado y aporta el contexto que les falta: para quién es, cómo es el éxito, qué entra y qué queda fuera del alcance, y el orden de las porciones. Ese contexto vive en una breve **ficha del epic** en `docs/epics/`.

**Usa un epic para:** tres o más issues sobre el mismo resultado; una idea demasiado grande para una sola especificación (tamaño L o XL); una petición que toca varias pantallas o módulos.
**No lo uses para:** un único bug; un cajón de sastre de cosas sin relación; un tema que nunca termina ("rendimiento", "pulir la UX"): eso son prioridades, no epics. Un epic tiene que poder terminarse, en semanas y no en trimestres.

### Cómo avanza un epic
1. **Agrupar.** `/triage group` mira los issues sueltos y propone epics: un título, el resultado en una línea, qué issues le pertenecen y por qué. Tú dices `ok` o ajustas (`merge 2 and 3`, `#40 out`). O empieza desde un tema: `/epic "reporting"`.
2. **Dar forma.** `/epic #9`: el agente lee todos los issues del epic, el contexto del producto y el código relevante, redacta la ficha y después **te hace hasta cinco preguntas por ronda**: para quién es, cómo es el éxito, lo imprescindible frente a lo deseable, restricciones, qué no debe cambiar, qué prioridad tiene. Después propone una limpieza: duplicados que cerrar, huecos que añadir como issues nuevos, issues poco claros que reescribir, issues grandes que dividir y un orden. No cambia nada hasta que lo confirmas.
3. **Decidir una vez (G1).** `/assess #9` añade el esfuerzo y la viabilidad de todo el epic; `/decide #9 approve high` lo aprueba, junto con las ideas que contiene, de una sola vez.
4. **Especificar y construir porción a porción.** Cada sub-issue tiene su propia especificación y pasa G2 por separado. Los agentes construyen los sub-issues, nunca el epic en sí.
5. **Terminar.** Cuando el último sub-issue llega a producción, el agente se ofrece a cerrar el epic.

**Prioridades:** dale una prioridad al epic; sus issues toman la misma salvo que digas otra cosa. Un bug dentro de un epic puede seguir siendo más urgente que el epic.

**Responder a las preguntas del agente:** las respuestas cortas están bien. "Todavía no lo sé" es una respuesta válida: queda abierta en la ficha. Responde sobre lo que necesitan los usuarios y por qué; deja el cómo a los agentes.

### Epics directamente en el tracker
- **GitHub Projects:** crea un issue y añádele la etiqueta `epic`; después, en la sección de sub-issues del epic, añade los issues que le pertenecen (o fija el padre desde cada issue). En el tablero, usa la vista **Epics** y muestra los campos *Parent issue* y *Sub-issues progress* en las vistas de tabla para que cada tarjeta muestre su epic.
- **Linear:** crea un issue con la etiqueta `epic` y convierte los issues relacionados en sus sub-issues (fija su padre). Para una iniciativa muy grande que abarque varios epics, un proyecto de Linear puede contener los epics.

---

## 5. Priorizar

### 5.1 Los cuatro niveles

| Prioridad | Criterio | Tratamiento esperado |
|---|---|---|
| **Urgent** | Producción está rota en un recorrido principal, se podrían perder o exponer datos, hay un agujero de seguridad o corre peligro un plazo legal o de cumplimiento | Empezar hoy. Se pueden anular las puertas, con un seguimiento |
| **High** | Hace avanzar directamente una de las prioridades actuales de `PRODUCT.md`, o es un bug en un recorrido principal sin alternativa | Lo siguiente, esta semana |
| **Medium** | Útil, pero fuera de las prioridades actuales, o con pocas pruebas | Por orden, cuando no quede nada High |
| **Low** | Estaría bien, estético, caso límite | Cuando no haya otra cosa; podar a los dos meses |
| *(ninguna)* | Todavía sin triaje | Los agentes no lo construyen |

Sé realista: si más de uno de cada cinco elementos abiertos es High o Urgent, los niveles han dejado de significar algo. Baja la prioridad de algo.

### 5.2 Bugs: impacto × alcance

| | La mayoría de los usuarios, o un recorrido principal | Algunos usuarios | Pocos usuarios, o un caso límite |
|---|---|---|---|
| **Bloquea la tarea, pierde o expone datos, seguridad, legal** | Urgent | Urgent | High |
| **Resultado erróneo, pero hay alternativa** | High | Medium | Low |
| **Molesto o estético** | Medium | Low | Low |

### 5.3 Ideas y features: valor, confianza, tamaño

Tras una evaluación tienes tres cosas: el **valor** (cuánto hace avanzar una prioridad actual), la **confianza** (lo buenas que son las pruebas) y el **tamaño** (XS–XL, a partir del código). Reglas prácticas:
- **High:** valor claro para una prioridad actual, buenas pruebas, tamaño S–M.
- **Medium:** buen valor pero pruebas más débiles; o valor alto pero tamaño L–XL (pide que se divida).
- **Low:** poco valor, sea cual sea el tamaño.
- **¿No está entre las prioridades actuales?** Como mucho Medium, salvo que cambies antes las prioridades.

Para comparar dos ideas rápidamente: valor (1–3) × confianza (0,5 / 0,8 / 1) ÷ tamaño (XS 1, S 2, M 3, L 5, XL 8). La puntuación más alta va primero. Es un criterio de desempate, no una fórmula que obedecer.

### 5.4 Orden dentro de una prioridad
Los agentes toman **bugs antes que features, lo más antiguo antes que lo más nuevo, lo más pequeño antes que lo más grande**. Leen la prioridad, no la posición de una tarjeta en el tablero. Si X tiene que ir antes que Y, dale a X una prioridad más alta, o escribe `Blocked by #X` en la descripción de Y.

### 5.5 Mantén las colas sanas

| Cola | Tamaño sano | Si no |
|---|---|---|
| **Agent queue** (Ready) | 3–10 elementos | Vacía: los agentes se quedan parados, así que especifica más. Más de 10: las prioridades se quedan viejas, así que reordena |
| **Decision** | 5 o menos | Resérvate 20 minutos y decide |
| **UAT** | `max_in_uat` (10 por defecto) | Los agentes frenan las construcciones nuevas al llegar al límite (`haam.py capacity`): es tu tiempo para probar, el límite principal en test-first. Prueba con `/test all`; los elementos que los agentes verificaron por completo se aprueban con una sola respuesta (`pass all verified`). Para un fin de semana de trabajo de agentes, abre una ventana de lote en `/haam-settings`: un aumento que termina solo |
| **Agentes en marcha** | No más de los que puedas probar mañana | Menos agentes, elementos más pequeños |
| **PR listas** | `max_open_prs` en `haam.config.json` (10 por defecto) | Los agentes frenan las construcciones nuevas al llegar al límite: cada PR lista cuesta minutos de CI en cada push. Los borradores y las PR solo de documentación no cuentan. Las especificaciones y las evaluaciones siguen adelante. Prueba y lleva a producción lo que está abierto |

### 5.6 Cambiar las prioridades
Cámbialas siempre que cambien los hechos, pero di por qué en un comentario. Los agentes y tus colegas leen el historial. Nunca bajes en silencio la prioridad de un elemento Urgent: coméntalo y avisa a quien lo notificó.

---

## 6. Hacerlo con IA

Usa **tu propio chat en la carpeta principal del proyecto**, no uno de los chats de agente que ejecutan `/work`.

| Quieres… | Escribe |
|---|---|
| Agrupar issues sueltos en epics | `/triage group` |
| Dar forma a un epic: ficha, preguntas para ti, limpieza | `/epic #9` (o `/epic "reporting"` para empezar desde un tema) |
| Hacer el triaje de la bandeja | `/triage` |
| Reordenar Ready y Backlog según las prioridades | `/triage backlog` |
| Encontrar trabajo atascado u olvidado | `/triage stale` |
| Capturar una idea o un bug desde cualquier sitio | `/idea …`, `/bug …` |
| Pedir que se evalúe una idea | `/assess #12` (o deja que `/work ideas` la elija) |
| Decidir (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Aprobar una especificación (G2) | Léela (enlazada en el issue) y después: "spec for #12 approved" |
| Probar un cambio y después llevarlo a producción o devolverlo (G4, G5) | `/test` (o `/test #12`) y después `pass` → `ship`, o di qué falla |
| Cerrar algo que se fusionó de otra forma | `/release #12` |
| Emergencia | `/override #12 "<reason>"` |

**Cómo funciona `/triage`.** El agente lee `PRODUCT.md` y los elementos, y te muestra una sola tabla: flujo propuesto, prioridad, siguiente paso y un motivo breve para cada uno. Responde `ok` para aplicarlo todo, o con cambios (`#14 Low, #9 park until Q3`). No cambia nada hasta que respondes, aplica exactamente lo que confirmaste y comenta en cada elemento para que el motivo quede registrado. Nunca aprueba ideas por ti; para eso te remite a `/decide`.

**Preguntas que vale la pena hacerle a tu agente:**
- "¿Qué está esperando por mí?"
- "¿Qué han terminado los agentes desde ayer y qué está bloqueado?"
- "¿Qué elementos en Ready no encajan con nuestras prioridades actuales?"
- "#12 es demasiado grande. Propón dividirlo en piezas de tamaño S."
- "Compara #12 y #15: ¿cuál debería ir primero y por qué?"
- "Redacta nuevas prioridades actuales para PRODUCT.md a partir de lo que hemos llevado a producción y de lo que hay en el backlog."

Las sugerencias del agente son borradores, y las decisiones son tuyas. Cuando `/bug` registra un bug, rellena una prioridad sugerida; tú la confirmas o la cambias al hacer el triaje.

---

## 7. Hacerlo directamente en GitHub Projects

Todo lo anterior se puede hacer a mano en el tablero. Las vistas guardadas (creadas con `haam.py github-project`) son tu espacio de trabajo:

| Vista | Para qué sirve |
|---|---|
| **Triage** (status: Triage) | Tu bandeja diaria |
| **Epics** (label: epic) | Cada feature y lo avanzados que van sus sub-issues |
| **Waiting on me** (status: Decision, UAT) | Decisiones y pruebas |
| **Agent queue** (status: Ready, sin asignar) | Lo que los agentes tomarán a continuación, por prioridad |
| **Bugs** | Todos los bugs abiertos por prioridad |
| **Ideas inbox** | Ideas en triaje o en evaluación |
| **Board** | Todo el flujo, agrupado por estado |

| Tarea | En el tablero |
|---|---|
| Hacer el triaje de un elemento | Ábrelo. Fija **Priority** y **Status**; corrige la etiqueta de flujo en la barra lateral del issue; comenta tu motivo |
| Aparcar | Status **Parked** y un comentario: "revisar cuando…" |
| Rechazar o marcar como duplicado | Status **Canceled** y después cierra el issue como *not planned* o *duplicate* |
| Aprobar una idea (G1) | Status **Backlog**; sustituye la etiqueta `stream:idea` por `stream:feature`; fija Priority; comenta "Aprobada" |
| Aprobar una especificación (G2) | Comenta "spec approved" en el issue; después Status **Ready** y etiqueta `agent-ready` |
| Agrupar issues en un epic | Crea un issue con la etiqueta `epic`; añade los demás como sus sub-issues |
| Reordenar muchos elementos | Diseño de tabla, agrupado u ordenado por Priority; edita las celdas (puedes copiar un valor y pegarlo en varias celdas seleccionadas) |

Deja esto a las skills: reservar (**In Progress**) es cosa de los agentes. Probar y llevar a producción es más fácil con `/test`; a mano sería: añade la etiqueta `uat-passed` a la PR (eso desbloquea la fusión), fusiónala, aprueba el despliegue (Actions → la ejecución → Review deployments), y después pon el issue en **Done** y ciérralo. Si ha fallado, comenta en el issue qué falla, añade la etiqueta `uat-failed`, vuelve a ponerlo en **Ready** y quita la persona asignada.

---

## 8. Hacerlo directamente en Linear

| Tarea | En Linear |
|---|---|
| Triaje | Usa la bandeja **Triage** del equipo. Puedes aceptar, rechazar, marcar como duplicado o posponer. Después de aceptar, **fija tú el estado de HAAM** (Ready para un bug, Discovery para una idea que evaluar), porque al aceptar el elemento pasa al estado predeterminado del equipo. Fija la prioridad |
| Aparcar o rechazar | Status **Parked** o **Canceled**, con un comentario |
| Agrupar issues en un epic | Crea un issue con la etiqueta `epic`; fíjalo como padre de los issues relacionados |
| Aprobar una idea (G1) | Status **Backlog**, sustituye la etiqueta `stream:idea` por `stream:feature`, fija la prioridad, comenta |
| Aprobar una especificación (G2) | Comenta "spec approved" en el issue; después estado **Ready** y etiqueta `agent-ready` |
| Reordenar | Las vistas de `docs/setup/LINEAR-SETUP.md` §7, ordenadas por prioridad; el menú de comandos (Cmd/Ctrl+K) cambia rápidamente la prioridad o el estado |

Igual que en GitHub, los agentes siguen el campo de prioridad, no el orden manual de una lista.

---

## 9. Trabajar con otras personas

- **Un product owner por producto** fija las prioridades y pasa las puertas. Todos los demás proponen: `/idea`, `/bug`, comentarios.
- Pide a tus colegas que sugieran una prioridad cuando notifiquen algo. Tú la confirmas en el triaje.
- **Los desacuerdos van en el issue,** no en chats privados. El product owner decide y explica por qué en un comentario.
- Si vas a estar fuera, nombra a alguien que apruebe en tu lugar (`haam.py config --backup-approvers`) y dile qué elementos pueden avanzar sin ti.

---

## 10. Mantener bajos los costes de GitHub Actions

Cada pull request ejecuta la CI y dos revisiones de IA en las máquinas de GitHub, y los repositorios privados tienen una asignación mensual de minutos. Los agentes trabajan rápido, así que la asignación se puede agotar en días. Lo que más ayuda, por orden:
1. **Mira primero:** `python3 tools/haam/haam.py ci-usage` muestra qué workflows y jobs han gastado los minutos.
2. **Menos pull requests:** junta los elementos pequeños de un epic en una sola (`/work epic #9`) y mantén bajo el límite de PR abiertas (`max_open_prs` en `haam.config.json`).
3. **Revisiones en tu máquina:** `haam.py settings --set review=local --apply --human` (o `/haam-settings`). Las revisiones de IA usan entonces tu plan de Claude en lugar de minutos; las áreas protegidas (`human-review`) se siguen revisando en GitHub. El compromiso: en GitHub el resultado de la revisión es a prueba de manipulaciones; en local no. Las revisiones se ejecutan en sesiones nuevas de solo lectura con las instrucciones de `main`, pero quien las inicia es el agente que construyó el cambio, y cualquier cosa que use tu inicio de sesión podría publicar un resultado favorable. Para más separación, ejecuta tú `haam.py review <ID>` desde tu propio chat.
4. **Tu propio runner:** `haam.py settings --set runner=self-hosted --apply --human` después de registrar una máquina que esté siempre encendida (`docs/setup/GITHUB-SETUP.md` §8).
5. **Pide una CI más pequeña:** si el proyecto tiene partes separadas (p. ej., backend y aplicación móvil), haz que un agente consiga que `make check` ejecute solo las partes que toca una PR.

## 11. Trampas que evitar

- **Todo es High.** Entonces nada lo es. Baja prioridades hasta que más o menos uno de cada cinco elementos sea High o Urgent.
- **Más agentes de los que puedes probar.** El trabajo se acumula en UAT y se queda viejo. Menos elementos, y más pequeños, avanzan más rápido.
- **"Constrúyelo y ya" en un chat.** Crea primero el issue (`/bug`, `/idea`): lleva un minuto y conserva el historial, la prioridad y la reserva.
- **Aprobar una especificación sin leer los criterios de aceptación.** Es lo que el agente construye y contra lo que tú pruebas. Léelos.
- **Prioridades solo en tu cabeza.** Si no están en `PRODUCT.md` y en el tracker, los agentes no pueden seguirlas.
- **Construir fragmentos sin ver el conjunto.** Si varios issues son en realidad una sola feature, agrúpalos en un epic y dale forma antes de que nadie especifique las piezas.
- **Epics que nunca terminan.** Si un epic lleva meses abierto, separa lo que está hecho y ciérralo.
- **Dejar Triage para "luego".** La bandeja crece y los bugs urgentes se esconden en ella.

---

## 12. Listas de comprobación

**Diaria**
- [ ] Todo lo que está en UAT, probado con `/test`
- [ ] Bandeja de Triage vacía
- [ ] Los bugs urgentes tienen un agente trabajando en ellos
- [ ] Preguntas de los agentes respondidas

**Semanal**
- [ ] Issues sueltos agrupados en epics; epic más prioritario con forma
- [ ] Cola de Decision decidida
- [ ] Especificaciones aprobadas o comentadas
- [ ] Ready y Backlog reordenados
- [ ] Trabajo atascado perseguido (`/triage stale`)
- [ ] Elementos Parked revisados
- [ ] Seguimientos de anulaciones cerrados
- [ ] Una mejora del proceso registrada

**Mensual**
- [ ] Prioridades actuales de `PRODUCT.md` reescritas
- [ ] Elementos Low antiguos aparcados
