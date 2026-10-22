# Linear einrichten (einmalig, ~30 Minuten, Workspace-Admin)

> **Nur wenn dein Tracker Linear ist** (`"tracker": "linear"` in `haam.config.json`). Du nutzt GitHub Projects? Führe stattdessen `python3 tools/haam/haam.py github-project` aus und lies `docs/process/TRACKER.md`.

Damit wird Linear passend zu `docs/process/LIFECYCLE.md` konfiguriert. Mach es einmal; danach nutzen alle Developer und Agenten dieselbe Struktur.

> **Automatisiert:** Die Abschnitte 1–4 erledigt `python3 tools/haam/haam.py linear --apply`, von dir in deinem eigenen Terminal ausgeführt (es fragt deinen persönlichen Linear-API-Schlüssel sicher ab und speichert ihn nie). Diese Seite ist die manuelle Entsprechung, plus die Abschnitte 5–9, die es nur in der Web-App von Linear gibt.

## 1. Team
- Lege ein Team mit dem Namen deines Produkts an (oder nutze ein bestehendes), mit einer kurzen Kennung (die Beispiele nutzen **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` ersetzt `APP` in jeder HAAM-Datei.
- Lade jede mitwirkende Person mit ihrem eigenen Linear-Konto ein. Agenten handeln als der Mensch, der sie laufen lässt, also brauchst du keine eigenen Plätze für Agenten.

## 2. Workflow-Status
Team settings → **Workflow**. Lege diese an, in dieser Reihenfolge, in der angegebenen Kategorie:

| Status | Kategorie | Hinweise |
|---|---|---|
| Triage | Triage | Triage für das Team einschalten |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Als Standard für neue Issues außerhalb der Triage markieren |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Lösche oder benenne die Standardstatus von Linear um (`Todo`, `Duplicate` usw.), sodass nur diese übrig bleiben. Die Namen müssen exakt übereinstimmen; Skills verweisen über den Namen auf sie.

## 3. Labels
Team settings → **Labels**. Lege diese Labels an (einfache Labels, keine Gruppe nötig):
- `stream:idea`
- `stream:feature`
- `stream:bug`

Und diese einzelnen Labels:

| Label | Bedeutung | Wer es setzt |
|---|---|---|
| `agent-ready` | G2 bestanden; Agenten dürfen es bauen | Agent, erst nachdem ein Mensch die Spec freigegeben hat |
| `human-review` | Berührt einen geschützten Bereich; menschliches Code-Review erforderlich | Agent oder Mensch |
| `human-only` | Agenten dürfen das nicht übernehmen | Mensch |
| `override-followup` | Nach einem Override eines Gates angelegt | `/override` |
| `epic` | Übergeordnetes Issue, das die Sub-Issues eines Features bündelt | `/triage group`, `/epic` oder ein Mensch |
| `uat-failed` | Beim Test durch den Menschen durchgefallen; Agenten arbeiten es zuerst nach | `/test`, `/uat-result` |
| `uat:skip` | Der Product Owner hat entschieden: kein Test durch ihn | `/triage` oder „Spec freigegeben, kein UAT“ |
| `claimed` | Ein Agenten-Chat bewertet es, schreibt seine Spec oder baut einen Prototyp | Der Agent, während er arbeitet |
| `mode:prototype` | Der Product Owner hat entschieden: erst einen Wegwerf-Prototyp bauen (`/spike`) | `/triage` |
| `mode:epic-build` | Der Product Owner hat entschieden: Ein leitender Agent baut dieses ganze Epic | `/decide` |
| `spike-ready` | Ein Prototyp ist bereit, damit der Product Owner ihn ausprobiert | `/spike` |

Optional: Bereichs-Labels (`area:onboarding`, `area:billing`, `area:checkout`…), um das Board zu filtern.

## 4. Prioritäten
Nutze die eingebaute Priorität von Linear (Urgent / High / Medium / Low / No priority). Keine eigenen Felder nötig.

## 5. Vorlagen für Issues
Team settings → **Templates** → lege drei Vorlagen für Issues an und füge den Inhalt ein aus:
- **Idea**: `docs/templates/idea.md` · Standard-Label `stream:idea` · Status Triage
- **Bug**: `docs/templates/bug.md` · Standard-Label `stream:bug` · Status Triage
- **Feature**: ein kurzer Text mit Link zur Spec · Standard-Label `stream:feature` · Status Backlog

Agenten füllen diese über `/idea` und `/bug` selbst aus; die Vorlagen sind für Menschen, die Issues in der Linear-App anlegen.

## 6. GitHub-Integration
Settings → **Integrations → GitHub** → die Organisation bzw. das Repo verbinden.

Dann in den Team settings → **Workflow → Pull request automations** (die Formulierung kann leicht abweichen):

| GitHub-Ereignis | Issue verschieben nach |
|---|---|
| Branch angelegt / Draft-PR geöffnet | In Progress |
| PR bereit zum Review (Agenten öffnen Drafts und markieren sie als bereit, wenn sie vollständig sind) | In Review |
| PR bereit zum Mergen | *(keine Änderung, Agenten verschieben es nach UAT)* |
| PR gemergt | Deploying |

**Format der Branch-Namen:** `{issue-identifier}-{issue-title}` (kleingeschrieben), z. B. `app-123-bulk-invite-users`. Entferne das Präfix mit dem Benutzernamen, damit Branches gleich heißen, egal wer sie anlegt.

Schalte **„link PRs by issue ID in title“** ein, damit PR-Titel wie `APP-123: ...` automatisch verknüpft werden.

## 7. Ansichten (gespeicherte Filter)
Lege diese Team-Ansichten an, damit Menschen sehen, was auf sie wartet:

| Ansicht | Filter |
|---|---|
| **Triage** | Der eingebaute Triage-Eingang von Linear (der tägliche Eingang des Product Owners; siehe `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Status in (Decision, UAT), plus Backlog-Issues mit einem Kommentar `📝 Spec ready for review` |
| **Agent queue** | Status = Ready, Label `agent-ready` oder `stream:bug`, niemand zugewiesen |
| **Ideas inbox** | Status in (Triage, Discovery), Label `stream:idea` |
| **Bugs** | Label `stream:bug`, nicht Done/Canceled, sortiert nach Priorität |
| **Epics** | Label `epic`, nicht Done/Canceled (Fortschritt der Sub-Issues anzeigen) |
| **Overrides to close** | Label `override-followup`, nicht Done |

## 8. Benachrichtigungen
Jeder Mensch: Settings → Notifications → stell sicher, dass du bei **Erwähnungen** und **dir zugewiesenen Issues** benachrichtigt wirst. `/uat` erwähnt den Product Owner, wenn etwas zum Testen bereit ist.

## 9. Das Agenten-Tool jeder Person mit Linear verbinden
Jede Person meldet sich einmal aus ihrem eigenen Tool an (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Schritte pro Tool: `docs/setup/AGENTS-SETUP.md`.
Test: Bitte den Agenten *„liste meine offenen Linear-Issues im Team APP auf“*.

Nutzt du außerdem eine Chat-App (Claude, ChatGPT…) mit einem Linear-Connector, verbinde sie auch, damit du Ideen vom Handy aus erfassen kannst.
