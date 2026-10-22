# Mappa dell'architettura

> Gli agenti la leggono all'inizio di ogni sessione (la importa `AGENTS.md`). È una **mappa**, non una documentazione completa: quanto basta perché un nuovo agente si orienti in due minuti.
> Gli agenti la tengono aggiornata: se la tua PR cambia la struttura o scopri un'insidia, aggiorna questo file nella stessa PR.
>
> **Primo setup:** chiedi al tuo agente di coding: *"Esplora questo repository e compila docs/product/ARCHITECTURE.md seguendo i titoli delle sue sezioni. Resta sotto le 150 righe."* Poi rivedila tu.

## Stack
- Linguaggio / framework: `TODO`
- Database: `TODO`
- Hosting / destinazione del deploy: `TODO`
- Servizi esterni principali: `TODO` (API, email, pagamenti, provider di autenticazione…)

## Struttura del repository
```
TODO: top-level folders and what lives in each
```

## Moduli principali
| Modulo / percorso | Responsabilità | Area protetta? |
|---|---|---|
| `TODO` | | |

## Modello dei dati (entità principali)
`TODO`

## Ambienti
| Ambiente | URL | Come viene fatto il deploy |
|---|---|---|
| Locale | http://localhost:`TODO` | `make dev` |
| Produzione | `TODO` | GitHub Actions `deploy.yml`, approvazione richiesta |

## Configurazione
- Le variabili d'ambiente sono documentate in `.env.example` (non committare mai valori reali).

## Test
- Gli unit test stanno in `TODO`, si eseguono con `make test`.
- Fixture di test sintetiche: `TODO` (non usare mai dati personali reali).
- E2E / browser: `TODO`

## Insidie
- `TODO`: cose che hanno già messo in difficoltà agenti o sviluppatori.
