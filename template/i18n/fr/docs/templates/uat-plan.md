# Plan UAT : <ID> <titre>

- **Issue :** <#123 ou APP-123> · **PR :** #NNN · **Spec :** docs/specs/<FILE-ID>-*.md
- **Durée estimée :** ~N minutes

## Mise en place (en local)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Ouvrir : http://localhost:XXXX
- Compte(s) de test : <comptes synthétiques / comment les créer>
- Feature flag : aucun / <comment l'activer>

## Cas de test
| # | AC | Étapes | Résultat attendu | Validé ? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Cas limite | | | [ ] |
| 4 | Non-régression | Dérouler le parcours principal de bout en bout : <décrire> | Fonctionne comme avant | [ ] |

## Hors périmètre de ce test
- 

## Vérification préalable par l'agent (Agent pre-check)
<!-- Remplie par l'agent : ce qu'il a vérifié lui-même (tests, `make e2e`, un outil de navigateur) et ce qu'il a constaté. -->
- **Fully verified by the agent:** no  <!-- « yes » uniquement selon les règles de l'étape 3 de /uat ; le product owner peut alors le valider avec « pass all verified ». Ce libellé reste en anglais : les skills le lisent tel quel. -->
- Preuves : <les commandes ou exécutions, et leurs résultats, une ligne par critère d'acceptation>

## Résultats
Consignés en commentaires dans l'issue et la PR par `/test` (ou `/uat-result`), si bien qu'enregistrer un résultat ne modifie jamais le code qui a été testé.
