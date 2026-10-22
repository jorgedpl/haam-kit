# Gates und Overrides

Zwischen einer Idee und der Produktion stehen fünf Gates. Jedes hat eine klare Verantwortung, eine Checkliste und, wo möglich, einen automatischen Kontrollpunkt, damit die Regel nicht davon abhängt, dass jemand an sie denkt.

| Gate | Zwischen | Verantwortlich | Durchgesetzt durch |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Mensch (PO) | Status im Tracker: Nur Menschen führen `/decide` aus |
| **G2 Ready** | Backlog → Ready | Mensch gibt die Spec frei | Label `agent-ready`; Agenten bauen nur Issues mit `agent-ready` |
| **G3 Verified** | In Progress → UAT | Automatische Checks + unabhängiger Reviewer-Agent (+ Mensch für geschützte Bereiche) | Erforderliche Checks `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → Merge | Testende Person | Erforderlicher Check `release-gate` (braucht das PR-Label `uat-passed` oder `gate-override`) |
| **G5 Released** | Merge → Produktion | Mensch (PO) | GitHub-Environment `production` mit verpflichtendem Reviewer |

---

## Checkliste für G1 Decision

Die Bewertung (oder, bei einer als Prototyp gebauten Idee, die Notizen zum Prototyp aus `/spike`) muss enthalten:
- [ ] Problembeschreibung und für wen es ist
- [ ] Schätzung des Werts mit Belegen (oder ausdrücklich „noch keine Belege“)
- [ ] Größe des Aufwands mit Begründung aus der Codebasis
- [ ] Risiken: Sicherheit, Datenschutz (z. B. DSGVO), Regulierung, Betrieb
- [ ] Mindestens zwei Optionen plus „nichts tun“
- [ ] Eine Empfehlung

Der Mensch antwortet mit einem von: **approve** (mit Priorität), **park** (mit Auslöser für die Wiedervorlage), **reject** (mit Begründung). Bei einem Prototyp probiert er ihn zuerst aus (`/test`), sodass die Entscheidung auf der Nutzung beruht statt auf dem Lesen darüber.

## G2 Definition of Ready

Ein Issue darf `agent-ready` nur bekommen, wenn:
- [ ] eine Spec in `docs/specs/` existiert und im Issue verlinkt ist
- [ ] die Akzeptanzkriterien als Given / When / Then geschrieben sind und jedes testbar ist
- [ ] Umfang und **was nicht dazugehört** ausdrücklich benannt sind
- [ ] voraussichtlich betroffene Dateien und Module aufgelistet sind
- [ ] Auswirkungen auf Daten, Migrationen und Konfiguration genannt sind (oder „keine“)
- [ ] ein Plan für Unit-Tests und eine Skizze für den UAT enthalten sind
- [ ] die Größe ≤ 1 Tag Agentenarbeit ist (~400 geänderte Zeilen); sonst in Sub-Issues aufteilen
- [ ] betroffene geschützte Bereiche markiert sind (Label `human-review` gesetzt)
- [ ] die Priorität gesetzt ist
- [ ] ein Mensch die Spec freigegeben hat

## G3 Verified (Definition of Done für Code)

- [ ] Jedes Akzeptanzkriterium hat mindestens einen automatischen Test
- [ ] `make check` läuft lokal und in der CI durch (Lint, Typen, Unit-Tests, Build)
- [ ] Keine fremden Änderungen im Diff
- [ ] Von der Änderung betroffene Doku ist aktualisiert (`ARCHITECTURE.md`, API-Doku, Liste der Umgebungsvariablen)
- [ ] Keine Secrets, keine echten personenbezogenen Daten in Code, Tests oder Fixtures
- [ ] Die PR-Beschreibung folgt der Vorlage und verlinkt das Issue (`Refs #123` auf GitHub Projects, ID im Titel auf Linear)
- [ ] Check `secrets` grün: keine Schlüssel, Tokens oder Passwörter in irgendeinem Commit des PR
- [ ] Check `dependencies` grün: keine bekannten Schwachstellen mit hohem oder kritischem Schweregrad
- [ ] `ai-review` grün: Der unabhängige Reviewer-Agent hat keine blockierenden Probleme gefunden
- [ ] `security-review` grün: Das Security-Review von Claude hat keine Schwachstellen gefunden
- [ ] Menschliches Code-Review erledigt, falls das Label `human-review` gesetzt ist

### So funktioniert das Code-Review

Das Review ist in Schichten aufgebaut, damit **kein Agent je seine eigene Arbeit prüft** und **Secrets von deterministischen Tools gefunden werden, nicht durch Einschätzung**.

| Schicht | Wann | Was | Wer / was es macht |
|---|---|---|---|
| 1. Lokaler Secret-Schutz | Vor jedem Commit | Blockiert Commits mit Schlüsseln oder Tokens | gitleaks über den Git-Pre-Commit-Hook (alle, jedes Tool), dazu Hooks im Agenten-Tool, wo unterstützt (Claude Code; Grok) |
| 2. Selbstprüfung | Vor dem Öffnen eines PR | `make check` + `/security-review` auf die eigenen Änderungen | Der bauende Agent |
| 3. Deterministische CI | Bei jedem Push auf einen PR | Tests, Lint, Typen, Secret-Scan jedes Commits, Prüfung der Abhängigkeiten | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Unabhängiges KI-Review | Bei jedem Push auf einen PR (nicht bei Drafts oder reinen Doku-PRs) | Übereinstimmung mit der Spec, ehrliche Tests, Korrektheit, Projektregeln; Sicherheitslücken | Ein separates Claude in GitHub Actions, das nie gesehen hat, wie der Code geschrieben wurde (`ai-review`, `security-review`) |
| 5. Menschliches Review | PRs mit dem Label `human-review` | Geschützte Bereiche: Kernlogik, Authentifizierung, Zahlungen, personenbezogene Daten, Migrationen, Infrastruktur | Product Owner oder ein benannter Developer |
| 6. Menschliche Abnahme | Jeder Code-PR | Das Verhalten funktioniert wirklich (G4 UAT) | Product Owner |

**Regeln für die Review-Schleife**
- Der bauende Agent liest den Kommentar des Reviewers, behebt jeden **Blocking**-Punkt und pusht; die Reviews laufen automatisch erneut.
- Hält der bauende Agent einen Befund für falsch, antwortet er im PR mit einer Begründung und fragt den Menschen. Er diskutiert nie im Kreis: **Nach zwei Review-Runden**, die immer noch fehlschlagen, hört er auf und übergibt an den Menschen.
- Nur ein Mensch kann ein KI-Review überstimmen, mit dem PR-Label `ai-review-overruled`. Das wird im PR festgehalten.
- KI-Reviewer können nicht freigeben oder mergen. Sie können nur blockieren.

### Falls je ein Secret auf GitHub landet
1. **Widerrufe und rotiere es sofort** beim Anbieter. Geh davon aus, dass es kompromittiert ist; es aus dem Code zu entfernen, macht das Leck nicht ungeschehen.
2. Entferne es aus dem Code; nutze eine Umgebungsvariable, die in `.env.example` dokumentiert ist.
3. Ein Repo-Admin schreibt die Historie des Branches vor dem Merge um (ein neuer Commit reicht nicht).
4. Lege einen `/bug` mit Priorität Urgent an, um festzuhalten, was passiert ist und was rotiert wurde (nie das Secret selbst hineinschreiben).

**Die Einstellungen des Product Owners ändern, wie G3 läuft, nicht wer entscheidet** (`/haam-settings`):
- `ci`: bei jedem PR, lokal (`ci-local`, gemeldet von `haam.py local-ci` auf dem Computer des Product Owners) oder aus.
- `review`: GitHub, lokal, nur geschützte Bereiche oder aus.
- `nightly`.

Die erforderlichen Checks folgen den Einstellungen (`settings --apply`). Der Secret-Scan läuft immer.

## G4 Accepted (UAT)

Im Standardablauf test-first kommt G4 vor G3: Der Product Owner testet den gepushten Branch des Agenten, bevor es einen PR gibt, und G3 prüft dann genau den Commit, der bestanden hat (`haam.py publish`, dann `ship`, das alles andere ablehnt).

**Spur ohne UAT:** Hier wird G4 stattdessen vorab entschieden. Markiert der Product Owner ein Issue mit `uat:skip` (in `/triage` oder mit „Spec freigegeben, kein UAT“), öffnet der Agent den PR mit demselben Label, und `release-gate` ist bestanden, sobald jedes Issue, zu dem der PR gehört, das Label trägt (GitHub Projects: Das Gate liest die Issues; Linear: Es vertraut dem PR-Label). Nie, wenn der PR einen geschützten Bereich ändert: Das Gate prüft die geänderten Dateien gegen `protected_paths` in `haam.config.json` auf `main` (standardmäßig die Konfiguration von Agenten und CI, dazu die eigenen des Projekts), setzt `human-review` und hält die Spur geschlossen, egal was die Labels sagen. Ein Update des Kits nimmt also nie diese Spur: Es ändert die Konfiguration der Agenten, und du prüfst es und lieferst es selbst aus. G3 gilt weiterhin vollständig, und Auto-Merge (braucht `HAAM_PROJECT_TOKEN`) mergt nur, wenn jeder erforderliche Check bestanden ist. Auf Linear gibt es kein Auto-Merge, und auch nicht, wenn die CI oder eines der KI-Reviews irgendwo anders läuft als auf GitHub für jeden PR (Auto-Merge braucht `ci: every-pr` und `review: github`): Lokale Ergebnisse sind nicht manipulationssicher, und reduzierte Checks reichen allein nicht aus. Diese PRs der Spur liefert also der Product Owner aus (`ship`), was trotzdem eine Entscheidung für viele ist. Nur die Entscheidung eines Menschen fügt einem Issue `uat:skip` hinzu (`issue create` und `issue label` lehnen es ohne `--human` ab).

- [ ] Ein UAT-Plan existiert in `docs/uat/` mit nummerierten Schritten und erwarteten Ergebnissen
- [ ] Ein Mensch hat ihn lokal auf dem Branch durchgeführt (test-first: auf dem gepushten Branch des Agenten, vor jedem PR; checks-first: auf dem Branch des PR)
- [ ] Alle Schritte bestehen, oder Fehler sind festgehalten und als Folge-Issues akzeptiert
- [ ] Das Bestehen durch den Menschen (`/test` oder `/uat-result <ID> pass`) fügt dem PR das Label `uat-passed` hinzu (test-first: `publish` hält es außerdem als Status `uat` auf dem getesteten Commit fest)
- [ ] Das Bestehen gilt für den Code, der gemergt wird: Ein Push danach entfernt `uat-passed` (`gates.yml`), außer der neue Head ist der getestete Commit; `ship` mergt nur diesen Commit

## G5 Released

- [ ] PR nach `main` gemergt, von einem Menschen oder von `haam.py ship --human`, nachdem der Mensch `ship` gesagt hat
- [ ] Produktions-Deploy freigegeben (Environment `production`): in GitHub oder durch `ship` auf das Wort des Menschen hin
- [ ] Smoke-Test nach dem Deploy bestanden (`make smoke`, falls definiert)
- [ ] Das Issue ist als Done markiert (`ship`, oder `/release` für Änderungen, die anders gemergt wurden); die Release Note in `docs/changes/` wurde mit ausgeliefert

---

## Overrides

Manchmal brennt die Produktion, oder eine Frist wartet nicht. Dafür gibt es Overrides, und sie sind **nur für Menschen**.

### Stufe 1: UAT überspringen (am häufigsten)
Nutze das, wenn der Fix dringend und durch Tests geprüft ist, aber keine Zeit für einen vollen UAT-Zyklus bleibt.

1. Der Mensch führt `/override <ID> "<reason>"` aus (für einen PR ohne Issue: `/override PR <number> "<reason>"`) oder kommentiert von Hand `OVERRIDE: <reason>` im PR (der Kommentar muss mit `OVERRIDE:` beginnen) und setzt das PR-Label `gate-override`.
2. Der Check `release-gate` besteht durch das Override-Label.
3. Die CI (Check `ci`) **muss trotzdem bestehen**.
4. Hat der PR ein Issue, legt der Agent ein Folge-Issue im Tracker an: `Post-override UAT for <ID>` (Priorität High, Label `stream:bug`, `override-followup`), damit die übersprungene Prüfung nachträglich doch noch stattfindet.

### Stufe 2: Notfall-Umgehung (selten)
Nur nutzen, wenn die CI selbst kaputt ist oder einen Fix in der Produktion blockiert.

1. Ein Admin des Repositorys mergt in GitHub mit „bypass branch protections“.
2. Der Admin kommentiert `EMERGENCY BYPASS: <reason>` im PR.
3. Ein Folge-Issue wird wie oben angelegt, dazu ein zweites, um zu beheben, was die CI blockiert hat.

### Regeln für Overrides
- Agenten setzen **nie** `gate-override`, umgehen nie Schutzregeln und schlagen nie einen Override vor, außer der Mensch bringt ihn zuerst ins Spiel.
- Jeder Override braucht eine schriftliche Begründung im PR.
- Overrides werden beim wöchentlichen Backlog-Review durchgesehen: Filtere den Tracker nach dem Label `override-followup`.
