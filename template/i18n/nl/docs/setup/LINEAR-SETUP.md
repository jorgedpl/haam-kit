# Linear opzetten (eenmalig, ~30 minuten, workspace-admin)

> **Alleen als je tracker Linear is** (`"tracker": "linear"` in `haam.config.json`). Gebruik je GitHub Projects? Voer dan `python3 tools/haam/haam.py github-project` uit en zie `docs/process/TRACKER.md`.

Hiermee configureer je Linear zodat het overeenkomt met `docs/process/LIFECYCLE.md`. Doe het één keer; daarna gebruikt elke developer en elke agent dezelfde structuur.

> **Geautomatiseerd:** de secties 1–4 worden gedaan door `python3 tools/haam/haam.py linear --apply`, dat je zelf in je eigen terminal uitvoert (het vraagt veilig om je persoonlijke Linear API-sleutel en slaat die nooit op). Deze pagina is het handmatige alternatief, plus de secties 5–9, die alleen in de webapp van Linear bestaan.

## 1. Team
- Maak een team aan (of hergebruik er een) met de naam van je product en een korte identifier (de voorbeelden gebruiken **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` vervangt `APP` in elk HAAM-bestand.
- Nodig elke menselijke bijdrager uit met een eigen Linear-account. Agents werken als de mens die ze draait, dus er zijn geen aparte plekken voor agents nodig.

## 2. Workflowstatussen
Team settings → **Workflow**. Maak deze aan, in deze volgorde, in de aangegeven categorie:

| Status | Categorie | Opmerkingen |
|---|---|---|
| Triage | Triage | Zet Triage aan voor het team |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Markeer als standaard voor nieuwe issues buiten triage |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Verwijder of hernoem de standaardstatussen van Linear (`Todo`, `Duplicate`, enz.), zodat alleen deze overblijven. De namen moeten precies overeenkomen; skills verwijzen er op naam naar.

## 3. Labels
Team settings → **Labels**. Maak deze labels aan (platte labels, geen groep nodig):
- `stream:idea`
- `stream:feature`
- `stream:bug`

En deze losse labels:

| Label | Betekenis | Wie zet het |
|---|---|---|
| `agent-ready` | G2 gepasseerd; agents mogen het bouwen | Agent, alleen nadat een mens de spec heeft goedgekeurd |
| `human-review` | Raakt een beschermd gebied; menselijke code review vereist | Agent of mens |
| `human-only` | Agents mogen dit niet oppakken | Mens |
| `override-followup` | Aangemaakt na een override van een gate | `/override` |
| `epic` | Parent-issue dat de sub-issues van één feature groepeert | `/triage group`, `/epic`, of een mens |
| `uat-failed` | Gezakt voor de test van de mens; agents werken het als eerste bij | `/test`, `/uat-result` |
| `uat:skip` | De product owner heeft besloten: geen eigen test | `/triage`, of "spec approved, no UAT" |
| `claimed` | Een agent-chat is het aan het beoordelen, schrijft de spec of bouwt een prototype | De agent, terwijl hij werkt |
| `mode:prototype` | De product owner heeft besloten: eerst een wegwerpprototype bouwen (`/spike`) | `/triage` |
| `mode:epic-build` | De product owner heeft besloten: één leidende agent bouwt deze hele epic | `/decide` |
| `spike-ready` | Een prototype staat klaar voor de product owner om uit te proberen | `/spike` |

Optioneel: labels per gebied (`area:onboarding`, `area:billing`, `area:checkout`…) om het board te filteren.

## 4. Prioriteiten
Gebruik de ingebouwde prioriteit van Linear (Urgent / High / Medium / Low / No priority). Geen eigen velden nodig.

## 5. Issuetemplates
Team settings → **Templates** → maak drie issuetemplates aan en plak de inhoud uit:
- **Idea**: `docs/templates/idea.md` · standaardlabel `stream:idea` · status Triage
- **Bug**: `docs/templates/bug.md` · standaardlabel `stream:bug` · status Triage
- **Feature**: een korte tekst met een link naar de spec · standaardlabel `stream:feature` · status Backlog

Agents vullen deze zelf in via `/idea` en `/bug`; de templates zijn voor mensen die issues aanmaken in de app van Linear.

## 6. GitHub-integratie
Settings → **Integrations → GitHub** → koppel de organisatie/repo.

Daarna in team settings → **Workflow → Pull request automations** (de formulering kan iets afwijken):

| GitHub-event | Issue verplaatsen naar |
|---|---|
| Branch aangemaakt / draft-PR geopend | In Progress |
| PR klaar voor review (agents openen drafts en zetten ze op ready als ze compleet zijn) | In Review |
| PR klaar om te mergen | *(geen wijziging, agents zetten het op UAT)* |
| PR gemerged | Deploying |

**Formaat voor branchnamen:** `{issue-identifier}-{issue-title}` (kleine letters), bijv. `app-123-bulk-invite-users`. Haal het voorvoegsel met de gebruikersnaam weg, zodat branches hetzelfde zijn, wie ze ook aanmaakt.

Zet **"link PRs by issue ID in title"** aan, zodat PR-titels als `APP-123: ...` automatisch gekoppeld worden.

## 7. Weergaven (opgeslagen filters)
Maak deze teamweergaven aan, zodat mensen zien wat er op hen wacht:

| Weergave | Filter |
|---|---|
| **Triage** | De ingebouwde Triage-inbox van Linear (de dagelijkse inbox van de product owner; zie `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Status in (Decision, UAT), plus Backlog-issues met een commentaar `📝 Spec ready for review` |
| **Agent queue** | Status = Ready, label `agent-ready` of `stream:bug`, niet toegewezen |
| **Ideas inbox** | Status in (Triage, Discovery), label `stream:idea` |
| **Bugs** | Label `stream:bug`, niet Done/Canceled, gesorteerd op prioriteit |
| **Epics** | Label `epic`, niet Done/Canceled (toon de voortgang van de sub-issues) |
| **Overrides to close** | Label `override-followup`, niet Done |

## 8. Meldingen
Iedereen: Settings → Notifications → zorg dat je meldingen krijgt bij **mentions** en **issues die aan jou zijn toegewezen**. `/uat` noemt de product owner als er iets klaarstaat om te testen.

## 9. De agent-tool van iedereen aan Linear koppelen
Iedereen logt één keer in vanuit de eigen tool (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Stappen per tool: `docs/setup/AGENTS-SETUP.md`.
Test: vraag de agent *"toon mijn openstaande Linear-issues in team APP"*.

Als je ook een chatapp gebruikt (Claude, ChatGPT…) met een Linear-connector, koppel die dan ook, zodat je vanaf je telefoon ideeën kunt vastleggen.
