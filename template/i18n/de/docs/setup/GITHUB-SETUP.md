# GitHub einrichten (einmalig, ~30 Minuten, Repo-Admin)

Damit werden die Gates G3–G5 von Konventionen zu Regeln, die GitHub durchsetzt.

> **Automatisiert:** Labels (§1), Branch-Regeln (§2), das Environment für die Produktion (§4) und Sicherheitsfunktionen (§3b–c) erledigt `python3 tools/haam/haam.py github --apply` (vorher ohne `--apply` den Plan ansehen). Diese Seite ist die manuelle Entsprechung, plus die Schritte, die GitHub nur im Browser anbietet. Das Secret für den Reviewer fügst du immer selbst hinzu: `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (Token aus `claude setup-token`, dein Claude-Plan) oder `gh secret set ANTHROPIC_API_KEY -R owner/repo` (API-Schlüssel, pro Review abgerechnet). Eines davon startet beide Reviews.

## 1. Labels
Lege diese Repository-Labels an (Issues → Labels), oder führe aus:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Branch-Schutz auf `main`
Settings → **Rules → Rulesets** → New branch ruleset (oder klassischer Branch protection), Ziel `main`:

- ✅ Löschen einschränken; Force-Pushes blockieren
- ✅ Vor dem Mergen einen Pull Request verlangen
  - Erforderliche Freigaben: **1**, sobald es einen zweiten Menschen gibt; **0**, solange du allein bist (das UAT-Label ist deine Freigabe)
  - ✅ Veraltete Freigaben verwerfen, wenn neue Commits gepusht werden
- ✅ Bestandene Status-Checks verlangen („require branches to be up to date“ aus lassen: Das lässt die CI nach jedem Merge auf jedem offenen PR erneut laufen)
  - Erforderliche Checks: **`ci`** (oder **`ci-local`**, wenn `ci` auf `local` steht; weglassen, wenn `ci` auf `off` steht), **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** und **`release-gate`** (sie erscheinen in der Liste, nachdem die Workflows einmal auf einem PR gelaufen sind). `haam.py settings --apply` / `github --apply` fügt die Checks hinzu, die die Einstellungen verlangen, und entfernt HAAM-Checks, die sie nicht mehr verlangen (z. B. `ci`, wenn du auf `off` wechselst)
- ✅ Lineare Historie verlangen (optional, hält die Historie sauber)
- **Bypass list:** nur Repository-Admins, **nur für Pull Requests** (nie „always“: Agenten arbeiten unter dem Login eines Menschen, oft eines Admins, und könnten sonst direkt auf `main` pushen). Das ist die Notfall-Umgehung der Stufe 2 in `docs/process/GATES.md`.

**Auto-Merge** (Settings → General → Pull Requests → *Allow auto-merge*; `haam.py github --apply` schaltet es ein): wird nur von der Spur ohne UAT genutzt, für PRs, deren Issues du mit `uat:skip` markiert hast. Das Gate schaltet es für einen solchen PR mit dem Secret `HAAM_PROJECT_TOKEN` ein (`docs/process/TRACKER.md`), und GitHub mergt erst, wenn jeder erforderliche Check bestanden ist. Verlangst du Freigaben, wartet die Spur auch auf eine.

## 3. Code-Review und Sicherheit

### 3a. Ein Claude-Secret für die Reviewer-Agenten
Die unabhängigen Reviewer (`.github/workflows/review.yml`) lassen Claude in GitHub Actions laufen. Ein Repository-Secret startet beide Reviews (Settings → **Secrets and variables → Actions** → New repository secret). Wähle eines davon:
- **`CLAUDE_CODE_OAUTH_TOKEN`:** Führe `claude setup-token` aus und nutze den Token, den es ausgibt. Die Reviews werden dann auf diesen Claude-Plan angerechnet.
- **`ANTHROPIC_API_KEY`:** ein eigener API-Schlüssel für dieses Repo von console.anthropic.com, mit monatlichem Ausgabelimit. Er wird pro Review abgerechnet, getrennt vom Claude-Abo jeder Person. Damit nutzt das Security-Review die Security-Review-Action von Anthropic.

Draft-PRs und reine Doku-PRs rufen Claude nicht auf. Die Anweisungen für die Reviews stehen in `.github/review/REVIEWER.md` und `SECURITY-REVIEWER.md` und werden immer von `main` gelesen. Passe sie an, während du dazulernst.

### 3b. Secret Scanning und Push Protection
Settings → **Security** (Code security / Advanced Security, je nach Plan):
- ✅ **Secret scanning**, ✅ **Push protection**: GitHub lehnt Pushes ab, die bekannte Secret-Formate enthalten.
- Kostenlos für öffentliche Repositories. Für private Repositories braucht es eventuell das kostenpflichtige Sicherheits-Add-on von GitHub; hast du es nicht, schützen dich weiterhin der eigene Check `secrets` des Kits (gitleaks) und die lokalen Hooks.

### 3c. Warnungen zu Abhängigkeiten
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Kommentiere dann dein Ökosystem in `.github/dependabot.yml` ein. PRs von Dependabot gehen durch dieselben Gates.

### 3d. Pull Requests aus Forks
Settings → **Actions → General** → *Fork pull request workflows*: Freigabe für alle externen Mitwirkenden verlangen. (PRs aus Forks bekommen keine Repository-Secrets, also können KI-Reviews auf ihnen nicht laufen; ein Mensch prüft und überstimmt bei Bedarf.)

## 4. Environment für die Produktion (Gate G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** Product Owner (+ eine Vertretung, falls vorhanden)
- ✅ Prevent self-review: **aus** lassen, solange du die einzige freigebende Person bist, später einschalten
- **Deployment branches and tags:** selected branches → nur `main`
- **Environment secrets:** Zugangsdaten für Produktions-Deploys gehören hierher und nirgendwo anders hin
- **Environment variables:** `PRODUCTION_URL` (vom Smoke-Test genutzt)

Jetzt startet jeder Merge nach `main` `deploy.yml`, das bei *deploy-production* pausiert, bis eine freigebende Person auf **Review deployments → Approve** klickt. GitHub benachrichtigt die freigebenden Personen per E-Mail oder Benachrichtigung.

Required reviewers funktionieren bei öffentlichen Repositories in jedem Plan, bei privaten aber nur mit GitHub Enterprise Cloud. Ohne sie starten Deploys beim Merge, und dein `ship` ist die Release-Entscheidung: Setz `deploy_approval: automatic` mit `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (optional, aber empfohlen, sobald es zwei Menschen gibt)
`.github/CODEOWNERS`:
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Schalte dann im Ruleset „Require review from Code Owners“ ein.

## 6. Den Befehlsvertrag ausfüllen
Bearbeite das `Makefile` (einschließlich `audit`) und die Schritte zur Einrichtung der Laufzeitumgebung in `.github/workflows/ci.yml`, `security.yml` und `deploy.yml` (such nach `TODO(setup)`). Öffne einen PR. Der Check `ci` muss auf diesem PR grün werden, bevor du erforderliche Checks einschaltest.

## 7. Optional: Claude-GitHub-App
Willst du in einem PR einen Agenten für einen schnellen Fix markieren (z. B. die Claude-GitHub-App über `/install-github-app` in Claude Code oder die GitHub-Integration deines anderen Tools), installiere sie. Jede solche App ist an denselben Branch-Schutz und dieselben Checks gebunden, kann die Gates also nicht umgehen.

## 8. Actions-Minuten sparen

Private Repositories bekommen ein monatliches Kontingent an Actions-Minuten; Agenten, die viele PRs öffnen, verbrauchen es schnell. Was das Kit schon tut: Standardmäßig (test-first) pushen Agenten Branches, ohne PRs zu öffnen, und ein PR wird erst geöffnet, nachdem du die Änderung getestet und bestanden hast, sodass die Checks einmal auf getestetem Code laufen (Projekte mit checks-first: Draft-PRs lösen nichts aus, und Agenten markieren einen PR einmal als bereit, wenn er vollständig ist); reine Doku-PRs überspringen die Checks; `main` wird nachts geprüft statt nach jedem Merge; Labels, Kommentare und neue Issues starten keine Runner; Agenten halten neue Arbeit bei 10 offenen PRs oder 10 Änderungen zurück, die auf deinen Test warten (`max_open_prs`, `max_in_uat`).

Finde heraus, wofür die Minuten draufgehen: `python3 tools/haam/haam.py ci-usage` (letzte 7 Tage, nach Workflow, Job, Auslöser und Tag).

Zwei Einstellungen in der Tabelle unten sparen Minuten, ohne dass du viel aufgibst. Ändere sie mit `/haam-settings` oder `python3 tools/haam/haam.py settings --set … --apply --human`; sie werden zu Repository-Variablen, die die Workflows lesen. Die anderen (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) sparen mehr: siehe `settings --explain`. Mit `ci: off` verlangen die Branch-Regeln den Check `ci` nicht mehr; behalte den Secret-Scan, die KI-Reviews und release-gate und lass beim Release einen vollständigen Check laufen (dein Deploy-Skript oder der CI-Workflow auf dem Commit, den du auslieferst), damit Fehler, die nur unter Linux auftreten, weiterhin gefunden werden.

| Schalter | Was sich ändert | Abwägung |
|---|---|---|
| `--review local` | Die beiden KI-Reviews laufen auf deinem Computer in frischen Claude-Sitzungen (`haam.py review`) und nutzen deinen Claude-Plan statt Actions-Minuten. PRs mit dem Label `human-review` werden weiterhin auf GitHub geprüft | Das Ergebnis ist nicht mehr manipulationssicher: Der bauende Agent startet das Review (frische Sitzungen ohne Schreibrechte, Anweisungen von `main`), und alles, was deinen Login nutzt, könnte ein bestandenes Ergebnis melden. Führe `haam.py review` aus deinem eigenen Chat aus, um mehr Trennung zu haben |
| `--runner self-hosted` | Alle Jobs außer dem Deploy laufen auf deiner eigenen Maschine (registriert unter Settings → Actions → Runners) statt auf denen von GitHub | Die Maschine muss eingeschaltet sein, mit git, make, Python 3, curl, gitleaks und den Tools deines Projekts; nur für private Repositories. Prüfe die aktuellen Preise von GitHub für selbst gehostete Runner |

Auch einen Blick wert: Jobs auf macOS-Runnern zählen 10 Minuten für jede Minute Laufzeit (Windows: 2). Lass Mobile-Builds nur laufen, wenn sich der Mobile-Code geändert hat (`make check` bekommt die geänderten Dateien in `$CI_CHANGED_FILES`), oder nachts.

## 9. Prüfen, ob es funktioniert
1. Öffne einen winzigen Test-PR (z. B. einen Tippfehler-Fix im Code). `ci`, `secrets` und `dependencies` laufen; der Reviewer-Agent postet einen Kommentar, und `ai-review` / `security-review` melden sich zurück; `release-gate` zeigt **failure: waiting for UAT**.
   - **Secret-Test:** Committe auf einem Wegwerf-Branch einen gefälschten Schlüssel im AWS-Stil, etwa `AKIA` gefolgt von 16 Großbuchstaben/Ziffern, in einer Code-Datei. Der lokale Hook sollte den Commit blockieren; umgehst du ihn mit `--no-verify`, sollte der Check `secrets` fehlschlagen. Lösche den Branch danach.
2. Setz das Label `uat-passed` → `release-gate` wird grün → Mergen ist erlaubt.
3. Nach dem Merge zeigt Actions → Deploy **Waiting for review** bei `deploy-production`.
4. Öffne einen reinen Doku-PR → `release-gate` besteht automatisch.
