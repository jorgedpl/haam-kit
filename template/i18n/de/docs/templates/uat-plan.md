# UAT-Plan: <ID> <Titel>

- **Issue:** <#123 oder APP-123> · **PR:** #NNN · **Spec:** docs/specs/<FILE-ID>-*.md
- **Geschätzte Zeit:** ~N Minuten

## Einrichtung (lokal)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Öffnen: http://localhost:XXXX
- Testkonto/-konten: <synthetische Konten / wie man sie anlegt>
- Feature-Flag: keines / <wie man es einschaltet>

## Testfälle
| # | AC | Schritte | Erwartetes Ergebnis | Bestanden? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Grenzfall | | | [ ] |
| 4 | Regression | Die Haupt-Journey von Anfang bis Ende durchspielen: <beschreiben> | Funktioniert wie vorher | [ ] |

## Nicht Teil dieses Tests
- 

## Vorabprüfung durch den Agenten (Agent pre-check)
<!-- Vom Agenten ausgefüllt: was er selbst geprüft hat (Tests, `make e2e`, ein Browser-Tool) und was er gesehen hat. -->
- **Fully verified by the agent:** no  <!-- „yes“ nur unter den Regeln in /uat Schritt 3; dann kann der Product Owner es mit „pass all verified“ bestehen lassen -->
- Belege: <die Befehle oder Läufe und ihre Ergebnisse, eine Zeile pro Akzeptanzkriterium>

## Ergebnisse
Werden von `/test` (oder `/uat-result`) als Kommentare im Issue und im PR festgehalten, sodass das Festhalten eines Ergebnisses nie den getesteten Code ändert.
