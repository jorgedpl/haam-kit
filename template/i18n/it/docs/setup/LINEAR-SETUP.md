# Setup di Linear (una volta sola, ~30 minuti, amministratore del workspace)

> **Solo se il tuo tracker è Linear** (`"tracker": "linear"` in `haam.config.json`). Usi GitHub Projects? Esegui invece `python3 tools/haam/haam.py github-project` e vedi `docs/process/TRACKER.md`.

Questo configura Linear in modo che corrisponda a `docs/process/LIFECYCLE.md`. Fallo una volta; poi ogni sviluppatore e ogni agente usa la stessa struttura.

> **Automatizzato:** le sezioni 1–4 le esegue `python3 tools/haam/haam.py linear --apply`, che lanci tu nel tuo terminale (chiede in modo sicuro la tua chiave API personale di Linear e non la salva mai). Questa pagina è l'equivalente manuale, più le sezioni 5–9 che esistono solo nell'app web di Linear.

## 1. Team
- Crea (o riusa) un team con il nome del tuo prodotto e un identificativo breve (gli esempi usano **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` sostituisce `APP` in ogni file di HAAM.
- Invita ogni persona che contribuisce con il proprio account Linear. Gli agenti agiscono come la persona che li usa, quindi non servono postazioni separate per gli agenti.

## 2. Stati del workflow
Team settings → **Workflow**. Crea questi stati, in quest'ordine, nella categoria indicata:

| Stato | Categoria | Note |
|---|---|---|
| Triage | Triage | Attiva il Triage per il team |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Impostalo come predefinito per le nuove issue fuori dal triage |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Cancella o rinomina gli stati predefiniti di Linear (`Todo`, `Duplicate`, ecc.) così che restino solo questi. I nomi devono corrispondere esattamente; le skill vi fanno riferimento per nome.

## 3. Etichette
Team settings → **Labels**. Crea queste etichette (semplici, senza bisogno di un gruppo):
- `stream:idea`
- `stream:feature`
- `stream:bug`

E queste etichette indipendenti:

| Etichetta | Significato | Chi la applica |
|---|---|---|
| `agent-ready` | Ha superato il G2; gli agenti possono costruirla | L'agente, solo dopo che una persona ha approvato la specifica |
| `human-review` | Tocca un'area protetta; serve una code review umana | Agente o persona |
| `human-only` | Gli agenti non devono prenderla | Persona |
| `override-followup` | Creata dopo un override di un gate | `/override` |
| `epic` | Issue padre che raggruppa le sotto-issue di una feature | `/triage group`, `/epic`, o una persona |
| `uat-failed` | Ha fallito il test umano; gli agenti la rilavorano con precedenza | `/test`, `/uat-result` |
| `uat:skip` | L'owner ha deciso: niente test da parte sua | `/triage`, oppure "spec approved, no UAT" |
| `claimed` | Una chat di agente la sta valutando, ne sta scrivendo la specifica o sta costruendo un prototipo | L'agente, mentre lavora |
| `mode:prototype` | L'owner ha deciso: prima si costruisce un prototipo usa e getta (`/spike`) | `/triage` |
| `mode:epic-build` | L'owner ha deciso: un agente capofila costruisce tutta questa epic | `/decide` |
| `spike-ready` | Un prototipo è pronto da provare per l'owner | `/spike` |

Facoltativo: etichette di area (`area:onboarding`, `area:billing`, `area:checkout`…) per filtrare la board.

## 4. Priorità
Usa la priorità nativa di Linear (Urgent / High / Medium / Low / No priority). Non servono campi personalizzati.

## 5. Template delle issue
Team settings → **Templates** → crea tre template di issue, incollando il corpo da:
- **Idea**: `docs/templates/idea.md` · etichetta predefinita `stream:idea` · stato Triage
- **Bug**: `docs/templates/bug.md` · etichetta predefinita `stream:bug` · stato Triage
- **Feature**: un corpo breve con il link alla specifica · etichetta predefinita `stream:feature` · stato Backlog

Gli agenti li compilano da soli tramite `/idea` e `/bug`; i template servono alle persone che creano issue nell'app di Linear.

## 6. Integrazione con GitHub
Settings → **Integrations → GitHub** → collega l'organizzazione/il repo.

Poi in team settings → **Workflow → Pull request automations** (la dicitura può variare leggermente):

| Evento GitHub | Sposta la issue in |
|---|---|
| Branch creato / PR in bozza aperta | In Progress |
| PR pronta per la revisione (gli agenti aprono bozze e le marcano come pronte quando sono complete) | In Review |
| PR pronta per il merge | *(nessun cambiamento, la spostano gli agenti in UAT)* |
| PR unita | Deploying |

**Formato dei nomi dei branch:** `{issue-identifier}-{issue-title}` (in minuscolo), ad es. `app-123-bulk-invite-users`. Togli il prefisso con il nome utente, così i branch sono uguali chiunque li crei.

Attiva **"link PRs by issue ID in title"** così i titoli di PR del tipo `APP-123: ...` si collegano automaticamente.

## 7. Viste (filtri salvati)
Crea queste viste di team così le persone vedono cosa le aspetta:

| Vista | Filtro |
|---|---|
| **Triage** | La casella Triage nativa di Linear (la casella quotidiana del product owner; vedi `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Stato in (Decision, UAT), più le issue in Backlog con un commento `📝 Spec ready for review` |
| **Agent queue** | Stato = Ready, etichetta `agent-ready` o `stream:bug`, non assegnate |
| **Ideas inbox** | Stato in (Triage, Discovery), etichetta `stream:idea` |
| **Bugs** | Etichetta `stream:bug`, non Done/Canceled, ordinate per priorità |
| **Epics** | Etichetta `epic`, non Done/Canceled (mostra l'avanzamento delle sotto-issue) |
| **Overrides to close** | Etichetta `override-followup`, non Done |

## 8. Notifiche
Ogni persona: Settings → Notifications → assicurati di ricevere le notifiche per le **menzioni** e per le **issue assegnate a te**. `/uat` menziona il product owner quando qualcosa è pronto da testare.

## 9. Collega a Linear lo strumento agente di ogni persona
Ogni persona fa il login una volta dal proprio strumento (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Passi per strumento: `docs/setup/AGENTS-SETUP.md`.
Prova: chiedi all'agente *"elenca le mie issue Linear aperte nel team APP"*.

Se usi anche un'app di chat (Claude, ChatGPT…) con un connettore Linear, collega anche quella, così puoi raccogliere idee dal telefono.
