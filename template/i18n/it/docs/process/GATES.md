# Gate e override

Tra un'idea e la produzione ci sono cinque gate. Ognuno ha un responsabile chiaro, una checklist e, dove possibile, un punto di applicazione automatica, così la regola non dipende dalla memoria di qualcuno.

| Gate | Tra | Responsabile | Applicato da |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Persona (PO) | Stato del tracker: solo le persone eseguono `/decide` |
| **G2 Ready** | Backlog → Ready | Una persona approva la specifica | Etichetta `agent-ready`; gli agenti costruiscono solo issue `agent-ready` |
| **G3 Verified** | In Progress → UAT | Controlli automatici + agente revisore indipendente (+ persona per le aree protette) | Controlli obbligatori `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → merge | Persona che testa | Controllo obbligatorio `release-gate` (richiede l'etichetta di PR `uat-passed` o `gate-override`). Contano solo le etichette del proprietario o di un approvatore di riserva. |
| **G5 Released** | merge → produzione | Persona (PO) | Environment GitHub `production` con revisore obbligatorio |

La tabella mostra l'ordine checks-first. Nel flusso predefinito test-first, il G4 viene prima del G3: prima testi il branch dell'agente, poi i controlli girano una volta su ciò che hai approvato (vedi la checklist del G4).

---

## Checklist del G1 Decision

La valutazione (oppure, per un'idea costruita come prototipo, le note del prototipo prodotte da `/spike`) deve contenere:
- [ ] La descrizione del problema e per chi è
- [ ] Una stima del valore con evidenze (oppure un esplicito "ancora nessuna evidenza")
- [ ] La dimensione dello sforzo, motivata sulla base del codice
- [ ] I rischi: sicurezza, protezione dei dati (ad es. GDPR), normativa, operatività
- [ ] Almeno due opzioni più "non fare nulla"
- [ ] Una raccomandazione

La persona risponde con una di queste: **approve** (con priorità), **park** (con il motivo per riprenderla), **reject** (con una motivazione). Per un prototipo, prima lo prova (`/test`), così la decisione si basa sull'averlo usato e non sull'averne letto.

## Definition of Ready del G2

Una issue può ricevere `agent-ready` solo quando:
- [ ] La specifica esiste in `docs/specs/` ed è collegata dalla issue
- [ ] I criteri di accettazione sono scritti come Given / When / Then e ognuno è testabile
- [ ] L'ambito e ciò che è **fuori ambito** sono espliciti
- [ ] I file/moduli che probabilmente verranno toccati sono elencati
- [ ] L'impatto su dati, migrazioni e configurazione è indicato (oppure "nessuno")
- [ ] Sono inclusi il piano degli unit test e una traccia della UAT
- [ ] Dimensione ≤ 1 giorno di lavoro dell'agente (~400 righe modificate); altrimenti va divisa in sotto-issue
- [ ] Le aree protette toccate sono segnalate (etichetta `human-review` aggiunta)
- [ ] La priorità è impostata
- [ ] Una persona ha approvato la specifica

## G3 Verified (Definition of Done per il codice)

- [ ] Ogni criterio di accettazione ha almeno un test automatico
- [ ] `make check` passa in locale e nella CI (lint, tipi, unit test, build)
- [ ] Nessuna modifica estranea nel diff
- [ ] La documentazione toccata dalla modifica è aggiornata (`ARCHITECTURE.md`, documentazione API, elenco delle variabili d'ambiente)
- [ ] Nessun secret, nessun dato personale reale nel codice, nei test o nelle fixture
- [ ] La descrizione della PR segue il template e collega la issue (`Refs #123` su GitHub Projects, l'ID nel titolo su Linear)
- [ ] Controllo `secrets` verde: nessuna chiave, token o password in nessun commit della PR
- [ ] Controllo `dependencies` verde: nessuna vulnerabilità nota alta/critica
- [ ] `ai-review` verde: l'agente revisore indipendente non ha trovato problemi bloccanti
- [ ] `security-review` verde: la security review di Claude non ha trovato vulnerabilità
- [ ] Code review umana fatta se è presente l'etichetta `human-review`

### Come funziona la code review

La revisione è a livelli, così **nessun agente rivede mai il proprio lavoro** e **i secret vengono intercettati da strumenti deterministici, non dal giudizio**.

| Livello | Quando | Cosa | Chi / cosa lo fa |
|---|---|---|---|
| 1. Protezione locale dai secret | Prima di ogni commit | Blocca i commit che contengono chiavi/token | gitleaks tramite l'hook git di pre-commit (tutti, con qualsiasi strumento), più gli hook degli strumenti agente dove supportati (Claude Code; Grok) |
| 2. Autocontrollo | Prima di aprire una PR | `make check` + `/security-review` sulle proprie modifiche | L'agente che costruisce |
| 3. CI deterministica | A ogni push sulla PR | Test, lint, tipi, scansione dei secret su ogni commit, audit delle dipendenze | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Revisione AI indipendente | A ogni push sulla PR (non bozze né sola documentazione) | Conformità alla specifica, test onesti, correttezza, regole del progetto; vulnerabilità di sicurezza | Un Claude separato in GitHub Actions che non ha mai visto scrivere il codice (`ai-review`, `security-review`) |
| 5. Revisione umana | PR con etichetta `human-review` | Aree protette: logica principale, autenticazione, pagamenti, dati personali, migrazioni, infrastruttura | Il product owner o uno sviluppatore designato |
| 6. Accettazione umana | Ogni PR di codice | Il comportamento funziona davvero (UAT del G4) | Il product owner |

**Regole del ciclo di revisione**
- L'agente che costruisce legge il commento del revisore, corregge ogni elemento **Blocking** e fa push; le revisioni ripartono automaticamente.
- Se l'agente che costruisce ritiene sbagliato un rilievo, risponde sulla PR spiegando perché e chiede alla persona. Non discute mai in circolo: **dopo due giri di revisione** che falliscono ancora, si ferma e passa la mano alla persona.
- Solo una persona può scavalcare una revisione AI, con l'etichetta di PR `ai-review-overruled`. Questo resta registrato sulla PR. Conta solo quando l'account che l'ha aggiunta è `product_owner_github` o uno dei `backup_approvers_github` in `haam.config.json` sul branch di base, mai un bot.
- I revisori AI non possono approvare né fare il merge. Possono solo bloccare.

### Se un secret arriva mai su GitHub
1. **Revocalo e ruotalo subito** presso il fornitore. Consideralo compromesso; toglierlo dal codice non annulla la fuga.
2. Toglilo dal codice; usa una variabile d'ambiente documentata in `.env.example`.
3. Un amministratore del repo riscrive la storia del branch prima del merge (un nuovo commit non basta).
4. Apri un `/bug` con priorità Urgent per registrare cosa è successo e cosa è stato ruotato (non includere mai il secret stesso).

**Le impostazioni dell'owner cambiano il modo in cui gira il G3, non chi decide** (`/haam-settings`):
- `ci`: su ogni PR, in locale (`ci-local`, pubblicato da `haam.py local-ci` sul computer dell'owner), oppure disattivata.
- `review`: su GitHub, in locale, solo per le aree protette, oppure disattivata.
- `nightly`.

I controlli obbligatori seguono le impostazioni (`settings --apply`). La scansione dei secret gira sempre.

## G4 Accepted (UAT)

Nel flusso predefinito test-first, il G4 viene prima del G3: l'owner testa il branch di cui l'agente ha fatto push prima che esista una PR, e il G3 poi controlla esattamente il commit che ha superato il test (`haam.py publish`, poi `ship`, che rifiuta qualsiasi altra cosa).

**Corsia senza UAT:** qui il G4 si decide in anticipo. Quando l'owner marca una issue `uat:skip` (in `/triage`, oppure con "spec approved, no UAT"), l'agente apre la PR con la stessa etichetta e `release-gate` passa quando ogni issue a cui la PR si riferisce la porta (GitHub Projects: il gate legge le issue; Linear: si fida dell'etichetta della PR). Mai quando la PR modifica un'area protetta: il gate confronta i file modificati con `protected_paths` in `haam.config.json` su `main` (per impostazione predefinita la configurazione degli agenti e della CI, più quelle del progetto), aggiunge `human-review` e tiene chiusa la corsia, qualunque cosa dicano le etichette. Quindi un aggiornamento del kit non prende mai la corsia: modifica la configurazione degli agenti, e lo revisioni e lo rilasci tu. Il G3 si applica comunque per intero, e l'auto-merge (richiede `HAAM_PROJECT_TOKEN`) fa il merge solo quando passano tutti i controlli obbligatori. Non c'è auto-merge su Linear, né quando la CI o una delle due revisioni AI gira altrove che su GitHub per ogni PR (l'auto-merge richiede `ci: every-pr` e `review: github`): i risultati locali non sono a prova di manomissione e i controlli ridotti non bastano da soli, quindi quelle PR della corsia le rilascia l'owner (`ship`), che resta comunque una decisione per molte. Solo la decisione di una persona aggiunge `uat:skip` a una issue (`issue create` e `issue label` la rifiutano senza `--human`).

**Corsia degli agenti** (l'impostazione `uat: agents-verify`, GitHub Projects): per una modifica il cui piano dice `Needs a person: no` e che non tocca nessuna delle aree proprie dell'owner (`owner_test_paths`), G4 lo fa un agente verificatore indipendente al posto del tuo test. Decide `haam.py lane <ID>`, e la corsia dell'owner vince sempre: l'etichetta `owner-test`, una rilavorazione dopo `uat-failed`, un file sotto `owner_test_paths` (un file rinominato conta con entrambi i nomi), commit tenuti da un prototipo, o un piano che dice `yes` o non dice niente. Una nuova chat che non ha costruito la modifica la controlla al commit consegnato e registra il verdetto con i propri segni: lo stato di commit `agent-verified`, l'etichetta `verified-by-agents` e un commento `🔎 Verified by agents`, mai `uat` né `uat-passed`. L'owner viene informato, può riprendersi qualsiasi ticket prima di `ship` (`test <ID> myself` aggiunge l'etichetta `owner-test`, che solo lui toglie), e niente va in produzione senza il suo `ship`. Un push dopo la verifica la annulla, a meno che cambi solo `docs/uat/` o `docs/changes/`. I primi `agents_verify_shadow` ticket verificati (10 per impostazione predefinita) passano anche dal tuo test, e uno su 10 viene verificato di nuovo con un altro modello (`spot-check`). Rimettere `uat` su `owner-decides` rende di nuovo tuo test ogni ticket non ancora rilasciato.

- [ ] Il piano di UAT esiste in `docs/uat/` con passi numerati e risultati attesi
- [ ] Una persona l'ha eseguito in locale sul branch (test-first: il branch di cui l'agente ha fatto push, prima di qualsiasi PR; checks-first: il branch della PR)
- [ ] Tutti i passi passano, oppure i problemi sono registrati e accettati come issue di follow-up
- [ ] Il superamento da parte della persona (`/test` o `/uat-result <ID> pass`) aggiunge l'etichetta `uat-passed` alla PR (test-first: `publish` lo registra anche sul commit testato come stato `uat`)
- [ ] Il superamento copre il codice che va in merge: un push successivo rimuove `uat-passed` (`gates.yml`), a meno che il nuovo head non sia il commit testato; `ship` fa il merge solo di quel commit

## G5 Released

- [ ] PR unita su `main` da una persona, oppure da `haam.py ship --human` dopo che la persona ha detto `ship`
- [ ] Deploy in produzione approvato (environment `production`): su GitHub, oppure da `ship` su parola della persona
- [ ] Smoke check post-deploy superato (`make smoke`, se definito)
- [ ] La issue è marcata come Done (`ship`, oppure `/release` per le modifiche unite in altro modo); la nota di rilascio in `docs/changes/` è stata rilasciata con essa

---

## Override

A volte la produzione va a fuoco o una scadenza non aspetta. Gli override esistono per questo e sono **riservati alle persone**.

### Livello 1: saltare la UAT (il più comune)
Da usare quando la correzione è urgente e verificata dai test, ma non c'è tempo per un ciclo completo di UAT.

1. La persona esegue `/override <ID> "<reason>"` (per una PR senza issue: `/override PR <number> "<reason>"`), oppure commenta a mano `OVERRIDE: <reason>` sulla PR (il commento deve iniziare con `OVERRIDE:`) e aggiunge l'etichetta di PR `gate-override`. Entrambi contano solo dall'account del proprietario o di un approvatore di riserva (`product_owner_github`, `backup_approvers_github` in `haam.config.json` su main), mai da un bot; lo stesso vale per `uat-passed` e per l'`uat:skip` della issue. Finché gli agenti accedono a GitHub come il proprietario, GitHub non può distinguere il proprietario da un agente: questo ferma i bot e ogni altro account, non un agente che ignora le regole. Il controllo di release gira dalla copia di `gates.yml` su main (`pull_request_target`), quindi una PR non può riscrivere il controllo che la giudica.
2. Il controllo `release-gate` passa grazie all'etichetta di override.
3. La CI (controllo `ci`) **deve comunque passare**.
4. Quando la PR ha una issue, l'agente crea una issue di follow-up nel tracker: `Post-override UAT for <ID>` (priorità High, etichetta `stream:bug`, `override-followup`), così la verifica saltata avviene comunque a posteriori.

### Livello 2: bypass di emergenza (raro)
Da usare solo quando la CI stessa è rotta o blocca una correzione in produzione.

1. Un amministratore del repository fa il merge con "bypass branch protections" su GitHub.
2. L'amministratore commenta `EMERGENCY BYPASS: <reason>` sulla PR.
3. Si crea una issue di follow-up come sopra, più una seconda per sistemare ciò che ha bloccato la CI.

### Regole sugli override
- Gli agenti non aggiungono **mai** `gate-override`, non aggirano mai le protezioni e non suggeriscono mai un override a meno che non sia la persona a parlarne per prima.
- Ogni override deve avere una motivazione scritta sulla PR.
- Gli override si rivedono nella revisione settimanale del backlog: filtra il tracker per l'etichetta `override-followup`.
