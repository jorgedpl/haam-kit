# Plano de UAT: <ID> <título>

- **Issue:** <#123 ou APP-123> · **PR:** #NNN · **Spec:** docs/specs/<FILE-ID>-*.md
- **Tempo estimado:** ~N minutos

## Preparação (local)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Abra: http://localhost:XXXX
- Conta(s) de teste: <contas sintéticas / como criá-las>
- Feature flag: nenhuma / <como ativar>

## Casos de teste
| # | AC | Passos | Resultado esperado | Passou? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Caso-limite | | | [ ] |
| 4 | Regressão | Percorra a jornada principal de ponta a ponta: <descreva> | Funciona como antes | [ ] |

## Fora do escopo deste teste
- 

## Pré-verificação do agente (Agent pre-check)
<!-- Preenchida pelo agente: o que ele mesmo verificou (testes, `make e2e`, uma ferramenta de navegador) e o que observou. -->
- **Fully verified by the agent:** no  <!-- verificado por completo pelo agente: "yes" só sob as regras do passo 3 do /uat; nesse caso, o product owner pode aprovar com "pass all verified" -->
- Evidências: <os comandos ou execuções e os resultados deles, uma linha por critério de aceitação>

## Resultados
Registrados como comentários na issue e no PR pelo `/test` (ou pelo `/uat-result`), para que registrar um resultado nunca altere o código que foi testado.
