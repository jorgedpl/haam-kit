# modifiche

Un piccolo file per ogni modifica rilasciata, chiamato `<FILE-ID>.md` (ad es. `GH-12.md`), aggiunto da `/uat` sul branch della modifica, così viene rilasciato insieme a essa. Un file per modifica significa che le PR in parallelo non vanno mai in conflitto qui.

Ogni file contiene una o due righe che un utente capirebbe:

```
- #12: Export to CSV now works on mobile.
```

Per scrivere le note di rilascio o aggiornare `CHANGELOG.md`, chiedi a un agente di raccogliere i file aggiunti dall'ultima release.
