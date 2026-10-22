# Entscheidungen bei der Einführung von HAAM

Diese Entscheidungen trifft der Product Owner zusammen mit dem Projekt-Admin. `/haam-setup` geht sie in dieser Reihenfolge durch, mit einer Empfehlung zu jeder, und mit `/haam-settings` änderst du sie später. Fang mit der empfohlenen Wahl an und schau nach der ersten vollen Woche noch einmal darauf. Dann zeigt `haam.py ci-usage`, wofür die Actions-Minuten draufgegangen sind, und `haam.py capacity`, was auf dich wartet.

**Ein paar Begriffe, die hier vorkommen:**
- **PR** (Pull Request): eine vorgeschlagene Änderung, die darauf wartet, nach `main` gemergt zu werden.
- **CI:** die automatischen Checks (Lint, Typen, Tests, Build), die auf GitHub für einen PR laufen. Sie verbrauchen Actions-Minuten.
- **UAT** (User Acceptance Test, Abnahmetest): dein eigener Test einer Änderung, auf deinem Computer, bevor sie ausgeliefert wird.
- **Die Spur ohne UAT:** Änderungen, die du mit `uat:skip` markierst (Updates von Abhängigkeiten, Konfiguration, unsichtbare Refactorings). Sie überspringen deinen Test und gehen direkt zu den Checks.
- **Release-Gate:** der Check, der verhindert, dass ein PR gemergt wird, bevor dein Test bestanden ist oder du die Spur ohne UAT gewählt hast.
- **Worktree:** eine separate Kopie des Projektordners für einen Agenten-Chat, damit sich Chats nicht gegenseitig überschreiben.

## Auf einen Blick

| Entscheidung | Start mit | Ändern, wenn | Siehe |
|---|---|---|---|
| GitHub-Konto und Plan | Eine Organisation. Öffentliches Repository: Free. Privat: Team | Das Repository ist privat, und du brauchst eine freigebende Person für Deploys: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | Das Team arbeitet schon jeden Tag in Linear | §2 |
| Wer ist wer | Ein Product Owner, eine Vertretung für Freigaben | Mehrere Produkte oder Owner | §3 |
| Sprache (`language`) | Die Sprache, in der dein Team schreibt | Das Team ändert sich | §3 |
| Reihenfolge beim Testen (`flow`) | `test-first` | Du testest auf einer gemeinsamen Staging-Seite statt lokal | §4 |
| Was du testest (`uat`) | `owner-decides` | Reguliertes Produkt: `always`. Viele kleine, gut getestete Fixes: `bugs-skip` | §4 |
| Bündelung (`grouping`) | `per-issue` | Epics aus kleinen Einträgen: `per-epic`. Actions-Minuten sind knapp: `release` | §4 |
| Checks (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | Die Actions-Minuten werden knapp | §4 |
| Ausliefern (`deploy`, `deploy_approval`) | `github`, `each` | Du deployst anders, oder dein Plan kann Deploys nicht bis zur Freigabe anhalten | §4 |
| Limits | `settings --recommend` | Deine Testzeit oder die Zahl der Agenten ändert sich | §5 |
| Geschützte Bereiche | Die Standards, plus dein sensibler Code | Die Architektur ändert sich | §6 |
| Gemeinsam genutzte Testressourcen (`heavy_runs`) | Keine | Tests teilen sich eine lokale Datenbank, einen Simulator oder ein Gerät | §7 |
| Wie viel Freiheit Agenten bekommen | Prototypen und Epic-Build-Modus, wenn du danach fragst; Produktionscode ist alles außer Prototypen, Tests und Doku | Du willst, dass Agenten mehr erkunden, oder dein Produktionscode liegt in wenigen Ordnern | §8 |

## 1. GitHub-Konto, Organisation und Plan

### Konten
Jede Person legt ihr eigenes Konto an und behält es; teile nie einen Login.

1. **Jede Person** registriert sich unter [github.com/signup](https://github.com/signup) mit ihrer beruflichen E-Mail-Adresse und schaltet die Zwei-Faktor-Authentifizierung ein (Settings → Password and authentication).
2. **Ein Admin** legt eine Organisation an ([github.com/organizations/plan](https://github.com/organizations/plan)) und lädt das Team ein. Für ein öffentliches Repository reicht der kostenlose Plan; ein privates braucht Team (siehe Tabelle unten). Die Organisation besitzt die Repositories, also hängt nichts vom Konto einer einzelnen Person ab. Mach zwei Personen zu Ownern.
3. **Das Repository** liegt in der Organisation: Leg es dort an oder verschiebe ein bestehendes (Settings des Repositorys → General → Transfer ownership).
4. **Installiere auf jedem Computer** die GitHub CLI ([cli.github.com](https://cli.github.com)) und führe `gh auth login` aus. Mit GitHub Projects als Tracker führst du außerdem `gh auth refresh -s project` aus.
5. **Keine eigenen Konten für Agenten.** Agenten handeln unter dem Konto der angemeldeten Person. Die Gates gehen davon aus, dass die Person an der Tastatur für das verantwortlich ist, was ihre Agenten tun.

### Welchen Plan du brauchst

| Was HAAM nutzt | Öffentliches Repository, jeder Plan | Privat, Free | Privat, Pro | Privat, Team | Privat, Enterprise Cloud |
|---|---|---|---|---|---|
| Branch-Regeln und erforderliche Checks ([Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Ja | Nein | Ja | Ja | Ja |
| Eine freigebende Person für Produktions-Deploys ([Environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Ja | Nein | Nein | Nein | Ja |
| Eigenes Secret Scanning und Push Protection von GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Ja | Nein | Nein | Kostenpflichtiges Add-on | Kostenpflichtiges Add-on |
| GitHub-Projects-Board | Ja | Ja | Ja | Ja | Ja |
| Actions-Minuten | Kostenlos auf Standard-Runnern | Ein monatliches Kontingent | Ein größeres Kontingent | Ein größeres Kontingent | Ein größeres Kontingent |

Pro ist für ein persönliches Konto; Team und Enterprise Cloud sind für Organisationen.

Was jedes fehlende Teil bedeutet:
- **Keine Branch-Regeln** (privates Repository im Plan Free): GitHub verhindert keinen Merge nach `main` ohne die Checks. Den Agenten wird zwar weiterhin gesagt, nie zu mergen, und `ship` durchläuft weiterhin jedes Gate, aber nichts setzt es durch. Nutze für jedes private Produkt Team (Organisation) oder Pro (persönliches Konto).
- **Keine freigebende Person für Deploys** (privates Repository unterhalb von Enterprise Cloud): Deploys starten, wenn ein PR gemergt wird. Dein `ship`, das den Merge macht, ist dann die Release-Entscheidung. Setz `deploy_approval: automatic`, damit HAAM nicht auf eine Freigabe wartet, die nie kommen kann, und lass `uat` auf `owner-decides` oder `always` (§4).
- **Kein Secret Scanning von GitHub:** kein Problem. Der eigene Check `secrets` des Kits und der Pre-Commit-Hook laufen in jedem Plan.

Pläne und Kontingente ändern sich, also prüfe [github.com/pricing](https://github.com/pricing), bevor du wählst.

### Der Zugang der Reviewer zu Claude
Die beiden KI-Reviews laufen mit einem Repository-Secret, das der Product Owner in seinem eigenen Terminal hinzufügt und nie in einen Chat einfügt:
- `CLAUDE_CODE_OAUTH_TOKEN` (aus `claude setup-token`): Die Reviews werden auf den Claude-Plan dieser Person angerechnet.
- `ANTHROPIC_API_KEY`: pro Review abgerechnet, getrennt von jedem Abo. Setz in der Anthropic-Konsole ein monatliches Ausgabelimit.

## 2. Der Tracker: GitHub Projects oder Linear

| | GitHub Projects | Linear |
|---|---|---|
| Kosten | Kostenlos in jedem GitHub-Plan | Kostenlos bis 250 aktive (nicht archivierte) Issues und 2 Teams; bezahlte Pläne pro Nutzer heben die Grenze auf. Prüfe [linear.app/pricing](https://linear.app/pricing) |
| Wie Agenten ihn nutzen | `haam.py issue …` aus jedem Agenten-Tool, mit dem `gh`-Login der Person | Die Linear-Verbindung (MCP), in jedem Agenten-Tool eingerichtet |
| Wird dir abgenommen | Claims, die verhindern, dass zwei Chats dieselbe Aufgabe nehmen; die UAT-Warteschlange wird für die Limits gezählt; die eigenen Felder des Boards (`--field`); die Spur ohne UAT mergt von selbst; `ship` schließt Issues | Agenten machen die Schritte über die Verbindung und zählen die UAT-Warteschlange für `capacity --in-uat N`. Die Spur ohne UAT mergt nicht von selbst: Diese PRs lieferst du aus |
| Einrichtung | `haam.py github-project --apply` | `haam.py linear --apply` mit dem API-Schlüssel des Product Owners, plus die Schritte im Browser in `LINEAR-SETUP.md` |
| Am besten für | Die meisten Teams: alles an einem Ort | Teams, die schon in Linear leben |

**Empfehlung:** GitHub Projects, außer das Team nutzt Linear schon jeden Tag. Triage und Agenten legen schnell Issues an, sodass die Grenze des kostenlosen Linear-Plans innerhalb weniger Wochen erreicht sein kann.

## 3. Wer ist wer
- **Product Owner:** eine Person, die entscheidet, testet und ausliefert. Nur sie führt die Skills aus, die Menschen vorbehalten sind: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` und `/haam-settings`.
- **Vertretungen für Freigaben:** eine oder zwei Personen, die Deploys freigeben können, wenn der Product Owner abwesend ist (`config --backup-approvers a,b`). Das braucht eine freigebende Person für Deploys, wirkt also bei einem privaten Repository unterhalb von Enterprise Cloud nicht.
- **Bauende:** alle, die Agenten-Chats laufen lassen. Jede Person braucht ihr eigenes GitHub-Konto mit Schreibzugriff und ihr eigenes Agenten-Tool. Der Admin führt `haam.py invite --github USER` aus, um den Plan zu sehen, dann dasselbe mit `--apply`. Danach führt jede bauende Person `/haam-onboard` aus.
- **Admin:** richtet GitHub, den Tracker und die Secrets ein. Oft der Product Owner.
- **Sobald zwei Personen am Code arbeiten,** verlange in den Branch-Regeln eine Freigabe (`GITHUB-SETUP.md` §2).
- **Sprache:** Die Doku des Kits gibt es auf Englisch, Spanisch, Französisch, Deutsch, Italienisch, Niederländisch und Portugiesisch (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Agenten schreiben Specs, Issues, UAT-Pläne und Nachrichten in der Sprache, die du wählst; Befehle, Labels, Status und Code bleiben auf Englisch. Wähle sie bei der Installation (`install --language es`). Um sie später zu ändern: `haam.py config --language fr`, dann stellt `update --target . --apply` aus dem Kit die Doku um, die du nicht bearbeitet hast.

## 4. Wie die Arbeit fließt: die Einstellungen
`python3 tools/haam/haam.py settings --explain` gibt jede Option mit ihrer Abwägung aus. Die Entscheidungen, auf die es ankommt:

| Einstellung | Start mit | Anders wählen, wenn | Was es kostet oder riskiert |
|---|---|---|---|
| `flow` | `test-first`: Du testest den Branch des Agenten, dann laufen PR und Checks einmal | `checks-first`: Du willst nur Code testen, der die Checks bestanden hat, oder du testest auf einer gemeinsamen Staging-Seite | Jede Nacharbeitsrunde lässt die Checks erneut laufen |
| `uat` | `owner-decides`: Du testest alles außer dem, was du mit `uat:skip` markierst | `always`: regulierte oder sicherheitskritische Produkte. `bugs-skip`: viele kleine Fixes mit guten Tests | `bugs-skip`: Ein falscher Fix kann ausgeliefert werden, ohne dass du ihn gesehen hast |
| `grouping` | `per-issue`: ein PR pro Issue | `per-epic`: Epics aus kleinen Einträgen. `release` (nur test-first): knappe Minuten und gebündelte Releases | Ein fehlschlagender Eintrag hält das ganze Paket auf |
| `ci` | `every-pr`, auf GitHub | `local`: Die Minuten gehen aus, und dein Computer baut alles. `off`: nur für Prototypen, an denen du allein arbeitest | `local` ist nicht manipulationssicher |
| `review` | `github`: zwei unabhängige KI-Reviews pro PR | `protected-only`: spart den Großteil der Review-Kosten. `local`: spart Minuten | Weniger unabhängige Prüfungen |
| `nightly` | `on` | `off`: wenn Minuten sehr knapp sind | Du findest Fehler und neue Schwachstellen später |
| `runner` | `github` | `self-hosted`: ein privates Repository mit aufwendigen Builds und eine Maschine, die eingeschaltet bleibt | Wartung. Nie für öffentliche Repositories |
| `deploy` | `github`: `deploy.yml` deployt beim Merge | `manual`: Du deployst anders | `ship` wartet, bis du „live“ sagst |
| `deploy_approval` | `each`: Jeder Deploy wartet auf deine Freigabe | `automatic`: Dein Plan kann Deploys nicht anhalten (§1), oder du hast `uat: always` gewählt | Eine gemergte Änderung geht ohne einen letzten Blick live |
| `worktree_cleanup` | `after-ship` | `manual`: Du räumst Worktrees lieber selbst auf | Speicherplatz |

Die Spur ohne UAT mergt nur auf GitHub Projects von selbst, mit dem Secret `HAAM_PROJECT_TOKEN`, `ci: every-pr` und `review: github`. Sonst lieferst du diese PRs selbst aus.

Vermeide diese Paare, denn zusammen entfernen sie die letzte Prüfung:
- `ci: off` mit `review: off`: Nichts prüft den Code vor deinem Test.
- `deploy_approval: automatic` mit `uat: bugs-skip`: Ein Bugfix kann in die Produktion gelangen, ohne dass ein Mensch ihn angesehen hat. Bei einem privaten Repository unterhalb von Enterprise Cloud sind Deploys automatisch, wähle dort also nicht `bugs-skip`.

## 5. Limits: wie viel Arbeit warten darf
Die Limits verhindern, dass Agenten mehr produzieren, als du testen kannst, und mehr PRs, als dein CI-Budget abdeckt. Ist ein Limit erreicht, starten Agenten keine neuen Builds mehr. Nacharbeit, Specs und Bewertungen von Ideen machen sie weiter.

| Limit | Was es zählt | Wie du es bemisst |
|---|---|---|
| `max_in_uat` | Änderungen, die auf deinen Test warten. Das wichtigste Limit bei test-first | Was du in einer Sitzung testen kannst: Minuten pro Sitzung ÷ Minuten pro Test (ein Test dauert oft 5 bis 10 Minuten). Eine Stunde am Tag bei etwa 6 Minuten pro Test ergibt 10 |
| `max_open_prs` | Bereite PRs. Drafts, reine Doku-PRs und PRs von Bots (Dependabot) zählen nicht | Test-first: PRs leben kurz (von deinem Bestehen bis `ship`), also reicht das Doppelte der gleichzeitig laufenden Agenten-Chats. Checks-first: Jede Änderung, die auf deinen Test wartet, ist ein bereiter PR, also setz es mindestens auf `max_in_uat` plus die gleichzeitig laufenden Chats |
| `max_review_rounds` | Fehlgeschlagene KI-Review-Runden, bevor ein Agent aufhört und dich fragt | 2. Für schwierige Bereiche auf 3 erhöhen |
| `max_pr_lines` | Zielgröße eines PR, in geänderten Zeilen | 400. Kleinere PRs bekommen bessere Reviews und Tests |

Rechne es für dein Team aus:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
Es gibt die vorgeschlagenen Limits aus und warnt, wenn die Agenten mehr produzieren können, als du testen kannst. Dann gibt es den Befehl aus, der sie anwendet. Es geht von etwa 6 Minuten pro Test und 2 Änderungen pro Chat und Tag aus; übergib `--minutes-per-test` und `--changes-per-chat` mit deinen eigenen Zahlen. Es liest `flow` aus den Einstellungen des Projekts oder nimmt `--flow`.

Wenn die Agenten mehr produzieren, als du testen kannst:
- füllt sich die Warteschlange, und die Agenten pausieren neue Builds: Das Limit tut seine Arbeit;
- räumt `/test all` mit „pass all verified“ die Änderungen ab, die die Agenten selbst nachgewiesen haben;
- schickt `uat: bugs-skip` kleine Bugfixes direkt zu den Checks;
- oder du lässt weniger Agenten-Chats laufen.

Für ein Wochenende voller Agentenarbeit, die du in einer Sitzung testest, öffne ein **Batch-Fenster**: eine Erhöhung, die nach ihrem letzten Tag von selbst endet, z. B. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. Was du schützen solltest
**Die Regel:** Schütze den Code, bei dem eine falsche Änderung Nutzern schaden, Geld oder Daten kosten, gegen das Gesetz verstoßen oder die Gates von HAAM selbst schwächen könnte. Jede geschützte Änderung braucht dein Code-Review und deinen Test und nimmt nie die Spur ohne UAT. Schütze also, was zählt, nicht alles.

| Bereich | Schützen | Typische Pfade (Beispiele) |
|---|---|---|
| Anmeldung, Sitzungen, Berechtigungen, Rollen | Immer | `src/auth/**`, `**/permissions/**`, *die Auth-Middleware* |
| Zahlungen, Abrechnung, Erstattungen, Preise | Immer | `src/billing/**`, `src/payments/**` |
| Personenbezogene Daten: Speicherung, Aufbewahrung, Löschung, Exporte | Wann immer du personenbezogene Daten hast | `src/users/**`, `**/privacy/**` |
| Logging, das personenbezogene Daten erfassen könnte | Wann immer du personenbezogene Daten hast | *die Logging-Konfiguration und die Audit-Module* |
| Entscheidungen über Nutzer: Berechtigung, Verifizierung, Freigaben, Scoring | Wenn ein falsches Ergebnis jemandem schadet | `src/verification/**`, `src/decisions/**` |
| Externe Anbieter, die für Nutzer handeln oder deren Daten erhalten | Ja | `src/integrations/**` |
| Datenbankmigrationen | Immer | `db/migrations/**`, `**/migrations/**` |
| Sicherheitskonfiguration: Kryptografie, CORS, CSP, Umgang mit Secrets | Ja | `**/security/**`, `**/crypto/**` |
| Infrastructure as Code | Ja | `infra/**`, `terraform/**` |
| Signierung und Release-Konfiguration für Mobile | Wenn du Apps auslieferst | *Entitlements, Signierung und Dateien für den Release-Build* |
| CI-, Deploy- und Build-Skripte | Standardmäßig geschützt | `.github/**`, `Makefile`, `scripts/**` |
| HAAM und das Setup der Agenten | Standardmäßig geschützt | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json` und mehr: `haam.py settings` listet sie auf |

Kursive Pfade beschreiben, wonach du suchen sollst; mach daraus echte Muster für deinen Code.

So richtest du es ein:
1. `/haam-setup` schlägt für jeden zutreffenden Bereich echte Pfade aus deinem Code vor. Du bestätigst sie.
2. `config --protected "src/auth/**,db/migrations/**" --human` fügt Muster hinzu, und `config --unprotected "…" --human` entfernt eines. `**` steht für beliebige Ordner und `*` für alles innerhalb eines Ordners. Ein einfacher Ordnername deckt alles darin ab.
3. `haam.py protected` listet auf jedem Branch die geschützten Dateien auf, die er ändert.
4. Das Release-Gate entscheidet anhand der Dateien, die ein PR ändert. Es liest die Liste von `main`, sodass ein Agent einen Schutz nicht in seinem eigenen PR entfernen kann.

Prüfe die Liste, wann immer sich `docs/product/ARCHITECTURE.md` ändert.

## 7. Gemeinsam genutzte Testressourcen
Manche Tests nutzen etwas, das sich der ganze Computer teilt, etwa eine lokale Datenbank, die die Tests klonen, einen Handy-Simulator oder ein angeschlossenes Gerät. Zwei Agenten-Chats, die sie gleichzeitig ausführen, stören sich gegenseitig, und der Fehler sieht aus wie eine kaputte Änderung. Liste diese Befehle als Muster auf: `config --heavy-run "make (check|test-integration)"`. Agenten führen sie dann nacheinander über `haam.py exclusive` aus. Lass die Liste leer, wenn deine Tests in sich abgeschlossen sind.

## 8. Wie viel Freiheit Agenten bekommen
Agenten können große Teile schnell bauen, so wie Menschen mit KI „Vibe-Coding“ betreiben, überall dort, wo sich ein Fehler billig wegwerfen lässt. Alles, was für echte Nutzer läuft, bleibt hinter den Gates.

**Ein paar Begriffe, die hier vorkommen:**
- **Prototyp** (oder **Spike**): eine schnelle, funktionierende Wegwerf-Version einer Idee, gebaut zum Ausprobieren, nie so ausgeliefert, wie sie ist.
- **Teilstück:** ein auslieferbares Stück eines Epics, mit eigenem Issue und eigener Spec.
- **Leitender Agent:** der eine Agenten-Chat, der ein ganzes Epic baut. Er kann unabhängige Teilstücke an Hilfsagenten (**Sub-Agenten**) abgeben.
- **Feature-Flag:** ein Schalter im Code, der ein neues Feature verborgen hält, bis jemand es einschaltet.
- **Produktionscode:** der Code, der für echte Nutzer läuft.

Drei Entscheidungen:

| Entscheidung | Was sie bewirkt | Wann du sie nutzt |
|---|---|---|
| **Erst ein Prototyp.** Tippe `/spike` oder wähle `prototype` in `/triage` | Ein Agent baut einen Prototyp auf einem Branch `spike/`, ohne Spec, PR oder Größenlimit. Du probierst ihn mit `/test` aus. Dann sagst du `discard`, `change: <what>`, `rebuild` (spezifizieren und neu bauen) oder `keep` (spezifizieren und aus diesem Code bauen) | Wenn dir das Ausprobieren der Idee mehr verrät als das Lesen darüber: ein neuer Bildschirm, ein Ablauf, eine Integration, bei der du unsicher bist |
| **Epic-Build-Modus.** Gib einem freigegebenen Epic das Label `mode:epic-build`; `/decide` und `/triage backlog` bieten es an | Ein leitender Agent baut jedes Teilstück des Epics auf einem Branch, mit einem Checkpoint nach jedem Teilstück. Du testest das ganze Feature einmal und lieferst es einmal aus | Ein Feature, dessen Teilstücke nur zusammen Sinn ergeben, oder das du lieber als Ganzes beurteilst |
| **Was als Produktionscode zählt** (`production_paths`, `non_production_paths`) | Sagt den Agenten und dir, was für Nutzer läuft, sodass die Notizen zu einem Prototyp und `haam.py production` zeigen, was eine Änderung berühren würde. Prototypen, Tests und Doku liegen standardmäßig außerhalb | Grenz es ein, wenn dein Produkt in wenigen Ordnern liegt: `config --production "src/**,api/**" --human`. Füge Ordner, die nie für Nutzer laufen, mit `config --not-production "…" --human` hinzu. Ist deine Doku das, was Nutzer sehen, nimm sie mit `config --remove-not-production "docs/**" --human` aus der Liste |

Egal in welchem Modus: Jede Änderung, die gemergt wird, besteht jedes Gate. Die Absicherung dahinter:
- Ein Prototyp wird nie gemergt: Das Release-Gate lehnt Branches `spike/` und alles unter `prototypes/` ab, und `publish` lehnt Spikes ab;
- behaltener Prototyp-Code erreicht Nutzer nur über `/spec`, einen normalen Branch und deinen Test, hinter einem Feature-Flag, das standardmäßig aus ist. Er nimmt nie die Spur ohne UAT: Das Gate sieht seine `spike:`-Commits;
- Produktionscode importiert nie aus `prototypes/`, und der KI-Reviewer blockiert es, wenn doch;
- ein Prototyp ändert nie geschützte Bereiche, und `/test` zeigt dir seine geänderten geschützten Dateien und neuen Abhängigkeiten, bevor irgendetwas läuft;
- geschützte Bereiche bekommen immer dein Code-Review;
- kein Agent berührt Produktionssysteme oder -daten, in keinem Modus.

## Quellen
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (Pläne, die sie enthalten) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (verpflichtende Reviewer bei privaten Repositories) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
