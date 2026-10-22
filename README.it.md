# HAAM: Human-Agent Agile Methodology

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Italiano** · [Nederlands](README.nl.md) · [Português](README.pt.md)

**Le persone decidono. Gli agenti eseguono. Tutto vive in Git e nel tuo tracker.**

HAAM è una metodologia e un kit open per sviluppare software con agenti di coding AI, dall'idea alla produzione, senza perdere il controllo. Dà a ogni agente le stesse regole, gli stessi comandi e gli stessi gate, qualunque sia lo strumento in cui gira: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI o GitHub Copilot**. Il lavoro si traccia su una board di **GitHub Projects** (gratuita) o in **Linear**, a tua scelta. Più persone, ognuna con il proprio agente e il proprio account, possono lavorare sullo stesso prodotto in parallelo.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## Cosa ottieni

- **Un ciclo di vita con cinque gate umani**: decidere l'idea, approvare la specifica, controlli automatici con revisione AI indipendente, test di accettazione da parte di una persona, approvazione per la produzione. Ogni gate si può scavalcare in caso di emergenza, e ogni override viene registrato e seguito.
- **Tre flussi di lavoro** da cui gli agenti attingono: bug, feature pronte e idee da valutare. Il tracker (GitHub Projects o Linear) contiene il backlog, le priorità e lo stato.
- **20 skill condivise** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), nel formato aperto Agent Skills.
- **Le tue impostazioni, i tuoi compromessi:** `/haam-settings` permette al product owner di scegliere quando girano la CI e le revisioni AI (su ogni PR, in locale, solo per le aree protette o mai), cosa testa di persona, come si raggruppa il lavoro (per issue, per epic o in un'unica PR di release), se i deploy aspettano un'approvazione, e i limiti, ognuno con il suo compromesso e con i numeri del progetto.
- **Test in una parola, prima che qualcosa costi minuti di CI**: scrivi `/test`, prova la modifica dell'agente sul tuo computer, rispondi `pass` (solo allora la pull request viene aperta e controllata, una volta sola, esattamente su ciò che hai testato) e poi `ship` (l'agente fa il merge, il deploy e la chiude), oppure di' semplicemente cosa non va (torna subito agli agenti e ritorna da te quando è corretta). `/test all` prende tutto ciò che è in attesa in una sola sessione, e `ship --all` lo rilascia con un'unica approvazione.
- **Una corsia senza UAT** per le modifiche che non puoi testare in modo significativo (configurazione, aggiornamenti di dipendenze, refactoring invisibili): marca la issue `uat:skip` una volta, e la sua PR va in merge da sola quando la CI ed entrambe le revisioni AI passano.
- **Epic con un agente che fa le domande giuste**: `/triage group` trasforma un mucchio di issue sparse in epic (una per feature); `/epic` le legge una per una, scrive un breve brief, ti fa qualche domanda mirata e poi mette ordine nelle issue: duplicati, lacune, suddivisioni, ordine.
- **Spazio perché gli agenti costruiscano grandi pezzi in fretta, con una protezione:**
  - `/spike` costruisce un prototipo funzionante usa e getta da provare prima di decidere;
  - la modalità di build per epic permette a un agente di costruire una feature intera, porzione per porzione, con checkpoint, un solo test e una sola release;
  - ogni modifica che va in merge supera tutti i gate, e i prototipi non vanno mai in merge.
- **Una guida alle decisioni** ([DECISIONS.md](template/i18n/it/docs/setup/DECISIONS.md)): ogni scelta che un team fa quando adotta HAAM, con una raccomandazione per ciascuna. Copre gli account GitHub e il piano che ti serve, GitHub Projects o Linear, le impostazioni, come dimensionare i limiti in base al tuo tempo per i test e cosa proteggere. `/haam-setup` ti accompagna passo per passo.
- **Una guida per il product manager** ([PRODUCT-MANAGER.md](template/i18n/it/docs/process/PRODUCT-MANAGER.md)): ritmo giornaliero e settimanale, come fare il triage, regole di priorità con una matrice impatto × portata per i bug, dimensioni sane delle code, il tutto con un agente (`/triage`) o direttamente in GitHub Projects o Linear.
- **Agenti in parallelo senza collisioni**: apri una nuova finestra di chat, scrivi `/work bugs`, e l'agente ottiene la propria copia del progetto (un git worktree), prende il bug in cima e lo porta avanti fino al tuo test. Avviane quanti ne vuoi, su un computer o su più computer.
- **Code review in cui nessuno si corregge i compiti da solo**: una scansione dei secret prima di ogni commit e nella CI, audit delle dipendenze e due revisori AI indipendenti (specifica/qualità e sicurezza) che non hanno mai visto scrivere il codice. Le persone rivedono le aree protette e possono avere l'ultima parola.
- **Gate applicati da GitHub**, non dalla fiducia: regole sui branch, controlli obbligatori, un gate con etichetta UAT e approvazioni dei deploy, così reggono qualunque agente o persona stia facendo push.
- **Documentazione in sette lingue:** inglese, spagnolo, francese, tedesco, italiano, olandese e portoghese. Scegline una all'installazione (`install --language es`) e anche gli agenti scriveranno in quella lingua specifiche, issue, piani di UAT e messaggi; comandi, etichette e codice restano in inglese.
- **Uno strumento di setup** (`haam.py`, Python 3, nessuna dipendenza) che installa il kit in un repo esistente senza sovrascrivere nulla, configura GitHub e il tracker (GitHub Projects o Linear), dà agli agenti un unico set di comandi per la board, fa l'onboarding degli sviluppatori, verifica il setup e aggiorna i progetti alle nuove versioni del kit.

## Avvio rapido

### Adotta HAAM nel tuo progetto (amministratore del progetto, circa mezza giornata)

1. Prendi una versione rilasciata del kit:
   ```bash
   git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (oppure scarica lo zip da [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Apri il tuo agente di coding **nella cartella principale del progetto** e scrivi:
   > Leggi `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` e seguilo per configurare HAAM in questo repository. Il kit si trova in `~/haam-kit/template`.

L'agente installa il kit su un branch, ti fa qualche domanda, compila le informazioni sul progetto a partire dal tuo codice e ti guida nella configurazione di GitHub e del tuo tracker. Ti mostra ogni modifica prima di farla. Tutto ciò che riguarda una password o una chiave API lo fai tu, nel tuo terminale, mai attraverso la chat dell'agente.

Preferisci farlo a mano? Segui [la guida all'adozione](template/i18n/it/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Unisciti a un progetto che usa già HAAM (sviluppatore, circa un'ora)

Clona il progetto, apri il tuo agente al suo interno ed esegui `/haam-onboard` (Codex: `$haam-onboard`; altri strumenti: *"segui `.agents/skills/haam-onboard/SKILL.md`"*).

### Aggiorna un progetto a una nuova versione del kit

Prendi la nuova versione del kit, poi nel tuo progetto esegui `/haam-update`, oppure:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
I file che non hai mai modificato vengono aggiornati; quelli che hai personalizzato vengono mantenuti e, dove sono cambiati entrambi, la nuova versione viene messa da parte perché il tuo agente faccia il merge. Non si cancella nulla.

## Lo strumento di setup

| Comando | Chi | Cosa |
|---|---|---|
| `install --target DIR` | admin | Copia il kit in un repo. Non sovrascrive mai; unisce i file di impostazioni degli agenti; mette i conflitti in `.haam/incoming/`; registra la versione in `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Aggiorna un progetto a questa versione del kit, mantenendo le personalizzazioni |
| `config` | admin | Nome del prodotto, chiave del team Linear, repo, approvatori → `haam.config.json`; li applica a ogni file di HAAM |
| `agents [--apply]` | admin | Collega skill e Linear per Claude Code, Cursor, Codex, Grok, Gemini, Copilot |
| `github [--apply]` | admin | Etichette, ruleset dei branch con controlli obbligatori, approvazione per la produzione, funzionalità di sicurezza |
| `github-project [--apply]` | admin | Board di GitHub Projects: 12 stati, campo Priority, etichette, collegamento al repo |
| `linear [--apply]` | admin, nel proprio terminale | Team Linear, triage, 12 stati, 9 etichette |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agenti | Lavora sulla board di GitHub Projects da qualsiasi strumento agente |
| `exclusive "<who>" -- <command>` | agenti | Esegue una sessione di test pesante (che usa una risorsa condivisa da tutta la macchina) quando su questa macchina non ne gira un'altra |
| `capacity` | agenti | Ferma il nuovo lavoro quando ci sono troppe PR aperte o in attesa del tuo test (limiti in `haam.config.json`) |
| `ci-usage [--days 7]` | admin | Dove sono finiti i minuti di GitHub Actions, per workflow, job, trigger e giorno |
| `settings [--explain] [--set key=value] [--apply]` | owner/admin | Le tue scelte: quando girano la CI e le revisioni AI, cosa testi, raggruppamento, rilascio, limiti (`/haam-settings` ti guida) |
| `local-ci ISSUE` | owner | Con `ci: local`: esegue `make check` qui sul commit della PR e pubblica il risultato (ship lo fa per te) |
| `review ISSUE` | agenti | Le due revisioni AI in sessioni locali nuove, pubblicate come stati della PR (quando le revisioni sono locali) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Porta una modifica su questa macchina per testarla; dopo `pass` + `ship`: merge, approva il deploy (uno per più modifiche), attende, chiude |
| `worktree status\|new\|prep\|list\|clean` | agenti, chiunque | Un worktree per ogni chat di agente; copia i file locali da `.worktreeinclude`; fa pulizia di quelli finiti |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Invita uno sviluppatore (scrittura su GitHub, non admin; accesso alla board o al team Linear) |
| `dev [--apply] [--run-checks]` | sviluppatore | Verifica della macchina, hook di commit, `.env` dall'esempio, controlli del progetto |
| `doctor [--role admin] [--check-updates]` | chiunque | Cosa è fatto, cosa manca e chi deve farlo |
| `version [--check]` | chiunque | Versioni dello strumento, del progetto e dell'ultimo kit rilasciato |

Ogni comando mostra prima un piano e cambia le cose solo con `--apply`. Aggiungi `--json` per un output leggibile da una macchina.

## Più agenti contemporaneamente

Ogni chat di agente ha la propria cartella, così le chat non si sovrascrivono mai il lavoro a vicenda:

1. Apri una nuova finestra di chat (Claude Code in VS Code: Cmd/Ctrl+Shift+Esc).
2. Scrivi `/work bugs` (oppure `/work features`, `/work specs`, `/work ideas`, o semplicemente `/work`; Codex: `$work`).
3. L'agente si sposta nel proprio git worktree, copia i file locali come `.env`, prende in carico l'elemento in cima alla board, lo costruisce e lo testa, apre la PR e ti consegna un piano di test.

Ripeti per tutti gli agenti che vuoi, su qualsiasi computer con il progetto clonato. La presa in carico sulla board impedisce a due agenti di prendere la stessa issue, che sia per costruirla, valutarla o scriverne la specifica. La tua chat resta nella cartella principale per idee, decisioni, test e release.

## Scegliere un tracker

| | GitHub Projects | Linear |
|---|---|---|
| Costo | Gratuito su ogni piano GitHub | Piano gratuito con limiti; a pagamento per utente |
| Dove | Accanto al tuo codice, un solo login | App separata |
| Gli agenti usano | `haam.py issue …` (qualsiasi agente) | Il server MCP di Linear |
| Ideale per | Progetti individuali e piccoli team, tenendo tutto in GitHub | Backlog più affollati, più team, pianificazione più ricca |

Stesso ciclo di vita, stessi gate e stesse skill in entrambi i casi, e puoi cambiare in seguito. Vedi [TRACKER.md](template/i18n/it/docs/process/TRACKER.md).

## Compatibilità con gli agenti

| | Regole | Skill | Richiamare una skill | Linear (se usato) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | da verificare al primo avvio | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` tramite `.gemini/settings.json` | per file | per file | per utente |
| GitHub Copilot | `AGENTS.md` | per file | per file | per utente |

Su GitHub Projects ogni agente usa gli stessi comandi `haam.py issue`, quindi non c'è nulla da collegare strumento per strumento. Dettagli e impostazioni sicure consigliate per ciascuno strumento: [AGENTS-SETUP.md](template/i18n/it/docs/setup/AGENTS-SETUP.md).

## Requisiti

- Un repository GitHub. I repository pubblici hanno tutto con il piano gratuito. Su quelli **privati**, le regole sui branch richiedono GitHub Pro o Team, e un approvatore obbligatorio sui deploy in produzione richiede GitHub Enterprise Cloud (senza, la decisione di rilascio è il tuo `ship`). [DECISIONS.md](template/i18n/it/docs/setup/DECISIONS.md) ha i dettagli.
- Un tracker: una board di GitHub Projects (gratuita, su qualsiasi piano GitHub) o un workspace Linear (qualsiasi piano)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Un secret Claude per gli agenti revisori della CI: un token di un piano Claude (`claude setup-token`) o una chiave API di Anthropic (a consumo; imposta un limite di spesa)
- Qualsiasi agente di coding supportato

## Struttura del repository

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  i18n/          The same docs in other languages
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Versionamento

HAAM segue il [versionamento semantico](https://semver.org):
- **Patch** (1.0.x): correzioni e modifiche di testo; `update` si applica senza problemi.
- **Minor** (1.x.0): nuove skill, controlli o documentazione; retrocompatibile.
- **Major** (x.0.0): modifiche che richiedono un passo di migrazione (ad es. stati di Linear rinominati o controlli obbligatori). Il [CHANGELOG](CHANGELOG.md) elenca i passi.

Installa sempre da un tag o da una release, non da `main`.

## Contribuire

Idee, segnalazioni di bug e pull request sono benvenute. Vedi [CONTRIBUTING.md](CONTRIBUTING.md). Problemi di sicurezza: vedi [SECURITY.md](SECURITY.md).

## Licenza

[MIT](LICENSE) © 2026 Jorge del Prado
