# De tracker: Linear of GitHub Projects

HAAM werkt hetzelfde met beide trackers. `haam.config.json` → `"tracker"` zegt welke dit project gebruikt:

- **`github`**: issues in deze GitHub-repository, op een GitHub Projects-board. Gratis bij elk GitHub-abonnement. Agents gebruiken `python3 tools/haam/haam.py issue …` (zie hieronder), dat vanuit elke agent-tool werkt.
- **`linear`**: issues in een Linear-team. Agents gebruiken de Linear-koppeling (MCP).

Skills zeggen "in de tracker"; deze pagina zegt hoe je elke handeling in elke tracker doet. **Agents: controleer `tracker` in `haam.config.json` één keer per sessie en gebruik dan de bijbehorende kolom.**

## Begrippen

| Begrip | GitHub Projects | Linear |
|---|---|---|
| Issue-ID (schrijf het zo) | `#123` | `APP-123` |
| Branchnaam | `123-short-title` | `app-123-short-title` (de branchnaam van Linear) |
| Commitbericht | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| PR-titel | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| PR → issue koppelen | **`Refs #123`** in de PR-beschrijving (niet `Closes`: het issue sluit bij `/release`, na de deploy) | Issue-ID in de PR-titel |
| Bestanden voor het issue | `docs/specs/GH-123-slug.md` (net zo voor beoordelingen en UAT) | `docs/specs/APP-123-slug.md` |
| 12 statussen | Het veld **Status** van het board | Workflowstatussen van het team |
| Prioriteit | Het veld **Priority** van het board (Urgent/High/Medium/Low) | Ingebouwde prioriteit |
| Stromen, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Labels op issues | Labels op issues |
| Epic (groepeert de issues van één feature) | Issue met het label `epic`; de issues ervan zijn GitHub-**sub-issues** | Issue met het label `epic`; de issues ervan zijn **sub-issues** (met parent ingesteld) |
| Wie werkt eraan | Status In Progress (bouwen) of label `claimed` (beoordelen, spec schrijven, prototype bouwen), plus het claimcommentaar. Aan de assignee alleen kun je twee chats van dezelfde persoon niet onderscheiden | Hetzelfde |
| Statuswijzigingen bij openen/mergen van een PR | Workflow `tracker-sync.yml`: alleen issues die geleverd worden (geen epics, geen PR's met alleen docs, geen spikes) | De GitHub-integratie van Linear |

## Handelingen

Commando's in de kolom GitHub draai je vanuit de hoofdmap van de repository. Voeg `--json` toe voor machineleesbare uitvoer.

| Handeling | GitHub Projects | Linear (via MCP) |
|---|---|---|
| **Werk vinden** (wachtrijen voor `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (voeg `--label agent-ready` toe voor features, `--label stream:bug` voor bugs) | Issues van het team opvragen op status, label, assignee |
| **Een issue lezen** | `haam.py issue view 123` | Issue ophalen |
| **Een idee aanmaken** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (komt in Triage) | Issue aanmaken, status Triage, label `stream:idea` |
| **Een bug melden** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Issue aanmaken, status Triage, label `stream:bug` |
| **Een epic aanmaken** | `haam.py issue create --epic --stream idea --title "…"` | Issue aanmaken met label `epic` |
| **Een issue in een epic zetten** | `haam.py issue link 14 --parent 9` | De parent van het issue op de epic zetten |
| **Een issue binnen een epic aanmaken** (bijv. slices van een spec, gaten) | `haam.py issue create --stream feature --parent 9 --title "…"` | Sub-issue van de epic aanmaken |
| **De eigen velden van het board** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` toont ze met hun opties. Stel ze in met `--field NAME=VALUE` bij `issue create` of `issue edit` (herhaalbaar; een lege waarde maakt een veld leeg; `Sprint=@current` is de iteratie die vandaag loopt), en filter met `issue list --field Area=Billing`. Een verkeerde naam of waarde wordt geweigerd voordat er iets verandert | De eigen velden van het team, via de Linear-koppeling |
| **Een issue uit een epic halen** | `haam.py issue unlink 14` | De parent van het issue leegmaken |
| **Een issue herschrijven** (titel, beschrijving) | `haam.py issue edit 14 --title "…" --body-file new.md` | Issue bijwerken |
| **De issues van een epic** | `haam.py issue children 9` (met voortgang) | De sub-issues van de epic opvragen |
| **Issues die in geen enkele epic zitten** | `haam.py issue list --open-only --no-parent --no-label epic` | Issues zonder parent opvragen |
| **Claimen** (voor bouwen, beoordelen of een spec schrijven) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (bouwen: weigert als het al geclaimd is of niet Ready is; `--force` voor bugs die direct vanuit Triage worden opgelost, alleen als de mens dat zei). Beoordelen: voeg `--for assess` toe; een spec schrijven: `--for spec`. Het toont een claim-id: bewaar dat | Opnieuw ophalen; als het In Progress is, het label `claimed` heeft of aan iemand anders is toegewezen: stoppen; anders aan jezelf toewijzen, op In Progress zetten (bouwen) of het label `claimed` toevoegen (beoordelen, spec), commentaar plaatsen met een claim-id, de commentaren opnieuw lezen (AGENTS.md §6) |
| **Een prototype bouwen** (`/spike`) | `haam.py issue claim 123 --for spike` (ideeën van Triage tot Decision, features in Backlog), daarna, na het pushen: `issue label 123 --add spike-ready` en `issue release 123 --claim <id> --status Decision` (een feature in Backlog: geen `--status`) | Claimen zoals hierboven (label `claimed`, een claimcommentaar met "to build a prototype"), label `spike-ready`, vrijgeven |
| **Productiecode in een wijziging** | `haam.py production` (de bestanden die een branch wijzigt en die voor gebruikers draaien) | Hetzelfde |
| **Een claim vrijgeven** (beoordeling of spec gepusht; of de chat stopt) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` in plaats van het id alleen in `/triage stale` of `/test`) | Toewijzing weghalen, `claimed` verwijderen, de status zetten, het commentaar `🔓 Claim released` plaatsen |
| **Status wijzigen** | `haam.py issue status 123 "UAT"` | Status van het issue bijwerken |
| **Status alleen voor mensen** (Done, Parked, Canceled, Decision→Backlog) | Hetzelfde, plus `--human`, **alleen** binnen `/triage`, `/epic`, `/decide`, `/test`, `/release` of `/override`, getypt door een mens | Dezelfde regel |
| **Prioriteit** | `haam.py issue priority 123 High` | Prioriteit bijwerken |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` vereist ook `--human`, nadat de mens de spec heeft goedgekeurd) | Labels bijwerken |
| **Commentaar** | `haam.py issue comment 123 --body "…"` of `--body-file` | Commentaar aanmaken |
| **Afwijzen of duplicaat** (in `/triage`, `/epic` of `/decide`) | `haam.py issue status 123 Canceled --human` (sluit het issue ook als niet gepland); zet de reden of het ID van het origineel in een commentaar | Status Canceled, commentaar |
| **Een wijziging testen** (mens, in `/test`) | `haam.py checkout-pr 123`, daarna `haam.py checkout-pr --back` | Hetzelfde (de code staat hoe dan ook in GitHub) |
| **De PR openen na een geslaagde test** (test-first, de mens zei `pass`) | `haam.py publish 123 --human`: pusht de geteste commit, opent de PR met het label `uat-passed`, zet het issue op In Review | `haam.py publish APP-123 --human` (`--label human-review` als het issue dat heeft), zet daarna het issue op In Review en plaats commentaar, zoals de tool aangeeft |
| **Een mislukte test vastleggen** (de mens zei dat hij faalde) | `haam.py test-failed 123 --human`, daarna label `uat-failed`, status Ready, geen assignee | `haam.py test-failed APP-123 --human`, daarna hetzelfde in Linear |
| **Live zetten na een geslaagde test** (de mens zei `ship`) | `haam.py ship 123 --human`: mergen, deploy goedkeuren, wachten, sluiten | `haam.py ship APP-123 --human`, daarna op Done zetten in Linear |
| **Alles wat klaar is live zetten, één deploy** | `haam.py ship --all --human` (of `ship 12 13 14 --human`): merget elk ervan, keurt alleen de nieuwste deploy goed, sluit ze allemaal | `haam.py ship APP-12 APP-13 --human` (noem ze op: `--all` kan Linear niet lezen) |
| **Bekijken of wijzigen hoe HAAM draait** (product owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (alleen de keuze van de product owner) | Hetzelfde |
| **CI hier draaien** (instelling `ci: local`) | `haam.py local-ci 123` (ship draait het voor je) | Hetzelfde |
| **Geen UAT voor dit issue** (beslissing van de product owner) | `haam.py issue label 123 --add uat:skip --human` | Label `uat:skip` |
| **Ruimte voor nieuw werk?** (`/next` controleert dit eerst) | `haam.py capacity` (de UAT-wachtrij en PR's die klaar zijn tegenover `max_in_uat`, `max_open_prs`, of de verhoging tijdens een batchvenster; drafts en PR's met alleen docs tellen niet mee) | Hetzelfde commando, met `--in-uat <count>` |
| **Botst nieuw werk met wat er wacht?** | `haam.py overlap --files src/auth/,src/api/users.py` (branches in UAT die dezelfde bestanden wijzigen) | Hetzelfde, met `--branch <name>` voor elke branch in UAT |
| **Batch-PR** (de bugs van een epic) | Titel `#12 #13 #14: …`, een regel `Refs #n` per issue; `ship` sluit ze allemaal | Titel `APP-12 APP-13: …` |
| **Sluiten na de release** | `haam.py issue close 123 --human` (zet op Done en sluit; alleen `/release`) | Status Done |

## Regels die voor beide gelden

- Elk stuk werk heeft een issue in de tracker; niets wordt ergens anders bijgehouden.
- Als de tracker niet bereikbaar is: stop en zeg het tegen de mens.
- Het claimprotocol voorkomt dat twee agent-chats (of twee machines) hetzelfde bouwen, beoordelen of specificeren. Sla het nooit over.
- Wijzigingen die alleen mensen mogen doen, gebeuren alleen binnen de skills die alleen voor mensen zijn, en op GitHub vraagt de tool ter herinnering om `--human`. Agents werken onder de eigen login van de product owner, dus GitHub kan niet zien wie een label van de product owner heeft gezet (`uat:skip`, `mode:prototype`, `mode:epic-build`): dat is een regel, die op GitHub Projects door de tool wordt gecontroleerd en op Linear door niets. Een agent die de regel brak met gewone `gh` zou, met `uat:skip`, een wijziging buiten de beschermde gebieden je test kunnen laten overslaan; CI en beide AI-reviews draaien nog steeds, en deploys wachten nog steeds op jou waar je abonnement dat toelaat.

## GitHub Projects opzetten (admin, één keer)

1. `gh auth refresh -s project` (laat je GitHub-login Projects gebruiken).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plan), daarna `--apply`: maakt het board aan met de naam van het product, koppelt de repo, stelt de 12 statussen en het veld Priority in, maakt de labels aan.
4. **Automatiseringstoken** (voor `tracker-sync.yml`, en voor auto-merge in de route zonder UAT): maak een klassieke token aan op github.com/settings/tokens met de scopes `project` en `repo` (`public_repo` is genoeg voor een publieke repository), en daarna `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Zonder token werkt alles, maar kaarten verschuiven niet vanzelf als PR's geopend of gemerged worden, en de route zonder UAT kan auto-merge niet aanzetten (de gate gebruikt deze token, omdat een merge met de eigen token van de workflow de deploy niet zou starten). Op projecten met Linear doet de route nooit een auto-merge, dus daarvoor is de token niet nodig.
5. **In de browser**, op het board: maak de opgeslagen weergaven aan die de setup noemt (Board grouped by Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics), en zet de ingebouwde workflow **Auto-add to project** van het board aan voor deze repository (board → Workflows). Die zet issues die op de website van GitHub zijn aangemaakt gratis op het board; `haam.py issue create` voegt zijn eigen issues zelf toe.
6. Elke developer voert één keer `gh auth refresh -s project` uit; `/haam-onboard` controleert dat.

## Later van tracker wisselen

Stel `"tracker"` in met `haam.py config --tracker …`, doe de setup van de nieuwe tracker en vraag je agent dan om de openstaande issues over te zetten (hij kan de ene tracker lezen en naar de andere schrijven). Houd de oude tracker alleen-lezen als archief.
