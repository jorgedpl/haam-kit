# Onboarding degli sviluppatori

Ti diamo il benvenuto. Questo repo è costruito da persone e agenti di coding che lavorano insieme secondo la **Human-Agent Agile Methodology (HAAM)**. Puoi usare lo strumento agente che preferisci: Claude Code, Cursor, Codex, Grok, Gemini o Copilot. Questa guida ti porta da zero alla tua prima issue in circa un'ora.

## La strada veloce: fatti guidare dal tuo agente

1. Clona il repo e apri il tuo strumento agente nella sua cartella principale:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Di' al tuo agente:
   - Claude Code, Cursor o Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Qualsiasi altro strumento: *"Leggi `.agents/skills/haam-onboard/SKILL.md` e seguilo."*

Verifica la tua macchina, gli accessi e la connessione al tracker, configura i tuoi hook locali e il `.env`, esegue i controlli del progetto, ti spiega come lavoriamo e ti suggerisce una prima issue. I passi che richiedono la tua password o le tue chiavi li fai tu, nel tuo terminale o nel tuo editor. Non incolli mai secret nella chat.

Preferisci farlo a mano? Le sezioni seguenti coprono gli stessi passi.

---

## 1. Da leggere prima (15 minuti)
1. `AGENTS.md`: le regole che ogni agente segue, qualunque sia lo strumento. Valgono anche per te.
2. `docs/process/LIFECYCLE.md`: flussi, stati, gate, chi fa cosa.
3. `docs/process/GATES.md`: checklist, code review e override.
4. `docs/product/PRODUCT.md` e `docs/product/ARCHITECTURE.md`: cosa stiamo costruendo e com'è strutturato.

## 2. Gli account che ti servono
| Account | Perché | Cosa chiedere |
|---|---|---|
| GitHub | Codice, PR, CI | Accesso in scrittura al repo |
| Tracker | Backlog e stato | **GitHub Projects:** accesso alla board (arriva con l'invito al repo). **Linear:** l'iscrizione al team **APP** |
| Il tuo strumento agente | Agente di coding | Il tuo account **personale** (Claude, Cursor, OpenAI, xAI…). Non condividere mai gli account |
| Servizi di test | Per far girare l'app in locale | Solo credenziali di test, dal product owner |

L'amministratore del progetto ti invita con un solo comando: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. **Non** riceverai credenziali di produzione; i deploy passano da GitHub con approvazione.

## 3. Installare gli strumenti
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (obbligatorio; senza, i commit vengono bloccati): macOS `brew install gitleaks`; altri: https://github.com/gitleaks/gitleaks/releases
- Il runtime del linguaggio di questo repo: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Il tuo strumento agente

Verifica tutto con: `python3 tools/haam/haam.py dev`

## 4. Far girare il codice
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Collegarsi al tracker
Controlla `"tracker"` in `haam.config.json`:
- **GitHub Projects:** esegui `gh auth refresh -s project` una volta, poi prova: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** segui la sezione del tuo strumento in `docs/setup/AGENTS-SETUP.md` (un solo accesso), poi chiedi al tuo agente: *"Elenca le issue Ready del team Linear APP."*

## 6. Le tue impostazioni personali (non condivise)
Note e preferenze personali vanno in file ignorati da git: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, o le impostazioni utente del tuo strumento. Non metterci mai regole condivise. Se qualcosa deve valere per tutti, proponi una modifica ad `AGENTS.md` tramite PR.

## 7. Il flusso di lavoro quotidiano
Qui sotto i comandi sono scritti `/name`; in Codex usa `$name`.

| Vuoi… | Fai così |
|---|---|
| Vedere cosa è in attesa | La vista del tracker **Agent queue** (da costruire) o **Waiting on me** |
| Avviare un agente in una nuova finestra di chat | `/work` (o `/work bugs`) |
| Iniziare a lavorare in questa chat | `/next`, oppure `/build APP-123` |
| Fare il triage e dare le priorità (product owner) | `/triage`, `/triage group`, `/epic`, e `docs/process/PRODUCT-MANAGER.md` |
| Registrare un'idea | `/idea …` |
| Segnalare un bug | `/bug …` |
| Trasformare un'idea approvata in una specifica | `/spec APP-123` |
| Testare una modifica (product owner) | `/test`, poi `pass` → `ship`, oppure di' cosa non va |
| Testare la modifica di qualcun altro (sviluppatore) | Segui `docs/uat/APP-123-*.md`, poi avvisa il product owner |
| Verificare il tuo setup | `python3 tools/haam/haam.py doctor` |

### Far girare agenti in parallelo
Apri una nuova finestra di chat per ogni agente e scrivi `/work` (oppure `/work bugs`, `/work features`, `/work specs`, `/work ideas`; Codex: `$work`). L'agente ottiene la propria copia del progetto (un git worktree sotto `.claude/worktrees/`), copia i file locali elencati in `.worktreeinclude` (come `.env`), prende l'elemento in cima e lo porta avanti fino al passaggio di consegne. Tieni la tua chat nella cartella principale per idee, decisioni e test.

- **Claude Code in VS Code:** nuova scheda di chat con Cmd+Shift+Esc (Mac) o Ctrl+Shift+Esc (Windows/Linux). In un terminale: `claude --worktree`.
- **Altri strumenti:** se lo strumento ha una propria opzione worktree o agenti in parallelo, usala; altrimenti `/work` crea il worktree e ti dice quale cartella aprire in una nuova finestra.
- **Un altro computer:** stessa cosa. La presa in carico sul tracker impedisce a due agenti di prendere la stessa issue; quando te lo chiede, dai un nome alla macchina, così il commento di presa in carico mostra dove sta girando.
- **Fai pulizia** dei worktree finiti ogni tanto: `python3 tools/haam/haam.py worktree clean` (piano), poi `--apply`.
- **Testare il branch di un agente:** il piano di UAT usa `git switch --detach origin/<branch>`, che funziona anche mentre il worktree dell'agente ha ancora il branch.

### Far lavorare gli agenti in modo semi-autonomo
- **Con supervisione:** scrivi `/next`, rivedi la sua scelta, lascialo lavorare. Il tuo strumento dovrebbe chiedere prima di fare push o aprire PR (vedi le impostazioni sicure in `docs/setup/AGENTS-SETUP.md`).
- **Senza supervisione:** un task programmato o un cron esegue il tuo agente headless con il prompt `/next` (Codex: `$next`). Prende solo lavoro che ha superato il suo gate, e si ferma alla UAT per una persona.
- Gli agenti si fermano a ogni gate umano per progettazione. Il tuo compito è tenere corta la vista **Waiting on me**.

## 8. Come viene revisionato il tuo lavoro
Ogni PR viene controllata da test, una scansione dei secret, un audit delle dipendenze e due revisori AI indipendenti (specifica/qualità e sicurezza) che non hanno mai visto scrivere il codice. Correggi i loro rilievi **Blocking**; se pensi che uno sia sbagliato, rispondi sulla PR e chiedi al product owner, che può scavalcarlo con l'etichetta `ai-review-overruled`. Le aree protette ricevono anche una revisione umana. Dettagli: `docs/process/GATES.md` § Come funziona la code review.

**Se ti capita di committare un secret vero:** avvisa subito il product owner. Va revocato e ruotato, anche se lo cancelli nel commit successivo.

## 9. Regole che vale la pena ripetere
- Niente push su `main`, niente merge, niente deploy da parte degli agenti.
- Niente secret o dati personali reali nel codice, nei test, nelle fixture, nel tracker o in chat. I dati personali sono protetti dalla legge (ad es. GDPR).
- Una issue → un branch → una PR, abbastanza piccola da revisionare in 15 minuti.
- Compila **Realizzato con (Built with)** in ogni PR (il tuo strumento e il modello).
- Se non è in Git o nel tracker, per la prossima persona non esiste.

## 10. Chiedere aiuto
- Domande sul processo: chiedi al tuo agente *"secondo LIFECYCLE.md, cosa dovrebbe succedere quando…"*
- Accessi e credenziali: il product owner.
- Migliorare il processo: apri una `/idea` con etichetta `area:process`. Le modifiche ad `AGENTS.md`, `.agents/`, alle cartelle di configurazione degli agenti e a `.github/` richiedono la revisione del product owner.
