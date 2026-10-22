# Specifica: <ID> <titolo>

- **Issue:** <#123 o APP-123> · **Valutazione:** docs/assessments/<FILE-ID>-*.md · **ADR:** <link o nessuna>
- **Stato:** Bozza / Approvata · **Approvata da:** <persona> il YYYY-MM-DD
- **Aree protette:** nessuna / <elenco> → `human-review`

## 1. Obiettivo
<!-- Un paragrafo: cosa cambia, per chi, e perché. -->

## 2. User story
- Come <ruolo>, voglio <capacità>, così da <beneficio>.

## 3. Criteri di accettazione
<!-- Ogni criterio deve essere testabile. Numerali; i test e i passi di UAT fanno riferimento a questi numeri. -->
**AC1:** <nome>
- Given …
- When …
- Then …

**AC2:** …

## 4. Fuori ambito
- 

## 5. Note di progettazione
- **File / moduli che probabilmente verranno toccati:** 
- **Modello dei dati / migrazioni:** nessuna / <descrivi, compresi backfill e reversibilità>
- **Configurazione / variabili d'ambiente:** nessuna / <nomi, e aggiungile a .env.example>
- **API esterne:** 
- **Note sulla UI / testi:** 
- **Stati di errore e casi limite:** 

## 6. Piano di test
| AC | Test unitari / di integrazione | Note |
|---|---|---|
| AC1 | `test_…` | |

**Traccia della UAT:** <cosa cliccherà una persona in locale>

## 7. Rollout e rollback
- **Feature flag:** nessuno / <nome>
- **Rollout:** 
- **Rollback:** <basta una PR di revert? ci sono dati da ripulire?>

## 8. Porzioni (se divisa)
| Sotto-issue | Ambito | Dipende da |
|---|---|---|

## 9. Domande aperte
1. 
