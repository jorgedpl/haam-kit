# Plan de UAT: <ID> <título>

- **Issue:** <#123 o APP-123> · **PR:** #NNN · **Especificación:** docs/specs/<FILE-ID>-*.md
- **Tiempo estimado:** ~N minutos

## Preparación (local)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Abre: http://localhost:XXXX
- Cuenta(s) de prueba: <cuentas sintéticas / cómo crearlas>
- Feature flag: ninguna / <cómo activarla>

## Casos de prueba
| # | AC | Pasos | Resultado esperado | ¿Superado? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Caso límite | | | [ ] |
| 4 | Regresión | Recorre el recorrido principal de principio a fin: <descríbelo> | Funciona como antes | [ ] |

## Fuera del alcance de esta prueba
- 

## Comprobación previa del agente (Agent pre-check)
<!-- La rellena el agente: lo que comprobó por sí mismo (pruebas, `make e2e`, una herramienta de navegador) y lo que vio. -->
- **Fully verified by the agent:** no  <!-- "yes" solo con las reglas del paso 3 de /uat; entonces el product owner puede aprobarlo con "pass all verified" -->
- Pruebas: <los comandos o ejecuciones y sus resultados, una línea por criterio de aceptación>

## Resultados
Se registran como comentarios en el issue y en la PR mediante `/test` (o `/uat-result`), de modo que registrar un resultado nunca cambia el código que se probó.
