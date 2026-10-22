# Arbeiten im Produktmanagement

*Ein Leitfaden für den Menschen, der entscheidet, was gebaut wird. Agenten müssen ihn nicht lesen; du schon.*

In HAAM entscheidest du **was** und **warum**; Agenten finden heraus, **wie**, und setzen es um. Agenten sind schnell, also bestimmt dein Tempo beim Triagieren, Entscheiden, Freigeben und Testen das Tempo des ganzen Systems. Deine Hauptaufgabe: die Warteschlange **Waiting on me** kurz halten und die **Agent queue** auf die richtigen Dinge ausrichten.

Die Beispiele nutzen IDs von GitHub Projects (`#12`); auf Linear heißt derselbe Eintrag `APP-12`. Befehle sind als `/name` geschrieben; in Codex nutzt du `$name`.

---

## 1. Deine Aufgabe auf einer Seite

| Was nur du machst | Wie oft | Mit KI | Direkt im Tracker |
|---|---|---|---|
| `docs/product/PRODUCT.md` aktuell halten: aktuelle Prioritäten, Unverhandelbares, Kern-Journeys | Monatlich | „Aktualisiere PRODUCT.md: Unsere Prioritäten sind jetzt…“ | Die Datei bearbeiten (über einen PR) |
| Neue Ideen und Bugs triagieren | Täglich | `/triage` | Ansicht Triage: Priorität, Status, Labels |
| Zusammengehörige Issues zu Epics bündeln und die Fragen des Agenten zu jedem beantworten | Wöchentlich | `/triage group`, dann `/epic #9` | Epic-Issue (Label `epic`) mit Sub-Issues |
| Prioritäten setzen und ändern | Täglich und wöchentlich | `/triage`, `/triage backlog` | Feld Priority |
| Über bewertete Ideen entscheiden (G1) | Wöchentlich | `/decide #12 approve high` | Status, Labels, Kommentar (§7–8) |
| Specs freigeben (G2) | Sobald sie kommen | Die Spec lesen (im Issue verlinkt), dann „Spec für #12 freigegeben“ | „Spec freigegeben“ kommentieren; Status Ready, Label `agent-ready` |
| Änderungen testen (G4) und ausliefern (G5) | Täglich | `/test`, dann `pass` → `ship` antworten oder sagen, was nicht stimmt | GitHub: Label `uat-passed`, mergen, den Deploy freigeben |
| Folge-Issues von Overrides schließen | Wöchentlich | „Zeig mir die offenen Folge-Issues von Overrides“ | Ansicht: Label `override-followup` |

Alles, was du entscheidest, kommt in den Tracker oder nach Git, nie nur in einen Chat. Steht es dort nicht, weiß der nächste Agent nichts davon.

---

## 2. Dein Rhythmus

### Täglich (10–15 Minuten)
1. **Zuerst testen.** Tippe `/test all`: Der Agent führt dich nacheinander durch jede Änderung, die auf dich wartet (§2a), und liefert dann alles Bestandene mit einem Deploy aus. Agenten können erst fertig werden, wenn du es bist, und ihr Kontext veraltet.
2. **Leere den Triage-Eingang** (`/triage` oder die Ansicht Triage). Nichts sollte dort länger als zwei Arbeitstage liegen.
3. **Dringende Bugs:** Gibt es einen, setz sofort einen Agenten darauf an: neues Chatfenster, `/work bugs`.
4. Überfliege die Übergabe- und „Blockiert“-Kommentare der Agenten und beantworte ihre Fragen.

### 2a. Eine Änderung testen: der ganze Ablauf
1. Tippe **`/test`** (oder `/test #12`). Der Agent holt die Änderung auf deinen Computer, startet die App und gibt dir den Link und eine kurze Checkliste: *mach das → dann solltest du das sehen*.
2. Probier es aus. Dann antworte mit einem Wort oder einem Satz:
   - **`pass`** → Der Agent öffnet den Pull Request (bis jetzt gab es keinen: Du hast den Branch des Agenten getestet), die Checks laufen einmal, genau auf dem, was du getestet hast, und er fragt *„Ausliefern, wenn die Checks bestanden sind?“* Antworte **`ship`**: Er wartet auf sie, mergt, gibt den Produktions-Deploy für dich frei und schließt das Issue. Du bekommst *„#12 ist live.“* Antworte `later`, um es zurückzuhalten.
   - Wenn dein Projekt **von Hand deployt** (`"deploy": "manual"`), mergt der Agent und bittet dich dann, zu deployen; antworte **`live`**, wenn es draußen ist, und er schließt das Issue.
   - Finden die Checks oder Reviews danach ein Problem, geht es wie ein fehlgeschlagener Test zurück an die Agenten und kommt repariert wieder zu dir.
   - **Was schiefgelaufen ist** (*„Schritt 3: Der Export-Button fehlt auf dem Handy immer noch“*) → Der Agent hält es im Issue fest, setzt das Label `uat-failed` und schickt es zurück an die Agenten, die es zuerst beheben. Ist es behoben, kommt es zurück zu `/test`.
3. Das war's. Du musst weder Branches noch Labels noch das Board anfassen.

**Wie HAAM läuft, entscheidest du.** Tippe `/haam-settings`: Es geht jede Einstellung mit deinen eigenen Zahlen durch (Actions-Minuten, die UAT-Warteschlange), empfiehlt eine Option und wendet an, was du wählst:
- wann CI und die KI-Reviews laufen (bei jedem PR, auf deinem Computer, nur für geschützte Bereiche oder gar nicht);
- was du selbst testest (alles, was du pro Issue entscheidest, oder Bugs überspringen den Test);
- wie Änderungen gebündelt werden (pro Issue, pro Epic oder ein Release-PR für alles, was bei dir bestanden hat);
- ob Deploys auf deine Freigabe warten;
- die Limits.

`python3 tools/haam/haam.py settings --explain` listet sie alle auf.

**Änderungen, die du nicht selbst testen kannst** (Updates des Kits oder der Konfiguration, Updates von Abhängigkeiten, Refactorings, die du nicht bemerken würdest, CI): Markiere sie beim Triagieren mit `uat:skip`, oder sag „Spec freigegeben, kein UAT“. Sie kommen nie zu `/test`: Ihr PR wird von selbst gemergt, sobald CI und beide KI-Reviews bestanden sind (GitHub Projects), und dein nächstes `ship` deployt sie mit allem anderen und schließt sie. Lieferst du eine Weile nichts aus, führe trotzdem `/test` aus und antworte `ship`, oder nutze `ship --all`: Ihr Deploy wartet auf deine Freigabe. Auf Linear lieferst du sie mit Namen aus (`ship APP-12 --human`). Nutze das nur für Änderungen, die kein Nutzer bemerken würde; nie für geschützte Bereiche.

### Wöchentlich (30–45 Minuten)
1. **Bündle** lose Issues zu Epics (`/triage group`) und forme das oberste Epic mit dem Agenten (`/epic #9`).
2. **Entscheide** alles in **Decision** (G1).
3. **Prüfe Specs** (in jedem Issue verlinkt) und gib sie frei oder kommentiere (G2).
4. **Ordne** Ready und Backlog neu, gemessen an den aktuellen Prioritäten (`/triage backlog`).
5. **Finde festhängende Arbeit:** `/triage stale` (beansprucht, aber still; UAT wartet zu lange; Entscheidungen überfällig).
6. **Schau dir Parked-Einträge wieder an**, deren „wieder anschauen, wenn“ eingetreten ist.
7. **Schließe Folge-Issues von Overrides** (Label `override-followup`).
8. Verbessere eine Sache im Prozess (eine `/idea` mit Label `area:process`).

### Monatlich oder quartalsweise (30 Minuten)
1. Schreib die **aktuellen Prioritäten** in `PRODUCT.md` neu: 3–5 Ergebnisse, in Reihenfolge. Agenten nutzen sie, um Prioritäten vorzuschlagen und Gleichstände aufzulösen. Das ist also das Nützlichste, was du aktuell halten kannst.
2. **Ausdünnen:** Alles mit Low, das länger als zwei Monate gewartet hat → parken, mit einem „wieder anschauen, wenn“. Ein kurzes Backlog ist ein brauchbares Backlog.

---

## 3. Triage: entscheiden, was jeder neue Eintrag ist

Der Status **Triage** ist dein Eingang. Ideen und Bugs landen dort über `/idea`, `/bug`, die Issue-Formulare, andere Personen und Agenten. Ziel: ein leerer Eingang am Ende jedes Tages.

Wirken mehrere Einträge zusammengehörig, oder fehlt den meisten Kontext, **bündle sie zuerst** (§4): Ein Feature auf einmal zu triagieren geht schneller und besser, als Bruchstücke zu triagieren.

Beantworte für jeden Eintrag vier Fragen:

1. **Ist er klar und neu?** Duplikat → schließen und das Original verlinken. Zu wenig Informationen → deine Frage kommentieren und in Triage lassen.
2. **Was ist es?** Ein **Bug** heißt, etwas funktioniert nicht wie gedacht. Eine **Idee** heißt neues oder geändertes Verhalten. „Funktioniert wie entworfen, aber der Nutzer hat etwas anderes erwartet“ ist eine Idee, kein Bug. Korrigiere das Strang-Label, wenn es falsch ist.
3. **Wie wichtig ist es?** Setz die Priorität (§5).
4. **Was passiert als Nächstes?**

| Eintrag | Deine Entscheidung | Status danach | Was folgt |
|---|---|---|---|
| Bug mit klaren Schritten zur Reproduktion | **Ready** | Ready, mit einer Priorität | Ein Agent nimmt ihn (`/work bugs`) |
| Bug ohne genug Anhaltspunkte | **Braucht Infos** | Bleibt in Triage, mit deiner Frage als Kommentar | Du oder die meldende Person antwortet, dann erneut triagieren |
| Dringender Bug | **Ready, sofort starten** | Ready, Urgent | Sofort einen Agenten starten; `/override` steht bereit, wenn der Deploy nicht warten kann |
| Idee, die eine Untersuchung wert ist | **Bewerten** | Discovery, mit einer Priorität | Ein Agent schreibt die Bewertung (`/work ideas` oder `/assess #12`) |
| Idee, die du besser verstehst, wenn du sie ausprobierst | **Prototyp** | Discovery, Label `mode:prototype` | Ein Agent baut eine funktionierende Wegwerf-Version (`/spike #12`); du probierst sie mit `/test` aus und entscheidest |
| Gute Idee, falscher Zeitpunkt | **Parken** | Parked, mit einem Kommentar „wieder anschauen, wenn…“ | Kommt bei einem wöchentlichen Review wieder |
| Idee, die du nicht umsetzen wirst | **Ablehnen** | Canceled, mit einer Begründung in einer Zeile | Geschlossen |
| Duplikat | **Duplikat** | Canceled, mit dem Original verlinkt | Geschlossen |

Auch kleine Ideen werden bewertet. Bitte um eine schnelle Bewertung („bewerte #12, halt es kurz“). In der Bewertung prüft der Agent die Codebasis und die Risiken, und dich kostet das Lesen eine Minute.

---

## 4. Epics: Issues zu Features bündeln

Einzelnen Issues fehlt oft Kontext. „Export-Button fehlt auf dem Handy“, „Export als CSV“ und „Geplante Berichte“ sind drei Bruchstücke eines Features, und einzeln triagiert wirkt jedes klein und unklar. Ein **Epic** ist ein übergeordnetes Issue (Label `epic`), das die Issues für ein Ergebnis bündelt und den Kontext liefert, der ihnen fehlt: für wen es ist, wie Erfolg aussieht, was dazugehört und was nicht, und die Reihenfolge der Teilstücke. Dieser Kontext steht in einem kurzen **Epic-Brief** in `docs/epics/`.

**Nutze ein Epic für:** drei oder mehr Issues zum selben Ergebnis; eine Idee, die für eine Spec zu groß ist (Größe L oder XL); eine Anforderung, die mehrere Bildschirme oder Module berührt.
**Nutze keines für:** einen einzelnen Bug; einen „Sonstiges“-Topf mit unzusammenhängenden Dingen; ein Thema, das nie endet („Performance“, „UX-Feinschliff“): Das sind Prioritäten, keine Epics. Ein Epic sollte abschließbar sein, eher in Wochen als in Quartalen.

### Wie ein Epic abläuft
1. **Bündeln.** `/triage group` schaut sich die losen Issues an und schlägt Epics vor: einen Titel, das Ergebnis in einer Zeile, welche Issues dazugehören und warum. Du sagst `ok` oder passt an (`merge 2 and 3`, `#40 out`). Oder du startest bei einem Thema: `/epic "reporting"`.
2. **Formen.** `/epic #9`: Der Agent liest jedes Issue im Epic, den Produktkontext und den relevanten Code, entwirft den Brief und **stellt dir dann bis zu fünf Fragen pro Runde**: für wen es ist, wie Erfolg aussieht, was Pflicht und was Kür ist, Einschränkungen, was sich nicht ändern darf, wie es im Vergleich rangiert. Dann schlägt er ein Aufräumen vor: Duplikate zum Schließen, Lücken, die als neue Issues dazukommen, unklare Issues zum Umschreiben, große zum Aufteilen, eine Reihenfolge. Nichts ändert sich, bevor du bestätigst.
3. **Einmal entscheiden (G1).** `/assess #9` ergänzt Aufwand und Machbarkeit für das ganze Epic; `/decide #9 approve high` gibt es und die Ideen darin in einem Rutsch frei.
4. **Spec und Bau Stück für Stück.** Jedes Sub-Issue bekommt seine eigene Spec und besteht G2 für sich. Agenten bauen Sub-Issues, nie das Epic selbst.
5. **Abschließen.** Wird das letzte Sub-Issue ausgeliefert, bietet der Agent an, das Epic zu schließen.

**Prioritäten:** Gib dem Epic eine Priorität; seine Issues übernehmen dieselbe, wenn du nichts anderes sagst. Ein Bug in einem Epic kann trotzdem dringender sein als das Epic.

**Die Fragen des Agenten beantworten:** Kurze Antworten reichen. „Weiß ich noch nicht“ ist eine gültige Antwort: Sie bleibt im Brief offen. Antworte darauf, was Nutzer brauchen und warum; das Wie überlass den Agenten.

### Epics direkt im Tracker
- **GitHub Projects:** Lege ein Issue an und setz das Label `epic`; füge dann im Abschnitt für Sub-Issues des Epics die Issues hinzu, die dazugehören (oder setz den Parent in jedem Issue). Nutze auf dem Board die Ansicht **Epics** und blende in Tabellenansichten die Felder *Parent issue* und *Sub-issues progress* ein, damit jede Karte ihr Epic zeigt.
- **Linear:** Lege ein Issue mit dem Label `epic` an und mach die zugehörigen Issues zu seinen Sub-Issues (setz ihren Parent). Für eine sehr große Initiative über mehrere Epics hinweg kann ein Linear-Projekt die Epics aufnehmen.

---

## 5. Priorisieren

### 5.1 Die vier Stufen

| Priorität | Test | Erwarteter Umgang |
|---|---|---|
| **Urgent** | Die Produktion ist für eine Kern-Journey kaputt, Daten könnten verloren gehen oder offengelegt werden, eine Sicherheitslücke, oder eine rechtliche oder Compliance-Frist ist in Gefahr | Heute starten. Gates können übergangen werden, mit einem Folge-Issue |
| **High** | Bringt direkt eine der aktuellen Prioritäten in `PRODUCT.md` voran, oder ein Bug in einer Kern-Journey ohne Workaround | Als Nächstes, diese Woche |
| **Medium** | Nützlich, aber nicht bei den aktuellen Prioritäten, oder die Belege sind dünn | Der Reihe nach, wenn High abgearbeitet ist |
| **Low** | Wäre schön, kosmetisch, Grenzfall | Wenn sonst nichts ansteht; nach zwei Monaten ausdünnen |
| *(keine)* | Noch nicht triagiert | Agenten bauen es nicht |

Bleib ehrlich: Ist mehr als etwa jeder fünfte offene Eintrag High oder Urgent, bedeuten die Stufen nichts mehr. Stuf etwas herunter.

### 5.2 Bugs: Auswirkung × Reichweite

| | Die meisten Nutzer oder eine Kern-Journey | Einige Nutzer | Wenige Nutzer oder ein Grenzfall |
|---|---|---|---|
| **Blockiert die Aufgabe, verliert oder legt Daten offen, Sicherheit, Recht** | Urgent | Urgent | High |
| **Falsches Ergebnis, aber es gibt einen Workaround** | High | Medium | Low |
| **Lästig oder kosmetisch** | Medium | Low | Low |

### 5.3 Ideen und Features: Wert, Sicherheit, Größe

Nach einer Bewertung hast du drei Dinge: **Wert** (wie sehr es eine aktuelle Priorität voranbringt), **Sicherheit** (wie gut die Belege sind) und **Größe** (XS–XL, aus der Codebasis). Faustregeln:
- **High:** klarer Wert für eine aktuelle Priorität, gute Belege, Größe S–M.
- **Medium:** guter Wert, aber schwächere Belege; oder hoher Wert, aber Größe L–XL (bitte um eine Aufteilung).
- **Low:** geringer Wert, egal welche Größe.
- **Nicht bei den aktuellen Prioritäten?** Höchstens Medium, außer du änderst zuerst die Prioritäten.

Um zwei Ideen schnell zu vergleichen: Wert (1–3) × Sicherheit (0,5 / 0,8 / 1) ÷ Größe (XS 1, S 2, M 3, L 5, XL 8). Der höhere Wert kommt zuerst. Das ist eine Entscheidungshilfe bei Gleichstand, keine Formel, der man gehorchen muss.

### 5.4 Reihenfolge innerhalb einer Priorität
Agenten nehmen **Bugs vor Features, ältere vor neueren, kleinere vor größeren**. Sie lesen die Priorität, nicht die Position einer Karte auf dem Board. Muss X vor Y passieren, gib X eine höhere Priorität, oder schreib `Blocked by #X` in die Beschreibung von Y.

### 5.5 Die Warteschlangen gesund halten

| Warteschlange | Gesunde Größe | Wenn nicht |
|---|---|---|
| **Agent queue** (Ready) | 3–10 Einträge | Leer: Agenten haben nichts zu tun, also mehr spezifizieren. Über 10: Prioritäten veralten, also neu ordnen |
| **Decision** | 5 oder weniger | 20 Minuten blocken und entscheiden |
| **UAT** | `max_in_uat` (Standard 10) | Agenten halten neue Builds am Limit zurück (`haam.py capacity`): Es ist deine Testzeit, das wichtigste Limit bei test-first. Teste mit `/test all`; Einträge, die die Agenten vollständig geprüft haben, bestehen mit einer Antwort (`pass all verified`). Für ein Wochenende voller Agentenarbeit öffne ein Batch-Fenster in `/haam-settings`: eine Erhöhung, die von selbst endet |
| **Laufende Agenten** | Nicht mehr, als du morgen testen kannst | Weniger Agenten, kleinere Einträge |
| **Bereite PRs** | `max_open_prs` in `haam.config.json` (Standard 10) | Agenten halten neue Builds am Limit zurück: Jeder bereite PR kostet bei jedem Push CI-Minuten. Drafts und reine Doku-PRs zählen nicht. Specs und Bewertungen laufen weiter. Teste und liefere aus, was offen ist |

### 5.6 Prioritäten ändern
Ändere sie, wann immer sich die Fakten ändern, aber sag in einem Kommentar, warum. Agenten und Kollegen lesen die Historie. Stuf einen Urgent-Eintrag nie stillschweigend herunter: Kommentiere und sag es der Person, die ihn gemeldet hat.

---

## 6. Mit KI erledigen

Nutze **deinen eigenen Chat im Hauptordner des Projekts**, nicht einen der Agenten-Chats, in denen `/work` läuft.

| Du willst… | Tippe |
|---|---|
| Lose Issues zu Epics bündeln | `/triage group` |
| Ein Epic formen: Brief, Fragen an dich, Aufräumen | `/epic #9` (oder `/epic "reporting"`, um bei einem Thema zu starten) |
| Den Eingang triagieren | `/triage` |
| Ready und Backlog anhand der Prioritäten neu ordnen | `/triage backlog` |
| Festhängende oder vergessene Arbeit finden | `/triage stale` |
| Eine Idee oder einen Bug von überall erfassen | `/idea …`, `/bug …` |
| Eine Idee bewerten lassen | `/assess #12` (oder `/work ideas` sie auswählen lassen) |
| Entscheiden (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Eine Spec freigeben (G2) | Lies sie (im Issue verlinkt), dann: „Spec für #12 freigegeben“ |
| Eine Änderung testen, dann ausliefern oder zurückschicken (G4, G5) | `/test` (oder `/test #12`), dann `pass` → `ship`, oder sag, was nicht stimmt |
| Etwas schließen, das auf anderem Weg gemergt wurde | `/release #12` |
| Notfall | `/override #12 "<reason>"` |

**So funktioniert `/triage`.** Der Agent liest `PRODUCT.md` und die Einträge und zeigt dir dann eine Tabelle: vorgeschlagener Strang, Priorität, nächster Schritt und eine kurze Begründung für jeden Eintrag. Antworte `ok`, um alles anzuwenden, oder mit Änderungen (`#14 Low, #9 park until Q3`). Er ändert nichts, bevor du antwortest, wendet genau an, was du bestätigt hast, und kommentiert jeden Eintrag, damit die Begründung festgehalten ist. Er gibt nie Ideen für dich frei; dafür verweist er dich auf `/decide`.

**Fragen, die du deinem Agenten stellen solltest:**
- „Was wartet auf mich?“
- „Was haben die Agenten seit gestern fertiggestellt, und was ist blockiert?“
- „Welche Ready-Einträge passen nicht zu unseren aktuellen Prioritäten?“
- „#12 ist zu groß. Schlag eine Aufteilung in Stücke der Größe S vor.“
- „Vergleiche #12 und #15: Was sollte zuerst kommen, und warum?“
- „Entwirf neue aktuelle Prioritäten für PRODUCT.md, ausgehend von dem, was wir ausgeliefert haben und was im Backlog liegt.“

Die Vorschläge des Agenten sind Entwürfe, und die Entscheidungen liegen bei dir. Wenn `/bug` einen Bug anlegt, trägt er eine vorgeschlagene Priorität ein; du bestätigst oder änderst sie beim Triagieren.

---

## 7. Direkt in GitHub Projects erledigen

Alles oben lässt sich auch von Hand auf dem Board erledigen. Die gespeicherten Ansichten (eingerichtet mit `haam.py github-project`) sind dein Arbeitsplatz:

| Ansicht | Wofür |
|---|---|
| **Triage** (status: Triage) | Dein täglicher Eingang |
| **Epics** (label: epic) | Jedes Feature und wie weit seine Sub-Issues sind |
| **Waiting on me** (status: Decision, UAT) | Entscheidungen und Tests |
| **Agent queue** (status: Ready, unassigned) | Was die Agenten als Nächstes nehmen, nach Priorität |
| **Bugs** | Alle offenen Bugs nach Priorität |
| **Ideas inbox** | Ideen, die triagiert oder bewertet werden |
| **Board** | Der ganze Ablauf, gruppiert nach Status |

| Aufgabe | Auf dem Board |
|---|---|
| Einen Eintrag triagieren | Öffne ihn. Setz **Priority** und **Status**; korrigiere das Strang-Label in der Seitenleiste des Issues; kommentiere deine Begründung |
| Parken | Status **Parked** und ein Kommentar: „wieder anschauen, wenn…“ |
| Ablehnen oder als Duplikat markieren | Status **Canceled**, dann das Issue als *not planned* oder *duplicate* schließen |
| Eine Idee freigeben (G1) | Status **Backlog**; Label `stream:idea` durch `stream:feature` ersetzen; Priority setzen; „Freigegeben“ kommentieren |
| Eine Spec freigeben (G2) | „Spec freigegeben“ im Issue kommentieren; dann Status **Ready** und Label `agent-ready` |
| Issues zu einem Epic bündeln | Ein Issue mit Label `epic` anlegen; die anderen als seine Sub-Issues hinzufügen |
| Viele Einträge neu ordnen | Tabellenlayout, gruppiert oder sortiert nach Priority; die Zellen bearbeiten (du kannst einen Wert kopieren und in mehrere ausgewählte Zellen einfügen) |

Überlass das hier den Skills: Beanspruchen (**In Progress**) ist Aufgabe der Agenten. Testen und Ausliefern geht am einfachsten mit `/test`; von Hand geht es so: dem PR das Label `uat-passed` geben (das gibt das Mergen frei), ihn mergen, den Deploy freigeben (Actions → der Lauf → Review deployments), dann das Issue auf **Done** setzen und schließen. Ist der Test fehlgeschlagen, kommentiere im Issue, was nicht stimmt, setz das Label `uat-failed`, setz es zurück auf **Ready** und entferne die zugewiesene Person.

---

## 8. Direkt in Linear erledigen

| Aufgabe | In Linear |
|---|---|
| Triage | Nutze den **Triage**-Eingang des Teams. Du kannst annehmen, ablehnen, als Duplikat markieren oder zurückstellen. **Setz nach dem Annehmen den HAAM-Status selbst** (Ready für einen Bug, Discovery für eine zu bewertende Idee), weil das Annehmen den Eintrag in den Standardstatus des Teams verschiebt. Setz die Priorität |
| Parken oder ablehnen | Status **Parked** oder **Canceled**, mit einem Kommentar |
| Issues zu einem Epic bündeln | Ein Issue mit Label `epic` anlegen; es als Parent der zugehörigen Issues setzen |
| Eine Idee freigeben (G1) | Status **Backlog**, Label `stream:idea` durch `stream:feature` ersetzen, Priorität setzen, kommentieren |
| Eine Spec freigeben (G2) | „Spec freigegeben“ im Issue kommentieren; dann Status **Ready** und Label `agent-ready` |
| Neu ordnen | Die Ansichten aus `docs/setup/LINEAR-SETUP.md` §7, sortiert nach Priorität; das Befehlsmenü (Cmd/Ctrl+K) ändert Priorität oder Status schnell |

Wie auf GitHub folgen Agenten dem Prioritätsfeld, nicht der manuellen Reihenfolge einer Liste.

---

## 9. Mit anderen Menschen arbeiten

- **Ein Product Owner pro Produkt** setzt Prioritäten und lässt Gates bestehen. Alle anderen schlagen vor: `/idea`, `/bug`, Kommentare.
- Bitte Kollegen, beim Melden eine Priorität vorzuschlagen. Du bestätigst sie bei der Triage.
- **Meinungsverschiedenheiten gehören ins Issue,** nicht in private Chats. Der Product Owner entscheidet und begründet es in einem Kommentar.
- Bist du abwesend, benenne eine Vertretung für Freigaben (`haam.py config --backup-approvers`) und sag ihr, welche Einträge ohne dich weiterlaufen dürfen.

---

## 10. Die Kosten für GitHub Actions niedrig halten

Jeder Pull Request lässt CI und zwei KI-Reviews auf den Maschinen von GitHub laufen, und private Repositories haben ein monatliches Kontingent an Minuten. Agenten arbeiten schnell, also kann das Kontingent in wenigen Tagen aufgebraucht sein. Was am meisten hilft, in dieser Reihenfolge:
1. **Erst nachsehen:** `python3 tools/haam/haam.py ci-usage` zeigt, welche Workflows und Jobs die Minuten verbraucht haben.
2. **Weniger Pull Requests:** Bündle die kleinen Einträge eines Epics in einem (`/work epic #9`) und halte das Limit für offene PRs niedrig (`max_open_prs` in `haam.config.json`).
3. **Reviews auf deinem Computer:** `haam.py settings --set review=local --apply --human` (oder `/haam-settings`). Die KI-Reviews nutzen dann deinen Claude-Plan statt Minuten; geschützte Bereiche (`human-review`) werden weiterhin auf GitHub geprüft. Die Abwägung: Auf GitHub ist das Review-Ergebnis manipulationssicher, lokal nicht. Die Reviews laufen in frischen Sitzungen ohne Schreibrechte, mit den Anweisungen von `main`, aber der Agent, der die Änderung gebaut hat, startet sie, und alles, was deinen Login nutzt, könnte ein bestandenes Ergebnis melden. Für mehr Trennung führe `haam.py review <ID>` selbst aus deinem eigenen Chat aus.
4. **Dein eigener Runner:** `haam.py settings --set runner=self-hosted --apply --human`, nachdem du eine Maschine registriert hast, die eingeschaltet bleibt (`docs/setup/GITHUB-SETUP.md` §8).
5. **Um kleinere CI bitten:** Hat das Projekt getrennte Teile (z. B. Backend und mobile App), lass einen Agenten `make check` so anpassen, dass nur die Teile laufen, die ein PR berührt.

## 11. Fallen, die du vermeiden solltest

- **Alles ist High.** Dann ist nichts High. Stuf herunter, bis etwa jeder fünfte Eintrag High oder Urgent ist.
- **Mehr Agenten, als du testen kannst.** Die Arbeit staut sich im UAT und veraltet. Weniger, kleinere Einträge kommen schneller voran.
- **„Bau es einfach“ in einem Chat.** Lege zuerst das Issue an (`/bug`, `/idea`): Das dauert eine Minute und bewahrt Historie, Priorität und Claim.
- **Eine Spec freigeben, ohne die Akzeptanzkriterien zu lesen.** Genau das baut der Agent, und dagegen testest du. Lies sie.
- **Prioritäten nur im Kopf.** Stehen sie nicht in `PRODUCT.md` und im Tracker, können Agenten ihnen nicht folgen.
- **Bruchstücke ohne das große Ganze bauen.** Sind mehrere Issues eigentlich ein Feature, bündle sie zu einem Epic und forme es, bevor irgendwer die Teile spezifiziert.
- **Epics, die nie enden.** Ist ein Epic seit Monaten offen, trenn das Erledigte ab und schließ es.
- **Triage auf „später“ verschieben.** Der Eingang wächst, und dringende Bugs verstecken sich darin.

---

## 12. Checklisten

**Täglich**
- [ ] Alles in UAT mit `/test` getestet
- [ ] Triage-Eingang leer
- [ ] An dringenden Bugs arbeitet ein Agent
- [ ] Fragen der Agenten beantwortet

**Wöchentlich**
- [ ] Lose Issues zu Epics gebündelt; oberstes Epic geformt
- [ ] Warteschlange Decision entschieden
- [ ] Specs freigegeben oder kommentiert
- [ ] Ready und Backlog neu geordnet
- [ ] Festhängender Arbeit nachgegangen (`/triage stale`)
- [ ] Parked-Einträge wieder angeschaut
- [ ] Folge-Issues von Overrides geschlossen
- [ ] Eine Prozessverbesserung festgehalten

**Monatlich**
- [ ] Aktuelle Prioritäten in `PRODUCT.md` neu geschrieben
- [ ] Alte Low-Einträge geparkt
