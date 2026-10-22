# Onboarding für Developer

Willkommen. Dieses Repo wird von Menschen und Coding-Agenten gemeinsam gebaut, nach der **Human-Agent Agile Methodology (HAAM)**. Du kannst das Agenten-Tool nutzen, das dir am liebsten ist: Claude Code, Cursor, Codex, Grok, Gemini oder Copilot. Mit diesem Leitfaden kommst du in etwa einer Stunde von null zu deinem ersten Issue.

## Der schnelle Weg: Lass dich von deinem Agenten onboarden

1. Klone das Repo und öffne dein Agenten-Tool in seinem Stammordner:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Sag deinem Agenten:
   - Claude Code, Cursor oder Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Jedes andere Tool: *„Lies `.agents/skills/haam-onboard/SKILL.md` und folge der Anleitung.“*

Er prüft deine Maschine, deine Zugänge und die Verbindung zum Tracker, richtet deine lokalen Hooks und `.env` ein, führt die Projekt-Checks aus, erklärt, wie wir arbeiten, und schlägt ein erstes Issue vor. Schritte, die dein Passwort oder deine Schlüssel brauchen, erledigst du selbst, in deinem eigenen Terminal oder Editor. Du fügst nie Secrets in den Chat ein.

Lieber von Hand? Die folgenden Abschnitte decken dasselbe ab.

---

## 1. Zuerst lesen (15 Minuten)
1. `AGENTS.md`: die Regeln, an die sich jeder Agent hält, egal mit welchem Tool. Sie gelten auch für dich.
2. `docs/process/LIFECYCLE.md`: Stränge, Status, Gates, wer was macht.
3. `docs/process/GATES.md`: Checklisten, Code-Review und Overrides.
4. `docs/product/PRODUCT.md` und `docs/product/ARCHITECTURE.md`: was wir bauen und wie es aufgebaut ist.

## 2. Konten, die du brauchst
| Konto | Wofür | Frag nach |
|---|---|---|
| GitHub | Code, PRs, CI | Schreibzugriff auf das Repo |
| Tracker | Backlog und Status | **GitHub Projects:** Zugriff auf das Board (kommt mit der Einladung zum Repo). **Linear:** Mitgliedschaft im Team **APP** |
| Dein Agenten-Tool | Coding-Agent | Dein **eigenes** Konto (Claude, Cursor, OpenAI, xAI…). Teile nie Konten |
| Testdienste | Lokal ausführen | Nur Testzugangsdaten, vom Product Owner |

Der Projekt-Admin lädt dich mit einem Befehl ein: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. Zugangsdaten für die Produktion bekommst du **nicht**; Deploys laufen über GitHub, mit Freigabe.

## 3. Tools installieren
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (Pflicht; ohne es werden Commits blockiert): macOS `brew install gitleaks`; andere: https://github.com/gitleaks/gitleaks/releases
- Laufzeitumgebung der Sprache dieses Repos: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Dein Agenten-Tool

Prüfe alles mit: `python3 tools/haam/haam.py dev`

## 4. Den Code zum Laufen bringen
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Mit dem Tracker verbinden
Prüfe `"tracker"` in `haam.config.json`:
- **GitHub Projects:** Führe einmal `gh auth refresh -s project` aus und teste dann: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** Folge dem Abschnitt für dein Tool in `docs/setup/AGENTS-SETUP.md` (eine Anmeldung) und bitte dann deinen Agenten: *„Liste die Ready-Issues im Linear-Team APP auf.“*

## 6. Deine persönlichen Einstellungen (nicht geteilt)
Persönliche Notizen und Vorlieben gehören in Dateien, die Git ignoriert: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json` oder die Benutzereinstellungen deines Tools. Leg dort nie gemeinsame Regeln ab. Soll etwas für alle gelten, schlag eine Änderung an `AGENTS.md` per PR vor.

## 7. Der Arbeitsalltag
Befehle sind unten als `/name` geschrieben; in Codex nutzt du `$name`.

| Du willst… | Mach das |
|---|---|
| Sehen, was wartet | Tracker-Ansicht **Agent queue** (zum Bauen) oder **Waiting on me** |
| Einen Agenten in einem neuen Chatfenster starten | `/work` (oder `/work bugs`) |
| In diesem Chat mit der Arbeit anfangen | `/next` oder `/build APP-123` |
| Triagieren und priorisieren (Product Owner) | `/triage`, `/triage group`, `/epic` und `docs/process/PRODUCT-MANAGER.md` |
| Eine Idee festhalten | `/idea …` |
| Einen Bug melden | `/bug …` |
| Aus einer freigegebenen Idee eine Spec machen | `/spec APP-123` |
| Eine Änderung testen (Product Owner) | `/test`, dann `pass` → `ship`, oder sagen, was nicht stimmt |
| Die Änderung von jemand anderem testen (Developer) | `docs/uat/APP-123-*.md` folgen, dann dem Product Owner Bescheid geben |
| Dein Setup prüfen | `python3 tools/haam/haam.py doctor` |

### Agenten parallel laufen lassen
Öffne pro Agent ein neues Chatfenster und tippe `/work` (oder `/work bugs`, `/work features`, `/work specs`, `/work ideas`; Codex: `$work`). Der Agent bekommt seine eigene Kopie des Projekts (einen Git-Worktree unter `.claude/worktrees/`), kopiert die lokalen Dateien, die in `.worktreeinclude` stehen (wie `.env`), nimmt sich den obersten Eintrag und arbeitet ihn bis zur Übergabe ab. Behalte deinen eigenen Chat im Hauptordner, für Ideen, Entscheidungen und Tests.

- **Claude Code in VS Code:** neuer Chat-Tab mit Cmd+Shift+Esc (Mac) oder Ctrl+Shift+Esc (Windows/Linux). In einem Terminal: `claude --worktree`.
- **Andere Tools:** Hat das Tool eine eigene Worktree- oder Parallel-Agenten-Option, nutze sie; sonst legt `/work` den Worktree an und sagt dir, welchen Ordner du in einem neuen Fenster öffnen sollst.
- **Ein anderer Computer:** genauso. Der Claim im Tracker verhindert, dass zwei Agenten dasselbe Issue nehmen; nenne den Namen der Maschine, wenn du gefragt wirst, damit der Claim-Kommentar zeigt, wo er läuft.
- **Räume** fertige Worktrees ab und zu **auf**: `python3 tools/haam/haam.py worktree clean` (Plan), dann `--apply`.
- **Den Branch eines Agenten testen:** Der UAT-Plan nutzt `git switch --detach origin/<branch>`, was funktioniert, solange der Worktree des Agenten den Branch noch hat.

### Agenten halbautonom laufen lassen
- **Beaufsichtigt:** Tippe `/next`, prüfe seine Auswahl und lass ihn laufen. Dein Tool sollte nachfragen, bevor es pusht oder PRs öffnet (siehe die sicheren Einstellungen in `docs/setup/AGENTS-SETUP.md`).
- **Unbeaufsichtigt:** Eine geplante Aufgabe oder ein Cronjob startet deinen Agenten ohne Oberfläche mit dem Prompt `/next` (Codex: `$next`). Er nimmt nur Arbeit, die ihr Gate bestanden hat, und hält beim UAT für einen Menschen an.
- Agenten halten absichtlich an jedem menschlichen Gate an. Deine Aufgabe ist es, die Ansicht **Waiting on me** kurz zu halten.

## 8. Wie deine Arbeit geprüft wird
Jeder PR wird durch Tests, einen Secret-Scan, eine Prüfung der Abhängigkeiten und zwei unabhängige KI-Reviewer (Spec/Qualität und Sicherheit) geprüft, die nie gesehen haben, wie der Code geschrieben wurde. Behebe ihre **Blocking**-Befunde; hältst du einen für falsch, antworte im PR und frag den Product Owner, der mit dem Label `ai-review-overruled` überstimmen kann. Geschützte Bereiche bekommen zusätzlich ein menschliches Review. Details: `docs/process/GATES.md` § So funktioniert das Code-Review.

**Falls du je ein echtes Secret committest:** Sag es sofort dem Product Owner. Es muss widerrufen und rotiert werden, auch wenn du es im nächsten Commit löschst.

## 9. Regeln, die es wert sind, wiederholt zu werden
- Keine Pushes auf `main`, keine Merges, keine Deploys durch Agenten.
- Keine Secrets oder echten personenbezogenen Daten in Code, Tests, Fixtures, im Tracker oder im Chat. Personenbezogene Daten sind gesetzlich geschützt (z. B. DSGVO).
- Ein Issue → ein Branch → ein PR, klein genug, um ihn in 15 Minuten zu prüfen.
- Fülle bei jedem PR **Built with** aus (dein Tool und Modell).
- Was nicht in Git oder im Tracker steht, existiert für die nächste Person nicht.

## 10. Hilfe bekommen
- Fragen zum Prozess: Frag deinen Agenten *„was soll laut LIFECYCLE.md passieren, wenn…“*
- Zugänge und Zugangsdaten: der Product Owner.
- Den Prozess verbessern: Öffne eine `/idea` mit Label `area:process`. Änderungen an `AGENTS.md`, `.agents/`, den Konfigurationsordnern der Agenten und `.github/` brauchen das Review des Product Owners.
