# Piano di UAT: <ID> <titolo>

- **Issue:** <#123 o APP-123> · **PR:** #NNN · **Specifica:** docs/specs/<FILE-ID>-*.md
- **Tempo stimato:** ~N minuti

## Preparazione (in locale)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Apri: http://localhost:XXXX
- Account di test: <account sintetici / come crearli>
- Feature flag: nessuno / <come attivarlo>

## Casi di test
| # | AC | Passi | Risultato atteso | Superato? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Caso limite | | | [ ] |
| 4 | Regressione | Esegui il percorso principale dall'inizio alla fine: <descrivi> | Funziona come prima | [ ] |

## Fuori dall'ambito di questo test
- 

## Verifica preliminare dell'agente (Agent pre-check)
<!-- La compila l'agente: cosa ha controllato da sé (test, `make e2e`, uno strumento di browser) e cosa ha visto. -->
- **Fully verified by the agent:** no  <!-- "yes" solo alle condizioni del passo 3 di /uat; allora l'owner può approvarlo con "pass all verified" -->
- Evidenze: <i comandi o le esecuzioni, e i loro risultati, una riga per criterio di accettazione>

## Risultati
Registrati come commenti sulla issue e sulla PR da `/test` (o `/uat-result`), così registrare un risultato non cambia mai il codice che è stato testato.
