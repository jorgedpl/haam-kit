# Der Tracker: Linear oder GitHub Projects

HAAM funktioniert mit beiden Trackern gleich. `haam.config.json` → `"tracker"` sagt, welchen dieses Projekt nutzt:

- **`github`**: Issues in diesem GitHub-Repository, auf einem GitHub-Projects-Board. Kostenlos in jedem GitHub-Plan. Agenten nutzen `python3 tools/haam/haam.py issue …` (siehe unten), das aus jedem Agenten-Tool funktioniert.
- **`linear`**: Issues in einem Linear-Team. Agenten nutzen die Linear-Verbindung (MCP).

Skills sagen „im Tracker“; diese Seite sagt, wie jede Operation in jedem Tracker geht. **Agenten: Prüf `tracker` in `haam.config.json` einmal pro Sitzung und nutz dann die passende Spalte.**

## Begriffe

| Begriff | GitHub Projects | Linear |
|---|---|---|
| Issue-ID (so schreiben) | `#123` | `APP-123` |
| Branch-Name | `123-short-title` | `app-123-short-title` (der Branch-Name von Linear) |
| Commit-Nachricht | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| PR-Titel | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| PR → Issue verknüpfen | **`Refs #123`** in der PR-Beschreibung (nicht `Closes`: Das Issue wird bei `/release` geschlossen, nach dem Deploy) | Issue-ID im PR-Titel |
| Dateien zum Issue | `docs/specs/GH-123-slug.md` (genauso für Bewertungen, UAT) | `docs/specs/APP-123-slug.md` |
| 12 Status | Feld **Status** des Boards | Workflow-Status des Teams |
| Priorität | Feld **Priority** des Boards (Urgent/High/Medium/Low) | Eingebaute Priorität |
| Stränge, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Issue-Labels | Issue-Labels |
| Epic (bündelt die Issues eines Features) | Issue mit Label `epic`; seine Issues sind GitHub-**Sub-Issues** | Issue mit Label `epic`; seine Issues sind **Sub-Issues** (Parent gesetzt) |
| Wer daran arbeitet | Status In Progress (beim Bauen) oder Label `claimed` (beim Bewerten, Schreiben einer Spec, Bauen eines Prototyps), dazu der Claim-Kommentar. Die zugewiesene Person allein kann zwei Chats derselben Person nicht unterscheiden | Genauso |
| Statuswechsel beim Öffnen/Mergen eines PR | Workflow `tracker-sync.yml`: nur Issues, die ausgeliefert werden (keine Epics, keine reinen Doku-PRs oder Spikes) | GitHub-Integration von Linear |

## Operationen

Befehle in der GitHub-Spalte laufen vom Stammverzeichnis des Repositorys aus. Mit `--json` bekommst du maschinenlesbare Ausgabe.

| Operation | GitHub Projects | Linear (über MCP) |
|---|---|---|
| **Arbeit finden** (Warteschlangen für `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (`--label agent-ready` für Features, `--label stream:bug` für Bugs ergänzen) | Issues des Teams nach Status, Label, zugewiesener Person auflisten |
| **Ein Issue lesen** | `haam.py issue view 123` | Issue abrufen |
| **Eine Idee anlegen** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (landet in Triage) | Issue anlegen, Status Triage, Label `stream:idea` |
| **Einen Bug melden** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Issue anlegen, Status Triage, Label `stream:bug` |
| **Ein Epic anlegen** | `haam.py issue create --epic --stream idea --title "…"` | Issue mit Label `epic` anlegen |
| **Ein Issue in ein Epic aufnehmen** | `haam.py issue link 14 --parent 9` | Das Epic als Parent des Issues setzen |
| **Ein Issue innerhalb eines Epics anlegen** (z. B. Teilstücke einer Spec, Lücken) | `haam.py issue create --stream feature --parent 9 --title "…"` | Sub-Issue des Epics anlegen |
| **Die eigenen Felder des Boards** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` listet sie und ihre Optionen auf. Setze sie mit `--field NAME=VALUE` bei `issue create` oder `issue edit` (wiederholbar; ein leerer Wert löscht eines; `Sprint=@current` ist die Iteration, die heute läuft), und filtere mit `issue list --field Area=Billing`. Ein falscher Name oder Wert wird abgelehnt, bevor sich etwas ändert | Die eigenen Felder des Teams, über die Linear-Verbindung |
| **Ein Issue aus einem Epic herausnehmen** | `haam.py issue unlink 14` | Den Parent des Issues entfernen |
| **Ein Issue umschreiben** (Titel, Beschreibung) | `haam.py issue edit 14 --title "…" --body-file new.md` | Issue aktualisieren |
| **Die Issues eines Epics** | `haam.py issue children 9` (mit Fortschritt) | Die Sub-Issues des Epics auflisten |
| **Issues in keinem Epic** | `haam.py issue list --open-only --no-parent --no-label epic` | Issues ohne Parent auflisten |
| **Beanspruchen** (vor dem Bauen, Bewerten oder Schreiben einer Spec) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (Bauen: lehnt ab, wenn schon beansprucht oder nicht Ready; `--force` nur für Bugs, die direkt aus Triage behoben werden, wenn der Mensch das gesagt hat). Bewerten: `--for assess` ergänzen; Spec schreiben: `--for spec`. Es gibt eine Claim-ID aus: Bewahre sie auf | Neu abrufen; wenn In Progress, mit Label `claimed` oder jemand anderem zugewiesen, aufhören; sonst dir zuweisen, In Progress setzen (Bauen) oder Label `claimed` setzen (Bewerten, Spec), mit einer Claim-ID kommentieren, die Kommentare erneut lesen (AGENTS.md §6) |
| **Einen Prototyp bauen** (`/spike`) | `haam.py issue claim 123 --for spike` (Ideen von Triage bis Decision, Features im Backlog), dann nach dem Push: `issue label 123 --add spike-ready` und `issue release 123 --claim <id> --status Decision` (ein Feature im Backlog: ohne `--status`) | Beanspruchen wie oben (Label `claimed`, ein Claim-Kommentar mit „to build a prototype“), Label `spike-ready`, freigeben |
| **Produktionscode in einer Änderung** | `haam.py production` (die Dateien, die ein Branch ändert und die für Nutzer laufen) | Genauso |
| **Einen Claim freigeben** (Bewertung oder Spec gepusht; oder der Chat hört auf) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` statt der ID nur in `/triage stale` oder `/test`) | Zuweisung entfernen, `claimed` entfernen, Status setzen, `🔓 Claim released` kommentieren |
| **Status ändern** | `haam.py issue status 123 "UAT"` | Status des Issues aktualisieren |
| **Status nur für Menschen** (Done, Parked, Canceled, Decision→Backlog) | Genauso, plus `--human`, **nur** innerhalb von `/triage`, `/epic`, `/decide`, `/test`, `/release` oder `/override`, von einem Menschen getippt | Dieselbe Regel |
| **Priorität** | `haam.py issue priority 123 High` | Priorität aktualisieren |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` braucht außerdem `--human`, nachdem der Mensch die Spec freigegeben hat) | Labels aktualisieren |
| **Kommentieren** | `haam.py issue comment 123 --body "…"` oder `--body-file` | Kommentar anlegen |
| **Ablehnen oder Duplikat** (in `/triage`, `/epic` oder `/decide`) | `haam.py issue status 123 Canceled --human` (schließt das Issue außerdem als nicht geplant); die Begründung oder die ID des Originals kommentieren | Status Canceled, Kommentar |
| **Eine Änderung testen** (Mensch, in `/test`) | `haam.py checkout-pr 123`, dann `haam.py checkout-pr --back` | Genauso (der Code liegt so oder so in GitHub) |
| **Den PR nach einem bestandenen Test öffnen** (test-first, der Mensch hat `pass` gesagt) | `haam.py publish 123 --human`: pusht den getesteten Commit, öffnet den PR mit dem Label `uat-passed`, verschiebt das Issue nach In Review | `haam.py publish APP-123 --human` (`--label human-review`, wenn das Issue es hat), dann das Issue nach In Review verschieben und kommentieren, wie ausgegeben |
| **Einen fehlgeschlagenen Test festhalten** (der Mensch hat gesagt, dass er fehlgeschlagen ist) | `haam.py test-failed 123 --human`, dann Label `uat-failed`, Status Ready, niemand zugewiesen | `haam.py test-failed APP-123 --human`, dann dasselbe in Linear |
| **Nach einem bestandenen Test ausliefern** (der Mensch hat `ship` gesagt) | `haam.py ship 123 --human`: mergen, Deploy freigeben, warten, schließen | `haam.py ship APP-123 --human`, dann in Linear Done setzen |
| **Alles Fertige ausliefern, ein Deploy** | `haam.py ship --all --human` (oder `ship 12 13 14 --human`): mergt jedes, gibt nur den neuesten Deploy frei, schließt alle | `haam.py ship APP-12 APP-13 --human` (aufzählen: `--all` kann Linear nicht lesen) |
| **Ansehen oder ändern, wie HAAM läuft** (Product Owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (nur die Entscheidung des Product Owners) | Genauso |
| **CI hier ausführen** (Einstellung `ci: local`) | `haam.py local-ci 123` (`ship` führt es für dich aus) | Genauso |
| **Kein UAT für dieses Issue** (Entscheidung des Product Owners) | `haam.py issue label 123 --add uat:skip --human` | Label `uat:skip` |
| **Platz für neue Arbeit?** (`/next` prüft das zuerst) | `haam.py capacity` (die UAT-Warteschlange und bereite PRs gegen `max_in_uat`, `max_open_prs` oder die Erhöhung durch ein Batch-Fenster; Drafts und reine Doku-PRs zählen nicht) | Derselbe Befehl, mit `--in-uat <count>` |
| **Kollidiert neue Arbeit mit dem, was wartet?** | `haam.py overlap --files src/auth/,src/api/users.py` (Branches im UAT, die dieselben Dateien ändern) | Genauso, mit `--branch <name>` für jeden Branch im UAT |
| **Batch-PR** (die Bugs eines Epics) | Titel `#12 #13 #14: …`, eine Zeile `Refs #n` pro Issue; `ship` schließt sie alle | Titel `APP-12 APP-13: …` |
| **Nach dem Release schließen** | `haam.py issue close 123 --human` (setzt Done und schließt; nur `/release`) | Status Done |

## Regeln für beide

- Jede Arbeit hat ein Issue im Tracker; nichts wird anderswo verfolgt.
- Ist der Tracker nicht erreichbar, hör auf und sag es dem Menschen.
- Das Claim-Protokoll verhindert, dass zwei Agenten-Chats (oder zwei Maschinen) dasselbe bauen, bewerten oder spezifizieren. Überspring es nie.
- Statuswechsel, die Menschen vorbehalten sind, passieren nur innerhalb der Skills nur für Menschen, und das Tool verlangt auf GitHub zur Erinnerung `--human`. Agenten handeln unter dem Login des Product Owners, also kann GitHub nicht erkennen, wer ein Label des Product Owners gesetzt hat (`uat:skip`, `mode:prototype`, `mode:epic-build`): Das ist eine Regel, die auf GitHub Projects vom Tool geprüft wird und auf Linear von nichts. Ein Agent, der sie mit einfachem `gh` bricht, könnte mit `uat:skip` eine Änderung außerhalb der geschützten Bereiche an deinem Test vorbeischleusen; CI und beide KI-Reviews laufen trotzdem, und Deploys warten weiterhin auf dich, wo dein Plan das erlaubt.

## Einrichtung von GitHub Projects (Admin, einmalig)

1. `gh auth refresh -s project` (erlaubt deinem GitHub-Login, Projects zu nutzen).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (Plan), dann `--apply`: legt das Board mit dem Namen des Produkts an, verknüpft das Repo, setzt die 12 Status und das Feld Priority, legt die Labels an.
4. **Token für die Automatisierung** (für `tracker-sync.yml` und Auto-Merge in der Spur ohne UAT): Erstelle unter github.com/settings/tokens einen klassischen Token mit den Scopes `project` und `repo` (`public_repo` reicht für ein öffentliches Repository), dann `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Ohne ihn funktioniert alles, aber die Karten bewegen sich nicht von selbst, wenn PRs geöffnet oder gemergt werden, und die Spur ohne UAT kann Auto-Merge nicht einschalten (das Gate nutzt diesen Token, weil ein Merge mit dem eigenen Token des Workflows den Deploy nicht starten würde). In Linear-Projekten mergt die Spur nie automatisch, dafür wird der Token also nicht gebraucht.
5. **Im Browser**, auf dem Board: Lege die gespeicherten Ansichten an, die das Setup auflistet (Board grouped by Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics), und schalte den eingebauten Workflow **Auto-add to project** des Boards für dieses Repository ein (Board → Workflows). Er bringt Issues, die auf der GitHub-Website angelegt werden, kostenlos auf das Board; `haam.py issue create` fügt seine eigenen selbst hinzu.
6. Jeder Developer führt einmal `gh auth refresh -s project` aus; `/haam-onboard` prüft das.

## Später den Tracker wechseln

Setze `"tracker"` mit `haam.py config --tracker …`, führe das Setup des neuen Trackers aus und bitte dann deinen Agenten, die offenen Issues hinüberzukopieren (er kann den einen Tracker lesen und in den anderen schreiben). Lass den alten Tracker für die Historie im Nur-Lese-Modus.
