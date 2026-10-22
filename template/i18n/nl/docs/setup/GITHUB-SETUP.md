# GitHub opzetten (eenmalig, ~30 minuten, repo-admin)

Hiermee worden de gates G3–G5 van afspraken omgezet in regels die GitHub afdwingt.

> **Geautomatiseerd:** labels (§1), branchregels (§2), de productie-environment (§4) en de security-functies (§3b–c) worden gedaan door `python3 tools/haam/haam.py github --apply` (eerst het plan, zonder `--apply`). Deze pagina is het handmatige alternatief, plus de stappen die GitHub alleen in de browser aanbiedt. De secret voor de reviewer voeg je altijd zelf toe: `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (token uit `claude setup-token`, je Claude-abonnement) of `gh secret set ANTHROPIC_API_KEY -R owner/repo` (API-sleutel, gefactureerd per review). Met een van beide draaien beide reviews.

## 1. Labels
Maak deze labels in de repository aan (Issues → Labels), of voer uit:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Branchbescherming op `main`
Settings → **Rules → Rulesets** → New branch ruleset (of de klassieke Branch protection), doel `main`:

- ✅ Verwijderen beperken; force pushes blokkeren
- ✅ Een pull request vereisen vóór het mergen
  - Vereiste goedkeuringen: **1** zodra er een tweede mens is; **0** zolang je alleen bent (het UAT-label is je goedkeuring)
  - ✅ Verouderde goedkeuringen intrekken als er nieuwe commits worden gepusht
- ✅ Vereisen dat statuschecks slagen (laat "require branches to be up to date" uit: dat draait na elke merge CI opnieuw op elke open PR)
  - Verplichte checks: **`ci`**, **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** en **`release-gate`** (ze verschijnen in de lijst nadat de workflows één keer op een PR hebben gedraaid)
- ✅ Lineaire geschiedenis vereisen (optioneel, houdt de geschiedenis netjes)
- **Bypass-lijst:** alleen repository-admins, **alleen voor pull requests** (nooit "always": agents werken onder de login van een mens, vaak die van een admin, en zouden anders direct naar `main` kunnen pushen). Dit is de noodomzeiling van niveau 2 in `docs/process/GATES.md`.

**Auto-merge** (Settings → General → Pull Requests → *Allow auto-merge*; `haam.py github --apply` zet het aan): alleen gebruikt door de route zonder UAT, voor PR's waarvan je de issues met `uat:skip` hebt gemarkeerd. De gate zet het voor zo'n PR aan met de secret `HAAM_PROJECT_TOKEN` (`docs/process/TRACKER.md`), en GitHub merget pas als elke verplichte check slaagt. Als je goedkeuringen vereist, wacht de route ook op een goedkeuring.

## 3. Code review en security

### 3a. Een Claude-secret voor de reviewer-agents
De onafhankelijke reviewers (`.github/workflows/review.yml`) draaien Claude in GitHub Actions. Eén repository-secret draait beide reviews (Settings → **Secrets and variables → Actions** → New repository secret). Kies een van deze:
- **`CLAUDE_CODE_OAUTH_TOKEN`:** voer `claude setup-token` uit en gebruik de token die het toont. De reviews worden dan afgeschreven van dat Claude-abonnement.
- **`ANTHROPIC_API_KEY`:** een aparte API-sleutel voor deze repo van console.anthropic.com, met een maandelijkse uitgavelimiet. Er wordt per review gefactureerd, los van ieders Claude-abonnement. Hiermee gebruikt de security review de security-review-action van Anthropic.

Draft-PR's en PR's met alleen docs roepen Claude niet aan. De instructies voor de review staan in `.github/review/REVIEWER.md` en `SECURITY-REVIEWER.md`, en worden altijd van `main` gelezen. Stel ze bij naarmate je meer leert.

### 3b. Secret scanning en push protection
Settings → **Security** (Code security / Advanced Security, afhankelijk van je abonnement):
- ✅ **Secret scanning**, ✅ **Push protection**: GitHub weigert pushes die bekende formaten van secrets bevatten.
- Gratis voor publieke repositories. Voor private repositories kan de betaalde security-add-on van GitHub nodig zijn; als je die niet hebt, ben je nog steeds gedekt door de eigen check `secrets` van de kit (gitleaks) en de lokale hooks.

### 3c. Meldingen over dependencies
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Haal daarna het commentaar weg bij je ecosysteem in `.github/dependabot.yml`. PR's van Dependabot gaan door dezelfde gates.

### 3d. Pull requests vanuit forks
Settings → **Actions → General** → *Fork pull request workflows*: goedkeuring vereisen voor alle externe bijdragers. (PR's vanuit forks krijgen geen repository-secrets, dus AI-reviews kunnen er niet op draaien; een mens reviewt en overrulet als dat nodig is.)

## 4. Productie-environment (Gate G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** de product owner (+ één vervanger als je die hebt)
- ✅ Prevent self-review: laat dit **uit** zolang jij de enige goedkeurder bent, zet het later aan
- **Deployment branches and tags:** geselecteerde branches → alleen `main`
- **Environment secrets:** inloggegevens voor de productiedeploy horen hier en nergens anders
- **Environment variables:** `PRODUCTION_URL` (gebruikt door de smoke test)

Nu draait elke merge naar `main` `deploy.yml`, dat pauzeert bij *deploy-production* tot een goedkeurder op **Review deployments → Approve** klikt. GitHub stuurt de goedkeurders een e-mail of melding.

Required reviewers werken op publieke repositories bij elk abonnement, maar op private repositories alleen met GitHub Enterprise Cloud. Zonder required reviewers starten deploys bij de merge, en is jouw `ship` de releasebeslissing: stel `deploy_approval: automatic` in met `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (optioneel, maar aanbevolen zodra er twee mensen zijn)
`.github/CODEOWNERS`:
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Zet daarna "Require review from Code Owners" aan in de ruleset.

## 6. Het commandocontract invullen
Bewerk `Makefile` (inclusief `audit`) en de runtime-stappen in `.github/workflows/ci.yml`, `security.yml` en `deploy.yml` (zoek naar `TODO(setup)`). Open een PR. De check `ci` moet op die PR groen worden voordat je de verplichte checks aanzet.

## 7. Optioneel: de Claude GitHub-app
Als je een agent op een PR wilt taggen voor een snelle fix (bijv. de Claude GitHub-app via `/install-github-app` in Claude Code, of de GitHub-integratie van je andere tool), installeer die dan. Elke zo'n app is gebonden aan dezelfde branchbescherming en checks, dus kan de gates niet omzeilen.

## 8. Actions-minuten beperken

Private repositories krijgen een maandelijks tegoed aan Actions-minuten; agents die veel PR's openen, verbruiken dat snel. Wat de kit al doet: standaard (test-first) pushen agents branches zonder PR's te openen, en een PR wordt pas geopend nadat jij de wijziging hebt getest en goedgekeurd, dus de checks draaien één keer op geteste code (checks-first-projecten: draft-PR's draaien niets, en agents zetten een PR één keer op ready, als hij compleet is); PR's met alleen docs slaan de checks over; `main` wordt 's nachts gecontroleerd in plaats van na elke merge; labels, commentaar en nieuwe issues starten geen runners; agents houden nieuw werk tegen bij 10 open PR's of 10 wijzigingen die op je test wachten (`max_open_prs`, `max_in_uat`).

Zoek uit waar de minuten naartoe gaan: `python3 tools/haam/haam.py ci-usage` (laatste 7 dagen, per workflow, job, trigger en dag).

Twee instellingen in de tabel hieronder besparen minuten met weinig nadelen. Wijzig ze met `/haam-settings`, of `python3 tools/haam/haam.py settings --set … --apply --human`; ze worden repositoryvariabelen die de workflows lezen. De andere (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) besparen meer: zie `settings --explain`.

| Schakelaar | Wat er verandert | Afweging |
|---|---|---|
| `--review local` | De twee AI-reviews draaien op je computer in nieuwe Claude-sessies (`haam.py review`), met je Claude-abonnement in plaats van Actions-minuten. PR's met het label `human-review` worden nog steeds op GitHub gereviewd | Het resultaat is niet langer bestand tegen manipulatie: de bouwende agent start de review (nieuwe, alleen-lezen sessies, instructies van `main`), en alles wat jouw login gebruikt, zou een geslaagd resultaat kunnen posten. Voer `haam.py review` uit vanuit je eigen chat voor meer scheiding |
| `--runner self-hosted` | Alle jobs behalve de deploy draaien op je eigen machine (geregistreerd onder Settings → Actions → Runners) in plaats van op die van GitHub | De machine moet aan staan, met git, make, Python 3, curl, gitleaks en de tools van je project; alleen private repositories. Bekijk de actuele prijzen van GitHub voor self-hosted runners |

Ook de moeite waard om te controleren: jobs op macOS-runners tellen 10 minuten voor elke minuut die ze draaien (Windows: 2). Draai mobiele builds alleen als de mobiele code veranderd is (`make check` krijgt de gewijzigde bestanden in `$CI_CHANGED_FILES`), of 's nachts.

## 9. Controleren of het werkt
1. Open een piepkleine test-PR (bijv. een typfout in code verbeteren). `ci`, `secrets` en `dependencies` draaien; de reviewer-agent plaatst een commentaar en `ai-review` / `security-review` melden hun resultaat; `release-gate` toont **failure: waiting for UAT**.
   - **Secret-test:** commit op een wegwerpbranch een nepsleutel in AWS-stijl, zoals `AKIA` gevolgd door 16 hoofdletters/cijfers, in een codebestand. De lokale hook moet de commit blokkeren; als je die omzeilt met `--no-verify`, moet de check `secrets` falen. Verwijder de branch daarna.
2. Voeg het label `uat-passed` toe → `release-gate` wordt groen → mergen is toegestaan.
3. Na de merge toont Actions → Deploy **Waiting for review** bij `deploy-production`.
4. Open een PR met alleen docs → `release-gate` slaagt automatisch.
