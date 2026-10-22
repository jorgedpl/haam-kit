# Human-Agent Agile Methodology (HAAM)
## Einführungsleitfaden für den Projekt-Admin

HAAM ist eine Art, Software zu bauen, bei der **Menschen entscheiden und Agenten ausführen**. Jede Arbeit geht von der Idee bis in die Produktion durch dieselben Phasen, mit menschlichen Gates an den Stellen, auf die es ankommt. Alles liegt in **Git** (Wissen und Code) und im **Tracker** (Arbeit und Status): einem **GitHub Projects**-Board (kostenlos) oder **Linear**. Menschen können verschiedene Coding-Agenten (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) mit eigenen Konten nutzen und trotzdem parallel arbeiten.

Dieser Leitfaden führt HAAM in einem bestehenden Repository in **sechs Phasen ein, insgesamt etwa ein halber Tag**. Du kannst nach jeder Phase aufhören und hast trotzdem schon etwas Nützliches.

---

## Das Kit holen

Das Kit ist der Ordner `template/` von https://github.com/jorgedpl/haam-kit. Nutze immer eine veröffentlichte Version:
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
oder lade das Zip von der Releases-Seite herunter. Im Folgenden meint `<path-to-kit>` diesen Ordner `template/`.

## Der schnelle Weg: Lass deinen Agenten das machen

Leg das Kit irgendwo außerhalb deines Projekts ab, öffne deinen Coding-Agenten **im Stammordner deines Projekts** und sag:

> Lies `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` und folge der Anleitung, um HAAM in diesem Repository einzurichten. Das Kit liegt unter `<path-to-kit>`.

Der Agent steuert das Setup-Tool (`tools/haam/haam.py`) durch jede der folgenden Phasen. Er stellt dir eine Handvoll Fragen, zeigt jede Änderung, bevor er sie vornimmt, und gibt dir die wenigen Schritte, die deine Passwörter oder Schlüssel brauchen, zum Ausführen in deinem eigenen Terminal. Nutze den Rest dieses Leitfadens, um zu verstehen, was er tut, oder um es von Hand zu machen.

### Wer beim Setup was macht

| Markiert als | Bedeutet |
|---|---|
| `[agent]` | Dein Coding-Agent erledigt es (oder du, wenn du es von Hand machst) |
| `[YOU, in your terminal]` | Du führst den Befehl selbst aus: Er betrifft ein Secret (API-Schlüssel, Login), das nie durch den Chat eines Agenten gehen darf |
| `[YOU, in the browser]` | Eine Einstellung, die GitHub oder Linear nur in der Web-App anbietet |

---

## Was du bekommst

```
START-HERE.md                 Kit entry point (not copied into your repo)
AGENTS.md                     Rules every agent reads, whatever the tool
CLAUDE.md                     Pointer to AGENTS.md for Claude Code
haam.config.json              Project settings for the setup tool (created by `config`; no secrets)
haam.lock.json                Installed kit version and file fingerprints (used by `update`)
docs/changes/                 One release note per shipped change (added by /uat)
Makefile                      Command contract: setup, hooks, dev, test, check, audit, secrets, smoke, deploy
tools/haam/haam.py            Setup tool: install, config, agents, github, github-project, linear, issue, worktree, invite, dev, doctor
scripts/scan-secrets.sh       Secret scan (gitleaks) shared by all commit hooks
.githooks/pre-commit          Blocks commits containing secrets (any human, any agent using git)
.agents/skills/               One skill per stage, shared by all agent tools
.worktreeinclude              Local files (like .env) to copy into each agent's worktree
.claude/                      Claude Code: settings (guard-rails), hooks, skills link
.cursor/mcp.json              Cursor: Linear connection (Linear projects)
.grok/skills                  Grok Build: skills link
.gemini/settings.json         Gemini CLI: read AGENTS.md
.mcp.json                     Linear connection (Claude Code, Grok; Linear projects)
.github/
  pull_request_template.md    Includes "Built with" (agent tool and model)
  workflows/ci.yml            Gate G3: tests on every PR
  workflows/security.yml      Gate G3: secret scan of every commit + dependency audit
  workflows/review.yml        Gate G3: independent AI reviewers (spec/quality + security)
  workflows/tracker-sync.yml    Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/              Idea and bug forms (GitHub Projects)
  workflows/gates.yml         Gate G4: blocks merge until UAT passed or overridden
  workflows/deploy.yml        Gate G5: production deploy waits for human approval
  review/REVIEWER.md          Instructions for the reviewer agent
  dependabot.yml              Dependency update PRs
docs/
  process/LIFECYCLE.md        The methodology: streams, stages, statuses, roles
  process/GATES.md            Gate checklists, code review, overrides
  process/TRACKER.md          How each tracker operation works on GitHub Projects and on Linear
  product/PRODUCT.md          Your product context (you confirm it)
  product/ARCHITECTURE.md     Map of your codebase (the agent drafts it)
  setup/HAAM-ADOPTION-GUIDE.md  This guide
  setup/DECISIONS.md          Every choice to make (accounts and plan, tracker, settings, limits, what to protect), with recommendations
  setup/AGENTS-SETUP.md       Per-tool setup: Claude Code, Cursor, Codex, Grok, Gemini, Copilot
  setup/LINEAR-SETUP.md       Linear configuration in detail
  setup/GITHUB-SETUP.md       GitHub configuration in detail
  ONBOARDING.md               Guide for new developers
  templates/                  idea, bug, assessment, feature-spec, uat-plan, adr
  decisions/0001-adopt-haam.md
  assessments/ specs/ uat/    Filled in automatically as work flows
```

### Der Lebenszyklus in einem Bild

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### Die Befehle

Hier als `/name` geschrieben (Claude Code, Cursor, Grok). In Codex nutzt du `$name`. Jedes andere Tool: *„folge `.agents/skills/<name>/SKILL.md`“*.

| Befehl | Phase | Wer |
|---|---|---|
| `/idea <text>` | Eine Idee erfassen | Alle |
| `/bug <text>` | Ein Problem melden | Alle |
| `/assess APP-12` | Wert, Aufwand, Risiko, Machbarkeit bewerten | Agent |
| `/triage` | Den Eingang triagieren, Issues zu Epics bündeln (`group`), neu ordnen (`backlog`), festhängender Arbeit nachgehen (`stale`) | Nur Menschen |
| `/epic APP-9` | Ein Epic formen: Brief, Fragen an dich, Aufräumen seiner Issues | Nur Menschen |
| `/decide APP-12 approve` | Gate G1 | Nur Menschen |
| `/spec APP-12` | Eine baufertige Spec schreiben | Agent |
| `/work bugs` | Einen Agenten in einem neuen Chatfenster starten: eigener Worktree, dann `/next` | Alle |
| `/next` | Den nächsten Eintrag aus Bugs, Features und Ideen nehmen | Agent |
| `/build APP-12` | Mit Unit-Tests implementieren, einen PR öffnen | Agent |
| `/uat APP-12` | Deinen lokalen Testplan schreiben | Agent |
| `/test` | Eine Änderung testen, dann `pass` → `ship`, oder sagen, was nicht stimmt (G4 und G5) | Nur Menschen |
| `/uat-result APP-12 pass` | Ein Testergebnis einzeln festhalten (G4) | Nur Menschen |
| `/override APP-12 "reason"` | UAT im Notfall überspringen | Nur Menschen |
| `/release APP-12` | Nach dem Deploy abschließen | Nur Menschen |
| `/haam-setup` | HAAM in einem Repo einführen | Projekt-Admin |
| `/haam-onboard` | Einen neuen Developer startklar machen | Neuer Developer |
| `/haam-update` | Auf eine neue Kit-Version aktualisieren | Projekt-Admin |

### So funktioniert das Code-Review

Kein Agent prüft je seine eigene Arbeit, und Secrets werden von einem Scanner gefunden statt durch Einschätzung. Jede Änderung durchläuft sechs Schichten:

| Schicht | Wann | Was sie prüft | Wer es macht |
|---|---|---|---|
| 1. Lokaler Secret-Schutz | Vor jedem Commit | Schlüssel, Tokens, Passwörter in den Änderungen; wird etwas gefunden, wird der Commit blockiert | gitleaks über den Git-Hook (alle), dazu Hooks im Agenten-Tool, wo unterstützt |
| 2. Selbstprüfung | Vor dem Öffnen eines PR | Tests bestehen; Sicherheits-Selbstreview des eigenen Diffs | Der Agent, der es gebaut hat |
| 3. Automatische CI | Bei jedem Update eines PR | Tests, Lint, Typen (`ci`); Secrets in jedem Commit (`secrets`); verwundbare Bibliotheken (`dependencies`) | GitHub Actions |
| 4. Unabhängiges KI-Review | Bei jedem Update eines PR (nicht bei Drafts oder reinen Doku-PRs) | Erfüllt es die Spec? Sind die Tests ehrlich? Bugs, ausufernder Umfang, Regelverstöße (`ai-review`). Sicherheitslücken (`security-review`) | Ein separates Claude in GitHub Actions, das nie gesehen hat, wie der Code geschrieben wurde (modellübergreifend, wenn der Code aus einem anderen Tool kam) |
| 5. Menschliches Code-Review | PRs, die geschützte Bereiche berühren | Kernlogik, Authentifizierung, Zahlungen, personenbezogene Daten, Migrationen, Infrastruktur, Konfiguration der Agenten | Product Owner oder ein benannter Developer |
| 6. Menschliche Abnahme | Jeder Code-PR | Es funktioniert wirklich (Gate G4 UAT) | Product Owner |

- Der Reviewer postet einen Kommentar mit **Blocking / Should fix / Nits**. Blockierende Befunde stoppen den Merge.
- Der bauende Agent behebt die Blocking-Punkte und pusht; die Reviews laufen automatisch erneut. Ist er anderer Meinung, antwortet er im PR und fragt einen Menschen. Nach **zwei** fehlgeschlagenen Runden hört er auf und übergibt.
- KI-Reviewer können blockieren, aber nie freigeben oder mergen. Nur ein Mensch kann sie überstimmen, mit dem PR-Label `ai-review-overruled`.
- Landet je ein echtes Secret auf GitHub: Widerrufe und rotiere es sofort, dann lass einen Admin die Historie des Branches umschreiben. Es in einem neuen Commit zu löschen, reicht nicht.

Alle Regeln: `docs/process/GATES.md`. Anweisungen für den Reviewer, die du anpassen kannst: `.github/review/REVIEWER.md`.

---

## Bevor du anfängst

Du brauchst:
- [ ] Admin-Zugriff auf das GitHub-Repository. Ist es privat, brauchen Branch-Regeln GitHub Pro oder Team, und eine freigebende Person für Produktions-Deploys braucht Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Einen Tracker: **GitHub Projects** (nichts zusätzlich; kostenlos in jedem Plan) oder Admin-Zugriff auf einen **Linear**-Workspace
- [ ] Einen installierten und angemeldeten Coding-Agenten, mit deinem eigenen Konto
- [ ] Python 3, Git, Make und die angemeldete GitHub CLI (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks` oder von seiner Releases-Seite auf GitHub)
- [ ] Ein Claude-Secret für die Reviewer-Agenten: ein Token aus einem Claude-Plan (`claude setup-token`) oder ein Anthropic-API-Schlüssel mit monatlichem Ausgabelimit (console.anthropic.com)
- [ ] Dein Projekt läuft heute schon lokal

Entscheide jetzt:
1. **Tracker:** GitHub Projects (kostenlos, alles in GitHub) oder Linear (angenehmer zu bedienen, kostenloser Plan begrenzt). Du kannst später wechseln.
2. **Produkt-Key:** ein kurzer Code, z. B. `ACM`, `SHOP`, `CRM` (der Team-Key von Linear, falls du Linear nutzt). Das Kit nutzt `APP` als Platzhalter, bis `config` ihn überall ersetzt.
3. **Product Owner:** die eine Person, die Ideen, Specs, UAT und Deploys freigibt (plus optional eine Vertretung für Freigaben).
4. **Agenten-Tools**, die dein Team nutzen wird.

Prüfe deine Maschine jederzeit mit: `python3 <kit>/tools/haam/haam.py dev`

---

## Phase 1: Das Kit installieren (15 Min.)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

Die Doku ist auf Englisch, außer du ergänzt bei beiden Befehlen `--language es` (oder `fr`, `de`, `it`, `nl`, `pt`). Die Agenten schreiben dann auch Specs, Issues, UAT-Pläne und Nachrichten in dieser Sprache; Befehle, Labels und Code bleiben auf Englisch. Ändern kannst du das später mit `haam.py config --language <code>`, danach `update --target . --apply` aus dem Kit.

Der Installer **überschreibt nie** deine Dateien:
- Neue Dateien werden hinzugefügt.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` und `.claude/settings.json` werden automatisch **zusammengeführt**.
- `.gitignore` bekommt einmalig einen HAAM-Block angehängt.
- Jede andere Datei, die du schon hast, bleibt unberührt, und die Version des Kits wird in `.haam/incoming/` abgelegt, damit du (oder der Agent) sie zusammenführst.

So führst du die üblichen Konflikte zusammen:

| Wenn dein Repo schon hat… | Mach das |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Verschiebe projektspezifisches Wissen (Konventionen, Stolperfallen, Befehle) nach `docs/product/ARCHITECTURE.md` oder in einen Abschnitt „Project specifics“ am Ende von `AGENTS.md`. Nutze dann `AGENTS.md` und `CLAUDE.md` aus dem Kit. Behalte Cursor-Regeln (`.mdc`) nur für Details, die per Glob auf Dateien beschränkt sind |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` verschiebt deine Skills nach `.agents/skills/` und verlinkt den Ordner. Benenne vorher alle um, deren Namen mit HAAM-Skills kollidieren |
| `Makefile` | Füge deinem die Targets des Kits hinzu |
| `.github/workflows/` mit CI | Behalte deine CI, aber sorg dafür, dass ein Job namens **`ci`** bei PRs deine ganze Testsuite ausführt. Füge `gates.yml`, `security.yml`, `review.yml` hinzu. Vergleiche deinen Deploy mit `deploy.yml` (Phase 4) |
| `.github/pull_request_template.md` | Übernimm „Erstellt mit (Built with)“, „Akzeptanzkriterien → Tests“ und „Checkliste (G3)“ |
| `.pre-commit-config.yaml` oder Husky | Behalte es und ruf von dort `scripts/scan-secrets.sh` auf, statt `.githooks/` zu nutzen |
| `CHANGELOG.md`, `.github/dependabot.yml` | Behalte deine (füge Dependabot das Ökosystem `github-actions` hinzu, falls es fehlt) |

Lösche `.haam/incoming/`, wenn du fertig bist.

---

## Phase 2: Konfigurieren und dem Kit dein Projekt beibringen (45 Min.)

1. **Projekteinstellungen** `[agent]` (Antworten von dir):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Das schreibt `haam.config.json` und ersetzt den Platzhalter `APP` und den Produktnamen in jeder HAAM-Datei.

2. **Agenten-Tools** `[agent]`: `python3 tools/haam/haam.py agents --apply`. Das verlinkt die gemeinsamen Skills für Claude Code und Grok, prüft die Dateien für Cursor/Codex/Gemini/Copilot und listet alle Schritte auf, die jede Person selbst machen muss. Details: `docs/setup/AGENTS-SETUP.md`.

3. **Befehlsvertrag** `[agent]`: Fülle jedes `TODO(setup)` im `Makefile` (setup, dev, test, lint, typecheck, build, audit) und die Laufzeitschritte in den Workflows mit den echten Befehlen deines Projekts aus. Danach muss `make check` auf dem aktuellen Code durchlaufen. Schlagen Tests auf `main` schon fehl, behebe oder markiere sie zuerst: HAAM verlässt sich darauf, dass Grün wirklich Grün heißt. Meldet `make audit` alte Schwachstellen mit hohem oder kritischem Schweregrad, behebe sie oder erfasse sie als Bugs und hebe die Schwelle vorübergehend an.

4. **Architekturkarte** `[agent]`: Fülle `docs/product/ARCHITECTURE.md` aus der Codebasis aus (unter 150 Zeilen) und schlage echte Pfade für die geschützten Bereiche in `AGENTS.md` §4 vor. Du prüfst.

5. **Produktkontext** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: was es ist, Nutzer, Journeys, die nie kaputtgehen dürfen, Unverhandelbares, aktuelle Prioritäten. Das liest jeder Agent, um Ermessensentscheidungen zu treffen.

6. **Onboarding-Doku** `[agent]`: Fülle die `TODO(setup)`-Punkte in `docs/ONBOARDING.md` aus (Clone-URL, Laufzeitumgebung, lokale URL).

7. **Hygiene bei Secrets** `[agent]`: `make hooks`, dann einmal die Historie scannen: `gitleaks git --redact -v .` Alles Echte muss beim Anbieter **widerrufen und rotiert** werden: Es ist bereits für alle mit Zugriff auf das Repo offengelegt. Du gibst alle Fingerprints für Fehlalarme frei, die zu `.gitleaksignore` hinzugefügt werden.

8. **Parallele Chats** `[agent]`: Liste die nur lokalen Dateien, die die App braucht (wie `.env`), in `.worktreeinclude` auf, schließe `.claude/worktrees/` in jedem Tool aus, das den ganzen Ordner scannt (Test-Runner, Linter, Watcher), und probiere einen frischen Worktree aus: `python3 tools/haam/haam.py worktree new setup-check`, darin `make setup && make check`, dann `git worktree remove .claude/worktrees/setup-check`. Ab dann startet jeder neue Agenten-Chat mit `/work`.

9. **Prüfen:** `python3 tools/haam/haam.py doctor` zeigt, was noch fehlt.

---

## Phase 3: Den Einführungs-PR öffnen (5 Min.)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Dadurch existieren die Checks in GitHub, sodass sie als erforderlich gesetzt werden können. Der erste Kommentar des KI-Reviews erscheint in diesem PR.

---

## Phase 4: Gates in GitHub (20 Min.)

1. **Planen, dann anwenden** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Es legt die Labels an und ein Ruleset auf dem Standard-Branch (PR erforderlich, die sechs erforderlichen Checks, keine Force-Pushes; Admins können die Regeln nur beim Mergen eines PR umgehen, für Notfälle, nie durch Pushen auf main; „up to date before merging“ aus, um CI-Läufe zu sparen). Gibt es das Ruleset schon, ergänzt es nur, was fehlt, und behält deine Einstellungen bei (`--reset` ersetzt es). Außerdem legt es das Environment `production` mit deinen freigebenden Personen an, die Variable `PRODUCTION_URL`, und schaltet Secret Scanning, Push Protection und Dependabot ein, wo dein Plan das erlaubt.
2. **Schlüssel für den Reviewer** `[YOU, in your terminal]`: Ein Secret startet beide Reviews. Entweder `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` mit dem Token aus `claude setup-token` (nutzt deinen Claude-Plan) oder `gh secret set ANTHROPIC_API_KEY -R owner/repo` mit einem eigenen API-Schlüssel (pro Review abgerechnet; damit nutzt das Security-Review die Security-Review-Action von Anthropic). Beide Befehle fragen den Wert ab, ohne ihn anzuzeigen.
3. **PRs aus Forks** `[YOU, in the browser]`: Settings → Actions → General → Freigabe für externe Mitwirkende verlangen.
4. **Deploys:**
   - *Deployst du schon aus GitHub Actions?* Füge deinem Deploy-Job `environment: production` hinzu: Das allein gibt dir Gate G5. Lösche das `deploy.yml` aus dem Kit oder behalte es als Referenz.
   - *Deployst du anders* (Git-Integration einer Hosting-Plattform, von Hand)? Verschiebe die Deploys entweder nach `deploy.yml` (fülle `make deploy` aus), oder behalte deine Methode und behandle G5 als manuellen Schritt: Der Product Owner deployt nach dem Merge und führt dann `/release` aus. Schalte Auto-Deploy bei Push ab, falls es die Freigabe umgehen würde.
5. **Private Repositories:** Branch-Regeln brauchen GitHub Pro oder Team, und eine freigebende Person für Produktions-Deploys braucht Enterprise Cloud; das Tool sagt dir, was dein Plan erlaubt. Ohne freigebende Person ist dein `ship` die Release-Entscheidung: Setz `deploy_approval: automatic` (`docs/setup/DECISIONS.md` §1).

Details und die manuellen Entsprechungen: `docs/setup/GITHUB-SETUP.md`.

---

## Phase 5: Der Tracker (20 Min.)

### Option A: GitHub Projects (kostenlos)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (erlaubt deinem GitHub-Login, Projects zu nutzen).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` Token für die Automatisierung, damit sich Karten bewegen, wenn PRs geöffnet und gemergt werden: Erstelle unter github.com/settings/tokens einen klassischen Token mit den Scopes `project` und `repo` (`public_repo` reicht für ein öffentliches Repository), dann `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` Lege auf dem Board die Ansichten an, die das Tool auflistet: Board grouped by Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Test: `python3 tools/haam/haam.py issue list`.

Agenten nutzen `python3 tools/haam/haam.py issue …` für jede Operation auf dem Board (`docs/process/TRACKER.md`), daher funktioniert es aus Claude Code, Cursor, Codex, Grok oder jedem anderen Tool gleich.

### Option B: Linear
1. **Status, Labels, Team** `[YOU, in your terminal]` (braucht deinen persönlichen Linear-API-Schlüssel, der nie durch einen Agenten geht):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Es legt das Team an, falls nötig, schaltet Triage ein, legt die 12 Status an (und benennt den Standardstatus „Todo“ von Linear in „Ready“ um) und die 9 Labels. Es löscht nie etwas; zusätzliche Status listet es auf, damit du sie archivierst.
2. **Einstellungen nur im Browser** `[YOU, in the browser]`: GitHub verbinden, PR-Automatisierungen (Draft-PR → In Progress, PR bereit zum Review → In Review, gemergt → Deploying), Format der Branch-Namen `{issue-identifier}-{issue-title}`, gespeicherte Ansichten. Siehe `docs/setup/LINEAR-SETUP.md`.
3. **Verbinde deinen Agenten** mit Linear (`docs/setup/AGENTS-SETUP.md`) und teste: *„Liste die Issues im Linear-Team ACM auf.“*

**Schon ein Backlog vorhanden?** Bitte deinen Agenten, es in den Tracker zu übernehmen (GitHub-Issues lassen sich einfach zum Board hinzufügen). Leg alles in **Triage**, triagiere einmal (`stream:bug`, `stream:idea` oder `stream:feature` + Backlog) und spezifiziere nur die obersten fünf.

---

## Phase 6: Mergen, Probedurchlauf und Menschen

### Den Einführungs-PR mergen
Wenn die Checks grün sind, setz `uat-passed` selbst (das Gate ist jetzt aktiv, also geht selbst dieser PR hindurch) und merge. Kritteln die Reviewer-Agenten am Kit selbst herum, überstimme sie mit `ai-review-overruled`. Führe zur abschließenden Prüfung `python3 tools/haam/haam.py doctor --role admin` aus.

### Einen vollen Durchlauf machen (45–60 Min.)
Nimm etwas Kleines und Echtes. Geh damit einmal durch jede Phase:

| Schritt | Du tippst | Was passieren sollte |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Neues Issue in Triage, Label `stream:idea` (auf GitHub: `#1`; auf Linear: `ACM-1`) |
| 2 | `/assess #1` | Bewertung auf dem Branch des Issues committet (kein PR); das Issue wechselt zu Decision |
| 3 | `/decide #1 approve medium` | Das Issue wechselt zu Backlog, das Label wird zu `stream:feature` |
| 4 | `/spec #1` | Spec mit Akzeptanzkriterien, auf demselben Branch |
| 5 | Lies die Spec (Link im Issue), sag dem Agenten „Spec freigegeben“ | Das Issue bekommt `agent-ready` und wechselt zu Ready |
| 6 | `/build #1` | Beansprucht es, legt einen Branch an, programmiert, schreibt Tests, prüft sich selbst, schreibt den UAT-Plan und pusht den Branch. Noch kein PR (test-first, der Standard) |
| 7 | `/uat #1` (`/build` führt es aus) | Das Issue wechselt zu UAT; du wirst benachrichtigt |
| 8 | `/test #1` | Der Agent holt die Änderung auf deine Maschine, startet die App und gibt dir eine kurze Checkliste |
| 9 | Probier es aus, antworte `pass` | Der Agent öffnet den PR mit dem Label `uat-passed`; `ci`, `secrets`, `dependencies` und die Reviewer-Agenten laufen einmal; `release-gate` wird grün; der Agent fragt „Ausliefern?“ |
| 10 | Antworte `ship` | Der Agent mergt, gibt den Produktions-Deploy für dich frei, wartet und schließt das Issue: Done |
| 11 | (einmal ausprobieren) `/test` bei einer Änderung und stattdessen ein Problem beschreiben | Es geht mit deinen Notizen zurück an die Agenten (`uat-failed`) und kommt repariert wieder zu dir |

(Auf Linear sehen die IDs aus wie `ACM-1`.)

Probiere dann einmal die Grenzfälle aus: Bitte den Agenten, auf einem Wegwerf-Branch einen gefälschten Schlüssel zu committen (`AKIA` + 16 Großbuchstaben/Ziffern): Der Commit muss blockiert werden. Lass dann einen UAT fehlschlagen und nutze einen Override. Passe die Skills in `.agents/skills/` oder den Prozess in `docs/process/LIFECYCLE.md` an, wo sich etwas falsch angefühlt hat.

**Probier beim Probedurchlauf auch ein zweites Agenten-Tool aus** (z. B. Cursor oder Codex für Schritt 6). Das bestätigt, dass die gemeinsamen Regeln und Skills auch über dein Haupttool hinaus funktionieren.

### Developer hinzufügen
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: Schreibzugriff auf GitHub (kein Admin), Zugriff auf das GitHub-Projects-Board oder eine Einladung zu Linear.
2. Schick ihnen den Link zum Repo und die Testzugangsdaten (Passwortmanager oder Einmal-Link, nie per Chat oder E-Mail).
3. Sie öffnen ihren eigenen Agenten im Repo und führen `/haam-onboard` aus (Codex: `$haam-onboard`).
4. Sobald ihr zu zweit seid: Das Tool setzt „1 approval required“, wenn du Vertretungen für Freigaben hinzufügst (`config --backup-approvers`, dann `github --apply`), und du kannst `.github/CODEOWNERS` für geschützte Bereiche hinzufügen.

### Agenten halbautonom arbeiten lassen

| Stufe | Wie | Wann |
|---|---|---|
| **1. Beaufsichtigt** | Du tippst `/next` oder `/build` und gibst jeden Push und PR frei | Die ersten 2–3 Wochen |
| **2. Gebündelt** | 2–3 Chatfenster (beliebige Mischung aus Tools und Computern), jedes mit `/work` gestartet, was ihm seinen eigenen Worktree gibt; du prüfst PRs gebündelt | Sobald die Specs zuverlässig gut sind |
| **3. Geplant** | Eine geplante Aufgabe startet einen Agenten ohne Oberfläche mit `/next` und hält beim UAT an | Sobald du den Gates vertraust |

Auf jeder Stufe halten Agenten an den menschlichen Gates an.

### Laufende Kosten
Neben GitHub, Linear (falls du es nutzt) und dem Agenten-Abo jeder Person sind die Reviewer-Agenten die einzigen nutzungsbasierten Kosten: zwei Claude-Aufrufe pro geprüftem Push auf einen PR, abgerechnet über `ANTHROPIC_API_KEY` oder auf deinen Claude-Plan angerechnet (`CLAUDE_CODE_OAUTH_TOKEN`). Lass das Ausgabelimit eingeschaltet und halte PRs klein.

### Auf dem neuesten Stand bleiben
Neue Kit-Versionen werden unter https://github.com/jorgedpl/haam-kit/releases veröffentlicht. `python3 tools/haam/haam.py doctor --check-updates` sagt dir, wenn eine draußen ist. Führe `/haam-update` (Codex: `$haam-update`) auf einem Branch aus: Dateien, die du nie geändert hast, werden aktualisiert, deine Anpassungen bleiben erhalten, und wo sich beide geändert haben, führt der Agent sie zusammen. Das CHANGELOG listet alle Migrationsschritte auf.

### Dein Rhythmus als Product Owner
Täglich (10–15 Min.): **UAT** testen, **Triage** leeren (`/triage`). Wöchentlich (30–45 Min.): alles in **Decision** entscheiden, das Backlog neu ordnen (`/triage backlog`), festhängender Arbeit nachgehen (`/triage stale`), **Parked** wieder anschauen, **Overrides** schließen. Der vollständige Leitfaden mit Prioritätsregeln und Checklisten: `docs/process/PRODUCT-MANAGER.md`.

---

## Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Lösung |
|---|---|---|
| Unklar, was noch fehlt | – | `python3 tools/haam/haam.py doctor --role admin` |
| Der Agent hält sich nicht an die Regeln | Das Tool liest `AGENTS.md` nicht | Prüfung beim ersten Start in `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` sagt, der Login kann Projects nicht nutzen | Dem gh-Login fehlt der Scope `project` | `gh auth refresh -s project` |
| Karten auf dem Board bewegen sich nicht, wenn PRs geöffnet/gemergt werden | `HAAM_PROJECT_TOKEN` fehlt, oder im PR steht kein `Refs #123` | Das Secret hinzufügen (Phase 5); die PR-Beschreibung prüfen |
| Der Agent sieht Linear nicht | MCP nicht verbunden oder nicht angemeldet | Schritte pro Tool in `docs/setup/AGENTS-SETUP.md` |
| Skills erscheinen in Cursor doppelt | Cursor liest sowohl `.agents/skills` als auch `.claude/skills` | Die Kompatibilität mit Claude-Skills in den Einstellungen von Cursor ausschalten |
| `.claude/skills` oder `.grok/skills` fehlt nach dem Klonen (Windows) | Git-Symlinks aus | `git config core.symlinks true` und neu klonen, oder `haam.py agents --apply` (kopiert stattdessen) |
| `haam.py github` sagt, Rulesets/Freigaben sind nicht verfügbar | Privates Repo im kostenlosen Plan | Upgraden, oder von Hand schützen und sich auf die Checks verlassen |
| `haam.py linear` bricht bei einem Schritt ab | API-Änderung oder Berechtigungen | Den Schritt von Hand mit `docs/setup/LINEAR-SETUP.md` abschließen |
| Zwei Chats haben dieselben Dateien oder denselben Branch geändert | Sie haben sich einen Ordner geteilt | Jeden Agenten-Chat mit `/work` starten (eigener Worktree) |
| Tests oder Linter finden doppelte Dateien unter `.claude/worktrees/` | Das Tool scannt den ganzen Ordner | `.claude/worktrees/` in der Konfiguration dieses Tools ausschließen |
| Ein Worktree kann die App nicht starten | Lokale Dateien fehlen | Sie zu `.worktreeinclude` hinzufügen, dann `haam.py worktree prep` im Worktree |
| `/build` weigert sich zu starten | Issue nicht in Ready, oder `agent-ready` fehlt | `/spec` und freigeben, oder das Issue selbst nach Ready verschieben |
| Linear-Status bewegen sich bei PR-Ereignissen nicht | GitHub-Integration oder Automatisierungen nicht eingerichtet | Team settings → Workflow → PR automations; der PR-Titel muss mit der Issue-ID beginnen |
| `release-gate` bleibt nach `uat-passed` rot | Der Workflow ist nicht erneut gelaufen | Das Label entfernen und wieder hinzufügen |
| Ein erforderlicher Check fehlt in der Liste | Er ist noch nicht gelaufen | Zuerst irgendeinen PR öffnen |
| Commits blockiert: „gitleaks is not installed“ | gitleaks fehlt auf dieser Maschine | Installieren, dann `make hooks` |
| Commit wegen eines Secrets blockiert, das keines ist | Fehlalarm | Ein Mensch fügt den Fingerprint in einem geprüften Commit zu `.gitleaksignore` hinzu |
| `ai-review` oder `security-review` hängt oder bricht ab | Kein Reviewer-Secret (`CLAUDE_CODE_OAUTH_TOKEN` oder `ANTHROPIC_API_KEY`), PR aus einem Fork, oder keine Turns mehr übrig | Das Secret hinzufügen; erneut ausführen; `--max-turns` erhöhen; oder `ai-review-overruled` |
| Reviewer zu streng | Anweisungen nicht angepasst | `.github/review/REVIEWER.md` bearbeiten |
| `dependencies` schlägt bei jedem PR fehl | Alte Schwachstellen | Beheben, oder die Schwelle vorübergehend anheben und als Bugs verfolgen |
| Specs zu vage, Builds gehen schief | G2 zu locker | Die Definition of Ready in `docs/process/GATES.md` verschärfen |

---

## Prinzipien

1. **Menschen entscheiden, Agenten führen aus.**
2. **Was nicht in Git oder im Tracker steht, existiert nicht** für die nächste Person oder den nächsten Agenten.
3. **Kleine Teilstücke:** ein Issue, ein Branch, ein PR, prüfbar in 15 Minuten.
4. **Gates sind billig zu bestehen und teuer zu überspringen.** Overrides sind erlaubt, werden immer festgehalten und immer nachverfolgt.
5. **Grün heißt grün.** Schwäche nie einen Test ab, um ein Gate zu bestehen.
6. **Niemand korrigiert seine eigenen Hausaufgaben.** Der Agent, der Code schreibt, prüft ihn nie; Secrets werden von Tools gefunden, nicht durch Einschätzung.
7. **Jeder Agent, dieselben Regeln.** Tools sind austauschbar; der Prozess und die Gates nicht.
