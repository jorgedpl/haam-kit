# Setup di GitHub (una volta sola, ~30 minuti, amministratore del repo)

Questo trasforma i gate G3–G5 da convenzioni in regole che GitHub fa rispettare.

> **Automatizzato:** etichette (§1), regole sui branch (§2), l'environment di produzione (§4) e le funzionalità di sicurezza (§3b–c) li configura `python3 tools/haam/haam.py github --apply` (prima guarda il piano senza `--apply`). Questa pagina è l'equivalente manuale, più i passi che GitHub offre solo nel browser. Il secret del revisore lo aggiungi sempre tu: `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (token da `claude setup-token`, il tuo piano Claude) oppure `gh secret set ANTHROPIC_API_KEY -R owner/repo` (chiave API, fatturata per revisione). Uno dei due fa girare entrambe le revisioni.

## 1. Etichette
Crea queste etichette del repository (Issues → Labels), oppure esegui:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Protezione del branch `main`
Settings → **Rules → Rulesets** → New branch ruleset (oppure la Branch protection classica), con destinazione `main`:

- ✅ Limita le cancellazioni; blocca i force push
- ✅ Richiedi una pull request prima del merge
  - Approvazioni richieste: **1** quando c'è una seconda persona; **0** finché nel progetto ci sei solo tu (l'etichetta UAT è la tua approvazione)
  - ✅ Annulla le approvazioni superate quando vengono fatti push di nuovi commit
- ✅ Richiedi che i controlli di stato passino (lascia disattivato "require branches to be up to date": rifà girare la CI su ogni PR aperta dopo ogni merge)
  - Controlli obbligatori: **`ci`** (o **`ci-local`** quando `ci` è `local`; ometti quando `ci` è `off`), **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** e **`release-gate`** (compaiono nell'elenco dopo che i workflow hanno girato una volta su una PR). `haam.py settings --apply` / `github --apply` aggiunge i controlli che le impostazioni chiedono e toglie quelli di HAAM che non chiedono più (ad es. `ci` quando passi a `off`)
- ✅ Richiedi una storia lineare (facoltativo, tiene pulita la storia)
- **Bypass list:** solo gli amministratori del repository, **solo per le pull request** (mai "always": gli agenti lavorano con il login di una persona, spesso un amministratore, e altrimenti potrebbero fare push direttamente su `main`). È il bypass di emergenza di Livello 2 descritto in `docs/process/GATES.md`.

**Auto-merge** (Settings → General → Pull Requests → *Allow auto-merge*; `haam.py github --apply` lo attiva): usato solo dalla corsia senza UAT, per le PR le cui issue hai marcato `uat:skip`. Il gate lo attiva per una PR di quel tipo con il secret `HAAM_PROJECT_TOKEN` (`docs/process/TRACKER.md`), e GitHub fa il merge solo quando passano tutti i controlli obbligatori. Se richiedi approvazioni, anche la corsia ne aspetta una.

## 3. Code review e sicurezza

### 3a. Un secret Claude per gli agenti revisori
I revisori indipendenti (`.github/workflows/review.yml`) eseguono Claude in GitHub Actions. Un solo secret del repository fa girare entrambe le revisioni (Settings → **Secrets and variables → Actions** → New repository secret). Scegline uno:
- **`CLAUDE_CODE_OAUTH_TOKEN`:** esegui `claude setup-token` e usa il token che stampa. Le revisioni vengono allora conteggiate in quel piano Claude.
- **`ANTHROPIC_API_KEY`:** una chiave API dedicata a questo repo, da console.anthropic.com, con un limite di spesa mensile. È fatturata per revisione, separatamente dall'abbonamento Claude di chiunque. Con questa, la revisione di sicurezza usa l'action di security review di Anthropic.

Le PR in bozza e quelle di sola documentazione non chiamano Claude. Le istruzioni delle revisioni sono in `.github/review/REVIEWER.md` e `SECURITY-REVIEWER.md`, e vengono lette sempre da `main`. Regolale man mano che impari.

### 3b. Secret scanning e push protection
Settings → **Security** (Code security / Advanced Security, a seconda del piano):
- ✅ **Secret scanning**, ✅ **Push protection**: GitHub rifiuta i push che contengono formati di secret noti.
- Gratuito per i repository pubblici. Per quelli privati può richiedere il componente aggiuntivo di sicurezza a pagamento di GitHub; se non ce l'hai, il controllo `secrets` del kit (gitleaks) e gli hook locali ti coprono comunque.

### 3c. Avvisi sulle dipendenze
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Poi togli il commento dal tuo ecosistema in `.github/dependabot.yml`. Le PR di Dependabot passano per gli stessi gate.

### 3d. Pull request da fork
Settings → **Actions → General** → *Fork pull request workflows*: richiedi l'approvazione per tutti i collaboratori esterni. (Le PR da fork non ricevono i secret del repository, quindi le revisioni AI non possono girare su di esse; una persona le revisiona e, se serve, scavalca.)

## 4. Environment di produzione (Gate G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** il product owner (+ una persona di riserva, se c'è)
- ✅ Prevent self-review: lascialo **disattivato** finché l'unica persona che approva sei tu, attivalo in seguito
- **Deployment branches and tags:** selected branches → solo `main`
- **Environment secrets:** le credenziali di deploy in produzione vanno qui e da nessun'altra parte
- **Environment variables:** `PRODUCTION_URL` (usata dallo smoke test)

Ora ogni merge su `main` esegue `deploy.yml`, che si ferma a *deploy-production* finché un approvatore non clicca **Review deployments → Approve**. GitHub avvisa gli approvatori via email o notifica.

I revisori obbligatori funzionano sui repository pubblici con ogni piano, ma su quelli privati solo con GitHub Enterprise Cloud. Senza, i deploy partono al merge, e la decisione di rilascio è il tuo `ship`: imposta `deploy_approval: automatic` con `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (facoltativo, ma consigliato quando le persone sono due)
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
Poi attiva "Require review from Code Owners" nel ruleset.

## 6. Compila il contratto dei comandi
Modifica il `Makefile` (compreso `audit`) e i passi di setup del runtime in `.github/workflows/ci.yml`, `security.yml` e `deploy.yml` (cerca `TODO(setup)`). Apri una PR. Il controllo `ci` deve diventare verde su quella PR prima che tu attivi i controlli obbligatori.

## 7. Facoltativo: app GitHub di Claude
Se vuoi taggare un agente su una PR per una correzione rapida (ad es. l'app GitHub di Claude tramite `/install-github-app` in Claude Code, o l'integrazione GitHub del tuo altro strumento), installala. Qualsiasi app del genere è vincolata dalla stessa protezione dei branch e dagli stessi controlli, quindi non può aggirare i gate.

## 8. Tenere bassi i minuti di Actions

I repository privati hanno una quota mensile di minuti di Actions; gli agenti che aprono molte PR la consumano in fretta. Cosa fa già il kit: per impostazione predefinita (test-first) gli agenti fanno push dei branch senza aprire PR, e una PR si apre solo dopo che hai testato e approvato la modifica, così i controlli girano una volta su codice testato (nei progetti checks-first: le PR in bozza non eseguono nulla, e gli agenti marcano una PR come pronta una volta sola, quando è completa); le PR di sola documentazione saltano i controlli; `main` viene controllato ogni notte invece che dopo ogni merge; etichette, commenti e nuove issue non avviano runner; gli agenti sospendono il nuovo lavoro a 10 PR aperte o a 10 modifiche in attesa del tuo test (`max_open_prs`, `max_in_uat`).

Scopri dove vanno i minuti: `python3 tools/haam/haam.py ci-usage` (ultimi 7 giorni, per workflow, job, trigger e giorno).

Due impostazioni nella tabella qui sotto fanno risparmiare minuti con un compromesso contenuto. Cambiale con `/haam-settings`, oppure `python3 tools/haam/haam.py settings --set … --apply --human`; diventano variabili del repository che i workflow leggono. Le altre (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) fanno risparmiare di più: vedi `settings --explain`. Con `ci: off`, le regole del branch smettono di richiedere il controllo `ci`; mantieni la scansione dei segreti, le revisioni IA e release-gate, ed esegui un controllo completo al momento del rilascio (il tuo script di deploy o il workflow CI sul commit che rilasci) così da catturare ancora i fallimenti che compaiono solo su Linux.

| Opzione | Cosa cambia | Compromesso |
|---|---|---|
| `--review local` | Le due revisioni AI girano sul tuo computer in sessioni Claude nuove (`haam.py review`), usando il tuo piano Claude invece dei minuti di Actions. Le PR con etichetta `human-review` vengono comunque revisionate su GitHub | Il risultato non è più a prova di manomissione: è l'agente che costruisce ad avviare la revisione (sessioni nuove, in sola lettura, istruzioni da `main`), e qualsiasi cosa usi il tuo login potrebbe pubblicare un risultato positivo. Esegui `haam.py review` dalla tua chat per una separazione maggiore |
| `--runner self-hosted` | Tutti i job tranne il deploy girano su una tua macchina (registrata in Settings → Actions → Runners) invece che su quelle di GitHub | La macchina deve essere accesa, con git, make, Python 3, curl, gitleaks e gli strumenti del tuo progetto; solo per repository privati. Controlla i prezzi attuali di GitHub per i runner self-hosted |

Vale anche la pena controllare: i job sui runner macOS contano 10 minuti per ogni minuto di esecuzione (Windows: 2). Esegui le build mobile solo quando il codice mobile è cambiato (`make check` riceve i file modificati in `$CI_CHANGED_FILES`), oppure di notte.

## 9. Verifica che funzioni
1. Apri una piccola PR di prova (ad es. la correzione di un refuso nel codice). Girano `ci`, `secrets` e `dependencies`; l'agente revisore pubblica un commento e `ai-review` / `security-review` riportano il risultato; `release-gate` mostra **failure: waiting for UAT**.
   - **Test dei secret:** su un branch usa e getta, committa in un file di codice una chiave finta in stile AWS, come `AKIA` seguito da 16 lettere maiuscole/cifre. L'hook locale dovrebbe bloccare il commit; se lo aggiri con `--no-verify`, il controllo `secrets` dovrebbe fallire. Poi cancella il branch.
2. Aggiungi l'etichetta `uat-passed` → `release-gate` diventa verde → il merge è consentito.
3. Dopo il merge, Actions → Deploy mostra **Waiting for review** su `deploy-production`.
4. Apri una PR di sola documentazione → `release-gate` passa automaticamente.
