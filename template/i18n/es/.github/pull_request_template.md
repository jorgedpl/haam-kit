## Issue
<!-- GitHub Projects: conserva la línea de abajo con el número del issue (usa Refs, no Closes: el issue se cierra en /release). Linear: pon el ID en el título de la PR (APP-123: …). -->
Refs #

## Hecho con (Built with)
<!-- Herramienta de agente y modelo (p. ej. Claude Code / Opus, Cursor / <model>, Codex, Grok Build), o "human". -->

## Qué y por qué
<!-- 2–4 frases. Qué cambió para el usuario y por qué. -->

## Criterios de aceptación → pruebas
| AC | Prueba(s) | Estado |
|---|---|---|
| AC1 | `test_…` | ✅ |

## Cómo verificarlo
- Plan de UAT: `docs/uat/<GH-123 or APP-123>-*.md` (lo añade `/uat`)
- Capturas de pantalla / notas:

## Riesgo
- Áreas protegidas afectadas: ninguna / <lista> (si hay alguna → etiqueta `human-review`)
- Migraciones: ninguna / <descripción + marcha atrás>
- Cambios de configuración o de entorno: ninguno / <lista>

## Lista de comprobación (G3)
- [ ] `make check` pasa en local
- [ ] Cada criterio de aceptación tiene una prueba
- [ ] No hay cambios ajenos
- [ ] Documentación actualizada (ARCHITECTURE.md, .env.example, …) o no hace falta
- [ ] Ni secretos ni datos personales reales

<!-- Puerta de release (G4): esta PR solo se puede fusionar con la etiqueta `uat-passed`, o con `gate-override` más un comentario "OVERRIDE: <reason>". Las PR solo de documentación están exentas. -->
