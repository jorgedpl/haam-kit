# ADR 0001: Adoptar la Human-Agent Agile Methodology (HAAM)

- **Estado:** Aceptada
- **Fecha:** YYYY-MM-DD
- **Decidido por:** Product owner

## Contexto
Cada vez más trabajo de este producto lo hacen agentes de programación (Claude Code, Cursor, Codex, Grok y otros). Sin un proceso compartido, el contexto vive en chats individuales, las prioridades son implícitas y un segundo desarrollador con su propia cuenta de Claude no puede trabajar en paralelo. También necesitamos que una persona verifique los cambios de producción antes de publicarlos, con una forma de ir rápido en las emergencias.

## Decisión
- El tracker (GitHub Projects o Linear, elegido por proyecto en `haam.config.json`) es el sistema de registro de los elementos de trabajo, su estado y su prioridad. Git es el sistema de registro de las especificaciones, las decisiones, los planes de UAT y el código.
- El trabajo sigue HAAM tal como se describe en `docs/process/LIFECYCLE.md`, con cinco puertas (`docs/process/GATES.md`).
- Los agentes, sea cual sea la herramienta, siguen `AGENTS.md` y las skills compartidas de `.agents/skills/`.
- Las puertas G3–G5 las impone GitHub (protección de rama, comprobaciones obligatorias, un entorno `production` protegido). G1–G2 se imponen por convención y por el estado del tracker.
- Las personas pueden anular puertas con un motivo registrado y un issue de seguimiento automático.

## Consecuencias
- Algo más de ceremonia para los cambios pequeños, compensada porque los agentes hacen la mayor parte del papeleo.
- Cualquiera puede retomar cualquier issue solo con el tracker y Git.
- Requiere un tracker (un tablero de GitHub Projects, o un espacio de trabajo de Linear con su integración con GitHub) y protección de rama en `main` en GitHub.

## Alternativas consideradas
- **Solo GitHub Issues + Projects:** menos herramientas, pero triaje, prioridades y vistas de planificación más pobres.
- **Jira:** más potente, pero más pesado de lo que necesita un equipo pequeño.
- **Sin proceso formal:** lo más rápido hoy, pero no escala a agentes en paralelo ni a un segundo desarrollador.
