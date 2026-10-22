# Glosario español (es)

Cómo se traducen los términos clave de HAAM en los documentos en español, para que las próximas ediciones sean coherentes.

**Registro:** tuteo ("tú"), en español neutro internacional, como la documentación de GitHub en español. Frases cortas. Sin regionalismos.

**Se mantiene en inglés siempre:** todo lo que va entre comillas invertidas, los bloques de código, los destinos de los enlaces, los nombres de estado del tablero (Triage, Discovery, Decision, Backlog, Ready, In Progress, In Review, UAT, Deploying, Done, Parked, Canceled), las etiquetas (epic, bug…), las puertas G1–G5, los nombres de productos y herramientas, y las palabras que se escriben al agente (`pass`, `ship`, `ship --all`, `OVERRIDE`, `EMERGENCY BYPASS`).

| Inglés | Español | Nota |
|---|---|---|
| agent / coding agent | agente / agente de programación | |
| human | persona, humano | "Humans decide" → "Las personas deciden" |
| product owner, owner | product owner | Se usa tal cual en el ágil en español; "the owner" → "el product owner" |
| product manager | product manager | |
| developer | desarrollador, persona desarrolladora | |
| project admin | administrador del proyecto | |
| computer / machine | máquina | "on your computer" → "en tu máquina"; "locally" → "en local". Evita "computadora/ordenador" |
| team | equipo | "equipo" solo para personas, nunca para la máquina |
| issue | issue (masc.: "el issue") | No "incidencia": los issues también son ideas y features |
| ticket | ticket | |
| tracker | tracker (masc.) | El gestor de trabajo: tablero de GitHub Projects o Linear |
| board | tablero | |
| backlog | backlog | También como concepto |
| work stream | flujo de trabajo | "three work streams" → "tres flujos de trabajo" |
| idea / feature / bug | idea / feature / bug | "feature" (fem.: "la feature") para el trabajo aprobado |
| epic | epic (masc.: "el epic") | Es una etiqueta del tablero |
| epic brief | ficha del epic | |
| sub-issue | sub-issue | |
| slice | porción | "small slices" → "porciones pequeñas" |
| gate | puerta | "Gate G1" → "puerta G1" |
| override (a gate) | anular (una puerta), anulación | |
| skill | skill (fem.: "la skill") | Formato Agent Skills |
| spec / specification | especificación | "spec" solo en nombres de comandos |
| assess / assessment | evaluar / evaluación | |
| spike | spike | Prototipo desechable en rama `spike/` |
| prototype | prototipo | |
| throwaway | desechable | |
| build (implement) | construir | "Build + unit tests" → "Construcción + pruebas unitarias" |
| build (compile step) | build | |
| unit tests | pruebas unitarias | |
| UAT | UAT (pruebas de aceptación de usuario) | "UAT plan" → "plan de UAT" |
| test (verb, by the owner) | probar | |
| pass / fail (UAT) | aprobar / suspender (la prueba) | La palabra que se escribe sigue siendo `pass` |
| check(s) | comprobación(es) | "required checks" → "comprobaciones obligatorias" |
| CI | CI | |
| secret scan | escaneo de secretos | |
| AI review / reviewer | revisión de IA / revisor | |
| code review | revisión de código | |
| protected area | área protegida | |
| pull request / PR | pull request / PR (fem.: "la PR") | |
| draft PR | PR en borrador | |
| commit | commit (masc.) | "hacer commit" |
| branch | rama | |
| merge | fusionar, fusión | "auto-merge" se mantiene |
| push | subir, hacer push | |
| rebase | hacer rebase | |
| worktree | worktree (masc.) | |
| repository / repo | repositorio / repo | |
| deploy | desplegar, despliegue | |
| ship | llevar a producción | El comando sigue siendo `ship` |
| release (kit version) | versión publicada, release | |
| release (close after deploy) | cerrar tras el despliegue | |
| release note | nota de versión | |
| smoke check / test | prueba de humo | |
| lane | carril | "no-UAT lane" → "carril sin UAT" |
| claim (an issue) | reservar, reserva | "the claim" → "la reserva" |
| handover | traspaso | |
| label | etiqueta | |
| status | estado | |
| settings | ajustes | |
| workflow (GitHub Actions) | workflow | |
| hook | hook | |
| feature flag | feature flag | |
| token / prompt | token / prompt | |
| triage (verb) | hacer triaje, clasificar | El estado es Triage |
| acceptance criteria | criterios de aceptación | |
| Definition of Ready | Definition of Ready (definición de listo) | |
| rollout / rollback | despliegue / marcha atrás | |
| gotcha | trampa, detalle a tener en cuenta | |
| queue | cola | |
| digest | resumen | |
| ceremonies | ceremonias | |
| guard-rails | barreras de seguridad | |
| Built with (PR field) | Hecho con (Built with) | Encabezado de la plantilla de PR; se cita igual en todos los documentos |
| Agent pre-check (UAT plan) | Comprobación previa del agente (Agent pre-check) | La línea `- **Fully verified by the agent:** no` se deja en inglés: las skills la buscan |
