# UAT-plan: <ID> <titel>

- **Issue:** <#123 of APP-123> · **PR:** #NNN · **Spec:** docs/specs/<FILE-ID>-*.md
- **Geschatte tijd:** ~N minuten

## Setup (lokaal)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Open: http://localhost:XXXX
- Testaccount(s): <synthetische accounts / hoe je ze aanmaakt>
- Feature flag: geen / <hoe je hem aanzet>

## Testgevallen
| # | AC | Stappen | Verwacht resultaat | Geslaagd? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Randgeval | | | [ ] |
| 4 | Regressie | Doorloop het hoofdtraject van begin tot eind: <beschrijf> | Werkt zoals voorheen | [ ] |

## Niet in scope voor deze test
- 

## Controle vooraf door de agent (Agent pre-check)
<!-- Ingevuld door de agent: wat hij zelf gecontroleerd heeft (tests, `make e2e`, een browsertool) en wat hij zag. -->
- **Fully verified by the agent:** no  <!-- "yes" alleen volgens de regels in /uat stap 3; dan kan de product owner het goedkeuren met "pass all verified". -->
- Bewijs: <de commando's of runs, en hun resultaten, één regel per acceptatiecriterium>

## Resultaten
Vastgelegd als commentaar op het issue en de PR door `/test` (of `/uat-result`), zodat het vastleggen van een resultaat nooit de code verandert die getest is.
