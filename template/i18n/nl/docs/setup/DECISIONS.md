# Beslissingen bij het invoeren van HAAM

De product owner neemt deze beslissingen, samen met de projectadmin. `/haam-setup` loopt ze in deze volgorde met je door, met een aanbeveling voor elke beslissing, en met `/haam-settings` verander je ze later. Begin met de aanbevolen keuze en kijk er na de eerste drukke week opnieuw naar. Tegen die tijd laat `haam.py ci-usage` zien waar de Actions-minuten naartoe gingen en `haam.py capacity` wat er op je wacht.

**Een paar woorden die hier gebruikt worden:**
- **PR** (pull request): een voorgestelde wijziging, die wacht om in `main` gemerged te worden.
- **CI:** de geautomatiseerde checks (lint, types, tests, build) die op GitHub voor een PR draaien. Ze verbruiken Actions-minuten.
- **UAT** (gebruikersacceptatietest): je eigen test van een wijziging, op je computer, voordat die live gaat.
- **De route zonder UAT:** wijzigingen die je markeert met `uat:skip` (dependency-updates, config, onzichtbare refactors). Ze slaan je test over en gaan direct naar de checks.
- **Release-gate:** de check die voorkomt dat een PR gemerged wordt tot je test geslaagd is, of tot je voor de route zonder UAT gekozen hebt.
- **Worktree:** een aparte kopie van de projectmap voor één agent-chat, zodat chats elkaars werk niet overschrijven.

## In één oogopslag

| Beslissing | Begin met | Verander het als | Zie |
|---|---|---|---|
| GitHub-account en abonnement | Een organisatie. Publieke repository: Free. Privé: Team | De repository privé is en je een goedkeurder voor deploys nodig hebt: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | Het team al dagelijks in Linear werkt | §2 |
| Wie is wie | Eén product owner, één vervangende goedkeurder | Meerdere producten of product owners | §3 |
| Taal (`language`) | De taal waarin je team schrijft | Het team verandert | §3 |
| Testvolgorde (`flow`) | `test-first` | Je test op een gedeelde stagingomgeving in plaats van lokaal | §4 |
| Wat je test (`uat`) | `owner-decides` | Gereguleerd product: `always`. Veel kleine, goed geteste fixes: `bugs-skip` | §4 |
| Groeperen (`grouping`) | `per-issue` | Epics die uit kleine items bestaan: `per-epic`. Actions-minuten zijn schaars: `release` | §4 |
| Checks (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | De Actions-minuten raken op | §4 |
| Uitrollen (`deploy`, `deploy_approval`) | `github`, `each` | Je deployt op een andere manier, of je abonnement kan deploys niet laten wachten op goedkeuring | §4 |
| Limieten | `settings --recommend` | Je testtijd of het aantal agents verandert | §5 |
| Beschermde gebieden | De standaardinstellingen, plus je gevoelige code | De architectuur verandert | §6 |
| Gedeelde testresources (`heavy_runs`) | Geen | Tests delen een lokale database, een simulator of een device | §7 |
| Hoeveel vrijheid agents krijgen | Prototypes en epic-bouwmodus als je erom vraagt; productiecode is alles behalve prototypes, tests en docs | Je wilt dat agents meer verkennen, of je productiecode staat in een paar mappen | §8 |

## 1. GitHub-account, organisatie en abonnement

### Accounts
Iedereen maakt een eigen account aan en beheert dat zelf; deel nooit een login.

1. **Iedereen** meldt zich aan op [github.com/signup](https://github.com/signup) met het werk-e-mailadres en zet tweestapsverificatie aan (Settings → Password and authentication).
2. **Eén admin** maakt een organisatie aan ([github.com/organizations/plan](https://github.com/organizations/plan)) en nodigt het team uit. Het gratis abonnement is genoeg voor een publieke repository; een private repository heeft Team nodig (zie de tabel hieronder). De organisatie is eigenaar van de repositories, dus niets hangt af van het account van één persoon. Maak twee mensen owner.
3. **De repository** staat in de organisatie: maak hem daar aan, of verplaats een bestaande (Settings van de repository → General → Transfer ownership).
4. **Installeer op elke computer** de GitHub CLI ([cli.github.com](https://cli.github.com)) en voer `gh auth login` uit. Met GitHub Projects als tracker voer je ook `gh auth refresh -s project` uit.
5. **Geen aparte accounts voor agents.** Agents werken onder het account van de ingelogde persoon. De gates gaan ervan uit dat de persoon achter het toetsenbord verantwoordelijk is voor wat de eigen agents doen.

### Welk abonnement je nodig hebt

| Wat HAAM gebruikt | Publieke repository, elk abonnement | Privé, Free | Privé, Pro | Privé, Team | Privé, Enterprise Cloud |
|---|---|---|---|---|---|
| Branchregels en verplichte checks ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Ja | Nee | Ja | Ja | Ja |
| Een goedkeurder voor productiedeploys ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Ja | Nee | Nee | Nee | Ja |
| De eigen secret scanning en push protection van GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Ja | Nee | Nee | Betaalde add-on | Betaalde add-on |
| GitHub Projects-board | Ja | Ja | Ja | Ja | Ja |
| Actions-minuten | Gratis op standaardrunners | Een maandelijks tegoed | Een groter tegoed | Een groter tegoed | Een groter tegoed |

Pro is voor een persoonlijk account; Team en Enterprise Cloud zijn voor organisaties.

Wat elk ontbrekend onderdeel betekent:
- **Geen branchregels** (private repository op Free): GitHub houdt een merge naar `main` zonder de checks niet tegen. Agents krijgen nog steeds de opdracht nooit te mergen, en `ship` draait nog steeds elke gate, maar niets dwingt het af. Gebruik voor elk privéproduct Team (organisatie) of Pro (persoonlijk account).
- **Geen goedkeurder voor deploys** (private repository onder Enterprise Cloud): deploys starten als een PR gemerged wordt. Jouw `ship`, dat de merge doet, is dan de releasebeslissing. Stel `deploy_approval: automatic` in, zodat HAAM niet wacht op een goedkeuring die niet kan komen, en houd `uat` op `owner-decides` of `always` (§4).
- **Geen secret scanning van GitHub:** geen probleem. De eigen check `secrets` van de kit en de pre-commit-hook draaien bij elk abonnement.

Abonnementen en tegoeden veranderen, dus kijk op [github.com/pricing](https://github.com/pricing) voordat je kiest.

### De toegang van de reviewers tot Claude
De twee AI-reviews draaien met één repository-secret, die de product owner in de eigen terminal toevoegt en nooit in een chat plakt:
- `CLAUDE_CODE_OAUTH_TOKEN` (uit `claude setup-token`): de reviews worden afgeschreven van het Claude-abonnement van die persoon.
- `ANTHROPIC_API_KEY`: gefactureerd per review, los van ieders abonnement. Stel een maandelijkse uitgavelimiet in de Anthropic-console in.

## 2. De tracker: GitHub Projects of Linear

| | GitHub Projects | Linear |
|---|---|---|
| Kosten | Gratis bij elk GitHub-abonnement | Gratis tot 250 actieve (niet-gearchiveerde) issues en 2 teams; betaalde abonnementen per gebruiker heffen de limiet op. Kijk op [linear.app/pricing](https://linear.app/pricing) |
| Hoe agents het gebruiken | `haam.py issue …` vanuit elke agent-tool, met de `gh`-login van de persoon | De Linear-koppeling (MCP), ingesteld in elke agent-tool |
| Wordt voor je gedaan | Claims die voorkomen dat twee chats dezelfde taak oppakken; de UAT-wachtrij die voor de limieten geteld wordt; de eigen velden van het board (`--field`); de route zonder UAT die vanzelf merget; `ship` dat issues sluit | Agents doen de wijzigingen via de koppeling en tellen de UAT-wachtrij voor `capacity --in-uat N`. De route zonder UAT merget niet vanzelf: jij zet die PR's live |
| Setup | `haam.py github-project --apply` | `haam.py linear --apply` met de API-sleutel van de product owner, plus de browserstappen in `LINEAR-SETUP.md` |
| Het best voor | De meeste teams: alles op één plek | Teams die al in Linear leven |

**Aanbeveling:** GitHub Projects, tenzij het team Linear al dagelijks gebruikt. Triage en agents maken snel issues aan, dus de gratis limiet van Linear kan binnen enkele weken bereikt zijn.

## 3. Wie is wie
- **Product owner:** één persoon, die beslist, test en live zet. Alleen de product owner voert de skills uit die alleen voor mensen zijn: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` en `/haam-settings`.
- **Vervangende goedkeurders:** een of twee mensen die deploys kunnen goedkeuren als de product owner weg is (`config --backup-approvers a,b`). Hiervoor is een goedkeurder voor deploys nodig, dus het heeft geen effect op een private repository onder Enterprise Cloud.
- **Bouwers:** iedereen die agent-chats draait. Elk van hen heeft een eigen GitHub-account met schrijfrechten nodig, en een eigen agent-tool. De admin voert `haam.py invite --github USER` uit om het plan te zien, en daarna hetzelfde met `--apply`. Elke bouwer voert daarna `/haam-onboard` uit.
- **Admin:** zet GitHub, de tracker en de secrets op. Vaak de product owner.
- **Zodra twee mensen aan de code werken,** vereis je één goedkeuring in de branchregels (`GITHUB-SETUP.md` §2).
- **Taal:** de docs van de kit zijn er in het Engels, Spaans, Frans, Duits, Italiaans, Nederlands en Portugees (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Agents schrijven specs, issues, UAT-plannen en berichten in de taal die je kiest; commando's, labels, statussen en code blijven Engels. Kies de taal bij de installatie (`install --language es`). Om hem later te wijzigen: `haam.py config --language fr`, daarna zet `update --target . --apply` van de kit de docs om die je niet bewerkt hebt.

## 4. Hoe werk stroomt: de instellingen
`python3 tools/haam/haam.py settings --explain` toont elke optie met de afweging erbij. De keuzes die ertoe doen:

| Instelling | Begin met | Kies iets anders als | Wat het kost of riskeert |
|---|---|---|---|
| `flow` | `test-first`: je test de branch van de agent, daarna draaien de PR en de checks één keer | `checks-first`: je wilt alleen code testen die door de checks is gekomen, of je test op een gedeelde stagingomgeving | Elke herstelronde draait de checks opnieuw |
| `uat` | `owner-decides`: je test alles behalve wat je markeert met `uat:skip` | `always`: gereguleerde of veiligheidskritieke producten. `bugs-skip`: veel kleine fixes met sterke tests | `bugs-skip`: een verkeerde fix kan live gaan zonder dat jij ernaar gekeken hebt |
| `grouping` | `per-issue`: één PR per issue | `per-epic`: epics die uit kleine items bestaan. `release` (alleen test-first): schaarse minuten en releases in batches | Eén item dat faalt, houdt de hele batch tegen |
| `ci` | `every-pr`, op GitHub | `local`: de minuten raken op en je computer bouwt alles. `off`: alleen voor solo-prototypes | `local` is niet bestand tegen manipulatie |
| `review` | `github`: twee onafhankelijke AI-reviews per PR | `protected-only`: bespaart de meeste reviewkosten. `local`: bespaart minuten | Minder onafhankelijke checks |
| `nightly` | `on` | `off`: als minuten heel schaars zijn | Je ontdekt kapotte dingen en nieuwe kwetsbaarheden later |
| `runner` | `github` | `self-hosted`: een private repository met zware builds en een machine die aan blijft staan | Onderhoud. Nooit voor publieke repositories |
| `deploy` | `github`: `deploy.yml` deployt bij de merge | `manual`: je deployt op een andere manier | `ship` wacht tot je "live" zegt |
| `deploy_approval` | `each`: elke deploy wacht op je goedkeuring | `automatic`: je abonnement kan deploys niet laten wachten (§1), of je koos `uat: always` | Een gemergede wijziging gaat live zonder laatste blik |
| `worktree_cleanup` | `after-ship` | `manual`: je ruimt worktrees liever zelf op | Schijfruimte |

De route zonder UAT merget alleen vanzelf op GitHub Projects, met de secret `HAAM_PROJECT_TOKEN`, `ci: every-pr` en `review: github`. Anders zet je die PR's zelf live.

Vermijd deze combinaties, want samen halen ze de laatste controle weg:
- `ci: off` met `review: off`: niets controleert de code vóór je test.
- `deploy_approval: automatic` met `uat: bugs-skip`: een bugfix kan productie bereiken zonder dat er een mens naar gekeken heeft. Deploys zijn automatisch op een private repository onder Enterprise Cloud, dus kies daar geen `bugs-skip`.

## 5. Limieten: hoeveel werk er mag wachten
De limieten voorkomen dat agents meer maken dan jij kunt testen, en meer PR's dan je CI-budget aankan. Als een limiet bereikt is, beginnen agents geen nieuwe builds meer. Ze lossen nog wel herstelwerk op, schrijven specs en beoordelen ideeën.

| Limiet | Wat het telt | Hoe je het afstemt |
|---|---|---|
| `max_in_uat` | Wijzigingen die op je test wachten. De belangrijkste limiet in test-first | Wat je in één sessie kunt testen: minuten per sessie ÷ minuten per test (een test duurt vaak 5 tot 10 minuten). Eén uur per dag met ongeveer 6 minuten per test is 10 |
| `max_open_prs` | PR's die klaar zijn. Drafts, PR's met alleen docs en PR's van bots (Dependabot) tellen niet mee | Test-first: PR's bestaan maar kort (van je goedkeuring tot `ship`), dus twee keer het aantal agent-chats dat tegelijk draait is ruim genoeg. Checks-first: elke wijziging die op je test wacht, is een PR die klaar is, dus stel het in op minstens `max_in_uat` plus het aantal chats dat tegelijk draait |
| `max_review_rounds` | Mislukte AI-reviewrondes voordat een agent stopt en het jou vraagt | 2. Verhoog naar 3 voor lastige gebieden |
| `max_pr_lines` | Streefgrootte van één PR, in gewijzigde regels | 400. Kleinere PR's krijgen betere reviews en tests |

Reken het uit voor je team:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
Het toont de voorgestelde limieten en waarschuwt als de agents meer kunnen maken dan jij kunt testen. Daarna geeft het het commando dat ze toepast. Het gaat uit van ongeveer 6 minuten per test en 2 wijzigingen per chat per dag; geef `--minutes-per-test` en `--changes-per-chat` mee met je eigen cijfers. Het leest `flow` uit de instellingen van het project, of neemt `--flow`.

Als de agents meer maken dan je kunt testen:
- loopt de wachtrij vol en pauzeren agents nieuwe builds, en dat is precies wat de limiet moet doen;
- ruimt `/test all` met "pass all verified" de wijzigingen op die de agents zelf hebben aangetoond;
- stuurt `uat: bugs-skip` kleine bugfixes direct naar de checks;
- of draai je minder agent-chats.

Voor een weekend agentwerk dat je in één sessie test, open je een **batchvenster**: een verhoging die vanzelf afloopt na de laatste dag, bijv. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. Wat je beschermt
**De regel:** bescherm de code waar een verkeerde wijziging gebruikers kan schaden, geld of data kan kosten, de wet kan overtreden, of de eigen gates van HAAM kan verzwakken. Elke beschermde wijziging heeft jouw code review en jouw test nodig, en gaat nooit via de route zonder UAT. Bescherm dus wat ertoe doet, niet alles.

| Gebied | Beschermen | Typische paden (voorbeelden) |
|---|---|---|
| Inloggen, sessies, rechten, rollen | Altijd | `src/auth/**`, `**/permissions/**`, *de auth-middleware* |
| Betalingen, facturering, terugbetalingen, prijzen | Altijd | `src/billing/**`, `src/payments/**` |
| Persoonsgegevens: opslag, bewaartermijnen, verwijdering, exports | Altijd als je persoonsgegevens hebt | `src/users/**`, `**/privacy/**` |
| Logging die persoonsgegevens kan vastleggen | Altijd als je persoonsgegevens hebt | *de loggingconfiguratie en de auditmodules* |
| Beslissingen over gebruikers: geschiktheid, verificatie, goedkeuringen, scores | Als een verkeerd resultaat iemand schaadt | `src/verification/**`, `src/decisions/**` |
| Externe providers die namens gebruikers handelen of hun data ontvangen | Ja | `src/integrations/**` |
| Databasemigraties | Altijd | `db/migrations/**`, `**/migrations/**` |
| Beveiligingsconfiguratie: crypto, CORS, CSP, omgang met secrets | Ja | `**/security/**`, `**/crypto/**` |
| Infrastructure as code | Ja | `infra/**`, `terraform/**` |
| Signing- en releaseconfiguratie voor mobiel | Als je apps uitbrengt | *entitlements, signing- en release-buildbestanden* |
| CI-, deploy- en buildscripts | Standaard beschermd | `.github/**`, `Makefile`, `scripts/**` |
| HAAM en de setup van de agents | Standaard beschermd | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json`, en meer: `haam.py settings` toont ze |

Paden in cursief beschrijven waar je naar moet zoeken; maak er echte patronen van voor je code.

Zo stel je het in:
1. `/haam-setup` stelt voor elk gebied dat van toepassing is echte paden uit je code voor. Jij bevestigt ze.
2. `config --protected "src/auth/**,db/migrations/**" --human` voegt patronen toe, en `config --unprotected "…" --human` verwijdert er een. `**` betekent willekeurige mappen en `*` betekent binnen één map. Een gewone mapnaam dekt alles wat erin staat.
3. `haam.py protected` toont op elke branch de beschermde bestanden die die branch wijzigt.
4. De release-gate beslist op basis van de bestanden die een PR wijzigt. Hij leest de lijst van `main`, dus een agent kan in zijn eigen PR geen bescherming weghalen.

Bekijk de lijst opnieuw als `docs/product/ARCHITECTURE.md` verandert.

## 7. Gedeelde testresources
Sommige tests gebruiken iets wat de hele computer deelt, zoals een lokale database die de tests clonen, een telefoonsimulator of een aangesloten device. Twee agent-chats die ze tegelijk draaien, zitten elkaar in de weg, en de fout ziet eruit als een kapotte wijziging. Zet die commando's als patronen in de lijst: `config --heavy-run "make (check|test-integration)"`. Agents draaien ze dan een voor een via `haam.py exclusive`. Laat de lijst leeg als je tests op zichzelf staan.

## 8. Hoeveel vrijheid agents krijgen
Agents kunnen snel grote stukken bouwen, zoals mensen met AI "vibe-coden", overal waar een fout goedkoop weg te gooien is. Alles wat voor echte gebruikers draait, blijft achter de gates.

**Een paar woorden die hier gebruikt worden:**
- **Prototype** (of **spike**): een snelle werkende wegwerpversie van een idee, gebouwd om uit te proberen, nooit zoals hij is live gezet.
- **Slice:** één stuk van een epic dat los live kan, met een eigen issue en spec.
- **Leidende agent:** de ene agent-chat die een hele epic bouwt. Die kan onafhankelijke slices aan hulpagents geven (**sub-agents**).
- **Feature flag:** een schakelaar in de code die een nieuwe feature verborgen houdt tot iemand hem aanzet.
- **Productiecode:** de code die voor echte gebruikers draait.

Drie keuzes:

| Keuze | Wat het doet | Wanneer je het gebruikt |
|---|---|---|
| **Eerst een prototype.** Typ `/spike`, of kies `prototype` in `/triage` | Een agent bouwt een prototype op een `spike/`-branch, zonder spec, PR of groottelimiet. Je probeert het uit met `/test`. Daarna zeg je `discard`, `change: <what>`, `rebuild` (specificeren en opnieuw bouwen) of `keep` (specificeren en vanuit die code bouwen) | Als het uitproberen van het idee je meer vertelt dan erover lezen: een nieuw scherm, een flow, een integratie waar je niet zeker van bent |
| **Epic-bouwmodus.** Geef een goedgekeurde epic het label `mode:epic-build`; `/decide` en `/triage backlog` bieden het aan | Eén leidende agent bouwt elke slice van de epic op één branch, met een checkpoint na elke slice. Je test de hele feature en zet die in één keer live | Een feature waarvan de slices alleen samen zinvol zijn, of die je liever als geheel beoordeelt |
| **Wat telt als productiecode** (`production_paths`, `non_production_paths`) | Vertelt agents en jou wat er voor gebruikers draait, zodat de notities bij een prototype en `haam.py production` laten zien wat een wijziging zou raken. Prototypes, tests en docs vallen er standaard buiten | Maak het smaller als je product in een paar mappen staat: `config --production "src/**,api/**" --human`. Voeg mappen die nooit voor gebruikers draaien toe met `config --not-production "…" --human`. Als je docs zijn wat gebruikers zien, haal ze dan uit de lijst met `config --remove-not-production "docs/**" --human` |

Welke modus ook: elke wijziging die gemerged wordt, gaat door elke gate. De vangrail daarachter:
- een prototype wordt nooit gemerged: de release-gate weigert `spike/`-branches en alles onder `prototypes/`, en `publish` weigert spikes;
- behouden prototypecode bereikt gebruikers alleen via `/spec`, een normale branch en jouw test, achter een feature flag die standaard uit staat. Die code gaat nooit via de route zonder UAT: de gate ziet de `spike:`-commits;
- productiecode importeert nooit uit `prototypes/`, en de AI-reviewer blokkeert het als dat toch gebeurt;
- een prototype wijzigt nooit beschermde gebieden, en `/test` laat je de gewijzigde beschermde bestanden en nieuwe dependencies zien voordat er iets draait;
- beschermde gebieden krijgen altijd jouw code review;
- geen enkele agent raakt productiesystemen of productiedata aan, in welke modus ook.

## Bronnen
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (abonnementen waarin ze zitten) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (verplichte reviewers op private repositories) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
