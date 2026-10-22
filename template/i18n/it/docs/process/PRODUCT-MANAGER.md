# Lavorare come product manager

*Una guida per la persona che decide cosa si costruisce. Gli agenti non hanno bisogno di leggerla; tu sì.*

In HAAM tu decidi **cosa** e **perché**; gli agenti capiscono **come** e lo fanno. Gli agenti sono veloci, quindi la velocità dell'intero sistema dipende da quanto in fretta fai il triage, decidi, approvi e testi. Il tuo compito principale è tenere corta la coda **Waiting on me** e tenere la **Agent queue** puntata sulle cose giuste.

Gli esempi usano gli ID di GitHub Projects (`#12`); su Linear lo stesso elemento è `APP-12`. I comandi sono scritti `/name`; in Codex usa `$name`.

---

## 1. Il tuo lavoro in una pagina

| Cosa fai solo tu | Quanto spesso | Con l'AI | Direttamente nel tracker |
|---|---|---|---|
| Tenere aggiornato `docs/product/PRODUCT.md`: priorità attuali, punti non negoziabili, percorsi principali | Ogni mese | "Aggiorna PRODUCT.md: ora le nostre priorità sono…" | Modifica il file (tramite una PR) |
| Fare il triage di nuove idee e bug | Ogni giorno | `/triage` | Vista Triage: priorità, stato, etichette |
| Raggruppare le issue correlate in epic e rispondere alle domande dell'agente su ciascuna | Ogni settimana | `/triage group`, poi `/epic #9` | Issue epic (etichetta `epic`) con sub-issue |
| Impostare e cambiare le priorità | Ogni giorno e ogni settimana | `/triage`, `/triage backlog` | Campo Priority |
| Decidere sulle idee valutate (G1) | Ogni settimana | `/decide #12 approve high` | Stato, etichette, commento (§7–8) |
| Approvare le specifiche (G2) | Man mano che arrivano | Leggi la specifica (collegata nella issue), poi "spec for #12 approved" | Commenta "spec approved"; stato Ready, etichetta `agent-ready` |
| Testare le modifiche (G4) e rilasciarle (G5) | Ogni giorno | `/test`, poi rispondi `pass` → `ship`, oppure di' cosa non va | GitHub: etichetta `uat-passed`, merge, approvazione del deploy |
| Chiudere i follow-up degli override | Ogni settimana | "Mostrami i follow-up degli override ancora aperti" | Vista: etichetta `override-followup` |

Tutto ciò che decidi finisce nel tracker o in Git, mai solo in una chat. Se non è scritto lì, il prossimo agente non lo sa.

---

## 2. Il tuo ritmo

### Ogni giorno (10–15 minuti)
1. **Prima i test.** Scrivi `/test all`: l'agente ti guida in ogni modifica che ti aspetta, una dopo l'altra (§2a), poi rilascia tutto ciò che è passato con un solo deploy. Gli agenti non possono finire finché non lo fai tu, e il loro contesto invecchia.
2. **Svuota la casella Triage** (`/triage`, o la vista Triage). Niente dovrebbe restarci per più di due giorni lavorativi.
3. **Bug urgenti:** se ce n'è uno, avvia subito un agente: nuova finestra di chat, `/work bugs`.
4. Scorri i commenti di passaggio di consegne e quelli "blocked" degli agenti e rispondi alle loro domande.

### 2a. Testare una modifica: il ciclo completo
1. Scrivi **`/test`** (o `/test #12`). L'agente porta la modifica sul tuo computer, avvia l'app e ti dà il link e una breve checklist: *fai questo → dovresti vedere quello*.
2. Provala. Poi rispondi con una parola o una frase:
   - **`pass`** → l'agente apre la pull request (fino a ora non c'era: hai testato il branch dell'agente), i controlli girano una volta esattamente su ciò che hai testato, e ti chiede *"La rilascio quando i controlli passano?"* Rispondi **`ship`**: aspetta i controlli, fa il merge, approva per te il deploy in produzione e chiude la issue. Ricevi *"#12 è in produzione."* Rispondi `later` per tenerla in sospeso.
   - Se il tuo progetto **fa il deploy a mano** (`"deploy": "manual"`), l'agente fa il merge e poi ti chiede di fare il deploy; rispondi **`live`** quando è online e lui chiude la issue.
   - Se poi i controlli o le revisioni trovano un problema, la modifica torna agli agenti come un test fallito, e ritorna da te una volta corretta.
   - **Cosa è andato storto** (*"passo 3: il pulsante di esportazione manca ancora su mobile"*) → l'agente lo registra sulla issue, le mette l'etichetta `uat-failed` e la rimanda agli agenti, che la correggono con precedenza. Quando è corretta torna a `/test`.
3. Tutto qui. Non devi toccare branch, etichette o la board.

**Come gira HAAM lo scegli tu.** Scrivi `/haam-settings`: passa in rassegna ogni impostazione con i tuoi numeri (minuti di Actions, la coda di UAT), consiglia un'opzione e applica ciò che scegli:
- quando girano la CI e le revisioni AI (su ogni PR, sul tuo computer, solo per le aree protette, o mai);
- cosa testi di persona (tutto, ciò che decidi issue per issue, oppure i bug saltano il test);
- come si raggruppano le modifiche (per issue, per epic, o un'unica PR di release per tutto ciò che hai approvato);
- se i deploy aspettano la tua approvazione;
- i limiti.

`python3 tools/haam/haam.py settings --explain` le elenca tutte.

**Modifiche che non puoi testare di persona** (aggiornamenti del kit o della configurazione, aggiornamenti di dipendenze, refactoring che non noteresti, CI): marcale `uat:skip` quando ne fai il triage, oppure di' "spec approved, no UAT". Non arrivano mai a `/test`: la loro PR va in merge da sola quando la CI ed entrambe le revisioni AI passano (GitHub Projects), e il tuo prossimo `ship` le rilascia insieme a tutto il resto e le chiude. Se per un po' non rilasci nulla, esegui `/test` e rispondi comunque `ship`, oppure `ship --all`: il loro deploy aspetta la tua approvazione. Su Linear, rilasciale per nome (`ship APP-12 --human`). Usa questa strada solo per modifiche che nessun utente noterebbe; mai per le aree protette.

### Ogni settimana (30–45 minuti)
1. **Raggruppa** le issue sparse in epic (`/triage group`) e definisci con l'agente l'epic in cima (`/epic #9`).
2. **Decidi** tutto ciò che è in **Decision** (G1).
3. **Rivedi le specifiche** (collegate in ogni issue) e approvale o commentale (G2).
4. **Riordina** Ready e Backlog in base alle priorità attuali (`/triage backlog`).
5. **Trova il lavoro bloccato:** `/triage stale` (preso in carico ma fermo, UAT in attesa da troppo, decisioni in ritardo).
6. **Riprendi gli elementi Parked** il cui "da riprendere quando" si è avverato.
7. **Chiudi i follow-up degli override** (etichetta `override-followup`).
8. Migliora una cosa nel processo (una `/idea` con etichetta `area:process`).

### Ogni mese o trimestre (30 minuti)
1. Riscrivi le **priorità attuali** in `PRODUCT.md`: 3–5 risultati, in ordine. Gli agenti le usano per suggerire priorità e risolvere i pareggi, quindi è in assoluto la cosa più utile che puoi tenere aggiornata.
2. **Sfoltisci:** tutto ciò che è Low e aspetta da più di due mesi → mettilo in Parked con un "da riprendere quando". Un backlog corto è un backlog utilizzabile.

---

## 3. Triage: decidere cos'è ogni nuovo elemento

Lo stato **Triage** è la tua casella di posta. Idee e bug ci arrivano da `/idea`, `/bug`, dai moduli delle issue, da altre persone e dagli agenti. Punta ad avere la casella vuota alla fine di ogni giornata.

Se diversi elementi sembrano correlati, o quasi tutti mancano di contesto, **raggruppali prima** (§4): fare il triage di una feature alla volta è più veloce e dà risultati migliori che fare il triage di frammenti.

Per ogni elemento, rispondi a quattro domande:

1. **È chiaro e nuovo?** Duplicato → chiudilo e collega l'originale. Informazioni insufficienti → commenta con la tua domanda e lascialo in Triage.
2. **Che cos'è?** Un **bug** significa che qualcosa non funziona come previsto. Un'**idea** significa un comportamento nuovo o diverso. "Funziona come progettato, ma l'utente si aspettava altro" è un'idea, non un bug. Correggi l'etichetta del flusso se è sbagliata.
3. **Quanto è importante?** Imposta la priorità (§5).
4. **Cosa succede dopo?**

| Elemento | La tua decisione | Stato dopo | Cosa segue |
|---|---|---|---|
| Bug con passi chiari per riprodurlo | **Ready** | Ready, con una priorità | Un agente lo prende (`/work bugs`) |
| Bug senza abbastanza elementi | **Servono informazioni** | Resta in Triage, con la tua domanda come commento | Tu o chi l'ha segnalato rispondete, poi si rifà il triage |
| Bug urgente | **Ready, inizia ora** | Ready, Urgent | Avvia subito un agente; `/override` è disponibile se il deploy non può aspettare |
| Idea da esplorare | **Valutare** | Discovery, con una priorità | Un agente scrive la valutazione (`/work ideas` o `/assess #12`) |
| Idea che capiresti meglio provandola | **Prototipo** | Discovery, etichetta `mode:prototype` | Un agente costruisce una versione funzionante usa e getta (`/spike #12`); la provi con `/test` e decidi |
| Buona idea, momento sbagliato | **Parcheggiare** | Parked, con un commento "da riprendere quando…" | Ritorna in una revisione settimanale |
| Idea che non farai | **Rifiutare** | Canceled, con una motivazione di una riga | Chiusa |
| Duplicato | **Duplicato** | Canceled, collegato all'originale | Chiuso |

Anche le idee piccole passano per la valutazione. Chiedine una rapida ("assess #12, keep it short"). La valutazione è il momento in cui l'agente controlla il codice e i rischi, e a te costa un minuto di lettura.

---

## 4. Epic: raggruppare le issue in feature

Le singole issue spesso mancano di contesto. "Pulsante di esportazione mancante su mobile", "Esportazione in CSV" e "Report programmati" sono tre frammenti di una sola feature, e presi uno per uno nel triage sembrano ciascuno piccoli e poco chiari. Una **epic** è una issue padre (etichetta `epic`) che raggruppa le issue per un risultato e porta il contesto che a loro manca: per chi è, che aspetto ha il successo, cosa è dentro e fuori dall'ambito, e l'ordine delle porzioni. Quel contesto vive in un breve **brief dell'epic** in `docs/epics/`.

**Usa un'epic per:** tre o più issue sullo stesso risultato; un'idea troppo grande per una sola specifica (taglia L o XL); una richiesta che tocca diverse schermate o moduli.
**Non usarla per:** un singolo bug; un contenitore "varie" di cose scollegate; un tema che non finisce mai ("prestazioni", "rifinitura UX"): quelle sono priorità, non epic. Un'epic deve poter finire, in settimane e non in trimestri.

### Come scorre un'epic
1. **Raggruppa.** `/triage group` guarda le issue sparse e propone delle epic: un titolo, il risultato in una riga, quali issue ne fanno parte e perché. Tu dici `ok` o aggiusti (`merge 2 and 3`, `#40 out`). Oppure parti da un tema: `/epic "reporting"`.
2. **Definisci.** `/epic #9`: l'agente legge ogni issue dell'epic, il contesto di prodotto e il codice pertinente, prepara una bozza del brief, poi **ti fa fino a cinque domande per giro**: per chi è, che aspetto ha il successo, cosa è indispensabile e cosa è un di più, vincoli, cosa non deve cambiare, che posizione ha in classifica. Poi propone una pulizia: duplicati da chiudere, lacune da aggiungere come nuove issue, issue poco chiare da riscrivere, issue grandi da dividere, un ordine. Non cambia nulla finché non confermi.
3. **Decidi una volta (G1).** `/assess #9` aggiunge sforzo e fattibilità per tutta l'epic; `/decide #9 approve high` approva l'epic e le idee che contiene in un colpo solo.
4. **Specifica e costruisci porzione per porzione.** Ogni sotto-issue ha la propria specifica e supera il G2 per conto suo. Gli agenti costruiscono le sotto-issue, mai l'epic in sé.
5. **Concludi.** Quando l'ultima sotto-issue viene rilasciata, l'agente propone di chiudere l'epic.

**Priorità:** dai una priorità all'epic; le sue issue prendono la stessa, salvo indicazione diversa. Un bug dentro un'epic può comunque essere più urgente dell'epic.

**Rispondere alle domande dell'agente:** le risposte brevi vanno bene. "Non lo so ancora" è una risposta valida: resta aperta nel brief. Rispondi su ciò di cui gli utenti hanno bisogno e sul perché; lascia il come agli agenti.

### Le epic direttamente nel tracker
- **GitHub Projects:** crea una issue e aggiungi l'etichetta `epic`; poi, nella sezione delle sub-issue dell'epic, aggiungi le issue che ne fanno parte (oppure imposta il padre da ciascuna issue). Sulla board, usa la vista **Epics** e mostra i campi *Parent issue* e *Sub-issues progress* nelle viste a tabella, così ogni scheda mostra la sua epic.
- **Linear:** crea una issue con l'etichetta `epic` e rendi le issue correlate sue sub-issue (impostane il padre). Per un'iniziativa molto grande che abbraccia più epic, un progetto Linear può contenere le epic.

---

## 5. Dare le priorità

### 5.1 I quattro livelli

| Priorità | Criterio | Gestione prevista |
|---|---|---|
| **Urgent** | La produzione è rotta su un percorso principale, dati che potrebbero andare persi o esposti, una falla di sicurezza, o una scadenza legale/di compliance a rischio | Si inizia oggi. I gate si possono scavalcare, con un follow-up |
| **High** | Fa avanzare direttamente una delle priorità attuali in `PRODUCT.md`, oppure un bug in un percorso principale senza soluzione alternativa | La prossima, questa settimana |
| **Medium** | Utile, ma non tra le priorità attuali, oppure le evidenze sono scarse | In ordine, quando le High sono esaurite |
| **Low** | Sarebbe bello averla, estetica, caso limite | Nei tempi morti; da sfoltire dopo due mesi |
| *(nessuna)* | Non ancora triagiata | Gli agenti non la costruiscono |

Mantieni i livelli credibili: se più di circa un elemento aperto su cinque è High o Urgent, i livelli hanno smesso di significare qualcosa. Abbassa la priorità di qualcosa.

### 5.2 Bug: impatto × portata

| | La maggior parte degli utenti, o un percorso principale | Alcuni utenti | Pochi utenti, o un caso limite |
|---|---|---|---|
| **Blocca l'attività, perde o espone dati, sicurezza, aspetti legali** | Urgent | Urgent | High |
| **Risultato sbagliato, ma c'è una soluzione alternativa** | High | Medium | Low |
| **Fastidioso o estetico** | Medium | Low | Low |

### 5.3 Idee e feature: valore, fiducia, dimensione

Dopo una valutazione hai tre elementi: **valore** (quanto fa avanzare una priorità attuale), **fiducia** (quanto sono buone le evidenze) e **dimensione** (XS–XL, in base al codice). Regole pratiche:
- **High:** valore chiaro per una priorità attuale, buone evidenze, taglia S–M.
- **Medium:** buon valore ma evidenze più deboli; oppure valore alto ma taglia L–XL (chiedi di dividerla).
- **Low:** valore piccolo, qualunque sia la taglia.
- **Non è tra le priorità attuali?** Al massimo Medium, a meno che prima non cambi le priorità.

Per confrontare velocemente due idee: valore (1–3) × fiducia (0,5 / 0,8 / 1) ÷ dimensione (XS 1, S 2, M 3, L 5, XL 8). Il punteggio più alto va prima. Serve a spareggiare, non è una formula da seguire ciecamente.

### 5.4 Ordine all'interno di una priorità
Gli agenti prendono **i bug prima delle feature, le più vecchie prima delle più nuove, le più piccole prima delle più grandi**. Leggono la priorità, non la posizione di una scheda sulla board. Se X deve avvenire prima di Y, dai a X una priorità più alta, oppure scrivi `Blocked by #X` nella descrizione di Y.

### 5.5 Tieni sane le code

| Coda | Dimensione sana | Se non lo è |
|---|---|---|
| **Agent queue** (Ready) | 3–10 elementi | Vuota: gli agenti restano fermi, quindi scrivi più specifiche. Oltre 10: le priorità invecchiano, quindi riordina |
| **Decision** | 5 o meno | Prenota 20 minuti e decidi |
| **UAT** | `max_in_uat` (predefinito 10) | Al limite gli agenti sospendono le nuove build (`haam.py capacity`): è il tuo tempo per i test, il limite principale in test-first. Testa con `/test all`; gli elementi che gli agenti hanno verificato completamente passano con una sola risposta (`pass all verified`). Per un weekend di lavoro degli agenti, apri una finestra di lotto in `/haam-settings`: un aumento che finisce da solo |
| **Agenti in esecuzione** | Non più di quanti ne puoi testare domani | Meno agenti, elementi più piccoli |
| **PR pronte** | `max_open_prs` in `haam.config.json` (predefinito 10) | Al limite gli agenti sospendono le nuove build: ogni PR pronta costa minuti di CI a ogni push. Bozze e PR di sola documentazione non contano. Specifiche e valutazioni vanno avanti. Testa e rilascia ciò che è aperto |

### 5.6 Cambiare le priorità
Cambiale ogni volta che cambiano i fatti, ma spiega il perché in un commento. Agenti e colleghi leggono lo storico. Non abbassare mai in silenzio un elemento Urgent: commenta e avvisa chi l'ha segnalato.

---

## 6. Farlo con l'AI

Usa **la tua chat nella cartella principale del progetto**, non una delle chat di agenti che eseguono `/work`.

| Vuoi… | Scrivi |
|---|---|
| Raggruppare le issue sparse in epic | `/triage group` |
| Definire un'epic: brief, domande per te, pulizia | `/epic #9` (o `/epic "reporting"` per partire da un tema) |
| Fare il triage della casella | `/triage` |
| Riordinare Ready e Backlog in base alle priorità | `/triage backlog` |
| Trovare lavoro bloccato o dimenticato | `/triage stale` |
| Raccogliere un'idea o un bug da qualsiasi parte | `/idea …`, `/bug …` |
| Far valutare un'idea | `/assess #12` (o lascia che la prenda `/work ideas`) |
| Decidere (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Approvare una specifica (G2) | Leggila (è collegata nella issue), poi: "spec for #12 approved" |
| Testare una modifica, poi rilasciarla o rimandarla indietro (G4, G5) | `/test` (o `/test #12`), poi `pass` → `ship`, oppure di' cosa non va |
| Chiudere qualcosa che è andato in merge in altro modo | `/release #12` |
| Emergenza | `/override #12 "<reason>"` |

**Come funziona `/triage`.** L'agente legge `PRODUCT.md` e gli elementi, poi ti mostra un'unica tabella: flusso proposto, priorità, passo successivo e una breve motivazione per ciascuno. Rispondi `ok` per applicare tutto, oppure con le modifiche (`#14 Low, #9 park until Q3`). Non cambia nulla finché non rispondi, applica esattamente ciò che hai confermato e commenta ogni elemento così la motivazione resta agli atti. Non approva mai le idee al posto tuo; per quello ti rimanda a `/decide`.

**Domande che vale la pena fare al tuo agente:**
- "Cosa aspetta me?"
- "Cosa hanno finito gli agenti da ieri, e cosa è bloccato?"
- "Quali elementi Ready non rientrano nelle nostre priorità attuali?"
- "#12 è troppo grande. Proponi una suddivisione in pezzi di taglia S."
- "Confronta #12 e #15: quale dovrebbe andare prima, e perché?"
- "Prepara una bozza delle nuove priorità attuali per PRODUCT.md in base a ciò che abbiamo rilasciato e a ciò che c'è nel backlog."

I suggerimenti dell'agente sono bozze, e le decisioni sono tue. Quando `/bug` registra un bug, compila una priorità suggerita; tu la confermi o la cambi quando fai il triage.

---

## 7. Farlo direttamente in GitHub Projects

Tutto quanto sopra si può fare a mano sulla board. Le viste salvate (configurate con `haam.py github-project`) sono il tuo spazio di lavoro:

| Vista | A cosa serve |
|---|---|
| **Triage** (stato: Triage) | La tua casella quotidiana |
| **Epics** (etichetta: epic) | Ogni feature e a che punto sono le sue sotto-issue |
| **Waiting on me** (stato: Decision, UAT) | Decisioni e test |
| **Agent queue** (stato: Ready, non assegnate) | Cosa prenderanno dopo gli agenti, per priorità |
| **Bugs** | Tutti i bug aperti per priorità |
| **Ideas inbox** | Idee in triage o in valutazione |
| **Board** | L'intero flusso, raggruppato per stato |

| Attività | Sulla board |
|---|---|
| Fare il triage di un elemento | Aprilo. Imposta **Priority** e **Status**; correggi l'etichetta del flusso nella barra laterale della issue; commenta la tua motivazione |
| Parcheggiare | Stato **Parked**, e un commento: "da riprendere quando…" |
| Rifiutare o segnare un duplicato | Stato **Canceled**, poi chiudi la issue come *not planned* o *duplicate* |
| Approvare un'idea (G1) | Stato **Backlog**; sostituisci l'etichetta `stream:idea` con `stream:feature`; imposta Priority; commenta "Approved" |
| Approvare una specifica (G2) | Commenta "spec approved" sulla issue; poi stato **Ready** ed etichetta `agent-ready` |
| Raggruppare le issue in un'epic | Crea una issue con etichetta `epic`; aggiungi le altre come sue sub-issue |
| Riordinare molti elementi | Layout a tabella, raggruppato o ordinato per Priority; modifica le celle (puoi copiare un valore e incollarlo in più celle selezionate) |

Lascia queste cose alle skill: la presa in carico (**In Progress**) è compito degli agenti. Testare e rilasciare è più facile con `/test`; a mano funziona così: aggiungi l'etichetta `uat-passed` alla PR (sblocca il merge), fai il merge, approva il deploy (Actions → l'esecuzione → Review deployments), poi imposta la issue su **Done** e chiudila. Se il test è fallito, commenta sulla issue cosa non va, aggiungi l'etichetta `uat-failed`, rimettila in **Ready** e togli l'assegnatario.

---

## 8. Farlo direttamente in Linear

| Attività | In Linear |
|---|---|
| Triage | Usa la casella **Triage** del team. Puoi accettare, rifiutare, segnare come duplicato o posticipare. Dopo aver accettato, **imposta tu lo stato HAAM** (Ready per un bug, Discovery per un'idea da valutare), perché accettare sposta l'elemento nello stato predefinito del team. Imposta la priorità |
| Parcheggiare o rifiutare | Stato **Parked** o **Canceled**, con un commento |
| Raggruppare le issue in un'epic | Crea una issue con etichetta `epic`; impostala come padre delle issue correlate |
| Approvare un'idea (G1) | Stato **Backlog**, sostituisci l'etichetta `stream:idea` con `stream:feature`, imposta la priorità, commenta |
| Approvare una specifica (G2) | Commenta "spec approved" sulla issue; poi stato **Ready** ed etichetta `agent-ready` |
| Riordinare | Le viste di `docs/setup/LINEAR-SETUP.md` §7, ordinate per priorità; il menu dei comandi (Cmd/Ctrl+K) cambia velocemente priorità o stato |

Come su GitHub, gli agenti seguono il campo della priorità, non l'ordine manuale di un elenco.

---

## 9. Lavorare con altre persone

- **Un product owner per prodotto** imposta le priorità e fa passare i gate. Tutti gli altri propongono: `/idea`, `/bug`, commenti.
- Chiedi ai colleghi di suggerire una priorità quando segnalano qualcosa. Tu la confermi durante il triage.
- **I disaccordi si discutono sulla issue,** non in chat private. Il product owner decide e spiega il perché in un commento.
- Quando sei assente, nomina un approvatore di riserva (`haam.py config --backup-approvers`) e indica a quella persona quali elementi possono andare avanti senza di te.

---

## 10. Tenere bassi i costi di GitHub Actions

Ogni pull request fa girare la CI e due revisioni AI sulle macchine di GitHub, e i repository privati hanno una quota mensile di minuti. Gli agenti lavorano in fretta, quindi la quota può finire in pochi giorni. Cosa aiuta di più, in ordine:
1. **Prima guarda:** `python3 tools/haam/haam.py ci-usage` mostra quali workflow e job hanno usato i minuti.
2. **Meno pull request:** raggruppa i piccoli elementi di un'epic in una sola (`/work epic #9`), e tieni basso il limite di PR aperte (`max_open_prs` in `haam.config.json`).
3. **Revisioni sul tuo computer:** `haam.py settings --set review=local --apply --human` (oppure `/haam-settings`). Le revisioni AI allora usano il tuo piano Claude invece dei minuti; le aree protette (`human-review`) vengono comunque revisionate su GitHub. Il compromesso: su GitHub il risultato della revisione è a prova di manomissione; in locale no. Le revisioni girano in sessioni nuove e in sola lettura con le istruzioni di `main`, ma è l'agente che ha costruito la modifica ad avviarle, e qualsiasi cosa usi il tuo login potrebbe pubblicare un risultato positivo. Per una separazione maggiore, esegui di persona `haam.py review <ID>` dalla tua chat.
4. **Il tuo runner:** `haam.py settings --set runner=self-hosted --apply --human` dopo aver registrato una macchina che resta accesa (`docs/setup/GITHUB-SETUP.md` §8).
5. **Chiedi una CI più piccola:** se il progetto ha parti separate (ad es. backend e app mobile), fai in modo che un agente faccia girare a `make check` solo le parti che una PR tocca.

## 11. Trappole da evitare

- **Tutto è High.** Allora niente lo è. Abbassa le priorità finché circa un elemento su cinque è High o Urgent.
- **Più agenti di quanti ne puoi testare.** Il lavoro si accumula in UAT e invecchia. Elementi più piccoli e in numero minore si muovono più in fretta.
- **"Costruiscilo e basta" in una chat.** Crea prima la issue (`/bug`, `/idea`): ci vuole un minuto e conserva lo storico, la priorità e la presa in carico.
- **Approvare una specifica senza leggere i criteri di accettazione.** È ciò che l'agente costruisce e ciò su cui testi. Leggili.
- **Priorità solo nella tua testa.** Se non sono in `PRODUCT.md` e nel tracker, gli agenti non possono seguirle.
- **Costruire frammenti senza il quadro d'insieme.** Se diverse issue sono in realtà una sola feature, raggruppale in un'epic e definiscila prima che qualcuno scriva le specifiche dei pezzi.
- **Epic che non finiscono mai.** Se un'epic è aperta da mesi, separa ciò che è fatto e chiudila.
- **Lasciare il Triage a "dopo".** La casella cresce, e i bug urgenti ci si nascondono dentro.

---

## 12. Checklist

**Ogni giorno**
- [ ] Tutto ciò che è in UAT testato con `/test`
- [ ] Casella Triage vuota
- [ ] I bug urgenti hanno un agente al lavoro
- [ ] Risposte date alle domande degli agenti

**Ogni settimana**
- [ ] Issue sparse raggruppate in epic; epic in cima definita
- [ ] Coda Decision decisa
- [ ] Specifiche approvate o commentate
- [ ] Ready e Backlog riordinati
- [ ] Lavoro fermo sollecitato (`/triage stale`)
- [ ] Elementi Parked ripresi in esame
- [ ] Follow-up degli override chiusi
- [ ] Un miglioramento del processo registrato

**Ogni mese**
- [ ] Priorità attuali in `PRODUCT.md` riscritte
- [ ] Vecchi elementi Low parcheggiati
