# Strumenti agente: setup per strumento

HAAM funziona con qualsiasi agente di coding. Ogni strumento legge le **stesse regole** (`AGENTS.md`) e le **stesse skill** (`.agents/skills/`), e lavora sullo **stesso tracker**: una board di GitHub Projects (tramite `python3 tools/haam/haam.py issue …`, che qualsiasi agente può eseguire) o Linear (tramite il suo server MCP, `https://mcp.linear.app/mcp`). Cambia solo l'impianto.

Esegui `python3 tools/haam/haam.py agents` per vedere cosa è collegato in questo repo, e `python3 tools/haam/haam.py dev` per verificare la tua macchina.

## Come ogni strumento recepisce HAAM

| | Regole | Skill | Richiamare una skill | MCP di Linear (solo progetti Linear) | Skill riservate alle persone |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importa `AGENTS.md` | `.claude/skills` (link a `.agents/skills`) | `/build APP-1` | `.mcp.json` (nel repo) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (nel repo) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | per utente: `codex mcp add` | `agents/openai.yaml` in ogni skill |
| **Grok Build** | da verificare al primo avvio (vedi sotto) | `.grok/skills` (link a `.agents/skills`) | `/build APP-1` | legge `.mcp.json` | secondo il testo della skill |
| **Gemini CLI** | `AGENTS.md` tramite `.gemini/settings.json` | segue `SKILL.md` per nome | "segui .agents/skills/build" | per utente | secondo il testo della skill |
| **GitHub Copilot** | `AGENTS.md` | segue `SKILL.md` per nome | "segui .agents/skills/build" | per utente | secondo il testo della skill |

Se uno strumento non carica le skill, digli: *"Apri `.agents/skills/<name>/SKILL.md` e seguilo."* Le skill sono semplice Markdown.

## Collegarsi al tracker (una volta per persona)

**GitHub Projects:** niente da installare nel tuo agente. Esegui `gh auth refresh -s project` una volta, e prova con `python3 tools/haam/haam.py issue list`. Il resto di questa sezione riguarda i progetti **Linear**.

Linear ti fa accedere con il tuo account (OAuth). Gli agenti agiscono come te.

- **Claude Code:** apri `claude` nel repo → approva il server `linear` → `/mcp` → **linear** → accedi.
- **Cursor:** Settings → MCP → `linear` compare da `.cursor/mcp.json` → attivalo → accedi.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp`, poi segui la richiesta di accesso.
- **Grok Build:** legge `.mcp.json`; altrimenti, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Accedi quando richiesto.
- **Gemini CLI / Copilot / altri:** aggiungi nelle impostazioni MCP dello strumento un server MCP remoto chiamato `linear` con URL `https://mcp.linear.app/mcp`.

**Prova:** chiedi al tuo agente *"Elenca le issue Ready del team Linear APP."*

## Più agenti contemporaneamente

Ogni chat di agente che modifica file ha bisogno della propria cartella (un git worktree), altrimenti le chat si sovrascrivono il lavoro a vicenda. Avvia ogni chat di agente con `/work` (Codex: `$work`): controlla dove si trova e, se serve, prepara un worktree. La tua chat resta nella cartella principale.

| Strumento | Nuova chat di agente |
|---|---|
| **Claude Code (VS Code)** | Nuova scheda di chat: Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux), oppure Command Palette → "Claude Code: Open in New Tab". Scrivi `/work`; Claude si sposta da solo in un worktree. |
| **Claude Code (terminale)** | `claude --worktree` (oppure `-w <name>`), poi `/work`. |
| **App desktop di Claude** | Avvia una sessione con l'opzione **worktree**, poi `/work`. |
| **Codex, Cursor, altri** | Usa l'opzione worktree o agenti in parallelo dello strumento, se ce l'ha, poi `/work`. Altrimenti scrivi `/work` nella cartella principale: crea un worktree con `haam.py worktree new` e ti dice quale cartella aprire in una nuova finestra. |

I file locali che non sono in Git (come `.env`) vengono copiati in ogni nuovo worktree dall'elenco in `.worktreeinclude`. Fai pulizia dei worktree finiti con `python3 tools/haam/haam.py worktree clean` (piano), poi `--apply`.

## Impostazioni sicure per strumento

Le protezioni rigide stanno in GitHub e in git, quindi ti proteggono **qualunque cosa faccia lo strumento**: niente push su `main`, controlli obbligatori, etichetta UAT, approvazione dei deploy, l'hook dei secret al commit (`make hooks`) e la scansione dei secret nella CI. Le impostazioni dello strumento sono un secondo livello che ferma gli errori prima. Consigliate:

| Strumento | Impostazioni consigliate |
|---|---|
| **Claude Code** | Già configurato in `.claude/settings.json`: chiede prima di push/PR, blocca merge/deploy/letture di `.env`, hook di scansione dei secret prima dei commit. Lascialo così. |
| **Cursor** | Auto-run dell'agente: usa una allow-list (target make, git status/diff/log, `gh pr view/checks`) e richiedi conferma per `git push`, `gh pr create/edit/merge`, e tutto ciò che contiene `deploy`. Aggiungi `.env*` all'elenco ignore di Cursor così l'agente non può leggerlo. |
| **Codex** | Sandbox *workspace-write* e politica di approvazione *on-request* (chiede prima delle azioni di rete e dei push). Evita le modalità "full access" in questo repo. |
| **Grok Build** | Usa le sue regole di permesso (consentite a livello di repo) per richiedere l'approvazione per `git push`, `gh pr merge` e i comandi di deploy; nega la lettura di `.env*`. Supporta gli hook `PreToolUse`: puoi chiamare `bash scripts/scan-secrets.sh` prima di `git commit`, come fa l'hook di Claude. Evita `--always-approve` fuori dalla CI. |
| **Gemini CLI / Copilot** | Tieni attive le conferme per i comandi di shell; non approvare mai automaticamente push o merge. |

Non dare mai a nessuno strumento agente le tue credenziali di produzione o un token GitHub con diritti da amministratore.

## Verifica al primo avvio per ogni strumento

Chiedi all'agente, nel repo:
1. *"Quali sono le regole rigide di questo repository?"* Dovrebbe elencare le regole di `AGENTS.md` §3. Se non lo fa, digli di leggere prima `AGENTS.md`, e controlla nelle impostazioni dello strumento il nome del file di istruzioni.
2. *"Quali skill hai per questo progetto?"* Dovrebbe elencare idea, bug, assess, spec, next, work, build, uat… Se non lo fa, vedi la tabella sopra.
3. *"Elenca le issue Ready del team Linear APP."* Questo verifica la connessione a Linear.

## Registrare quale strumento ha fatto il lavoro
Il commento di presa in carico sulla issue e il campo **Realizzato con (Built with)** della PR registrano lo strumento e il modello. Dopo qualche settimana puoi confrontare per strumento i rilievi delle revisioni e le UAT fallite.

## Revisione tra modelli diversi
Gli agenti revisori della CI usano Claude. Quando il codice viene scritto con un altro strumento (Codex, Grok, Cursor con un altro modello), la revisione è anche tra modelli diversi, il che è un utile controllo in più.
