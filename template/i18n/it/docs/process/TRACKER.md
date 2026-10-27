# Il tracker: Linear o GitHub Projects

HAAM funziona allo stesso modo con entrambi i tracker. `haam.config.json` → `"tracker"` dice quale usa questo progetto:

- **`github`**: issue in questo repository GitHub, su una board di GitHub Projects. Gratuito su ogni piano GitHub. Gli agenti usano `python3 tools/haam/haam.py issue …` (vedi sotto), che funziona da qualsiasi strumento agente.
- **`linear`**: issue in un team Linear. Gli agenti usano la connessione a Linear (MCP).

Le skill dicono "nel tracker"; questa pagina spiega come fare ogni operazione in ciascun tracker. **Se sei un agente: controlla `tracker` in `haam.config.json` una volta per sessione, poi usa la colonna corrispondente.**

## Concetti

| Concetto | GitHub Projects | Linear |
|---|---|---|
| ID della issue (scrivilo così) | `#123` | `APP-123` |
| Nome del branch | `123-short-title` | `app-123-short-title` (il nome di branch di Linear) |
| Messaggio di commit | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Titolo della PR | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Collegamento PR → issue | **`Refs #123`** nella descrizione della PR (non `Closes`: la issue si chiude con `/release`, dopo il deploy) | ID della issue nel titolo della PR |
| File della issue | `docs/specs/GH-123-slug.md` (lo stesso per valutazioni, UAT) | `docs/specs/APP-123-slug.md` |
| 12 stati | Campo **Status** della board | Stati del workflow del team |
| Priorità | Campo **Priority** della board (Urgent/High/Medium/Low) | Priorità nativa |
| Flussi, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Etichette delle issue | Etichette delle issue |
| Epic (raggruppa le issue di una feature) | Issue con etichetta `epic`; le sue issue sono **sub-issue** di GitHub | Issue con etichetta `epic`; le sue issue sono **sub-issue** (con il padre impostato) |
| Chi ci sta lavorando | Stato In Progress (in costruzione) o etichetta `claimed` (in valutazione, specifica in scrittura, prototipo in costruzione), più il commento di presa in carico. L'assegnatario da solo non distingue due chat della stessa persona | Uguale |
| Cambi di stato all'apertura/merge della PR | Workflow `tracker-sync.yml`: solo le issue in consegna (non le epic, non le PR di sola documentazione né gli spike) | Integrazione di Linear con GitHub |

## Operazioni

I comandi della colonna GitHub si eseguono dalla radice del repository. Aggiungi `--json` per un output leggibile da una macchina.

| Operazione | GitHub Projects | Linear (tramite MCP) |
|---|---|---|
| **Trovare lavoro** (code per `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (aggiungi `--label agent-ready` per le feature, `--label stream:bug` per i bug) | Elenca le issue del team per stato, etichetta, assegnatario |
| **Leggere una issue** | `haam.py issue view 123` | Get issue |
| **Creare un'idea** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (finisce in Triage) | Crea la issue, stato Triage, etichetta `stream:idea` |
| **Segnalare un bug** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Crea la issue, stato Triage, etichetta `stream:bug` |
| **Creare un'epic** | `haam.py issue create --epic --stream idea --title "…"` | Crea una issue con etichetta `epic` |
| **Mettere una issue in un'epic** | `haam.py issue link 14 --parent 9` | Imposta l'epic come padre della issue |
| **Creare una issue dentro un'epic** (ad es. porzioni della specifica, lacune) | `haam.py issue create --stream feature --parent 9 --title "…"` | Crea una sub-issue dell'epic |
| **I campi propri della board** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` li elenca con le loro opzioni. Impostali con `--field NAME=VALUE` su `issue create` o `issue edit` (ripetibile; un valore vuoto ne svuota uno; `Sprint=@current` è l'iterazione in corso oggi), e filtra con `issue list --field Area=Billing`. Un nome o un valore sbagliato viene rifiutato prima di cambiare qualsiasi cosa | I campi propri del team, con la connessione a Linear |
| **Togliere una issue da un'epic** | `haam.py issue unlink 14` | Rimuovi il padre della issue |
| **Riscrivere una issue** (titolo, descrizione) | `haam.py issue edit 14 --title "…" --body-file new.md` | Update issue |
| **Le issue di un'epic** | `haam.py issue children 9` (con l'avanzamento) | Elenca le sub-issue dell'epic |
| **Issue che non stanno in nessuna epic** | `haam.py issue list --open-only --no-parent --no-label epic` | Elenca le issue senza padre |
| **Prendere in carico** (prima di costruire, valutare o scrivere una specifica) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (build: rifiuta se è già presa in carico o non è Ready; `--force` per i bug corretti direttamente da Triage, solo quando la persona l'ha detto). Per valutare: aggiungi `--for assess`; per scrivere una specifica: `--for spec`. Stampa un id di presa in carico: conservalo | Ricarica la issue; se è In Progress, ha l'etichetta `claimed` o è assegnata a qualcun altro, fermati; altrimenti assegnala a te, imposta In Progress (build) o aggiungi l'etichetta `claimed` (valutazione, specifica), commenta con un id di presa in carico, rileggi i commenti (AGENTS.md §6) |
| **Costruire un prototipo** (`/spike`) | `haam.py issue claim 123 --for spike` (idee da Triage a Decision, feature in Backlog), poi, dopo il push: `issue label 123 --add spike-ready` e `issue release 123 --claim <id> --status Decision` (per una feature in Backlog: senza `--status`) | Presa in carico come sopra (etichetta `claimed`, un commento di presa in carico che dice "to build a prototype"), etichetta `spike-ready`, rilascio |
| **Codice di produzione in una modifica** | `haam.py production` (i file modificati da un branch che girano per gli utenti) | Uguale |
| **Rilasciare una presa in carico** (valutazione o specifica pubblicata; oppure la chat si ferma) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` al posto dell'id solo in `/triage stale` o `/test`) | Togli l'assegnatario, rimuovi `claimed`, imposta lo stato, commenta `🔓 Claim released` |
| **Cambiare stato** | `haam.py issue status 123 "UAT"` | Aggiorna lo stato della issue |
| **Stato riservato alle persone** (Done, Parked, Canceled, Decision→Backlog) | Uguale, più `--human`, **solo** dentro `/triage`, `/epic`, `/decide`, `/test`, `/release` o `/override` scritti da una persona | Stessa regola |
| **Priorità** | `haam.py issue priority 123 High` | Aggiorna la priorità |
| **Etichette** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` richiede anche `--human`, dopo che la persona ha approvato la specifica) | Aggiorna le etichette |
| **Commentare** | `haam.py issue comment 123 --body "…"` oppure `--body-file` | Crea un commento |
| **Rifiutare o segnare come duplicato** (in `/triage`, `/epic` o `/decide`) | `haam.py issue status 123 Canceled --human` (chiude anche la issue come non pianificata); commenta il motivo o l'ID dell'originale | Stato Canceled, commento |
| **Testare una modifica** (persona, in `/test`) | `haam.py checkout-pr 123`, poi `haam.py checkout-pr --back` | Uguale (il codice è comunque su GitHub) |
| **Aprire la PR dopo un superamento** (test-first, la persona ha detto `pass`) | `haam.py publish 123 --human`: fa push del commit testato, apre la PR con l'etichetta `uat-passed`, sposta la issue in In Review | `haam.py publish APP-123 --human` (`--label human-review` se la issue ce l'ha), poi sposta la issue in In Review e commenta, come indica l'output |
| **Registrare un test fallito** (la persona ha detto che è fallito) | `haam.py test-failed 123 --human`, poi etichetta `uat-failed`, stato Ready, nessun assegnatario | `haam.py test-failed APP-123 --human`, poi lo stesso in Linear |
| **Rilasciare dopo un superamento** (la persona ha detto `ship`) | `haam.py ship 123 --human`: merge, approvazione del deploy, attesa, chiusura | `haam.py ship APP-123 --human`, poi imposta Done in Linear |
| **Rilasciare tutto ciò che è pronto, con un solo deploy** | `haam.py ship --all --human` (oppure `ship 12 13 14 --human`): fa il merge di ciascuna, approva solo il deploy più recente, le chiude tutte | `haam.py ship APP-12 APP-13 --human` (elencale: `--all` non sa leggere Linear) |
| **Vedere o cambiare come gira HAAM** (owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (solo per scelta dell'owner) | Uguale |
| **Eseguire la CI qui** (impostazione `ci: local`) | `haam.py local-ci 123` (ship lo esegue per te) | Uguale |
| **Niente UAT per questa issue** (decisione dell'owner) | `haam.py issue label 123 --add uat:skip --human` | Etichetta `uat:skip` |
| **C'è spazio per nuovo lavoro?** (`/next` lo controlla prima) | `haam.py capacity` (la coda di UAT e le PR pronte rispetto a `max_in_uat`, `max_open_prs`, o all'aumento di una finestra di lotto; bozze e PR di sola documentazione non contano) | Stesso comando, con `--in-uat <count>` |
| **Il nuovo lavoro si scontrerà con ciò che è in attesa?** | `haam.py overlap --files src/auth/,src/api/users.py` (branch in UAT che modificano gli stessi file) | Uguale, con `--branch <name>` per ogni branch in UAT |
| **PR a lotto** (i bug di un'epic) | Titolo `#12 #13 #14: …`, una riga `Refs #n` per ogni issue; `ship` le chiude tutte | Titolo `APP-12 APP-13: …` |
| **Chiudere dopo il rilascio** | `haam.py issue close 123 --human` (imposta Done e chiude; solo `/release`) | Stato Done |

## Regole valide per entrambi

- Ogni lavoro ha una issue nel tracker; niente si traccia altrove.
- Se il tracker non è raggiungibile, fermati e avvisa la persona.
- Il protocollo di presa in carico è ciò che impedisce a due chat di agenti (o a due macchine) di costruire, valutare o specificare la stessa cosa. Non saltarlo mai.
- Gli spostamenti riservati alle persone avvengono solo dentro le skill riservate alle persone, e su GitHub lo strumento chiede `--human` come promemoria. Gli agenti agiscono con il login dell'owner, quindi GitHub non può sapere chi ha impostato un'etichetta dell'owner (`uat:skip`, `mode:prototype`, `mode:epic-build`): è una regola, verificata dallo strumento su GitHub Projects e da niente su Linear. Un agente che la violasse con un semplice `gh` potrebbe, con `uat:skip`, far saltare il tuo test a una modifica fuori dalle aree protette; la CI ed entrambe le revisioni AI girano comunque, e i deploy aspettano comunque te dove il tuo piano lo consente.

## Setup di GitHub Projects (admin, una volta)

1. `gh auth refresh -s project` (permette al tuo login GitHub di usare Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (piano), poi `--apply`: crea la board con il nome del prodotto, collega il repo, imposta i 12 stati e il campo Priority, crea le etichette.
4. **Token di automazione** (per `tracker-sync.yml` e per l'auto-merge nella corsia senza UAT): crea un token classic su github.com/settings/tokens con gli scope `project` e `repo` (`public_repo` basta per un repository pubblico), poi `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Senza, tutto funziona, ma le schede non si spostano da sole quando le PR si aprono o vanno in merge, e la corsia senza UAT non può attivare l'auto-merge (il gate usa questo token, perché un merge fatto con il token del workflow stesso non farebbe partire il deploy). Sui progetti Linear la corsia non fa mai auto-merge, quindi lì il token non serve.
5. **Nel browser**, sulla board: crea le viste salvate che il setup elenca (Board grouped by Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics), e attiva il workflow integrato della board **Auto-add to project** per questo repository (board → Workflows). Mette sulla board, gratis, le issue create sul sito di GitHub; `haam.py issue create` aggiunge da sé le proprie. **Disattiva** il workflow integrato **Item closed → Status: Done**: sovrascrive `Canceled` dopo che `issue status … Canceled` chiude l'issue, e `ship` imposta già Done da solo.
6. Ogni sviluppatore esegue `gh auth refresh -s project` una volta; `/haam-onboard` lo verifica.

## Cambiare tracker in seguito

Imposta `"tracker"` con `haam.py config --tracker …`, esegui il setup del nuovo tracker, poi chiedi al tuo agente di copiare le issue aperte (sa leggere un tracker e scrivere nell'altro). Tieni il vecchio tracker in sola lettura per lo storico.
