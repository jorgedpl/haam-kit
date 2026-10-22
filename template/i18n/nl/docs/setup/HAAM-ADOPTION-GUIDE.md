# Human-Agent Agile Methodology (HAAM)
## Invoeringsgids voor de projectadmin

HAAM is een manier om software te bouwen waarbij **mensen beslissen en agents uitvoeren**. Elk stuk werk gaat van idee naar productie door dezelfde fasen, met menselijke gates op de momenten die ertoe doen. Alles staat in **Git** (kennis en code) en in de **tracker** (werk en status): een **GitHub Projects**-board (gratis) of **Linear**. Mensen kunnen verschillende coding agents gebruiken (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) met hun eigen accounts en toch parallel werken.

Deze gids past HAAM toe op een bestaande repository in **zes fasen, in totaal ongeveer een halve dag**. Je kunt na elke fase stoppen en hebt dan toch al iets nuttigs.

---

## De kit ophalen

De kit is de map `template/` van https://github.com/jorgedpl/haam-kit. Gebruik altijd een gereleasede versie:
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
of download de zip van de pagina Releases. Hieronder betekent `<path-to-kit>` die map `template/`.

## De snelle route: laat je agent het doen

Zet de kit ergens buiten je project, open je coding agent **in de hoofdmap van je project** en zeg:

> Lees `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` en volg het om HAAM in deze repository op te zetten. De kit staat in `<path-to-kit>`.

De agent bedient de setup-tool (`tools/haam/haam.py`) door alle fasen hieronder. Hij stelt je een handvol vragen, laat elke wijziging zien voordat hij die doorvoert, en geeft je de paar stappen die je wachtwoorden of sleutels nodig hebben, zodat je die in je eigen terminal uitvoert. Gebruik de rest van deze gids om te begrijpen wat hij doet, of om het met de hand te doen.

### Wie doet wat tijdens de setup

| Gemarkeerd als | Betekent |
|---|---|
| `[agent]` | Je coding agent doet het (of jij, als je het met de hand doet) |
| `[YOU, in your terminal]` | Je voert het commando zelf uit: er komt een secret bij kijken (API-sleutel, login) die nooit door de chat van een agent mag gaan |
| `[YOU, in the browser]` | Een instelling die GitHub of Linear alleen in de webapp aanbiedt |

---

## Wat je krijgt

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
  workflows/tracker-sync.yml  Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/             Idea and bug forms (GitHub Projects)
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

### De levenscyclus in één plaatje

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### De commando's

Hier geschreven als `/name` (Claude Code, Cursor, Grok). In Codex gebruik je `$name`. Elke andere tool: *"volg `.agents/skills/<name>/SKILL.md`"*.

| Commando | Fase | Wie |
|---|---|---|
| `/idea <text>` | Een idee vastleggen | Iedereen |
| `/bug <text>` | Een probleem melden | Iedereen |
| `/assess APP-12` | Waarde, inspanning, risico en haalbaarheid beoordelen | Agent |
| `/triage` | De inbox triëren, issues in epics groeperen (`group`), opnieuw rangschikken (`backlog`), vastgelopen werk najagen (`stale`) | Alleen mensen |
| `/epic APP-9` | Een epic vormgeven: briefing, vragen voor jou, opruimen van de issues erin | Alleen mensen |
| `/decide APP-12 approve` | Gate G1 | Alleen mensen |
| `/spec APP-12` | Een spec schrijven die klaar is om te bouwen | Agent |
| `/work bugs` | Een agent starten in een nieuw chatvenster: eigen worktree, daarna `/next` | Iedereen |
| `/next` | Het volgende item kiezen uit bugs, features en ideeën | Agent |
| `/build APP-12` | Implementeren met unittests, een PR openen | Agent |
| `/uat APP-12` | Je lokale testplan schrijven | Agent |
| `/test` | Een wijziging testen, daarna `pass` → `ship`, of zeggen wat er mis is (G4 en G5) | Alleen mensen |
| `/uat-result APP-12 pass` | Los een testresultaat vastleggen (G4) | Alleen mensen |
| `/override APP-12 "reason"` | UAT overslaan in een noodgeval | Alleen mensen |
| `/release APP-12` | Afsluiten na de deploy | Alleen mensen |
| `/haam-setup` | HAAM invoeren in een repo | Projectadmin |
| `/haam-onboard` | Een nieuwe developer klaarmaken | Nieuwe developer |
| `/haam-update` | Bijwerken naar een nieuwe versie van de kit | Projectadmin |

### Hoe code review werkt

Geen enkele agent reviewt ooit zijn eigen werk, en secrets worden opgevangen door een scanner, niet door een oordeel. Elke wijziging gaat door zes lagen:

| Laag | Wanneer | Wat het controleert | Wie doet het |
|---|---|---|---|
| 1. Lokale secret-bewaking | Voor elke commit | Sleutels, tokens, wachtwoorden in de wijzigingen; de commit wordt geblokkeerd als er iets gevonden wordt | gitleaks via de git-hook (iedereen), plus hooks van de agent-tool waar dat kan |
| 2. Zelfcontrole | Voordat er een PR wordt geopend | Tests slagen; security-zelfreview van de eigen diff | De agent die het bouwde |
| 3. Geautomatiseerde CI | Elke update van een PR | Tests, lint, types (`ci`); secrets in elke commit (`secrets`); kwetsbare libraries (`dependencies`) | GitHub Actions |
| 4. Onafhankelijke AI-review | Elke update van een PR (niet bij drafts of PR's met alleen docs) | Voldoet het aan de spec? Zijn de tests eerlijk? Bugs, scope creep, overtredingen van regels (`ai-review`). Beveiligingskwetsbaarheden (`security-review`) | Een aparte Claude in GitHub Actions die de code nooit heeft zien schrijven (een ander model als de code uit een andere tool kwam) |
| 5. Menselijke code review | PR's die beschermde gebieden raken | Kernlogica, auth, betalingen, persoonsgegevens, migraties, infrastructuur, configuratie van agents | Product owner of een aangewezen developer |
| 6. Menselijke acceptatie | Elke PR met code | Het werkt echt (Gate G4 UAT) | Product owner |

- De reviewer plaatst één commentaar met **Blocking / Should fix / Nits**. Blokkerende bevindingen houden de merge tegen.
- De bouwende agent lost de Blocking-items op en pusht; de reviews draaien automatisch opnieuw. Als hij het er niet mee eens is, antwoordt hij op de PR en vraagt hij het een mens. Na **twee** mislukte rondes stopt hij en draagt hij het over.
- AI-reviewers kunnen blokkeren, maar nooit goedkeuren of mergen. Alleen een mens kan ze overrulen, met het PR-label `ai-review-overruled`.
- Als er ooit een echte secret op GitHub belandt: trek hem direct in en vervang hem, en laat daarna een admin de geschiedenis van de branch herschrijven. Hem verwijderen in een nieuwe commit is niet genoeg.

Alle regels: `docs/process/GATES.md`. Instructies voor de reviewer die je kunt bijstellen: `.github/review/REVIEWER.md`.

---

## Voordat je begint

Je hebt nodig:
- [ ] Admintoegang tot de GitHub-repository. Als die privé is, hebben branchregels GitHub Pro of Team nodig, en een goedkeurder voor productiedeploys vereist Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Een tracker: **GitHub Projects** (niets extra; gratis bij elk abonnement) of admintoegang tot een **Linear**-workspace
- [ ] Een geïnstalleerde coding agent waarop je bent ingelogd, met je eigen account
- [ ] Python 3, Git, Make, en de GitHub CLI met een actieve login (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, of via de releasepagina op GitHub)
- [ ] Een Claude-secret voor de reviewer-agents: een token van een Claude-abonnement (`claude setup-token`) of een Anthropic API-sleutel met een maandelijkse uitgavelimiet (console.anthropic.com)
- [ ] Je project draait vandaag al lokaal

Beslis nu:
1. **Tracker:** GitHub Projects (gratis, alles in GitHub) of Linear (prettiger in gebruik, gratis abonnement beperkt). Je kunt later overstappen.
2. **Productsleutel:** een korte code, bijv. `ACM`, `SHOP`, `CRM` (de Linear-teamsleutel als je Linear gebruikt). De kit gebruikt `APP` als placeholder tot `config` die overal vervangt.
3. **Product owner:** de ene persoon die ideeën, specs, UAT en deploys goedkeurt (plus eventueel een vervangende goedkeurder).
4. **Agent-tools** die je team gaat gebruiken.

Controleer je machine wanneer je wilt met: `python3 <kit>/tools/haam/haam.py dev`

---

## Fase 1: De kit installeren (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

De docs zijn in het Engels, tenzij je `--language es` (of `fr`, `de`, `it`, `nl`, `pt`) aan beide commando's toevoegt. De agents schrijven dan ook specs, issues, UAT-plannen en berichten in die taal; commando's, labels en code blijven Engels. Wijzig het later met `haam.py config --language <code>`, en daarna `update --target . --apply` van de kit.

De installer **overschrijft nooit** je bestanden:
- Nieuwe bestanden worden toegevoegd.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` en `.claude/settings.json` worden automatisch **gemerged**.
- `.gitignore` krijgt één keer een HAAM-blok erbij.
- Elk ander bestand dat je al hebt, blijft ongemoeid, en de versie van de kit wordt opgeslagen in `.haam/incoming/`, zodat jij (of de agent) ze kan mergen.

Zo merge je de gebruikelijke conflicten:

| Als je repo al heeft… | Doe dit |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Verplaats projectspecifieke kennis (conventies, valkuilen, commando's) naar `docs/product/ARCHITECTURE.md` of naar een sectie "Project specifics" aan het eind van `AGENTS.md`. Gebruik daarna `AGENTS.md` en `CLAUDE.md` van de kit. Houd Cursor-regels in `.mdc` alleen voor details die met een glob afgebakend zijn |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` verplaatst je skills naar `.agents/skills/` en linkt de map. Hernoem eerst skills waarvan de naam botst met die van HAAM |
| `Makefile` | Voeg de targets van de kit toe aan de jouwe |
| `.github/workflows/` met CI | Houd je CI, maar zorg dat een job met de naam **`ci`** je volledige testsuite op PR's draait. Voeg `gates.yml`, `security.yml`, `review.yml` toe. Vergelijk je deploy met `deploy.yml` (Fase 4) |
| `.github/pull_request_template.md` | Merge er "Gebouwd met (Built with)", "Acceptatiecriteria → tests" en "Checklist (G3)" in |
| `.pre-commit-config.yaml` of Husky | Houd het en roep er `scripts/scan-secrets.sh` vanuit aan, in plaats van `.githooks/` te gebruiken |
| `CHANGELOG.md`, `.github/dependabot.yml` | Houd de jouwe (voeg het ecosysteem `github-actions` toe aan Dependabot als het ontbreekt) |

Verwijder `.haam/incoming/` als je klaar bent.

---

## Fase 2: Configureren en je project aanleren (45 min)

1. **Projectinstellingen** `[agent]` (antwoorden van jou):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Dit schrijft `haam.config.json` en vervangt de placeholder `APP` en de productnaam in elk HAAM-bestand.

2. **Agent-tools** `[agent]`: `python3 tools/haam/haam.py agents --apply`. Dit linkt de gedeelde skills voor Claude Code en Grok, controleert de bestanden van Cursor/Codex/Gemini/Copilot en noemt eventuele stappen per persoon. Details: `docs/setup/AGENTS-SETUP.md`.

3. **Commandocontract** `[agent]`: vul elke `TODO(setup)` in `Makefile` in (setup, dev, test, lint, typecheck, build, audit) en de runtime-stappen in de workflows, met de echte commando's van je project. Daarna moet `make check` slagen op de huidige code. Als tests op `main` al falen, repareer of markeer ze dan eerst: HAAM rekent erop dat groen ook echt groen is. Als `make audit` oude kwetsbaarheden van niveau high/critical meldt, los ze op of leg ze vast als bugs en verhoog de drempel tijdelijk.

4. **Architectuurkaart** `[agent]`: vul `docs/product/ARCHITECTURE.md` in vanuit de codebase (minder dan 150 regels) en stel echte paden voor de beschermde gebieden in `AGENTS.md` §4 voor. Jij reviewt het.

5. **Productcontext** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: wat het is, gebruikers, trajecten die nooit mogen breken, harde voorwaarden, huidige prioriteiten. Dit leest elke agent om afwegingen te maken.

6. **Onboardingdoc** `[agent]`: vul de `TODO(setup)`-items in `docs/ONBOARDING.md` in (clone-URL, runtime, lokale URL).

7. **Hygiëne rond secrets** `[agent]`: `make hooks`, en scan daarna één keer de geschiedenis: `gitleaks git --redact -v .` Alles wat echt is, moet bij de provider worden **ingetrokken en vervangen**: het ligt al open voor iedereen met toegang tot de repo. Jij keurt eventuele fingerprints van valse positieven goed die aan `.gitleaksignore` worden toegevoegd.

8. **Parallelle chats** `[agent]`: zet de bestanden die alleen lokaal bestaan en die de app nodig heeft (zoals `.env`) in `.worktreeinclude`, sluit `.claude/worktrees/` uit bij elke tool die de hele map scant (testrunner, linter, watcher), en probeer een nieuwe worktree: `python3 tools/haam/haam.py worktree new setup-check`, daarna `make setup && make check` erin, daarna `git worktree remove .claude/worktrees/setup-check`. Vanaf dan begint elke nieuwe agent-chat met `/work`.

9. **Controle:** `python3 tools/haam/haam.py doctor` laat zien wat er nog over is.

---

## Fase 3: De invoerings-PR openen (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Hierdoor bestaan de checks in GitHub, zodat ze verplicht gemaakt kunnen worden. Het eerste commentaar van de AI-review verschijnt op deze PR.

---

## Fase 4: Gates in GitHub (20 min)

1. **Eerst plannen, dan toepassen** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Het maakt de labels aan, een ruleset op de standaardbranch (PR verplicht, de zes verplichte checks, geen force pushes; admins kunnen alleen omzeilen bij het mergen van een PR, voor noodgevallen, nooit door naar main te pushen; "up to date before merging" uit, om CI-runs te besparen). Als de ruleset al bestaat, voegt het alleen toe wat ontbreekt en behoudt het je instellingen (`--reset` vervangt hem), de environment `production` met je goedkeurders, de variabele `PRODUCTION_URL`, en zet het secret scanning, push protection en Dependabot aan waar je abonnement dat toelaat.
2. **Sleutel voor de reviewer** `[YOU, in your terminal]`: één secret draait beide reviews. Ofwel `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` met de token uit `claude setup-token` (gebruikt je Claude-abonnement), ofwel `gh secret set ANTHROPIC_API_KEY -R owner/repo` met een aparte API-sleutel (gefactureerd per review; daarmee gebruikt de security review de security-review-action van Anthropic). Beide commando's vragen om de waarde zonder die te tonen.
3. **PR's vanuit forks** `[YOU, in the browser]`: Settings → Actions → General → goedkeuring vereisen voor externe bijdragers.
4. **Deploys:**
   - *Deploy je al vanuit GitHub Actions?* Voeg `environment: production` toe aan je deploy-job: dat alleen geeft je al Gate G5. Verwijder `deploy.yml` van de kit of houd hem als referentie.
   - *Deploy je op een andere manier* (de Git-integratie van een hostingplatform, met de hand)? Verplaats de deploys naar `deploy.yml` (vul `make deploy` in) of houd je eigen methode en behandel G5 als een handmatige stap: de product owner deployt na de merge en voert daarna `/release` uit. Zet automatisch deployen bij een push uit als dat de goedkeuring zou omzeilen.
5. **Private repositories:** branchregels hebben GitHub Pro of Team nodig, en een goedkeurder voor productiedeploys vereist Enterprise Cloud; de tool vertelt je wat je abonnement toelaat. Zonder goedkeurder is jouw `ship` de releasebeslissing: stel `deploy_approval: automatic` in (`docs/setup/DECISIONS.md` §1).

Details en handmatige alternatieven: `docs/setup/GITHUB-SETUP.md`.

---

## Fase 5: De tracker (20 min)

### Optie A: GitHub Projects (gratis)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (laat je GitHub-login Projects gebruiken).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` automatiseringstoken, zodat kaarten verschuiven als PR's geopend en gemerged worden: maak een klassieke token aan op github.com/settings/tokens met de scopes `project` en `repo` (`public_repo` is genoeg voor een publieke repository), en daarna `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` maak op het board de weergaven aan die de tool noemt: Board grouped by Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Test: `python3 tools/haam/haam.py issue list`.

Agents gebruiken `python3 tools/haam/haam.py issue …` voor elke handeling op het board (`docs/process/TRACKER.md`), dus het werkt hetzelfde vanuit Claude Code, Cursor, Codex, Grok of wat dan ook.

### Optie B: Linear
1. **Statussen, labels, team** `[YOU, in your terminal]` (vereist je persoonlijke Linear API-sleutel, die nooit via een agent gaat):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Het maakt het team aan als dat nodig is, zet Triage aan, maakt de 12 statussen aan (de standaardstatus "Todo" van Linear wordt hernoemd naar "Ready"), en de 14 labels. Het verwijdert nooit iets; het noemt extra statussen die je zelf kunt archiveren.
2. **Instellingen die alleen in de browser kunnen** `[YOU, in the browser]`: GitHub koppelen, PR-automatiseringen (draft-PR → In Progress, PR klaar voor review → In Review, gemerged → Deploying), het formaat voor branchnamen `{issue-identifier}-{issue-title}`, opgeslagen weergaven. Zie `docs/setup/LINEAR-SETUP.md`.
3. **Koppel je agent** aan Linear (`docs/setup/AGENTS-SETUP.md`) en test: *"Toon de issues in het Linear-team ACM."*

**Heb je al een backlog?** Vraag je agent om die naar de tracker over te zetten (GitHub-issues kun je gewoon aan het board toevoegen). Zet alles in **Triage**, triëer één keer (`stream:bug`, `stream:idea`, of `stream:feature` + Backlog), en specificeer alleen de bovenste vijf.

---

## Fase 6: Mergen, een proefronde, en mensen

### De invoerings-PR mergen
Als de checks groen zijn, voeg je zelf `uat-passed` toe (de gate is nu actief, dus ook deze PR gaat erdoor) en merge je. Als de reviewer-agents muggenziften over de kit zelf, overrule dan met `ai-review-overruled`. Voer `python3 tools/haam/haam.py doctor --role admin` uit voor een laatste controle.

### Doe één volledige ronde (45–60 min)
Kies iets kleins en echts. Loop er één keer elke fase mee door:

| Stap | Jij typt | Wat er moet gebeuren |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Nieuw issue in Triage, label `stream:idea` (op GitHub: `#1`; op Linear: `ACM-1`) |
| 2 | `/assess #1` | Beoordeling gecommit op de branch van het issue (geen PR); het issue gaat naar Decision |
| 3 | `/decide #1 approve medium` | Het issue gaat naar Backlog, het label wordt `stream:feature` |
| 4 | `/spec #1` | Spec met acceptatiecriteria, op dezelfde branch |
| 5 | Lees de spec (link op het issue), zeg tegen de agent "spec approved" | Het issue krijgt `agent-ready`, gaat naar Ready |
| 6 | `/build #1` | Claimt het, maakt een branch, codeert, schrijft tests, reviewt zichzelf, schrijft het UAT-plan en pusht de branch. Nog geen PR (test-first, de standaard) |
| 7 | `/uat #1` (`/build` voert het uit) | Het issue gaat naar UAT; je krijgt een melding |
| 8 | `/test #1` | De agent zet de wijziging op je machine, start de app en geeft je een korte checklist |
| 9 | Probeer het uit, antwoord `pass` | De agent opent de PR met het label `uat-passed`; `ci`, `secrets`, `dependencies` en de reviewer-agents draaien één keer; `release-gate` wordt groen; de agent vraagt "Live zetten?" |
| 10 | Antwoord `ship` | De agent merget, keurt de productiedeploy voor je goed, wacht en sluit het issue: Done |
| 11 | (probeer het één keer) `/test` op een wijziging en beschrijf in plaats daarvan een probleem | Het gaat terug naar de agents met je notities (`uat-failed`) en komt bij je terug als het opgelost is |

(Op Linear zien de ID's eruit als `ACM-1`.)

Probeer daarna één keer de randgevallen: vraag de agent om op een wegwerpbranch een nepsleutel te committen (`AKIA` + 16 hoofdletters/cijfers): de commit moet geblokkeerd worden. Laat daarna een UAT falen, en gebruik een override. Stel de skills in `.agents/skills/` of het proces in `docs/process/LIFECYCLE.md` bij waar iets niet goed voelde.

**Probeer in de proefronde ook een tweede agent-tool** (bijv. Cursor of Codex voor stap 6). Dat bevestigt dat de gedeelde regels en skills ook buiten je hoofdtool werken.

### Developers toevoegen
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: schrijfrechten op GitHub (geen admin), toegang tot het GitHub Projects-board, of een uitnodiging voor Linear.
2. Stuur ze de link naar de repo en de testgegevens (via een wachtwoordmanager of een eenmalige link, nooit via chat of e-mail).
3. Zij openen hun eigen agent in de repo en voeren `/haam-onboard` uit (Codex: `$haam-onboard`).
4. Zodra jullie met z'n tweeën zijn: de tool stelt "1 approval required" in als je vervangende goedkeurders toevoegt (`config --backup-approvers`, daarna `github --apply`), en je kunt `.github/CODEOWNERS` toevoegen voor beschermde gebieden.

### Agents semi-autonoom laten werken

| Niveau | Hoe | Wanneer |
|---|---|---|
| **1. Onder toezicht** | Je typt `/next` of `/build`, keurt elke push en PR goed | De eerste 2–3 weken |
| **2. In batches** | 2–3 chatvensters (elke mix van tools en computers), elk gestart met `/work`, dat er een eigen worktree aan geeft; je reviewt PR's in een batch | Zodra specs betrouwbaar goed zijn |
| **3. Gepland** | Een geplande taak draait een agent headless met `/next` en stopt bij UAT | Zodra je de gates vertrouwt |

Op elk niveau stoppen agents bij de menselijke gates.

### Lopende kosten
Naast GitHub, Linear (als je het gebruikt) en het agent-abonnement van elke persoon zijn de enige kosten op basis van verbruik de reviewer-agents: twee Claude-aanroepen per gereviewde push naar een PR, gefactureerd op `ANTHROPIC_API_KEY` of afgeschreven van je Claude-abonnement (`CLAUDE_CODE_OAUTH_TOKEN`). Laat de uitgavelimiet aan staan en houd PR's klein.

### Bijblijven
Nieuwe versies van de kit worden gepubliceerd op https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` vertelt je wanneer er een uit is. Voer `/haam-update` uit (Codex: `$haam-update`) op een branch: bestanden die je nooit hebt gewijzigd, worden bijgewerkt, je aanpassingen blijven behouden, en waar beide kanten iets veranderd hebben, merget de agent ze. De CHANGELOG noemt eventuele migratiestappen.

### Je ritme als product owner
Dagelijks (10–15 min): test **UAT**, maak **Triage** leeg (`/triage`). Wekelijks (30–45 min): beslis over alles in **Decision**, rangschik de backlog opnieuw (`/triage backlog`), jaag vastgelopen werk na (`/triage stale`), bekijk **Parked** opnieuw, sluit de **overrides** af. De volledige gids, met prioriteitsregels en checklists: `docs/process/PRODUCT-MANAGER.md`.

---

## Problemen oplossen

| Symptoom | Waarschijnlijke oorzaak | Oplossing |
|---|---|---|
| Niet zeker wat er nog moet gebeuren | – | `python3 tools/haam/haam.py doctor --role admin` |
| De agent volgt de regels niet | De tool leest `AGENTS.md` niet | Controle bij de eerste run in `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` zegt dat de login Projects niet kan gebruiken | De gh-login mist de scope `project` | `gh auth refresh -s project` |
| Kaarten op het board verschuiven niet als PR's geopend/gemerged worden | `HAAM_PROJECT_TOKEN` ontbreekt, of de PR bevat geen `Refs #123` | Voeg de secret toe (Fase 5); controleer de PR-beschrijving |
| De agent ziet Linear niet | MCP niet gekoppeld of niet ingelogd | Stappen per tool in `docs/setup/AGENTS-SETUP.md` |
| Skills verschijnen twee keer in Cursor | Cursor leest zowel `.agents/skills` als `.claude/skills` | Zet de compatibiliteit met Claude-skills uit in de instellingen van Cursor |
| `.claude/skills` of `.grok/skills` ontbreekt na het clonen (Windows) | Git-symlinks staan uit | `git config core.symlinks true` en opnieuw clonen, of `haam.py agents --apply` (kopieert in plaats daarvan) |
| `haam.py github` zegt dat rulesets/goedkeuringen niet beschikbaar zijn | Private repo met een gratis abonnement | Upgraden, of met de hand beschermen en op de checks vertrouwen |
| `haam.py linear` geeft een fout bij een stap | Wijziging in de API of rechten | Maak die stap met de hand af met `docs/setup/LINEAR-SETUP.md` |
| Twee chats wijzigden dezelfde bestanden of branch | Ze deelden één map | Begin elke agent-chat met `/work` (eigen worktree) |
| Tests of linter vinden dubbele bestanden onder `.claude/worktrees/` | De tool scant de hele map | Sluit `.claude/worktrees/` uit in de config van die tool |
| Een worktree kan de app niet draaien | Lokale bestanden ontbreken | Voeg ze toe aan `.worktreeinclude`, daarna `haam.py worktree prep` in de worktree |
| `/build` weigert te starten | Het issue staat niet in Ready, of `agent-ready` ontbreekt | `/spec` en keur hem goed, of zet het issue zelf op Ready |
| Linear-statussen bewegen niet bij PR-events | GitHub-integratie of automatiseringen niet ingesteld | Team settings → Workflow → PR automations; de PR-titel moet beginnen met het issue-ID |
| `release-gate` blijft rood na `uat-passed` | De workflow draaide niet opnieuw | Verwijder het label en voeg het opnieuw toe |
| Een verplichte check ontbreekt in de lijst | Hij heeft nog niet gedraaid | Open eerst een willekeurige PR |
| Commits geblokkeerd: "gitleaks is not installed" | gitleaks ontbreekt op die machine | Installeer het, daarna `make hooks` |
| Commit geblokkeerd voor een secret die er geen is | Valse positief | Een mens voegt de fingerprint toe aan `.gitleaksignore` in een gereviewde commit |
| `ai-review` of `security-review` blijft hangen of geeft fouten | Geen secret voor de reviewer (`CLAUDE_CODE_OAUTH_TOKEN` of `ANTHROPIC_API_KEY`), PR vanuit een fork, of de beurten zijn op | Voeg de secret toe; opnieuw draaien; verhoog `--max-turns`; of `ai-review-overruled` |
| Reviewer te streng | Instructies niet bijgesteld | Bewerk `.github/review/REVIEWER.md` |
| `dependencies` faalt bij elke PR | Oude kwetsbaarheden | Oplossen, of de drempel tijdelijk verhogen en ze als bugs bijhouden |
| Specs te vaag, builds gaan mis | G2 te los | Maak de Definition of Ready in `docs/process/GATES.md` strenger |

---

## Principes

1. **Mensen beslissen, agents voeren uit.**
2. **Wat niet in Git of in de tracker staat, bestaat niet** voor de volgende persoon of agent.
3. **Kleine slices:** één issue, één branch, één PR, te reviewen in 15 minuten.
4. **Een gate passeren is goedkoop, een gate overslaan is duur.** Overrides mogen, worden altijd vastgelegd en altijd opgevolgd.
5. **Groen is groen.** Maak nooit een test zwakker om door een gate te komen.
6. **Niemand kijkt het eigen huiswerk na.** De agent die code schrijft, reviewt die nooit; secrets worden opgevangen door tools, niet door een oordeel.
7. **Elke agent, dezelfde regels.** Tools zijn uitwisselbaar; het proces en de gates niet.
