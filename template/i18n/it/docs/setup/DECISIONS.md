# Decisioni da prendere quando adotti HAAM

Le prende il product owner, insieme all'amministratore del progetto. `/haam-setup` le percorre in quest'ordine, con una raccomandazione per ciascuna, e `/haam-settings` le cambia in seguito. Parti dalla scelta consigliata, poi rivedila dopo la prima settimana intensa. A quel punto, `haam.py ci-usage` mostra dove sono finiti i minuti di Actions e `haam.py capacity` mostra cosa ti aspetta.

**Alcuni termini usati qui:**
- **PR** (pull request): una modifica proposta, in attesa del merge su `main`.
- **CI:** i controlli automatici (lint, tipi, test, build) che girano su GitHub per una PR. Usano minuti di Actions.
- **UAT** (test di accettazione utente): il tuo test di una modifica, sul tuo computer, prima che venga rilasciata.
- **La corsia senza UAT:** le modifiche che marchi `uat:skip` (aggiornamenti di dipendenze, configurazione, refactoring invisibili). Saltano il tuo test e vanno direttamente ai controlli.
- **Gate di rilascio:** il controllo che impedisce il merge di una PR finché il tuo test non è passato, o finché non hai scelto la corsia senza UAT.
- **Worktree:** una copia separata della cartella del progetto per una chat di agente, così le chat non si sovrascrivono a vicenda.

## In sintesi

| Decisione | Parti con | Cambiala quando | Vedi |
|---|---|---|---|
| Account e piano GitHub | Un'organizzazione. Repository pubblico: Free. Privato: Team | Il repository è privato e ti serve un approvatore sui deploy: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | Il team lavora già in Linear ogni giorno | §2 |
| Chi è chi | Un product owner, un approvatore di riserva | Più prodotti o più owner | §3 |
| Lingua (`language`) | La lingua in cui scrive il tuo team | Il team cambia | §3 |
| Ordine dei test (`flow`) | `test-first` | Testi su un sito di staging condiviso invece che in locale | §4 |
| Cosa testi (`uat`) | `owner-decides` | Prodotto regolamentato: `always`. Molte piccole correzioni ben testate: `bugs-skip` | §4 |
| Raggruppamento (`grouping`) | `per-issue` | Epic fatte di piccoli elementi: `per-epic`. Minuti di Actions scarsi: `release` | §4 |
| Controlli (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | I minuti di Actions scarseggiano | §4 |
| Rilascio (`deploy`, `deploy_approval`) | `github`, `each` | Fai il deploy in un altro modo, oppure il tuo piano non può trattenere i deploy in attesa di approvazione | §4 |
| Limiti | `settings --recommend` | Cambiano il tuo tempo per i test o il numero di agenti | §5 |
| Aree protette | Quelle predefinite, più il tuo codice sensibile | Cambia l'architettura | §6 |
| Risorse di test condivise (`heavy_runs`) | Nessuna | I test condividono un database locale, un simulatore o un dispositivo | §7 |
| Quanta libertà hanno gli agenti | Prototipi e modalità di build per epic quando li chiedi; il codice di produzione è tutto tranne prototipi, test e documentazione | Vuoi che gli agenti esplorino di più, oppure il tuo codice di produzione sta in poche cartelle | §8 |

## 1. Account GitHub, organizzazione e piano

### Account
Ogni persona crea e mantiene il proprio account; non condividere mai un login.

1. **Ogni persona** si registra su [github.com/signup](https://github.com/signup) con la propria email di lavoro e attiva l'autenticazione a due fattori (Settings → Password and authentication).
2. **Un amministratore** crea un'organizzazione ([github.com/organizations/plan](https://github.com/organizations/plan)) e invita il team. Il piano gratuito basta per un repository pubblico; uno privato richiede Team (vedi la tabella sotto). I repository appartengono all'organizzazione, quindi niente dipende dall'account di una sola persona. Nomina due persone come owner.
3. **Il repository** vive nell'organizzazione: crealo lì, oppure sposta uno esistente (Settings del repository → General → Transfer ownership).
4. **Su ogni computer**, installa la GitHub CLI ([cli.github.com](https://cli.github.com)) ed esegui `gh auth login`. Con GitHub Projects come tracker, esegui anche `gh auth refresh -s project`.
5. **Niente account separati per gli agenti.** Gli agenti agiscono con l'account della persona che ha fatto il login. I gate presuppongono che la persona alla tastiera risponda di ciò che fanno i suoi agenti.

### Quale piano ti serve

| Cosa usa HAAM | Repository pubblico, qualsiasi piano | Privato, Free | Privato, Pro | Privato, Team | Privato, Enterprise Cloud |
|---|---|---|---|---|---|
| Regole sui branch e controlli obbligatori ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Sì | No | Sì | Sì | Sì |
| Un approvatore sui deploy in produzione ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Sì | No | No | No | Sì |
| Secret scanning e push protection di GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Sì | No | No | Componente aggiuntivo a pagamento | Componente aggiuntivo a pagamento |
| Board di GitHub Projects | Sì | Sì | Sì | Sì | Sì |
| Minuti di Actions | Gratuiti sui runner standard | Una quota mensile | Una quota più ampia | Una quota più ampia | Una quota più ampia |

Pro è per un account personale; Team ed Enterprise Cloud sono per le organizzazioni.

Cosa significa ciascun pezzo mancante:
- **Niente regole sui branch** (repository privato su Free): GitHub non impedisce un merge su `main` senza i controlli. Agli agenti viene comunque detto di non fare mai il merge, e `ship` esegue comunque tutti i gate, ma niente lo impone. Per qualsiasi prodotto privato, usa Team (organizzazione) o Pro (account personale).
- **Niente approvatore dei deploy** (repository privato sotto Enterprise Cloud): i deploy partono quando una PR va in merge. A quel punto la decisione di rilascio è il tuo `ship`, che fa il merge. Imposta `deploy_approval: automatic` così HAAM non aspetta un'approvazione che non può arrivare, e tieni `uat` su `owner-decides` o `always` (§4).
- **Niente secret scanning di GitHub:** va bene. Il controllo `secrets` del kit e l'hook di pre-commit girano su ogni piano.

Piani e quote cambiano, quindi controlla [github.com/pricing](https://github.com/pricing) prima di scegliere.

### L'accesso dei revisori a Claude
Le due revisioni AI girano con un solo secret del repository, aggiunto dall'owner nel proprio terminale e mai incollato in una chat:
- `CLAUDE_CODE_OAUTH_TOKEN` (da `claude setup-token`): le revisioni vengono conteggiate nel piano Claude di quella persona.
- `ANTHROPIC_API_KEY`: fatturata per revisione, separatamente dall'abbonamento di chiunque. Imposta un limite di spesa mensile nella console di Anthropic.

## 2. Il tracker: GitHub Projects o Linear

| | GitHub Projects | Linear |
|---|---|---|
| Costo | Gratuito su ogni piano GitHub | Gratuito fino a 250 issue attive (non archiviate) e 2 team; i piani a pagamento per utente tolgono il limite. Controlla [linear.app/pricing](https://linear.app/pricing) |
| Come lo usano gli agenti | `haam.py issue …` da qualsiasi strumento agente, con il login `gh` della persona | La connessione a Linear (MCP) configurata in ogni strumento agente |
| Fatto per te | Prese in carico che impediscono a due chat di prendere lo stesso compito; la coda di UAT conteggiata per i limiti; i campi propri della board (`--field`); la corsia senza UAT che va in merge da sola; `ship` che chiude le issue | Gli agenti fanno gli spostamenti tramite la connessione, e contano la coda di UAT per `capacity --in-uat N`. La corsia senza UAT non va in merge da sola: quelle PR le rilasci tu |
| Setup | `haam.py github-project --apply` | `haam.py linear --apply` con la chiave API dell'owner, più i passi da browser in `LINEAR-SETUP.md` |
| Ideale per | La maggior parte dei team: tutto in un unico posto | Team che vivono già in Linear |

**Raccomandazione:** GitHub Projects, a meno che il team non usi già Linear ogni giorno. Il triage e gli agenti creano issue in fretta, quindi il limite del piano gratuito di Linear si può raggiungere nel giro di settimane.

## 3. Chi è chi
- **Product owner:** una persona, che decide, testa e rilascia. Solo questa persona esegue le skill riservate alle persone: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` e `/haam-settings`.
- **Approvatori di riserva:** una o due persone che possono approvare i deploy quando l'owner non c'è (`config --backup-approvers a,b`). Serve un approvatore sui deploy, quindi non ha effetto su un repository privato sotto Enterprise Cloud.
- **Chi costruisce:** tutte le persone che usano chat di agenti. Ognuna ha bisogno del proprio account GitHub con accesso in scrittura e del proprio strumento agente. L'amministratore esegue `haam.py invite --github USER` per vedere il piano, poi lo stesso con `--apply`. Ognuna poi esegue `/haam-onboard`.
- **Amministratore:** configura GitHub, il tracker e i secret. Spesso è l'owner.
- **Quando due persone lavorano sul codice,** richiedi un'approvazione nelle regole sui branch (`GITHUB-SETUP.md` §2).
- **Lingua:** la documentazione del kit è disponibile in inglese, spagnolo, francese, tedesco, italiano, olandese e portoghese (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Gli agenti scrivono specifiche, issue, piani di UAT e messaggi nella lingua che scegli; comandi, etichette, stati e codice restano in inglese. Sceglila all'installazione (`install --language es`). Per cambiarla in seguito: `haam.py config --language fr`, poi `update --target . --apply` del kit cambia la documentazione che non hai modificato.

## 4. Come scorre il lavoro: le impostazioni
`python3 tools/haam/haam.py settings --explain` stampa ogni opzione con il suo compromesso. Le scelte che contano:

| Impostazione | Parti con | Scegli diversamente quando | Cosa costa o rischia |
|---|---|---|---|
| `flow` | `test-first`: testi il branch dell'agente, poi la PR e i controlli girano una volta | `checks-first`: vuoi testare solo codice che ha superato i controlli, oppure testi su un sito di staging condiviso | Ogni giro di rilavorazione rifà girare i controlli |
| `uat` | `owner-decides`: testi tutto tranne ciò che marchi `uat:skip` | `always`: prodotti regolamentati o critici per la sicurezza. `bugs-skip`: molte piccole correzioni con test solidi | `bugs-skip`: una correzione sbagliata può essere rilasciata senza che tu la veda |
| `grouping` | `per-issue`: una PR per issue | `per-epic`: epic fatte di piccoli elementi. `release` (solo test-first): minuti scarsi e rilasci a lotti | Un elemento che fallisce trattiene tutto il lotto |
| `ci` | `every-pr`, su GitHub | `local`: i minuti finiscono e il tuo computer compila tutto. `off`: solo per prototipi di una persona sola | `local` non è a prova di manomissione |
| `review` | `github`: due revisioni AI indipendenti per PR | `protected-only`: risparmia gran parte del costo delle revisioni. `local`: risparmia minuti | Meno controlli indipendenti |
| `nightly` | `on` | `off`: quando i minuti sono molto scarsi | Scopri più tardi rotture e nuove vulnerabilità |
| `runner` | `github` | `self-hosted`: un repository privato con build pesanti e una macchina che resta accesa | Manutenzione. Mai per i repository pubblici |
| `deploy` | `github`: `deploy.yml` fa il deploy al merge | `manual`: fai il deploy in un altro modo | `ship` aspetta che tu dica "live" |
| `deploy_approval` | `each`: ogni deploy aspetta la tua approvazione | `automatic`: il tuo piano non può trattenere i deploy (§1), oppure hai scelto `uat: always` | Una modifica unita va in produzione senza un ultimo sguardo |
| `worktree_cleanup` | `after-ship` | `manual`: preferisci fare pulizia dei worktree da te | Spazio su disco |

La corsia senza UAT va in merge da sola solo su GitHub Projects, con il secret `HAAM_PROJECT_TOKEN`, `ci: every-pr` e `review: github`. Altrimenti quelle PR le rilasci tu.

Evita queste coppie, perché insieme tolgono l'ultimo controllo:
- `ci: off` con `review: off`: niente controlla il codice prima del tuo test.
- `deploy_approval: automatic` con `uat: bugs-skip`: la correzione di un bug può arrivare in produzione senza che nessuno la guardi. Su un repository privato sotto Enterprise Cloud i deploy sono automatici, quindi lì non scegliere `bugs-skip`.

## 5. Limiti: quanto lavoro può restare in attesa
I limiti impediscono agli agenti di produrre più di quanto tu possa testare, e più PR di quante il tuo budget di CI ne copra. Quando si raggiunge un limite, gli agenti smettono di avviare nuove build. Continuano comunque a correggere le rilavorazioni, scrivere specifiche e valutare idee.

| Limite | Cosa conta | Come dimensionarlo |
|---|---|---|
| `max_in_uat` | Le modifiche in attesa del tuo test. Il limite principale in test-first | Quanto riesci a testare in una sessione: minuti per sessione ÷ minuti per test (un test richiede spesso da 5 a 10 minuti). Un'ora al giorno a circa 6 minuti per test fa 10 |
| `max_open_prs` | Le PR pronte. Bozze, PR di sola documentazione e PR dei bot (Dependabot) non contano | Test-first: le PR vivono poco (dal tuo superamento a `ship`), quindi il doppio delle chat di agenti attive contemporaneamente è più che sufficiente. Checks-first: ogni modifica in attesa del tuo test è una PR pronta, quindi impostalo almeno a `max_in_uat` più le chat attive contemporaneamente |
| `max_review_rounds` | I giri di revisione AI falliti prima che un agente si fermi e ti chieda | 2. Alzalo a 3 per le aree difficili |
| `max_pr_lines` | La dimensione obiettivo di una PR, in righe modificate | 400. Le PR più piccole ricevono revisioni e test migliori |

Fai il calcolo per il tuo team:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
Stampa i limiti suggeriti e ti avvisa quando gli agenti possono produrre più di quanto tu possa testare. Poi ti dà il comando che li applica. Presuppone circa 6 minuti per test e 2 modifiche per chat al giorno; passa `--minutes-per-test` e `--changes-per-chat` con i tuoi numeri. Legge `flow` dalle impostazioni del progetto, oppure accetta `--flow`.

Se gli agenti producono più di quanto riesci a testare:
- la coda si riempie e gli agenti sospendono le nuove build, ed è il limite che fa il suo lavoro;
- `/test all` con "pass all verified" smaltisce le modifiche che gli agenti hanno verificato da soli;
- `uat: bugs-skip` manda le piccole correzioni di bug direttamente ai controlli;
- oppure usa meno chat di agenti.

Per un weekend di lavoro degli agenti testato in una sola sessione, apri una **finestra di lotto**: un aumento che finisce da solo dopo il suo ultimo giorno, ad es. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. Cosa proteggere
**La regola:** proteggi il codice in cui una modifica sbagliata potrebbe danneggiare gli utenti, far perdere soldi o dati, violare la legge o indebolire i gate stessi di HAAM. Ogni modifica protetta richiede la tua code review e il tuo test, e non prende mai la corsia senza UAT. Quindi proteggi ciò che conta, non tutto.

| Area | Proteggere | Percorsi tipici (esempi) |
|---|---|---|
| Accesso, sessioni, permessi, ruoli | Sempre | `src/auth/**`, `**/permissions/**`, *il middleware di autenticazione* |
| Pagamenti, fatturazione, rimborsi, prezzi | Sempre | `src/billing/**`, `src/payments/**` |
| Dati personali: archiviazione, conservazione, cancellazione, esportazioni | Ogni volta che gestisci dati personali | `src/users/**`, `**/privacy/**` |
| Log che potrebbero catturare dati personali | Ogni volta che gestisci dati personali | *la configurazione dei log e i moduli di audit* |
| Decisioni sugli utenti: idoneità, verifica, approvazioni, punteggi | Quando un risultato sbagliato danneggia qualcuno | `src/verification/**`, `src/decisions/**` |
| Fornitori esterni che agiscono per gli utenti o ricevono i loro dati | Sì | `src/integrations/**` |
| Migrazioni del database | Sempre | `db/migrations/**`, `**/migrations/**` |
| Configurazione di sicurezza: crittografia, CORS, CSP, gestione dei secret | Sì | `**/security/**`, `**/crypto/**` |
| Infrastructure as code | Sì | `infra/**`, `terraform/**` |
| Firma e configurazione di rilascio delle app mobile | Se rilasci app | *entitlement, file di firma e di build di rilascio* |
| Script di CI, deploy e build | Protetti per impostazione predefinita | `.github/**`, `Makefile`, `scripts/**` |
| HAAM e la configurazione degli agenti | Protetti per impostazione predefinita | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json` e altri: `haam.py settings` li elenca |

I percorsi in corsivo descrivono cosa cercare; trasformali in pattern reali per il tuo codice.

Come configurarlo:
1. `/haam-setup` propone percorsi reali dal tuo codice per ogni area che si applica. Tu li confermi.
2. `config --protected "src/auth/**,db/migrations/**" --human` aggiunge pattern, e `config --unprotected "…" --human` ne rimuove uno. `**` significa qualsiasi cartella e `*` significa all'interno di una cartella. Il semplice nome di una cartella copre tutto ciò che contiene.
3. `haam.py protected` su qualsiasi branch elenca i file protetti che modifica.
4. Il gate di rilascio decide in base ai file che una PR modifica. Legge l'elenco da `main`, quindi un agente non può rimuovere una protezione nella propria PR.

Rivedi l'elenco ogni volta che cambia `docs/product/ARCHITECTURE.md`.

## 7. Risorse di test condivise
Alcuni test usano qualcosa che tutto il computer condivide, come un database locale che i test clonano, un simulatore di telefono o un dispositivo collegato. Due chat di agenti che li eseguono contemporaneamente si danneggiano a vicenda, e il fallimento sembra una modifica rotta. Elenca quei comandi come pattern: `config --heavy-run "make (check|test-integration)"`. Gli agenti allora li eseguono uno alla volta tramite `haam.py exclusive`. Lascia l'elenco vuoto quando i tuoi test sono autonomi.

## 8. Quanta libertà hanno gli agenti
Gli agenti possono costruire grandi pezzi in fretta, come quando le persone fanno "vibe coding" con l'AI, ovunque un errore costi poco da buttare via. Tutto ciò che gira per gli utenti reali resta dietro i gate.

**Alcuni termini usati qui:**
- **Prototipo** (o **spike**): una versione funzionante, rapida e usa e getta, di un'idea, costruita per essere provata e mai rilasciata così com'è.
- **Porzione:** un pezzo rilasciabile di un'epic, con la propria issue e la propria specifica.
- **Agente capofila:** l'unica chat di agente che costruisce un'intera epic. Può affidare porzioni indipendenti ad agenti di supporto (**sub-agenti**).
- **Feature flag:** un interruttore nel codice che tiene nascosta una nuova funzionalità finché qualcuno non la attiva.
- **Codice di produzione:** il codice che gira per gli utenti reali.

Tre scelte:

| Scelta | Cosa fa | Quando usarla |
|---|---|---|
| **Prima il prototipo.** Scrivi `/spike`, oppure scegli `prototype` in `/triage` | Un agente costruisce un prototipo su un branch `spike/`, senza specifica, PR o limite di dimensione. Lo provi con `/test`. Poi dici `discard`, `change: <what>`, `rebuild` (scrivine la specifica e ricostruiscilo da zero) o `keep` (scrivine la specifica e costruisci a partire da quel codice) | Quando provare l'idea ti dice di più che leggerne: una nuova schermata, un flusso, un'integrazione su cui hai dubbi |
| **Modalità di build per epic.** Metti l'etichetta `mode:epic-build` a un'epic approvata; `/decide` e `/triage backlog` la propongono | Un agente capofila costruisce ogni porzione dell'epic su un unico branch, con un checkpoint dopo ogni porzione. Testi e rilasci l'intera feature una volta sola | Una feature le cui porzioni hanno senso solo insieme, o che preferisci giudicare nel suo insieme |
| **Cosa conta come codice di produzione** (`production_paths`, `non_production_paths`) | Dice agli agenti e a te cosa gira per gli utenti, così le note di un prototipo e `haam.py production` mostrano cosa toccherebbe una modifica. Prototipi, test e documentazione ne sono fuori per impostazione predefinita | Restringilo quando il tuo prodotto vive in poche cartelle: `config --production "src/**,api/**" --human`. Aggiungi le cartelle che non girano mai per gli utenti con `config --not-production "…" --human`. Se la tua documentazione è ciò che vedono gli utenti, toglila dall'elenco con `config --remove-not-production "docs/**" --human` |

Qualunque sia la modalità, ogni modifica che va in merge supera tutti i gate. La protezione dietro questo principio:
- un prototipo non va mai in merge: il gate di rilascio rifiuta i branch `spike/` e qualsiasi cosa sotto `prototypes/`, e `publish` rifiuta gli spike;
- il codice di un prototipo tenuto arriva agli utenti solo tramite `/spec`, un branch normale e il tuo test, dietro un feature flag disattivato per impostazione predefinita. Non prende mai la corsia senza UAT: il gate vede i suoi commit `spike:`;
- il codice di produzione non importa mai da `prototypes/`, e il revisore AI lo blocca se lo fa;
- un prototipo non modifica mai le aree protette, e `/test` ti mostra i file protetti che ha modificato e le nuove dipendenze prima di eseguire qualsiasi cosa;
- le aree protette ricevono sempre la tua code review;
- nessun agente tocca sistemi o dati di produzione, in nessuna modalità.

## Fonti
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (i piani che li includono) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (revisori obbligatori sui repository privati) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
