# HAAM: Human-Agent Agile Methodology

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · **Deutsch** · [Italiano](README.it.md) · [Nederlands](README.nl.md) · [Português](README.pt.md)

**Menschen entscheiden. Agenten führen aus. Alles liegt in Git und in deinem Tracker.**

HAAM ist eine offene Methodik und ein Kit, um Software mit KI-Coding-Agenten zu bauen, von der Idee bis in die Produktion, ohne die Kontrolle zu verlieren. Jeder Agent bekommt dieselben Regeln, dieselben Befehle und dieselben Gates, egal in welchem Tool er läuft: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI oder GitHub Copilot**. Die Arbeit wird auf einem **GitHub Projects**-Board (kostenlos) oder in **Linear** verfolgt, ganz wie du willst. Mehrere Personen, jede mit eigenem Agenten und eigenem Konto, können parallel am selben Produkt arbeiten.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## Was du bekommst

- **Einen Lebenszyklus mit fünf menschlichen Gates**: über die Idee entscheiden, die Spec freigeben, automatische Checks mit unabhängigem KI-Review, Abnahmetest durch einen Menschen, Freigabe für die Produktion. Im Notfall lässt sich jedes Gate übergehen, und jeder Override wird festgehalten und nachverfolgt.
- **Drei Arbeitsstränge**, aus denen sich Agenten Arbeit holen: Bugs, fertig spezifizierte Features und Ideen, die bewertet werden müssen. Der Tracker (GitHub Projects oder Linear) enthält Backlog, Prioritäten und Status.
- **20 gemeinsame Skills** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`) im offenen Format Agent Skills.
- **Deine Einstellungen, deine Abwägungen:** Mit `/haam-settings` legt der Product Owner fest, wann CI und die KI-Reviews laufen (bei jedem PR, lokal, nur für geschützte Bereiche oder gar nicht), was selbst getestet wird, wie Arbeit gebündelt wird (pro Issue, pro Epic oder ein Release-PR), ob Deploys auf Freigabe warten und welche Limits gelten. Zu jeder Option gibt es die Abwägung und die eigenen Zahlen des Projekts.
- **Testen mit einem Wort, bevor irgendetwas CI-Minuten kostet**: Tippe `/test`, probiere die Änderung des Agenten auf deinem Computer aus und antworte `pass` (erst jetzt wird der Pull Request geöffnet und geprüft, einmal, genau auf dem, was du getestet hast), dann `ship` (der Agent mergt, deployt und schließt ihn). Oder sag einfach, was nicht stimmt (das geht direkt zurück an die Agenten und kommt repariert wieder zu dir). `/test all` nimmt alles Wartende in einer Sitzung durch, und `ship --all` deployt es mit einer einzigen Freigabe.
- **Eine Spur ohne UAT** für Änderungen, die du nicht sinnvoll testen kannst (Konfiguration, Updates von Abhängigkeiten, unsichtbare Refactorings): Markiere das Issue einmal mit `uat:skip`, und sein PR wird von selbst gemergt, wenn CI und beide KI-Reviews bestanden sind.
- **Epics mit einem Agenten, der die richtigen Fragen stellt**: `/triage group` macht aus einem Haufen loser Issues Epics (eines pro Feature); `/epic` liest jedes davon, schreibt einen kurzen Brief, stellt dir ein paar gezielte Fragen und räumt dann die Issues auf: Duplikate, Lücken, Aufteilungen, Reihenfolge.
- **Raum für Agenten, große Teile schnell zu bauen, mit Absicherung:**
  - `/spike` baut einen funktionierenden Wegwerf-Prototyp, den du ausprobierst, bevor du entscheidest;
  - im Epic-Build-Modus baut ein Agent ein ganzes Feature, Stück für Stück, mit Checkpoints, einem Test und einem Release;
  - jede Änderung, die gemergt wird, besteht jedes Gate, und Prototypen werden nie gemergt.
- **Ein Leitfaden für Entscheidungen** ([DECISIONS.md](template/i18n/de/docs/setup/DECISIONS.md)): jede Entscheidung, die ein Team bei der Einführung von HAAM trifft, jeweils mit einer Empfehlung. Er behandelt GitHub-Konten und den nötigen Plan, GitHub Projects oder Linear, die Einstellungen, wie du die Limits auf deine Testzeit abstimmst und was du schützen solltest. `/haam-setup` führt dich durch.
- **Ein Leitfaden für das Produktmanagement** ([PRODUCT-MANAGER.md](template/i18n/de/docs/process/PRODUCT-MANAGER.md)): täglicher und wöchentlicher Rhythmus, wie du triagierst, Prioritätsregeln mit einer Matrix aus Auswirkung × Reichweite für Bugs, gesunde Warteschlangengrößen, erledigt mit einem Agenten (`/triage`) oder direkt in GitHub Projects oder Linear.
- **Parallele Agenten ohne Kollisionen**: Öffne ein neues Chatfenster, tippe `/work bugs`, und der Agent bekommt seine eigene Kopie des Projekts (einen Git-Worktree), nimmt sich den obersten Bug und arbeitet ihn bis zu deinem Test ab. Starte so viele, wie du willst, auf einem Computer oder auf mehreren.
- **Code-Review, bei dem niemand seine eigenen Hausaufgaben korrigiert**: ein Secret-Scan vor jedem Commit und in der CI, eine Prüfung der Abhängigkeiten und zwei unabhängige KI-Reviewer (Spec/Qualität und Sicherheit), die nie gesehen haben, wie der Code geschrieben wurde. Menschen prüfen geschützte Bereiche und können die Reviewer überstimmen.
- **Gates, die GitHub durchsetzt**, nicht Vertrauen: Branch-Regeln, erforderliche Checks, ein UAT-Label-Gate und Deploy-Freigaben, damit sie halten, egal welcher Agent oder welche Person pusht.
- **Doku in sieben Sprachen:** Englisch, Spanisch, Französisch, Deutsch, Italienisch, Niederländisch und Portugiesisch. Wähle eine bei der Installation (`install --language es`), und die Agenten schreiben auch Specs, Issues, UAT-Pläne und Nachrichten in dieser Sprache; Befehle, Labels und Code bleiben auf Englisch.
- **Ein Setup-Tool** (`haam.py`, Python 3, keine Abhängigkeiten), das das Kit in ein bestehendes Repo installiert, ohne etwas zu überschreiben. Es konfiguriert GitHub und den Tracker (GitHub Projects oder Linear), gibt den Agenten einen einheitlichen Befehlssatz für das Board, onboardet Developer, prüft das Setup und aktualisiert Projekte auf neue Kit-Versionen.

## Schnellstart

### HAAM in deinem Projekt einführen (Projekt-Admin, etwa ein halber Tag)

1. Hol dir eine veröffentlichte Version des Kits:
   ```bash
   git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (oder lade das Zip unter [Releases](https://github.com/jorgedpl/haam-kit/releases) herunter).
2. Öffne deinen Coding-Agenten **im Stammordner deines Projekts** und sag:
   > Lies `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` und folge der Anleitung, um HAAM in diesem Repository einzurichten. Das Kit liegt unter `~/haam-kit/template`.

Der Agent installiert das Kit auf einem Branch, stellt dir ein paar Fragen, füllt das Projektwissen aus deinem Code aus und führt dich durch GitHub und deinen Tracker. Er zeigt dir jede Änderung, bevor er sie vornimmt. Alles, was ein Passwort oder einen API-Schlüssel betrifft, erledigst du selbst, in deinem eigenen Terminal, nie über den Chat des Agenten.

Lieber von Hand? Folge [dem Einführungsleitfaden](template/i18n/de/docs/setup/HAAM-ADOPTION-GUIDE.md).

### In ein Projekt einsteigen, das HAAM schon nutzt (Developer, etwa eine Stunde)

Klone das Projekt, öffne deinen Agenten darin und führe `/haam-onboard` aus (Codex: `$haam-onboard`; andere Tools: *„folge `.agents/skills/haam-onboard/SKILL.md`“*).

### Ein Projekt auf eine neue Kit-Version aktualisieren

Hol dir die neue Version des Kits und führe dann in deinem Projekt `/haam-update` aus, oder:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Dateien, die du nie geändert hast, werden aktualisiert. Dateien, die du angepasst hast, bleiben erhalten. Wo beide Seiten geändert wurden, wird die neue Version beiseitegelegt, damit dein Agent sie zusammenführt. Nichts wird gelöscht.

## Das Setup-Tool

| Befehl | Wer | Was |
|---|---|---|
| `install --target DIR` | Admin | Kopiert das Kit in ein Repo. Überschreibt nie; führt Einstellungsdateien der Agenten zusammen; legt Konflikte in `.haam/incoming/` ab; hält die Version in `haam.lock.json` fest |
| `update --target DIR [--apply]` | Admin | Aktualisiert ein Projekt auf diese Kit-Version und behält Anpassungen bei |
| `config` | Admin | Produktname, Linear-Team-Key, Repo, freigebende Personen → `haam.config.json`; überträgt sie in jede HAAM-Datei |
| `agents [--apply]` | Admin | Bindet Skills und Linear für Claude Code, Cursor, Codex, Grok, Gemini, Copilot an |
| `github [--apply]` | Admin | Labels, Branch-Ruleset mit erforderlichen Checks, Freigabe für die Produktion, Sicherheitsfunktionen |
| `github-project [--apply]` | Admin | GitHub-Projects-Board: 12 Status, Feld Priority, Labels, Verknüpfung mit dem Repo |
| `linear [--apply]` | Admin, im eigenen Terminal | Linear-Team, Triage, 12 Status, 14 Labels |
| `issue list\|create\|claim\|release\|status\|fields\|…` | Agenten | Arbeiten am GitHub-Projects-Board aus jedem Agenten-Tool |
| `exclusive "<who>" -- <command>` | Agenten | Startet einen schweren Testlauf (einen, der eine maschinenweite Ressource nutzt), wenn auf dieser Maschine kein anderer läuft |
| `capacity` | Agenten | Hält neue Arbeit zurück, wenn zu viele PRs offen sind oder auf deinen Test warten (Limits in `haam.config.json`) |
| `ci-usage [--days 7]` | Admin | Wofür die GitHub-Actions-Minuten draufgegangen sind, nach Workflow, Job, Auslöser und Tag |
| `settings [--explain] [--set key=value] [--apply]` | Owner/Admin | Deine Entscheidungen: wann CI und die KI-Reviews laufen, was du testest, Bündelung, Ausliefern, Limits (`/haam-settings` führt dich durch) |
| `local-ci ISSUE` | Owner | Mit `ci: local`: führt `make check` hier auf dem Commit des PR aus und meldet das Ergebnis (`ship` erledigt das für dich) |
| `review ISSUE` | Agenten | Die beiden KI-Reviews in frischen lokalen Sitzungen, gemeldet als Status des PR (wenn die Reviews lokal laufen) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Holt eine Änderung zum Testen auf diese Maschine; nach `pass` + `ship`: mergen, Deploy freigeben (einer für mehrere), warten, schließen |
| `worktree status\|new\|prep\|list\|clean` | Agenten, alle | Ein Worktree pro Agenten-Chat; kopiert lokale Dateien laut `.worktreeinclude`; räumt fertige auf |
| `invite --github USER [--linear-email EMAIL] [--apply]` | Admin | Lädt einen Developer ein (GitHub-Schreibrecht, kein Admin; Zugriff auf das Board oder das Linear-Team) |
| `dev [--apply] [--run-checks]` | Developer | Prüft die Maschine, Commit-Hook, `.env` aus der Vorlage, Projekt-Checks |
| `doctor [--role admin] [--check-updates]` | alle | Was erledigt ist, was fehlt und wer es tun muss |
| `version [--check]` | alle | Versionen von Tool, Projekt und neuestem veröffentlichtem Kit |

Jeder Befehl zeigt zuerst einen Plan und ändert nur mit `--apply` etwas. Mit `--json` bekommst du maschinenlesbare Ausgabe.

## Mehrere Agenten gleichzeitig laufen lassen

Jeder Agenten-Chat bekommt seinen eigenen Ordner, damit sich Chats nie gegenseitig die Arbeit überschreiben:

1. Öffne ein neues Chatfenster (Claude Code in VS Code: Cmd/Ctrl+Shift+Esc).
2. Tippe `/work bugs` (oder `/work features`, `/work specs`, `/work ideas` oder einfach `/work`; Codex: `$work`).
3. Der Agent wechselt in seinen eigenen Git-Worktree, kopiert lokale Dateien wie `.env`, beansprucht den obersten Eintrag auf dem Board, baut und testet ihn, öffnet den PR und gibt dir einen Testplan.

Wiederhole das für so viele Agenten, wie du willst, auf jedem Computer, auf dem das Projekt geklont ist. Der Claim auf dem Board verhindert, dass zwei Agenten dasselbe Issue nehmen, egal ob sie es bauen, bewerten oder seine Spec schreiben. Dein eigener Chat bleibt im Hauptordner, für Ideen, Entscheidungen, Tests und Releases.

## Einen Tracker wählen

| | GitHub Projects | Linear |
|---|---|---|
| Kosten | Kostenlos in jedem GitHub-Plan | Kostenloser Plan mit Limits; sonst pro Nutzer bezahlt |
| Wo | Direkt neben deinem Code, ein Login | Separate App |
| Agenten nutzen | `haam.py issue …` (jeder Agent) | den MCP-Server von Linear |
| Am besten für | Einzelne und kleine Teams, die alles in GitHub halten wollen | Vollere Backlogs, mehrere Teams, umfangreichere Planung |

Lebenszyklus, Gates und Skills sind in beiden Fällen gleich, und du kannst später wechseln. Siehe [TRACKER.md](template/i18n/de/docs/process/TRACKER.md).

## Kompatibilität der Agenten

| | Regeln | Skills | Skill aufrufen | Linear (falls genutzt) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | beim ersten Start prüfen | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` über `.gemini/settings.json` | per Datei | per Datei | pro Nutzer |
| GitHub Copilot | `AGENTS.md` | per Datei | per Datei | pro Nutzer |

Auf GitHub Projects nutzt jeder Agent dieselben Befehle `haam.py issue`, es gibt also nichts pro Tool zu verbinden. Details und empfohlene sichere Einstellungen pro Tool: [AGENTS-SETUP.md](template/i18n/de/docs/setup/AGENTS-SETUP.md).

## Voraussetzungen

- Ein GitHub-Repository. Öffentliche Repositories bekommen alles im kostenlosen Plan. Bei **privaten** brauchen die Branch-Regeln GitHub Pro oder Team, und eine verpflichtende Freigabe für Produktions-Deploys braucht GitHub Enterprise Cloud (ohne sie ist dein `ship` die Release-Entscheidung). Die Details stehen in [DECISIONS.md](template/i18n/de/docs/setup/DECISIONS.md).
- Ein Tracker: ein GitHub-Projects-Board (kostenlos, in jedem GitHub-Plan) oder ein Linear-Workspace (jeder Plan)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Ein Claude-Secret für die Reviewer-Agenten in der CI: ein Token aus einem Claude-Plan (`claude setup-token`) oder ein Anthropic-API-Schlüssel (nutzungsbasiert; setz ein Ausgabelimit)
- Ein beliebiger unterstützter Coding-Agent

## Aufbau des Repositorys

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  i18n/          The same docs in other languages
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Versionierung

HAAM folgt der [semantischen Versionierung](https://semver.org):
- **Patch** (1.0.x): Korrekturen und Formulierungen; `update` lässt sich sauber anwenden.
- **Minor** (1.x.0): neue Skills, Checks oder Doku; abwärtskompatibel.
- **Major** (x.0.0): Änderungen, die einen Migrationsschritt brauchen (z. B. umbenannte Linear-Status oder erforderliche Checks). Das [CHANGELOG](CHANGELOG.md) listet die Schritte auf.

Installiere immer von einem Tag oder Release, nicht von `main`.

## Mitwirken

Ideen, Bug-Reports und Pull Requests sind willkommen. Siehe [CONTRIBUTING.md](CONTRIBUTING.md). Sicherheitsprobleme: siehe [SECURITY.md](SECURITY.md).

## Lizenz

[MIT](LICENSE) © 2026 Jorge del Prado
