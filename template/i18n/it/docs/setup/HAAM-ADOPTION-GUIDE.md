# Human-Agent Agile Methodology (HAAM)
## Guida all'adozione per l'amministratore del progetto

HAAM è un modo di costruire software in cui **le persone decidono e gli agenti eseguono**. Ogni lavoro va dall'idea alla produzione passando per le stesse fasi, con gate umani nei punti che contano. Tutto vive in **Git** (conoscenza e codice) e nel **tracker** (lavoro e stato): una board di **GitHub Projects** (gratuita) o **Linear**. Le persone possono usare agenti di coding diversi (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) con i propri account e lavorare comunque in parallelo.

Questa guida applica HAAM a un repository esistente in **sei fasi, circa mezza giornata in tutto**. Puoi fermarti dopo qualsiasi fase e avere comunque qualcosa di utile.

---

## Ottenere il kit

Il kit è la cartella `template/` di https://github.com/jorgedpl/haam-kit. Usa sempre una versione rilasciata:
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
oppure scarica lo zip dalla pagina Releases. Più avanti, `<path-to-kit>` indica quella cartella `template/`.

## La strada veloce: lascia fare al tuo agente

Metti il kit in un posto qualsiasi fuori dal tuo progetto, apri il tuo agente di coding **nella cartella principale del progetto** e scrivi:

> Leggi `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` e seguilo per configurare HAAM in questo repository. Il kit si trova in `<path-to-kit>`.

L'agente guida lo strumento di setup (`tools/haam/haam.py`) attraverso tutte le fasi descritte sotto. Ti fa un pugno di domande, ti mostra ogni modifica prima di farla e ti passa i pochi passi che richiedono le tue password o chiavi, da eseguire nel tuo terminale. Usa il resto di questa guida per capire cosa sta facendo, o per farlo a mano.

### Chi fa cosa durante il setup

| Indicato come | Significa |
|---|---|
| `[agent]` | Lo fa il tuo agente di coding (o tu, se lo fai a mano) |
| `[YOU, in your terminal]` | Esegui tu il comando: coinvolge un secret (chiave API, login) che non deve mai passare dalla chat di un agente |
| `[YOU, in the browser]` | Un'impostazione che GitHub o Linear offrono solo nella loro app web |

---

## Cosa ottieni

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

### Il ciclo di vita in un'immagine

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### I comandi

Qui sono scritti `/name` (Claude Code, Cursor, Grok). In Codex usa `$name`. Con qualsiasi altro strumento: *"segui `.agents/skills/<name>/SKILL.md`"*.

| Comando | Fase | Chi |
|---|---|---|
| `/idea <text>` | Raccogliere un'idea | Chiunque |
| `/bug <text>` | Segnalare un problema | Chiunque |
| `/assess APP-12` | Valutare valore, sforzo, rischio, fattibilità | Agente |
| `/triage` | Fare il triage della casella, raggruppare le issue in epic (`group`), riordinare (`backlog`), sollecitare il lavoro fermo (`stale`) | Solo persone |
| `/epic APP-9` | Definire un'epic: brief, domande per te, pulizia delle sue issue | Solo persone |
| `/decide APP-12 approve` | Gate G1 | Solo persone |
| `/spec APP-12` | Scrivere una specifica pronta per la build | Agente |
| `/work bugs` | Avviare un agente in una nuova finestra di chat: worktree proprio, poi `/next` | Chiunque |
| `/next` | Scegliere il prossimo elemento tra bug, feature e idee | Agente |
| `/build APP-12` | Implementare con gli unit test, aprire una PR | Agente |
| `/uat APP-12` | Scrivere il tuo piano di test in locale | Agente |
| `/test` | Testare una modifica, poi `pass` → `ship`, oppure dire cosa non va (G4 e G5) | Solo persone |
| `/uat-result APP-12 pass` | Registrare solo un risultato di test (G4) | Solo persone |
| `/override APP-12 "reason"` | Saltare la UAT in un'emergenza | Solo persone |
| `/release APP-12` | Chiudere dopo il deploy | Solo persone |
| `/haam-setup` | Adottare HAAM in un repo | Amministratore del progetto |
| `/haam-onboard` | Preparare un nuovo sviluppatore | Nuovo sviluppatore |
| `/haam-update` | Aggiornare a una nuova versione del kit | Amministratore del progetto |

### Come funziona la code review

Nessun agente rivede mai il proprio lavoro, e i secret vengono intercettati da uno scanner invece che dal giudizio. Ogni modifica passa per sei livelli:

| Livello | Quando | Cosa controlla | Chi lo fa |
|---|---|---|---|
| 1. Protezione locale dai secret | Prima di ogni commit | Chiavi, token, password nelle modifiche; se ne trova, il commit viene bloccato | gitleaks tramite l'hook git (tutti), più gli hook degli strumenti agente dove supportati |
| 2. Autocontrollo | Prima di aprire una PR | I test passano; revisione di sicurezza del proprio diff | L'agente che l'ha costruita |
| 3. CI automatica | A ogni aggiornamento della PR | Test, lint, tipi (`ci`); secret in ogni commit (`secrets`); librerie vulnerabili (`dependencies`) | GitHub Actions |
| 4. Revisione AI indipendente | A ogni aggiornamento della PR (non bozze né sola documentazione) | Rispetta la specifica? Test onesti? Bug, ambito che si allarga, regole violate (`ai-review`). Vulnerabilità di sicurezza (`security-review`) | Un Claude separato in GitHub Actions che non ha mai visto scrivere il codice (un modello diverso quando il codice viene da un altro strumento) |
| 5. Code review umana | PR che toccano aree protette | Logica principale, autenticazione, pagamenti, dati personali, migrazioni, infrastruttura, configurazione degli agenti | Il product owner o uno sviluppatore designato |
| 6. Accettazione umana | Ogni PR di codice | Funziona davvero (UAT del Gate G4) | Il product owner |

- Il revisore pubblica un commento con **Blocking / Should fix / Nits**. I rilievi bloccanti fermano il merge.
- L'agente che costruisce corregge gli elementi Blocking e fa push; le revisioni ripartono automaticamente. Se non è d'accordo, risponde sulla PR e chiede a una persona. Dopo **due** giri falliti si ferma e passa la mano.
- I revisori AI possono bloccare, ma non approvano né fanno il merge. Solo una persona può scavalcarli, con l'etichetta di PR `ai-review-overruled`.
- Se un secret vero arriva mai su GitHub: revocalo e ruotalo subito, poi fai riscrivere la storia del branch a un amministratore. Cancellarlo in un nuovo commit non basta.

Tutte le regole: `docs/process/GATES.md`. Le istruzioni del revisore, che puoi regolare: `.github/review/REVIEWER.md`.

---

## Prima di iniziare

Ti serve:
- [ ] Accesso da amministratore al repository GitHub. Se è privato, le regole sui branch richiedono GitHub Pro o Team, e un approvatore sui deploy in produzione richiede Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Un tracker: **GitHub Projects** (niente di aggiuntivo; gratuito su ogni piano) o accesso da amministratore a un workspace **Linear**
- [ ] Un agente di coding installato e con login fatto, con il tuo account
- [ ] Python 3, Git, Make e la GitHub CLI con login fatto (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, o dalla sua pagina delle release su GitHub)
- [ ] Un secret Claude per gli agenti revisori: un token di un piano Claude (`claude setup-token`) o una chiave API di Anthropic con un limite di spesa mensile (console.anthropic.com)
- [ ] Il tuo progetto oggi gira in locale

Decidi adesso:
1. **Tracker:** GitHub Projects (gratuito, tutto in GitHub) o Linear (più piacevole da usare, piano gratuito limitato). Puoi cambiare in seguito.
2. **Chiave del prodotto:** un codice breve, ad es. `ACM`, `SHOP`, `CRM` (la chiave del team Linear se usi Linear). Il kit usa `APP` come segnaposto finché `config` non lo sostituisce ovunque.
3. **Product owner:** l'unica persona che approva idee, specifiche, UAT e deploy (più un approvatore di riserva facoltativo).
4. **Strumenti agente** che userà il tuo team.

Verifica la tua macchina in qualsiasi momento con: `python3 <kit>/tools/haam/haam.py dev`

---

## Fase 1: Installare il kit (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

La documentazione è in inglese, a meno che tu non aggiunga `--language es` (oppure `fr`, `de`, `it`, `nl`, `pt`) a entrambi i comandi. Allora anche gli agenti scrivono in quella lingua specifiche, issue, piani di UAT e messaggi; comandi, etichette e codice restano in inglese. Puoi cambiarla in seguito con `haam.py config --language <code>`, poi con `update --target . --apply` del kit.

L'installer **non sovrascrive mai** i tuoi file:
- I file nuovi vengono aggiunti.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` e `.claude/settings.json` vengono **uniti** automaticamente.
- `.gitignore` riceve un blocco HAAM aggiunto in fondo una sola volta.
- Qualsiasi altro file che hai già resta com'è, e la versione del kit viene salvata in `.haam/incoming/` perché tu (o l'agente) faccia il merge.

Come risolvere i conflitti più comuni:

| Se il tuo repo ha già… | Fai così |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Sposta le conoscenze specifiche del progetto (convenzioni, insidie, comandi) in `docs/product/ARCHITECTURE.md` o in una sezione "Project specifics" alla fine di `AGENTS.md`. Poi usa `AGENTS.md` e `CLAUDE.md` del kit. Tieni le regole `.mdc` di Cursor solo per i dettagli limitati a certi glob |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` sposta le tue skill in `.agents/skills/` e collega la cartella. Prima rinomina quelle che si scontrano con i nomi delle skill di HAAM |
| `Makefile` | Aggiungi i target del kit ai tuoi |
| `.github/workflows/` con la CI | Tieni la tua CI, ma assicurati che un job chiamato **`ci`** esegua tutta la tua suite di test sulle PR. Aggiungi `gates.yml`, `security.yml`, `review.yml`. Confronta il tuo deploy con `deploy.yml` (Fase 4) |
| `.github/pull_request_template.md` | Unisci "Realizzato con (Built with)", "Criteri di accettazione → test" e "Checklist (G3)" |
| `.pre-commit-config.yaml` o Husky | Tienilo e richiama `scripts/scan-secrets.sh` da lì invece di usare `.githooks/` |
| `CHANGELOG.md`, `.github/dependabot.yml` | Tieni i tuoi (aggiungi l'ecosistema `github-actions` a Dependabot se manca) |

Cancella `.haam/incoming/` quando hai finito.

---

## Fase 2: Configurare e insegnargli il tuo progetto (45 min)

1. **Impostazioni del progetto** `[agent]` (con le tue risposte):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Questo scrive `haam.config.json` e sostituisce il segnaposto `APP` e il nome del prodotto in ogni file di HAAM.

2. **Strumenti agente** `[agent]`: `python3 tools/haam/haam.py agents --apply`. Collega le skill condivise per Claude Code e Grok, verifica i file di Cursor/Codex/Gemini/Copilot ed elenca gli eventuali passi per persona. Dettagli: `docs/setup/AGENTS-SETUP.md`.

3. **Contratto dei comandi** `[agent]`: compila ogni `TODO(setup)` nel `Makefile` (setup, dev, test, lint, typecheck, build, audit) e i passi del runtime nei workflow, a partire dai comandi reali del tuo progetto. Poi `make check` deve passare sul codice attuale. Se i test falliscono già su `main`, prima correggili o segnalali: HAAM si basa sul fatto che verde significhi verde. Se `make audit` segnala vecchie vulnerabilità alte/critiche, correggile o registrale come bug e alza temporaneamente la soglia.

4. **Mappa dell'architettura** `[agent]`: compila `docs/product/ARCHITECTURE.md` a partire dal codice (meno di 150 righe) e proponi i percorsi reali per le aree protette in `AGENTS.md` §4. Tu revisioni.

5. **Contesto di prodotto** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: cos'è, utenti, percorsi che non devono mai rompersi, punti non negoziabili, priorità attuali. È ciò che ogni agente legge per prendere decisioni di giudizio.

6. **Documento di onboarding** `[agent]`: compila gli elementi `TODO(setup)` in `docs/ONBOARDING.md` (URL di clonazione, runtime, URL locale).

7. **Igiene dei secret** `[agent]`: `make hooks`, poi scansiona la storia una volta: `gitleaks git --redact -v .` Tutto ciò che è reale va **revocato e ruotato** presso il fornitore: è già esposto a chiunque abbia accesso al repo. Sei tu ad approvare le eventuali impronte di falsi positivi aggiunte a `.gitleaksignore`.

8. **Chat in parallelo** `[agent]`: elenca in `.worktreeinclude` i file solo locali di cui l'app ha bisogno (come `.env`), escludi `.claude/worktrees/` da qualsiasi strumento che scansiona l'intera cartella (test runner, linter, watcher) e prova un worktree nuovo: `python3 tools/haam/haam.py worktree new setup-check`, poi `make setup && make check` al suo interno, poi `git worktree remove .claude/worktrees/setup-check`. Da quel momento, ogni nuova chat di agente inizia con `/work`.

9. **Verifica:** `python3 tools/haam/haam.py doctor` mostra cosa resta da fare.

---

## Fase 3: Aprire la PR di adozione (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Così i controlli esistono su GitHub e possono essere resi obbligatori. Il primo commento della revisione AI comparirà su questa PR.

---

## Fase 4: I gate di GitHub (20 min)

1. **Prima il piano, poi l'applicazione** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Crea le etichette, un ruleset sul branch predefinito (PR obbligatoria, i sei controlli obbligatori, niente force push; gli admin possono aggirarlo solo facendo il merge di una PR, per le emergenze, mai facendo push su main; "up to date before merging" disattivato, per risparmiare esecuzioni di CI). Se il ruleset esiste già, aggiunge solo ciò che manca e mantiene le tue impostazioni (`--reset` lo sostituisce). Crea anche l'environment `production` con i tuoi approvatori e la variabile `PRODUCTION_URL`, e attiva secret scanning, push protection e Dependabot dove il tuo piano lo consente.
2. **Chiave del revisore** `[YOU, in your terminal]`: un solo secret fa girare entrambe le revisioni. O `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` con il token di `claude setup-token` (usa il tuo piano Claude), oppure `gh secret set ANTHROPIC_API_KEY -R owner/repo` con una chiave API dedicata (fatturata per revisione; con questa, la revisione di sicurezza usa l'action di security review di Anthropic). Entrambi i comandi chiedono il valore senza mostrarlo.
3. **PR da fork** `[YOU, in the browser]`: Settings → Actions → General → richiedi l'approvazione per i collaboratori esterni.
4. **Deploy:**
   - *Fai già il deploy da GitHub Actions?* Aggiungi `environment: production` al tuo job di deploy: basta questo per avere il Gate G5. Cancella il `deploy.yml` del kit o tienilo come riferimento.
   - *Fai il deploy in un altro modo* (l'integrazione Git di una piattaforma di hosting, a mano)? O sposti i deploy in `deploy.yml` (compila `make deploy`), oppure tieni il tuo metodo e tratti il G5 come un passo manuale: il product owner fa il deploy dopo il merge, poi esegue `/release`. Disattiva il deploy automatico al push se aggirerebbe l'approvazione.
5. **Repository privati:** le regole sui branch richiedono GitHub Pro o Team, e un approvatore sui deploy in produzione richiede Enterprise Cloud; lo strumento ti dice cosa consente il tuo piano. Senza un approvatore, la decisione di rilascio è il tuo `ship`: imposta `deploy_approval: automatic` (`docs/setup/DECISIONS.md` §1).

Dettagli ed equivalenti manuali: `docs/setup/GITHUB-SETUP.md`.

---

## Fase 5: Il tracker (20 min)

### Opzione A: GitHub Projects (gratuito)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (permette al tuo login GitHub di usare Projects).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` token di automazione, così le schede si spostano quando le PR si aprono e vanno in merge: crea un token classic su github.com/settings/tokens con gli scope `project` e `repo` (`public_repo` basta per un repository pubblico), poi `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` sulla board, crea le viste che lo strumento elenca: Board grouped by Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Prova: `python3 tools/haam/haam.py issue list`.

Gli agenti usano `python3 tools/haam/haam.py issue …` per ogni operazione sulla board (`docs/process/TRACKER.md`), quindi funziona allo stesso modo da Claude Code, Cursor, Codex, Grok o qualsiasi altro strumento.

### Opzione B: Linear
1. **Stati, etichette, team** `[YOU, in your terminal]` (serve la tua chiave API personale di Linear, che non passa mai da un agente):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Crea il team se serve, attiva il Triage, crea i 12 stati (rinominando lo stato predefinito di Linear "Todo" in "Ready") e le 14 etichette. Non cancella mai nulla; elenca gli stati in più perché tu li archivi.
2. **Impostazioni solo da browser** `[YOU, in the browser]`: collega GitHub, automazioni delle PR (PR in bozza → In Progress, PR pronta per la revisione → In Review, merge → Deploying), formato dei nomi dei branch `{issue-identifier}-{issue-title}`, viste salvate. Vedi `docs/setup/LINEAR-SETUP.md`.
3. **Collega il tuo agente** a Linear (`docs/setup/AGENTS-SETUP.md`) e prova: *"Elenca le issue del team Linear ACM."*

**Hai già un backlog?** Chiedi al tuo agente di portarlo nel tracker (le issue GitHub si possono semplicemente aggiungere alla board). Metti tutto in **Triage**, fai il triage una volta (`stream:bug`, `stream:idea`, oppure `stream:feature` + Backlog) e scrivi le specifiche solo delle prime cinque.

---

## Fase 6: Merge, ciclo di prova e persone

### Fare il merge della PR di adozione
Quando i controlli sono verdi, aggiungi tu `uat-passed` (il gate ora è attivo, quindi ci passa anche questa PR) e fai il merge. Se gli agenti revisori fanno i pignoli sul kit stesso, scavalcali con `ai-review-overruled`. Esegui `python3 tools/haam/haam.py doctor --role admin` per una verifica finale.

### Fai un ciclo completo (45–60 min)
Scegli qualcosa di piccolo e reale. Portalo una volta attraverso ogni fase:

| Passo | Scrivi | Cosa dovrebbe succedere |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Nuova issue in Triage, etichetta `stream:idea` (su GitHub: `#1`; su Linear: `ACM-1`) |
| 2 | `/assess #1` | Valutazione committata sul branch della issue (senza PR); la issue passa a Decision |
| 3 | `/decide #1 approve medium` | La issue passa a Backlog, l'etichetta diventa `stream:feature` |
| 4 | `/spec #1` | Specifica con i criteri di accettazione, sullo stesso branch |
| 5 | Leggi la specifica (link nella issue), di' all'agente "spec approved" | La issue riceve `agent-ready`, passa a Ready |
| 6 | `/build #1` | La prende in carico, crea il branch, scrive il codice e i test, si autorevisiona, scrive il piano di UAT e fa push del branch. Ancora nessuna PR (test-first, il valore predefinito) |
| 7 | `/uat #1` (lo esegue `/build`) | La issue passa a UAT; ricevi una notifica |
| 8 | `/test #1` | L'agente porta la modifica sulla tua macchina, avvia l'app e ti dà una breve checklist |
| 9 | Provala, rispondi `pass` | L'agente apre la PR con l'etichetta `uat-passed`; `ci`, `secrets`, `dependencies` e gli agenti revisori girano una volta; `release-gate` diventa verde; l'agente chiede "Lo rilascio?" |
| 10 | Rispondi `ship` | L'agente fa il merge, approva per te il deploy in produzione, aspetta e chiude la issue: Done |
| 11 | (prova una volta) `/test` su una modifica e descrivi invece un problema | Torna agli agenti con le tue note (`uat-failed`) e ritorna da te quando è corretta |

(Su Linear gli ID hanno la forma `ACM-1`.)

Poi prova una volta i casi limite: chiedi all'agente di committare una chiave finta su un branch usa e getta (`AKIA` + 16 lettere maiuscole/cifre): il commit deve essere bloccato. Poi fai fallire una UAT, e usa un override. Regola le skill in `.agents/skills/` o il processo in `docs/process/LIFECYCLE.md` dove qualcosa ti è sembrato sbagliato.

**Prova un secondo strumento agente anche nel ciclo di prova** (ad es. Cursor o Codex per il passo 6). Così confermi che le regole e le skill condivise funzionano anche al di là del tuo strumento principale.

### Aggiungere sviluppatori
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: accesso in scrittura a GitHub (non admin), accesso alla board di GitHub Projects, oppure un invito a Linear.
2. Invia loro il link al repo e le credenziali di test (password manager o link monouso, mai chat o email).
3. Aprono il proprio agente nel repo ed eseguono `/haam-onboard` (Codex: `$haam-onboard`).
4. Quando siete in due: lo strumento imposta "1 approval required" quando aggiungi approvatori di riserva (`config --backup-approvers`, poi `github --apply`), e puoi aggiungere `.github/CODEOWNERS` per le aree protette.

### Lasciare che gli agenti lavorino in modo semi-autonomo

| Livello | Come | Quando |
|---|---|---|
| **1. Supervisionato** | Scrivi `/next` o `/build`, approvi ogni push e ogni PR | Le prime 2–3 settimane |
| **2. A lotti** | 2–3 finestre di chat (con qualsiasi mix di strumenti e computer), ognuna avviata con `/work`, che le dà il suo worktree; revisioni le PR a lotti | Quando le specifiche sono affidabilmente buone |
| **3. Programmato** | Un task programmato esegue un agente headless con `/next` e si ferma alla UAT | Quando ti fidi dei gate |

A ogni livello, gli agenti si fermano ai gate umani.

### Costi di esercizio
Oltre a GitHub, Linear (se lo usi) e l'abbonamento all'agente di ciascuna persona, l'unico costo a consumo sono gli agenti revisori: due chiamate a Claude per ogni push revisionato su una PR, fatturate su `ANTHROPIC_API_KEY` o conteggiate nel tuo piano Claude (`CLAUDE_CODE_OAUTH_TOKEN`). Tieni attivo il limite di spesa e le PR piccole.

### Restare aggiornati
Le nuove versioni del kit vengono pubblicate su https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` ti avvisa quando ne esce una. Esegui `/haam-update` (Codex: `$haam-update`) su un branch: i file che non hai mai modificato vengono aggiornati, le tue personalizzazioni vengono mantenute, e dove sono cambiati entrambi l'agente fa il merge. Il CHANGELOG elenca gli eventuali passi di migrazione.

### Il tuo ritmo come product owner
Ogni giorno (10–15 min): testa ciò che è in **UAT**, svuota **Triage** (`/triage`). Ogni settimana (30–45 min): decidi tutto ciò che è in **Decision**, riordina il backlog (`/triage backlog`), sollecita il lavoro fermo (`/triage stale`), riprendi i **Parked**, chiudi gli **override**. La guida completa, con le regole di priorità e le checklist: `docs/process/PRODUCT-MANAGER.md`.

---

## Risoluzione dei problemi

| Sintomo | Causa probabile | Soluzione |
|---|---|---|
| Non sai cosa resta da fare | – | `python3 tools/haam/haam.py doctor --role admin` |
| L'agente non segue le regole | Lo strumento non legge `AGENTS.md` | Verifica al primo avvio in `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` dice che il login non può usare Projects | Al login di gh manca lo scope `project` | `gh auth refresh -s project` |
| Le schede della board non si spostano quando le PR si aprono/vanno in merge | Manca `HAAM_PROJECT_TOKEN`, oppure la PR non dice `Refs #123` | Aggiungi il secret (Fase 5); controlla la descrizione della PR |
| L'agente non vede Linear | MCP non collegato o login non fatto | Passi per strumento in `docs/setup/AGENTS-SETUP.md` |
| Le skill compaiono due volte in Cursor | Cursor legge sia `.agents/skills` sia `.claude/skills` | Disattiva la compatibilità con le skill di Claude nelle impostazioni di Cursor |
| `.claude/skills` o `.grok/skills` mancano dopo il clone (Windows) | Symlink di Git disattivati | `git config core.symlinks true` e clona di nuovo, oppure `haam.py agents --apply` (copia invece di collegare) |
| `haam.py github` dice che ruleset/approvazioni non sono disponibili | Repo privato su un piano gratuito | Passa a un piano superiore, oppure proteggi a mano e affidati ai controlli |
| `haam.py linear` dà errore su un passo | Modifica dell'API o permessi | Completa quel passo a mano con `docs/setup/LINEAR-SETUP.md` |
| Due chat hanno modificato gli stessi file o lo stesso branch | Condividevano una cartella | Avvia ogni chat di agente con `/work` (worktree proprio) |
| Test o linter trovano file duplicati sotto `.claude/worktrees/` | Lo strumento scansiona l'intera cartella | Escludi `.claude/worktrees/` nella configurazione di quello strumento |
| Un worktree non riesce ad avviare l'app | Mancano file locali | Aggiungili a `.worktreeinclude`, poi `haam.py worktree prep` nel worktree |
| `/build` si rifiuta di partire | Issue non in Ready, oppure manca `agent-ready` | `/spec` e approvala, oppure sposta tu la issue in Ready |
| Gli stati di Linear non si spostano con gli eventi delle PR | Integrazione GitHub o automazioni non impostate | Team settings → Workflow → PR automations; il titolo della PR deve iniziare con l'ID della issue |
| `release-gate` resta rosso dopo `uat-passed` | Il workflow non è ripartito | Rimuovi e riaggiungi l'etichetta |
| Un controllo obbligatorio manca dall'elenco | Non ha ancora girato | Prima apri una PR qualsiasi |
| Commit bloccati: "gitleaks is not installed" | Manca gitleaks su quella macchina | Installalo, poi `make hooks` |
| Commit bloccato per un secret che non è un secret | Falso positivo | Una persona aggiunge l'impronta a `.gitleaksignore` in un commit revisionato |
| `ai-review` o `security-review` in attesa o in errore | Nessun secret per il revisore (`CLAUDE_CODE_OAUTH_TOKEN` o `ANTHROPIC_API_KEY`), PR da fork, oppure turni esauriti | Aggiungi il secret; rilancia; alza `--max-turns`; oppure `ai-review-overruled` |
| Revisore troppo severo | Istruzioni non regolate | Modifica `.github/review/REVIEWER.md` |
| `dependencies` fallisce su ogni PR | Vecchie vulnerabilità | Correggile, oppure alza temporaneamente la soglia e tracciale come bug |
| Specifiche troppo vaghe, build che vanno storte | G2 troppo permissivo | Rendi più rigorosa la Definition of Ready in `docs/process/GATES.md` |

---

## Principi

1. **Le persone decidono, gli agenti eseguono.**
2. **Se non è in Git o nel tracker, non esiste** per la prossima persona o il prossimo agente.
3. **Porzioni piccole:** una issue, un branch, una PR, revisionabile in 15 minuti.
4. **I gate costano poco da superare e molto da saltare.** Gli override sono consentiti, sempre registrati, sempre seguiti.
5. **Verde significa verde.** Non indebolire mai un test per superare un gate.
6. **Nessuno si corregge i compiti da solo.** L'agente che scrive il codice non lo revisiona mai; i secret vengono intercettati dagli strumenti, non dal giudizio.
7. **Qualsiasi agente, stesse regole.** Gli strumenti sono intercambiabili; il processo e i gate no.
