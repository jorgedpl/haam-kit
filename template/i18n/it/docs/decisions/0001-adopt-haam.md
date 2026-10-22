# ADR 0001: Adottare la Human-Agent Agile Methodology (HAAM)

- **Stato:** Accettata
- **Data:** YYYY-MM-DD
- **Chi decide:** Product owner

## Contesto
Il lavoro su questo prodotto è svolto sempre più da agenti di coding (Claude Code, Cursor, Codex, Grok e altri). Senza un processo condiviso, il contesto vive nelle singole chat, le priorità sono implicite, e un secondo sviluppatore con il proprio account Claude non può lavorare in parallelo. Abbiamo anche bisogno che le modifiche in produzione siano verificate da una persona prima del rilascio, con un modo per muoversi in fretta nelle emergenze.

## Decisione
- Il tracker (GitHub Projects o Linear, scelto per ogni progetto in `haam.config.json`) è il sistema di riferimento per gli elementi di lavoro, lo stato e la priorità. Git è il sistema di riferimento per specifiche, decisioni, piani di UAT e codice.
- Il lavoro segue HAAM come descritto in `docs/process/LIFECYCLE.md`, con cinque gate (`docs/process/GATES.md`).
- Gli agenti, qualunque sia lo strumento, seguono `AGENTS.md` e le skill condivise in `.agents/skills/`.
- I gate G3–G5 sono imposti da GitHub (protezione dei branch, controlli obbligatori, un environment `production` protetto). G1–G2 sono imposti per convenzione e tramite lo stato del tracker.
- Le persone possono scavalcare i gate con una motivazione registrata e una issue di follow-up automatica.

## Conseguenze
- Un po' più di formalità per le modifiche piccole, compensata dal fatto che gran parte della burocrazia la fanno gli agenti.
- Chiunque può riprendere qualsiasi issue partendo solo da tracker + Git.
- Richiede un tracker (una board di GitHub Projects, o un workspace Linear con la sua integrazione GitHub) e la protezione dei branch di GitHub su `main`.

## Alternative considerate
- **Solo GitHub Issues + Projects:** meno strumenti, ma triage, priorità e viste di pianificazione più deboli.
- **Jira:** più potente, ma più pesante di quanto serva a un piccolo team.
- **Nessun processo formale:** il più veloce oggi, non scala con agenti in parallelo o un secondo sviluppatore.
