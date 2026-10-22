## Issue
<!-- GitHub Projects: mantieni la riga qui sotto con il numero della issue (usa Refs, non Closes: la issue si chiude con /release). Linear: metti l'ID nel titolo della PR (APP-123: …). -->
Refs #

## Realizzato con (Built with)
<!-- Strumento agente e modello (ad es. Claude Code / Opus, Cursor / <modello>, Codex, Grok Build), oppure "persona". -->

## Cosa e perché
<!-- 2–4 frasi. Cosa è cambiato per l'utente, e perché. -->

## Criteri di accettazione → test
| AC | Test | Stato |
|---|---|---|
| AC1 | `test_…` | ✅ |

## Come verificare
- Piano di UAT: `docs/uat/<GH-123 or APP-123>-*.md` (aggiunto da `/uat`)
- Screenshot / note:

## Rischi
- Aree protette toccate: nessuna / <elenco> (se ce ne sono → etichetta `human-review`)
- Migrazioni: nessuna / <descrizione + rollback>
- Modifiche di configurazione / variabili d'ambiente: nessuna / <elenco>

## Checklist (G3)
- [ ] `make check` passa in locale
- [ ] Ogni criterio di accettazione ha un test
- [ ] Nessuna modifica estranea
- [ ] Documentazione aggiornata (ARCHITECTURE.md, .env.example, …) oppure non necessaria
- [ ] Nessun secret né dato personale reale

<!-- Gate di rilascio (G4): questa PR può andare in merge solo con l'etichetta `uat-passed`, oppure con `gate-override` più un commento "OVERRIDE: <reason>". Le PR di sola documentazione sono esenti. -->
