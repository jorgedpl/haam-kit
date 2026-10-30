# HAAM: Human-Agent Agile Methodology

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · **Nederlands** · [Português](README.pt.md)

**Mensen beslissen. Agents voeren uit. Alles staat in Git en in je tracker.**

HAAM is een open methodologie en kit om software te bouwen met AI-coding agents, van idee tot productie, zonder de controle te verliezen. Elke agent krijgt dezelfde regels, dezelfde commando's en dezelfde gates, in welke tool hij ook draait: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI of GitHub Copilot**. Het werk wordt bijgehouden op een **GitHub Projects**-board (gratis) of in **Linear**, wat jij kiest. Meerdere mensen, elk met een eigen agent en account, kunnen tegelijk aan hetzelfde product werken.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## Wat je krijgt

- **Een levenscyclus met vijf menselijke gates**: over het idee beslissen, de spec goedkeuren, geautomatiseerde checks met een onafhankelijke AI-review, een acceptatietest door een mens, goedkeuring voor productie. Elke gate kun je in een noodgeval overrulen, en elke override wordt vastgelegd en opgevolgd.
- **Drie werkstromen** waaruit agents werk halen: bugs, features die klaar zijn, en ideeën om te beoordelen. De tracker (GitHub Projects of Linear) bevat de backlog, de prioriteiten en de status.
- **20 gedeelde skills** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), in het open Agent Skills-formaat.
- **Jouw instellingen, jouw afwegingen:** met `/haam-settings` kiest de product owner wanneer CI en de AI-reviews draaien (bij elke PR, lokaal, alleen voor beschermde gebieden, of uit), wat die zelf test, hoe werk wordt gegroepeerd (per issue, per epic of één release-PR), of deploys op goedkeuring wachten, en de limieten, elk met de afweging erbij en de eigen cijfers van het project.
- **Testen in één woord, voordat er CI-minuten verbruikt worden**: typ `/test`, probeer de wijziging van de agent uit op je eigen computer, antwoord `pass` (pas dan wordt de pull request geopend en gecontroleerd, één keer, op precies wat jij getest hebt) en daarna `ship` (de agent merget, deployt en sluit hem), of zeg gewoon wat er mis is (het gaat direct terug naar de agents en komt bij je terug als het opgelost is). `/test all` neemt alles wat wacht in één sessie door, en `ship --all` deployt het met één goedkeuring.
- **Een route zonder UAT** voor wijzigingen die je niet zinvol kunt testen (config, dependency-updates, onzichtbare refactors): markeer het issue één keer met `uat:skip`, en de PR merget vanzelf zodra CI en beide AI-reviews slagen.
- **Epics met een agent die de juiste vragen stelt**: `/triage group` maakt van een stapel losse issues epics (één per feature); `/epic` leest ze een voor een, schrijft een korte briefing, stelt je een paar gerichte vragen en ruimt daarna de issues op: duplicaten, gaten, splitsingen, volgorde.
- **Ruimte voor agents om snel grote stukken te bouwen, met een vangrail:**
  - `/spike` bouwt een werkend wegwerpprototype dat je kunt uitproberen voordat je beslist;
  - in epic-bouwmodus bouwt één agent een hele feature, slice voor slice, met checkpoints, één test en één release;
  - elke wijziging die gemerged wordt, gaat door elke gate, en prototypes worden nooit gemerged.
- **Een gids voor beslissingen** ([DECISIONS.md](template/i18n/nl/docs/setup/DECISIONS.md)): elke keuze die een team maakt bij het invoeren van HAAM, met een aanbeveling voor elke keuze. Over GitHub-accounts en het abonnement dat je nodig hebt, GitHub Projects of Linear, de instellingen, hoe je de limieten afstemt op je testtijd, en wat je beschermt. `/haam-setup` loopt het met je door.
- **Een gids voor de product manager** ([PRODUCT-MANAGER.md](template/i18n/nl/docs/process/PRODUCT-MANAGER.md)): dagelijks en wekelijks ritme, hoe je triëert, prioriteitsregels met een matrix van impact × bereik voor bugs, gezonde wachtrijgroottes, te doen met een agent (`/triage`) of direct in GitHub Projects of Linear.
- **Parallelle agents zonder botsingen**: open een nieuw chatvenster, typ `/work bugs`, en de agent krijgt een eigen kopie van het project (een git worktree), pakt de belangrijkste bug op en werkt die af tot aan jouw test. Draai er zoveel als je wilt, op één computer of op meerdere.
- **Code review waarbij niemand het eigen huiswerk nakijkt**: een secret-scan voor elke commit en in CI, een dependency-audit, en twee onafhankelijke AI-reviewers (spec/kwaliteit en security) die de code nooit hebben zien schrijven. Mensen reviewen beschermde gebieden en kunnen overrulen.
- **Gates afgedwongen door GitHub**, niet op vertrouwen: branchregels, verplichte checks, een UAT-labelgate en goedkeuringen voor deploys, zodat ze gelden welke agent of welk persoon er ook pusht.
- **Docs in zeven talen:** Engels, Spaans, Frans, Duits, Italiaans, Nederlands en Portugees. Kies er een bij de installatie (`install --language es`) en de agents schrijven ook specs, issues, UAT-plannen en berichten in die taal; commando's, labels en code blijven Engels.
- **Een setup-tool** (`haam.py`, Python 3, zonder dependencies) die de kit in een bestaande repo installeert zonder iets te overschrijven, GitHub en de tracker (GitHub Projects of Linear) configureert, agents één set commando's voor het board geeft, developers onboardt, de setup controleert en projecten bijwerkt naar nieuwe versies van de kit.

## Snel starten

### HAAM invoeren in je project (projectadmin, ongeveer een halve dag)

1. Haal een gereleasede versie van de kit op:
   ```bash
   git clone --depth 1 --branch v1.18.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (of download de zip van [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Open je coding agent **in de hoofdmap van je project** en zeg:
   > Lees `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` en volg het om HAAM in deze repository op te zetten. De kit staat in `~/haam-kit/template`.

De agent installeert de kit op een branch, stelt je een paar vragen, vult de projectkennis aan op basis van je code, en loodst je door GitHub en je tracker. Hij laat elke wijziging zien voordat hij die doorvoert. Alles waar een wachtwoord of API-sleutel bij komt kijken, doe je zelf, in je eigen terminal, nooit via de chat met de agent.

Doe je het liever met de hand? Volg [de invoeringsgids](template/i18n/nl/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Meedoen aan een project dat HAAM al gebruikt (developer, ongeveer een uur)

Clone het project, open je agent erin en voer `/haam-onboard` uit (Codex: `$haam-onboard`; andere tools: *"volg `.agents/skills/haam-onboard/SKILL.md`"*).

### Een project bijwerken naar een nieuwe versie van de kit

Haal de nieuwe versie van de kit op en voer dan in je project `/haam-update` uit, of:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Bestanden die je nooit hebt gewijzigd, worden bijgewerkt; bestanden die je hebt aangepast, blijven staan, en waar beide kanten iets veranderd hebben, wordt de nieuwe versie apart gezet zodat je agent ze kan mergen. Er wordt niets verwijderd.

## De setup-tool

| Commando | Wie | Wat |
|---|---|---|
| `install --target DIR` | admin | Kopieert de kit naar een repo. Overschrijft nooit; merget instellingenbestanden van agents; zet conflicten apart in `.haam/incoming/`; legt de versie vast in `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Werkt een project bij naar deze versie van de kit en behoudt de aanpassingen |
| `config` | admin | Productnaam, Linear-teamsleutel, repo, goedkeurders → `haam.config.json`; past ze toe op elk HAAM-bestand |
| `agents [--apply]` | admin | Koppelt skills en Linear voor Claude Code, Cursor, Codex, Grok, Gemini, Copilot |
| `github [--apply]` | admin | Labels, branch-ruleset met verplichte checks, goedkeuring voor productie, security-functies |
| `github-project [--apply]` | admin | GitHub Projects-board: 12 statussen, Priority-veld, labels, koppeling met de repo |
| `linear [--apply]` | admin, in de eigen terminal | Linear-team, triage, 12 statussen, 14 labels |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agents | Werken met het GitHub Projects-board vanuit elke agent-tool |
| `exclusive "<who>" -- <command>` | agents | Draait een zware testrun (een die een resource van de hele machine gebruikt) als er op deze machine geen andere draait |
| `capacity` | agents | Houdt nieuw werk tegen als er te veel PR's open staan of op jouw test wachten (limieten in `haam.config.json`) |
| `ci-usage [--days 7]` | admin | Waar de GitHub Actions-minuten naartoe gingen, per workflow, job, trigger en dag |
| `metrics [--days 30] [--save]` | owner | Hoe het werk stroomt: tijd tot Done, tijd in elke wachtrij (beslissing, spec, bouw, jouw test, uitrol), herhalingen, in UAT gevonden fouten tegenover later gevonden, reverts. `--save` bewaart de cijfers in `docs/metrics/` |
| `settings [--explain] [--set key=value] [--apply]` | owner/admin | Jouw keuzes: wanneer CI en de AI-reviews draaien, wat je test, groeperen, uitrollen, limieten (`/haam-settings` loopt ze met je door) |
| `local-ci ISSUE` | owner | Met `ci: local`: draait hier `make check` op de commit van de PR en post het resultaat (ship doet het voor je) |
| `review ISSUE` | agents | De twee AI-reviews in nieuwe lokale sessies, gepost als statussen van de PR (als de reviews lokaal zijn) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Zet een wijziging op deze machine om te testen; na `pass` + `ship`: mergen, de deploy goedkeuren (één voor meerdere), wachten, sluiten |
| `worktree status\|new\|prep\|list\|clean` | agents, iedereen | Eén worktree per agent-chat; kopieert lokale bestanden uit `.worktreeinclude`; ruimt afgeronde worktrees op |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Nodigt een developer uit (schrijfrechten op GitHub, geen admin; toegang tot het board of het Linear-team) |
| `dev [--apply] [--run-checks]` | developer | Controle van de machine, commit-hook, `.env` uit het voorbeeld, checks van het project |
| `doctor [--role admin] [--check-updates]` | iedereen | Wat er klaar is, wat er ontbreekt en wie het moet doen |
| `version [--check]` | iedereen | Versies van de tool, het project en de laatst gereleasede kit |

Elk commando laat eerst een plan zien en verandert alleen iets met `--apply`. Voeg `--json` toe voor machineleesbare uitvoer.

## Meerdere agents tegelijk draaien

Elke agent-chat krijgt een eigen map, zodat chats nooit elkaars werk overschrijven:

1. Open een nieuw chatvenster (Claude Code in VS Code: Cmd/Ctrl+Shift+Esc).
2. Typ `/work bugs` (of `/work features`, `/work specs`, `/work ideas`, of gewoon `/work`; Codex: `$work`).
3. De agent gaat naar zijn eigen git worktree, kopieert lokale bestanden zoals `.env`, claimt het bovenste item op het board, bouwt en test het, opent de PR en geeft je een testplan.

Herhaal dit voor zoveel agents als je wilt, op elke computer waarop het project gecloned is. De claim op het board voorkomt dat twee agents hetzelfde issue oppakken, of het nu is om het te bouwen, te beoordelen of de spec te schrijven. Je eigen chat blijft in de hoofdmap voor ideeën, beslissingen, testen en releases.

## Een tracker kiezen

| | GitHub Projects | Linear |
|---|---|---|
| Kosten | Gratis bij elk GitHub-abonnement | Gratis abonnement met limieten; betaald per gebruiker |
| Waar | Naast je code, één login | Aparte app |
| Agents gebruiken | `haam.py issue …` (elke agent) | De MCP-server van Linear |
| Het best voor | Solo en kleine teams, alles in GitHub houden | Drukkere backlogs, meerdere teams, uitgebreidere planning |

Dezelfde levenscyclus, gates en skills in beide gevallen, en je kunt later overstappen. Zie [TRACKER.md](template/i18n/nl/docs/process/TRACKER.md).

## Compatibiliteit met agents

| | Regels | Skills | Een skill aanroepen | Linear (indien gebruikt) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | controleren bij de eerste run | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` via `.gemini/settings.json` | per bestand | per bestand | per gebruiker |
| GitHub Copilot | `AGENTS.md` | per bestand | per bestand | per gebruiker |

Op GitHub Projects gebruikt elke agent dezelfde `haam.py issue`-commando's, dus er hoeft per tool niets gekoppeld te worden. Details en aanbevolen veilige instellingen per tool: [AGENTS-SETUP.md](template/i18n/nl/docs/setup/AGENTS-SETUP.md).

## Vereisten

- Een GitHub-repository. Publieke repositories krijgen alles met het gratis abonnement. Bij **private** repositories hebben de branchregels GitHub Pro of Team nodig, en een verplichte goedkeurder voor productiedeploys vereist GitHub Enterprise Cloud (zonder dat is jouw `ship` de releasebeslissing). [DECISIONS.md](template/i18n/nl/docs/setup/DECISIONS.md) heeft de details.
- Een tracker: een GitHub Projects-board (gratis, bij elk GitHub-abonnement) of een Linear-workspace (elk abonnement)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Een Claude-secret voor de reviewer-agents in CI: een token van een Claude-abonnement (`claude setup-token`) of een Anthropic API-sleutel (op basis van verbruik; stel een uitgavelimiet in)
- Een van de ondersteunde coding agents

## Opbouw van de repository

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

## Versiebeheer

HAAM volgt [semantic versioning](https://semver.org):
- **Patch** (1.0.x): fixes en formuleringen; `update` past ze zonder conflicten toe.
- **Minor** (1.x.0): nieuwe skills, checks of docs; achterwaarts compatibel.
- **Major** (x.0.0): wijzigingen die een migratiestap vragen (bijv. hernoemde Linear-statussen of verplichte checks). De [CHANGELOG](CHANGELOG.md) noemt de stappen.

Installeer altijd vanaf een tag of release, niet vanaf `main`.

## Bijdragen

Ideeën, bugmeldingen en pull requests zijn welkom. Zie [CONTRIBUTING.md](CONTRIBUTING.md). Beveiligingsproblemen: zie [SECURITY.md](SECURITY.md).

## Licentie

[MIT](LICENSE) © 2026 Jorge del Prado
