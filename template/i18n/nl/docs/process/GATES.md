# Gates en overrides

Tussen een idee en productie staan vijf gates. Elke gate heeft een duidelijke eigenaar, een checklist en, waar mogelijk, een geautomatiseerd handhavingspunt, zodat de regel er niet van afhangt dat iemand eraan denkt.

| Gate | Tussen | Eigenaar | Afgedwongen door |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Mens (PO) | Status in de tracker: alleen mensen voeren `/decide` uit |
| **G2 Ready** | Backlog → Ready | Mens keurt de spec goed | Label `agent-ready`; agents bouwen alleen issues met `agent-ready` |
| **G3 Verified** | In Progress → UAT | Geautomatiseerde checks + onafhankelijke reviewer-agent (+ mens voor beschermde gebieden) | Verplichte checks `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → merge | Menselijke tester | Verplichte check `release-gate` (vereist het PR-label `uat-passed` of `gate-override`) |
| **G5 Released** | merge → productie | Mens (PO) | GitHub-environment `production` met verplichte reviewer |

De tabel toont de volgorde van checks-first. In de standaardflow test-first komt G4 vóór G3: je test eerst de branch van de agent, en daarna draaien de checks één keer op wat je hebt goedgekeurd (zie de checklist van G4).

---

## Checklist voor G1 Decision

De beoordeling (of, voor een idee dat als prototype is gebouwd, de notities bij het prototype uit `/spike`) moet bevatten:
- [ ] Probleemstelling en voor wie het is
- [ ] Schatting van de waarde met bewijs (of expliciet "nog geen bewijs")
- [ ] Omvang van de inspanning met onderbouwing vanuit de codebase
- [ ] Risico's: security, gegevensbescherming (bijv. AVG/GDPR), regelgeving, operationeel
- [ ] Minstens twee opties plus "niets doen"
- [ ] Een aanbeveling

De mens antwoordt met een van deze: **approve** (met prioriteit), **park** (met een aanleiding om er later op terug te komen), **reject** (met reden). Bij een prototype probeert de mens het eerst uit (`/test`), zodat de beslissing berust op het gebruik ervan en niet op erover lezen.

## G2 Definition of Ready

Een issue mag `agent-ready` alleen krijgen als:
- [ ] De spec bestaat in `docs/specs/` en vanuit het issue gelinkt is
- [ ] Acceptatiecriteria geschreven zijn als Given / When / Then en elk ervan testbaar is
- [ ] Scope en **buiten scope** expliciet zijn
- [ ] Bestanden/modules die waarschijnlijk geraakt worden, zijn opgesomd
- [ ] De impact op data, migraties en config vermeld is (of "geen")
- [ ] Een plan voor unittests en een UAT-schets erin staan
- [ ] De omvang ≤ 1 dag agentwerk is (~400 gewijzigde regels); anders opsplitsen in sub-issues
- [ ] Geraakte beschermde gebieden gemarkeerd zijn (label `human-review` toegevoegd)
- [ ] De prioriteit ingesteld is
- [ ] Een mens de spec heeft goedgekeurd

## G3 Verified (Definition of Done voor code)

- [ ] Elk acceptatiecriterium heeft minstens één geautomatiseerde test
- [ ] `make check` slaagt lokaal en in CI (lint, types, unittests, build)
- [ ] Geen wijzigingen in de diff die er niets mee te maken hebben
- [ ] Docs die door de wijziging geraakt worden, zijn bijgewerkt (`ARCHITECTURE.md`, API-docs, lijst met omgevingsvariabelen)
- [ ] Geen secrets, geen echte persoonsgegevens in code, tests of fixtures
- [ ] De PR-beschrijving volgt de template en linkt het issue (`Refs #123` op GitHub Projects, het ID in de titel op Linear)
- [ ] Check `secrets` groen: geen sleutels, tokens of wachtwoorden in welke commit van de PR ook
- [ ] Check `dependencies` groen: geen bekende kwetsbaarheden van niveau high/critical
- [ ] `ai-review` groen: de onafhankelijke reviewer-agent vond geen blokkerende problemen
- [ ] `security-review` groen: de security review van Claude vond geen kwetsbaarheden
- [ ] Menselijke code review gedaan als het label `human-review` aanwezig is

### Hoe code review werkt

De review bestaat uit lagen, zodat **geen enkele agent ooit zijn eigen werk reviewt** en **secrets worden opgevangen door deterministische tools, niet door een oordeel**.

| Laag | Wanneer | Wat | Wie / wat doet het |
|---|---|---|---|
| 1. Lokale secret-bewaking | Voor elke commit | Blokkeert commits met sleutels/tokens | gitleaks via de git pre-commit-hook (iedereen, elke tool), plus hooks van de agent-tool waar dat kan (Claude Code; Grok) |
| 2. Zelfcontrole | Voordat er een PR wordt geopend | `make check` + `/security-review` op de eigen wijzigingen | De bouwende agent |
| 3. Deterministische CI | Elke push naar een PR | Tests, lint, types, secret-scan van elke commit, dependency-audit | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Onafhankelijke AI-review | Elke push naar een PR (niet bij drafts of PR's met alleen docs) | Overeenstemming met de spec, eerlijke tests, correctheid, projectregels; beveiligingskwetsbaarheden | Een aparte Claude in GitHub Actions die de code nooit heeft zien schrijven (`ai-review`, `security-review`) |
| 5. Menselijke review | PR's met het label `human-review` | Beschermde gebieden: kernlogica, auth, betalingen, persoonsgegevens, migraties, infra | Product owner of een aangewezen developer |
| 6. Menselijke acceptatie | Elke PR met code | Het gedrag werkt echt (G4 UAT) | Product owner |

**Regels voor de reviewcyclus**
- De bouwende agent leest het commentaar van de reviewer, lost elk **Blocking**-item op en pusht; de reviews draaien automatisch opnieuw.
- Als de bouwende agent vindt dat een bevinding niet klopt, antwoordt hij op de PR met uitleg waarom en vraagt hij het de mens. Hij blijft nooit in cirkels discussiëren: **na twee reviewrondes** die nog steeds falen, stopt hij en draagt hij het over aan de mens.
- Alleen een mens kan een AI-review overrulen, met het PR-label `ai-review-overruled`. Dit wordt op de PR vastgelegd.
- AI-reviewers kunnen niet goedkeuren of mergen. Ze kunnen alleen blokkeren.

### Als er ooit een secret op GitHub belandt
1. **Trek hem direct in en vervang hem** bij de provider. Ga ervan uit dat hij gecompromitteerd is; hem uit de code halen maakt het lek niet ongedaan.
2. Haal hem uit de code; gebruik een omgevingsvariabele die in `.env.example` gedocumenteerd is.
3. Een repo-admin herschrijft de geschiedenis van de branch vóór de merge (een nieuwe commit is niet genoeg).
4. Maak een `/bug` aan met prioriteit Urgent om vast te leggen wat er gebeurd is en wat er vervangen is (zet de secret zelf er nooit in).

**De instellingen van de product owner veranderen hoe G3 draait, niet wie er beslist** (`/haam-settings`):
- `ci`: bij elke PR, lokaal (`ci-local`, gepost door `haam.py local-ci` op de computer van de product owner), of uit.
- `review`: GitHub, lokaal, alleen beschermde gebieden, of uit.
- `nightly`.

De verplichte checks volgen de instellingen (`settings --apply`). De secret-scan draait altijd.

## G4 Accepted (UAT)

In de standaardflow test-first komt G4 vóór G3: de product owner test de gepushte branch van de agent voordat er een PR bestaat, en G3 controleert daarna precies de commit die is goedgekeurd (`haam.py publish`, daarna `ship`, dat al het andere weigert).

**Route zonder UAT:** G4 wordt dan vooraf beslist. Als de product owner een issue markeert met `uat:skip` (in `/triage`, of "spec approved, no UAT"), opent de agent de PR met hetzelfde label en slaagt `release-gate` zodra elk issue waarvoor de PR is dat label heeft (GitHub Projects: de gate leest de issues; Linear: hij vertrouwt het label van de PR). Nooit als de PR een beschermd gebied wijzigt: de gate vergelijkt de gewijzigde bestanden met `protected_paths` in `haam.config.json` op `main` (standaard de configuratie van agents en CI, plus die van het project zelf), voegt `human-review` toe en houdt de route dicht, wat de labels ook zeggen. Een update van de kit gaat dus nooit via deze route: die wijzigt de configuratie van agents, en die review en zet je zelf live. G3 geldt nog steeds volledig, en auto-merge (vereist `HAAM_PROJECT_TOKEN`) merget alleen als elke verplichte check slaagt. Er is geen auto-merge op Linear, en ook niet als CI of een van de AI-reviews ergens anders draait dan op GitHub bij elke PR (auto-merge vereist `ci: every-pr` en `review: github`): lokale resultaten zijn niet bestand tegen manipulatie en beperkte checks zijn op zichzelf niet genoeg, dus de product owner zet die PR's van de route zelf live (`ship`), en dat blijft één beslissing voor vele. Alleen een beslissing van een mens voegt `uat:skip` toe aan een issue (`issue create` en `issue label` weigeren het zonder `--human`).

- [ ] Het UAT-plan bestaat in `docs/uat/` met genummerde stappen en verwachte resultaten
- [ ] Een mens heeft het lokaal op de branch uitgevoerd (test-first: de gepushte branch van de agent, vóór elke PR; checks-first: de branch van de PR)
- [ ] Alle stappen slagen, of fouten zijn vastgelegd en geaccepteerd als vervolgissues
- [ ] De goedkeuring van de mens (`/test` of `/uat-result <ID> pass`) voegt het label `uat-passed` toe aan de PR (test-first: `publish` legt het ook vast op de geteste commit als de status `uat`)
- [ ] De goedkeuring dekt de code die gemerged wordt: een push daarna verwijdert `uat-passed` (`gates.yml`), tenzij de nieuwe head de geteste commit is; `ship` merget alleen die commit

## G5 Released

- [ ] PR naar `main` gemerged door een mens, of door `haam.py ship --human` nadat de mens `ship` zei
- [ ] Productiedeploy goedgekeurd (environment `production`): in GitHub, of door `ship` op het woord van de mens
- [ ] Smoke check na de deploy geslaagd (`make smoke`, als die bestaat)
- [ ] Het issue staat op Done (`ship`, of `/release` voor wijzigingen die op een andere manier gemerged zijn); de release note in `docs/changes/` ging mee

---

## Overrides

Soms staat productie in brand of wacht een deadline niet. Daarvoor zijn overrides, en die zijn **alleen voor mensen**.

### Niveau 1: UAT overslaan (meest voorkomend)
Gebruik dit als de fix dringend is en door tests geverifieerd, maar er geen tijd is voor een volledige UAT-cyclus.

1. De mens voert `/override <ID> "<reason>"` uit (voor een PR zonder issue: `/override PR <number> "<reason>"`), of plaatst met de hand het commentaar `OVERRIDE: <reason>` op de PR (het commentaar moet beginnen met `OVERRIDE:`) en voegt het PR-label `gate-override` toe.
2. De check `release-gate` slaagt op het override-label.
3. CI (check `ci`) **moet nog steeds slagen**.
4. Als de PR een issue heeft, maakt de agent een vervolgissue aan in de tracker: `Post-override UAT for <ID>` (prioriteit High, label `stream:bug`, `override-followup`), zodat de overgeslagen verificatie achteraf toch gebeurt.

### Niveau 2: noodomzeiling (zeldzaam)
Gebruik dit alleen als CI zelf kapot is of een fix voor productie blokkeert.

1. Een admin van de repository merget met "bypass branch protections" in GitHub.
2. De admin plaatst het commentaar `EMERGENCY BYPASS: <reason>` op de PR.
3. Er wordt een vervolgissue aangemaakt zoals hierboven, plus een tweede om op te lossen wat CI blokkeerde.

### Regels voor overrides
- Agents voegen **nooit** `gate-override` toe, omzeilen nooit beschermingen en stellen nooit een override voor, tenzij de mens er zelf over begint.
- Elke override moet een geschreven reden op de PR hebben.
- Overrides worden besproken bij de wekelijkse backlog-review: filter de tracker op het label `override-followup`.
