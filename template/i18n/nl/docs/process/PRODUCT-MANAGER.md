# Werken als product manager

*Een gids voor de mens die beslist wat er gebouwd wordt. Agents hoeven hem niet te lezen; jij wel.*

In HAAM beslis jij **wat** en **waarom**; agents bedenken **hoe** en doen het. Agents zijn snel, dus de snelheid van het hele systeem wordt bepaald door hoe snel jij triëert, beslist, goedkeurt en test. Je belangrijkste taak is de wachtrij **Waiting on me** kort te houden en de **Agent queue** op de juiste dingen gericht.

De voorbeelden gebruiken ID's van GitHub Projects (`#12`); op Linear is hetzelfde item `APP-12`. Commando's worden geschreven als `/name`; in Codex gebruik je `$name`.

---

## 1. Je taak op één pagina

| Wat alleen jij doet | Hoe vaak | Met AI | Direct in de tracker |
|---|---|---|---|
| `docs/product/PRODUCT.md` actueel houden: huidige prioriteiten, harde voorwaarden, kerntrajecten | Maandelijks | "Werk PRODUCT.md bij: onze prioriteiten zijn nu…" | Het bestand bewerken (via een PR) |
| Nieuwe ideeën en bugs triëren | Dagelijks | `/triage` | Weergave Triage: prioriteit, status, labels |
| Verwante issues in epics groeperen en de vragen van de agent over elke epic beantwoorden | Wekelijks | `/triage group`, daarna `/epic #9` | Epic-issue (label `epic`) met sub-issues |
| Prioriteiten instellen en wijzigen | Dagelijks en wekelijks | `/triage`, `/triage backlog` | Veld Priority |
| Beslissen over beoordeelde ideeën (G1) | Wekelijks | `/decide #12 approve high` | Status, labels, commentaar (§7–8) |
| Specs goedkeuren (G2) | Zodra ze binnenkomen | Lees de spec (gelinkt op het issue), daarna "spec for #12 approved" | Commentaar "spec approved"; Status Ready, label `agent-ready` |
| Wijzigingen testen (G4) en live zetten (G5) | Dagelijks | `/test`, daarna antwoorden met `pass` → `ship`, of zeggen wat er mis is | GitHub: label `uat-passed`, mergen, de deploy goedkeuren |
| Vervolgissues van overrides sluiten | Wekelijks | "Laat de openstaande vervolgissues van overrides zien" | Weergave: label `override-followup` |

Alles wat je beslist, komt in de tracker of in Git, nooit alleen in een chat. Als het daar niet is opgeschreven, weet de volgende agent het niet.

---

## 2. Je ritme

### Dagelijks (10–15 minuten)
1. **Eerst testen.** Typ `/test all`: de agent loodst je door elke wijziging die op je wacht, de een na de ander (§2a), en zet daarna alles wat geslaagd is met één deploy live. Agents kunnen pas afronden als jij dat gedaan hebt, en hun context veroudert.
2. **Maak de Triage-inbox leeg** (`/triage`, of de weergave Triage). Niets zou er langer dan twee werkdagen moeten liggen.
3. **Urgente bugs:** als er een is, zet er nu een agent op: nieuw chatvenster, `/work bugs`.
4. Lees de overdrachts- en "blocked"-commentaren van agents door en beantwoord hun vragen.

### 2a. Een wijziging testen: de hele cyclus
1. Typ **`/test`** (of `/test #12`). De agent zet de wijziging op je computer, start de app en geeft je de link en een korte checklist: *doe dit → dan zie je dat*.
2. Probeer het uit. Antwoord daarna met één woord of één zin:
   - **`pass`** → de agent opent de pull request (tot nu toe was er geen: je testte de branch van de agent), de checks draaien één keer op precies wat jij getest hebt, en hij vraagt *"Live zetten als de checks slagen?"* Antwoord **`ship`**: hij wacht op de checks, merget, keurt de productiedeploy voor je goed en sluit het issue. Je krijgt *"#12 staat live."* Antwoord `later` om het aan te houden.
   - Als je project **met de hand deployt** (`"deploy": "manual"`), merget de agent en vraagt hij je daarna om te deployen; antwoord **`live`** als het live staat, en hij sluit het issue.
   - Als de checks of reviews daarna een probleem vinden, gaat het terug naar de agents zoals een mislukte test, en komt het bij je terug zodra het opgelost is.
   - **Wat er mis ging** (*"stap 3: de exportknop ontbreekt nog steeds op mobiel"*) → de agent legt het vast op het issue, geeft het het label `uat-failed` en stuurt het terug naar de agents, die het als eerste oplossen. Als het opgelost is, komt het terug bij `/test`.
3. Dat is alles. Je hoeft geen branches, labels of het board aan te raken.

**Hoe HAAM draait, is jouw keuze.** Typ `/haam-settings`: het loopt elke instelling met je door met je eigen cijfers (Actions-minuten, de UAT-wachtrij), raadt één optie aan en past toe wat je kiest:
- wanneer CI en de AI-reviews draaien (bij elke PR, op je computer, alleen voor beschermde gebieden, of uit);
- wat je zelf test (alles, wat je per issue beslist, of bugs overslaan);
- hoe wijzigingen gegroepeerd worden (per issue, per epic, of één release-PR voor alles wat je hebt goedgekeurd);
- of deploys op je goedkeuring wachten;
- de limieten.

`python3 tools/haam/haam.py settings --explain` toont ze allemaal.

**Wijzigingen die je zelf niet kunt testen** (updates van de kit of de config, dependency-updates, refactors die je niet zou merken, CI): markeer ze met `uat:skip` als je ze triëert, of zeg "spec approved, no UAT". Ze komen nooit bij `/test`: hun PR merget vanzelf zodra CI en beide AI-reviews slagen (GitHub Projects), en je volgende `ship` deployt ze samen met al het andere en sluit ze. Als je een tijd niets live zet, voer dan toch `/test` uit en antwoord `ship`, of `ship --all`: hun deploy wacht op je goedkeuring. Op Linear zet je ze op naam live (`ship APP-12 --human`). Gebruik het alleen voor wijzigingen die geen gebruiker zou merken; nooit voor beschermde gebieden.

### Wekelijks (30–45 minuten)
1. **Groepeer** losse issues in epics (`/triage group`) en geef de bovenste epic samen met de agent vorm (`/epic #9`).
2. **Beslis** over alles in **Decision** (G1).
3. **Review specs** (gelinkt op elk issue) en keur ze goed of geef commentaar (G2).
4. **Rangschik** Ready en Backlog opnieuw tegen de huidige prioriteiten (`/triage backlog`).
5. **Zoek vastgelopen werk:** `/triage stale` (geclaimd maar stil, UAT die te lang wacht, beslissingen die te laat zijn).
6. **Bekijk Parked-items opnieuw** waarvan de "terugkomen wanneer" is uitgekomen.
7. **Sluit vervolgissues van overrides** (label `override-followup`).
8. Verbeter één ding in het proces (een `/idea` met het label `area:process`).

### Maandelijks of per kwartaal (30 minuten)
1. Herschrijf **Huidige prioriteiten** in `PRODUCT.md`: 3–5 resultaten, op volgorde. Agents gebruiken ze om prioriteiten voor te stellen en knopen door te hakken, dus dit is het allernuttigste wat je actueel kunt houden.
2. **Snoeien:** alles met Low dat meer dan twee maanden heeft gewacht → parkeer het met een "terugkomen wanneer". Een korte backlog is een bruikbare backlog.

---

## 3. Triage: beslissen wat elk nieuw item is

De status **Triage** is je inbox. Ideeën en bugs komen daar binnen via `/idea`, `/bug`, de issueformulieren, andere mensen en agents. Streef naar een lege inbox aan het eind van elke dag.

Als meerdere items met elkaar te maken lijken te hebben, of de meeste context missen, **groepeer ze dan eerst** (§4): één feature tegelijk triëren is sneller en beter dan losse fragmenten triëren.

Beantwoord voor elk item vier vragen:

1. **Is het duidelijk en nieuw?** Duplicaat → sluit het en link het origineel. Niet genoeg informatie → stel je vraag in een commentaar en laat het in Triage staan.
2. **Wat is het?** Een **bug** betekent dat iets niet werkt zoals bedoeld. Een **idee** betekent nieuw of gewijzigd gedrag. "Werkt zoals ontworpen, maar de gebruiker verwachtte iets anders" is een idee, geen bug. Corrigeer het stroomlabel als het niet klopt.
3. **Hoe belangrijk is het?** Stel de prioriteit in (§5).
4. **Wat gebeurt er nu?**

| Item | Jouw besluit | Status daarna | Wat er volgt |
|---|---|---|---|
| Bug met duidelijke reproductiestappen | **Ready** | Ready, met een prioriteit | Een agent pakt het op (`/work bugs`) |
| Bug zonder genoeg om mee verder te kunnen | **Info nodig** | Blijft in Triage, met je vraag als commentaar | Jij of de melder antwoordt, daarna opnieuw triëren |
| Urgente bug | **Ready, nu beginnen** | Ready, Urgent | Zet nu een agent aan het werk; `/override` is beschikbaar als de deploy niet kan wachten |
| Idee dat het onderzoeken waard is | **Beoordelen** | Discovery, met een prioriteit | Een agent schrijft de beoordeling (`/work ideas` of `/assess #12`) |
| Idee dat je beter zou begrijpen door het uit te proberen | **Prototype** | Discovery, label `mode:prototype` | Een agent bouwt een werkende wegwerpversie (`/spike #12`); je probeert het uit met `/test` en beslist |
| Goed idee, verkeerd moment | **Parkeren** | Parked, met een commentaar "terugkomen wanneer…" | Komt terug bij een wekelijkse review |
| Idee dat je niet gaat doen | **Afwijzen** | Canceled, met een reden van één regel | Gesloten |
| Duplicaat | **Duplicaat** | Canceled, gelinkt aan het origineel | Gesloten |

Ook kleine ideeën gaan door een beoordeling. Vraag om een snelle ("beoordeel #12, houd het kort"). In de beoordeling controleert de agent de codebase en de risico's, en het kost je een minuut om te lezen.

---

## 4. Epics: issues groeperen in features

Losse issues missen vaak context. "Exportknop ontbreekt op mobiel", "Exporteren naar CSV" en "Geplande rapporten" zijn drie fragmenten van één feature, en als je ze een voor een triëert, ziet elk er klein en onduidelijk uit. Een **epic** is een parent-issue (label `epic`) dat de issues voor één resultaat groepeert en de context bevat die ze missen: voor wie het is, hoe succes eruitziet, wat binnen en buiten scope valt, en de volgorde van de slices. Die context staat in een korte **epic-briefing** in `docs/epics/`.

**Gebruik een epic voor:** drie of meer issues over hetzelfde resultaat; een idee dat te groot is voor één spec (maat L of XL); een verzoek dat meerdere schermen of modules raakt.
**Gebruik er geen voor:** één bug; een bak "diversen" met dingen die niets met elkaar te maken hebben; een thema dat nooit af is ("performance", "UX-polish"): dat zijn prioriteiten, geen epics. Een epic moet af te ronden zijn, in weken in plaats van kwartalen.

### Hoe een epic verloopt
1. **Groeperen.** `/triage group` bekijkt de losse issues en stelt epics voor: een titel, het resultaat in één regel, welke issues erbij horen en waarom. Je zegt `ok` of past aan (`merge 2 and 3`, `#40 out`). Of begin vanuit een thema: `/epic "reporting"`.
2. **Vormgeven.** `/epic #9`: de agent leest elk issue in de epic, de productcontext en de relevante code, schrijft een concept van de briefing en **stelt je dan per ronde tot vijf vragen**: voor wie het is, hoe succes eruitziet, must-haves tegenover nice-to-haves, beperkingen, wat niet mag veranderen, hoe het zich verhoudt tot de rest. Daarna stelt hij een opruimactie voor: duplicaten om te sluiten, gaten om als nieuwe issues toe te voegen, onduidelijke issues om te herschrijven, grote om te splitsen, een volgorde. Er verandert niets tot je het bevestigt.
3. **Eén keer beslissen (G1).** `/assess #9` voegt inspanning en haalbaarheid voor de hele epic toe; `/decide #9 approve high` keurt hem en de ideeën erin in één keer goed.
4. **Slice voor slice specificeren en bouwen.** Elk sub-issue krijgt een eigen spec en passeert G2 apart. Agents bouwen sub-issues, nooit de epic zelf.
5. **Afronden.** Als het laatste sub-issue live gaat, biedt de agent aan de epic te sluiten.

**Prioriteiten:** geef de epic een prioriteit; de issues erin krijgen dezelfde, tenzij je iets anders zegt. Een bug binnen een epic kan nog steeds urgenter zijn dan de epic.

**De vragen van de agent beantwoorden:** korte antwoorden zijn prima. "Weet ik nog niet" is een geldig antwoord: het blijft open staan in de briefing. Antwoord over wat gebruikers nodig hebben en waarom; laat het hoe aan de agents over.

### Epics direct in de tracker
- **GitHub Projects:** maak een issue aan en voeg het label `epic` toe; voeg daarna in de sectie met sub-issues van de epic de issues toe die erbij horen (of stel vanuit elk issue de parent in). Gebruik op het board de weergave **Epics**, en toon de velden *Parent issue* en *Sub-issues progress* in tabelweergaven, zodat elke kaart zijn epic laat zien.
- **Linear:** maak een issue aan met het label `epic` en maak de verwante issues er sub-issues van (stel hun parent in). Voor een heel groot initiatief dat meerdere epics omvat, kan een Linear-project de epics bevatten.

---

## 5. Prioriteren

### 5.1 De vier niveaus

| Prioriteit | Toets | Verwachte aanpak |
|---|---|---|
| **Urgent** | Productie is kapot voor een kerntraject, data kan verloren gaan of uitlekken, een beveiligingslek, of een wettelijke/compliance-deadline is in gevaar | Vandaag beginnen. Gates kunnen worden overruled, met een vervolgissue |
| **High** | Brengt direct een van de huidige prioriteiten in `PRODUCT.md` verder, of een bug in een kerntraject zonder workaround | Als volgende, deze week |
| **Medium** | Nuttig, maar niet bij de huidige prioriteiten, of het bewijs is mager | Op volgorde, als High leeg is |
| **Low** | Leuk om te hebben, cosmetisch, randgeval | Als er tijd is; na twee maanden snoeien |
| *(geen)* | Nog niet getrieerd | Agents bouwen het niet |

Blijf eerlijk: als meer dan ongeveer een op de vijf openstaande items High of Urgent is, betekenen de niveaus niets meer. Verlaag iets.

### 5.2 Bugs: impact × bereik

| | De meeste gebruikers, of een kerntraject | Sommige gebruikers | Een paar gebruikers, of een randgeval |
|---|---|---|---|
| **Blokkeert de taak, data verloren of uitgelekt, security, juridisch** | Urgent | Urgent | High |
| **Verkeerd resultaat, maar er is een workaround** | High | Medium | Low |
| **Irritant of cosmetisch** | Medium | Low | Low |

### 5.3 Ideeën en features: waarde, vertrouwen, omvang

Na een beoordeling heb je drie dingen: **waarde** (hoeveel het een huidige prioriteit vooruithelpt), **vertrouwen** (hoe goed het bewijs is) en **omvang** (XS–XL, vanuit de codebase). Vuistregels:
- **High:** duidelijke waarde voor een huidige prioriteit, goed bewijs, omvang S–M.
- **Medium:** goede waarde maar zwakker bewijs; of hoge waarde maar omvang L–XL (vraag om het te splitsen).
- **Low:** weinig waarde, wat de omvang ook is.
- **Niet bij de huidige prioriteiten?** Hoogstens Medium, tenzij je eerst de prioriteiten verandert.

Om twee ideeën snel te vergelijken: waarde (1–3) × vertrouwen (0,5 / 0,8 / 1) ÷ omvang (XS 1, S 2, M 3, L 5, XL 8). De hoogste score gaat eerst. Het is een manier om knopen door te hakken, geen formule om blind te volgen.

### 5.4 Volgorde binnen een prioriteit
Agents nemen **bugs vóór features, ouder vóór nieuwer, kleiner vóór groter**. Ze lezen de prioriteit, niet de positie van een kaart op het board. Als X vóór Y moet gebeuren, geef X dan een hogere prioriteit, of schrijf `Blocked by #X` in de beschrijving van Y.

### 5.5 Houd de wachtrijen gezond

| Wachtrij | Gezonde grootte | Zo niet |
|---|---|---|
| **Agent queue** (Ready) | 3–10 items | Leeg: agents zitten stil, dus specificeer meer. Meer dan 10: prioriteiten verouderen, dus rangschik opnieuw |
| **Decision** | 5 of minder | Plan 20 minuten in en beslis |
| **UAT** | `max_in_uat` (standaard 10) | Agents houden nieuwe builds tegen bij de limiet (`haam.py capacity`): het gaat om je testtijd, de belangrijkste limiet in test-first. Test met `/test all`; items die de agents volledig hebben geverifieerd, keur je goed met één antwoord (`pass all verified`). Voor een weekend agentwerk open je een batchvenster in `/haam-settings`: een verhoging die vanzelf afloopt |
| **Draaiende agents** | Niet meer dan je morgen kunt testen | Minder agents, kleinere items |
| **PR's die klaar zijn** | `max_open_prs` in `haam.config.json` (standaard 10) | Agents houden nieuwe builds tegen bij de limiet: elke PR die klaar is, kost bij elke push CI-minuten. Drafts en PR's met alleen docs tellen niet mee. Specs en beoordelingen gaan door. Test en zet live wat er openstaat |

### 5.6 Prioriteiten wijzigen
Wijzig ze wanneer de feiten veranderen, maar zeg in een commentaar waarom. Agents en collega's lezen de geschiedenis. Verlaag een Urgent item nooit stilletjes: plaats een commentaar en laat het weten aan wie het gemeld heeft.

---

## 6. Het doen met AI

Gebruik **je eigen chat in de hoofdmap van het project**, niet een van de agent-chats die `/work` draaien.

| Je wilt… | Typ |
|---|---|
| Losse issues in epics groeperen | `/triage group` |
| Eén epic vormgeven: briefing, vragen voor jou, opruimen | `/epic #9` (of `/epic "reporting"` om vanuit een thema te beginnen) |
| De inbox triëren | `/triage` |
| Ready en Backlog opnieuw rangschikken tegen de prioriteiten | `/triage backlog` |
| Vastgelopen of vergeten werk vinden | `/triage stale` |
| Een idee of bug vastleggen, waar je ook bent | `/idea …`, `/bug …` |
| Een idee laten beoordelen | `/assess #12` (of laat `/work ideas` het kiezen) |
| Beslissen (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Een spec goedkeuren (G2) | Lees hem (gelinkt op het issue), daarna: "spec for #12 approved" |
| Een wijziging testen, en die daarna live zetten of terugsturen (G4, G5) | `/test` (of `/test #12`), daarna `pass` → `ship`, of zeg wat er mis is |
| Iets sluiten dat op een andere manier gemerged is | `/release #12` |
| Noodgeval | `/override #12 "<reason>"` |

**Hoe `/triage` werkt.** De agent leest `PRODUCT.md` en de items en laat je dan één tabel zien: voorgestelde stroom, prioriteit, volgende stap en een korte reden voor elk item. Antwoord `ok` om alles toe te passen, of met wijzigingen (`#14 Low, #9 park until Q3`). Er verandert niets tot je antwoordt, hij past precies toe wat je bevestigd hebt, en hij plaatst op elk item een commentaar, zodat de reden vastligt. Hij keurt nooit ideeën voor je goed; daarvoor verwijst hij je naar `/decide`.

**Vragen die het waard zijn om aan je agent te stellen:**
- "Wat wacht er op mij?"
- "Wat hebben de agents sinds gisteren afgerond, en wat is er geblokkeerd?"
- "Welke Ready-items passen niet bij onze huidige prioriteiten?"
- "#12 is te groot. Stel een splitsing voor in stukken van maat S."
- "Vergelijk #12 en #15: welke moet eerst, en waarom?"
- "Schrijf een concept voor nieuwe huidige prioriteiten in PRODUCT.md, op basis van wat we live hebben gezet en wat er in de backlog staat."

De suggesties van de agent zijn concepten, en de beslissingen zijn van jou. Als `/bug` een bug aanmaakt, vult hij een voorgestelde prioriteit in; die bevestig of wijzig je bij het triëren.

---

## 7. Het direct doen in GitHub Projects

Alles hierboven kun je ook met de hand op het board doen. De opgeslagen weergaven (ingesteld met `haam.py github-project`) zijn je werkplek:

| Weergave | Gebruik je voor |
|---|---|
| **Triage** (status: Triage) | Je dagelijkse inbox |
| **Epics** (label: epic) | Elke feature en hoe ver de sub-issues ervan zijn |
| **Waiting on me** (status: Decision, UAT) | Beslissingen en tests |
| **Agent queue** (status: Ready, niet toegewezen) | Wat agents als volgende oppakken, op prioriteit |
| **Bugs** | Alle openstaande bugs op prioriteit |
| **Ideas inbox** | Ideeën die getrieerd of beoordeeld worden |
| **Board** | De hele flow, gegroepeerd op status |

| Taak | Op het board |
|---|---|
| Een item triëren | Open het. Stel **Priority** en **Status** in; corrigeer het stroomlabel in de zijbalk van het issue; zet je reden in een commentaar |
| Parkeren | Status **Parked**, en een commentaar: "terugkomen wanneer…" |
| Afwijzen of als duplicaat markeren | Status **Canceled**, sluit daarna het issue als *not planned* of *duplicate* |
| Een idee goedkeuren (G1) | Status **Backlog**; vervang het label `stream:idea` door `stream:feature`; stel Priority in; commentaar "Goedgekeurd" |
| Een spec goedkeuren (G2) | Commentaar "spec approved" op het issue; daarna Status **Ready** en label `agent-ready` |
| Issues in een epic groeperen | Maak een issue aan met het label `epic`; voeg de andere toe als sub-issues ervan |
| Veel items opnieuw rangschikken | Tabelweergave, gegroepeerd of gesorteerd op Priority; bewerk de cellen (je kunt een waarde kopiëren en in meerdere geselecteerde cellen plakken) |

Laat dit aan de skills over: claimen (**In Progress**) is het werk van de agents. Testen en live zetten gaat het makkelijkst met `/test`; met de hand gaat het zo: voeg het label `uat-passed` toe aan de PR (daarmee wordt mergen vrijgegeven), merge hem, keur de deploy goed (Actions → de run → Review deployments), zet daarna het issue op **Done** en sluit het. Als de test faalde, zet dan in een commentaar op het issue wat er mis is, voeg het label `uat-failed` toe, zet het terug op **Ready** en haal de assignee weg.

---

## 8. Het direct doen in Linear

| Taak | In Linear |
|---|---|
| Triëren | Gebruik de **Triage**-inbox van het team. Je kunt accepteren, weigeren, als duplicaat markeren of snoozen. **Stel na het accepteren zelf de HAAM-status in** (Ready voor een bug, Discovery voor een idee om te beoordelen), want accepteren zet het item op de standaardstatus van het team. Stel de prioriteit in |
| Parkeren of afwijzen | Status **Parked** of **Canceled**, met een commentaar |
| Issues in een epic groeperen | Maak een issue aan met het label `epic`; stel het in als parent van de verwante issues |
| Een idee goedkeuren (G1) | Status **Backlog**, vervang het label `stream:idea` door `stream:feature`, stel de prioriteit in, commentaar |
| Een spec goedkeuren (G2) | Commentaar "spec approved" op het issue; daarna status **Ready** en label `agent-ready` |
| Opnieuw rangschikken | De weergaven uit `docs/setup/LINEAR-SETUP.md` §7, gesorteerd op prioriteit; het commandomenu (Cmd/Ctrl+K) wijzigt snel de prioriteit of status |

Net als op GitHub volgen agents het prioriteitsveld, niet de handmatige volgorde van een lijst.

---

## 9. Werken met andere mensen

- **Eén product owner per product** stelt de prioriteiten in en laat werk door de gates. Alle anderen doen voorstellen: `/idea`, `/bug`, commentaar.
- Vraag collega's een prioriteit voor te stellen als ze iets melden. Jij bevestigt die bij de triage.
- **Meningsverschillen horen op het issue,** niet in privéchats. De product owner beslist en zegt in een commentaar waarom.
- Als je weg bent, wijs dan een vervangende goedkeurder aan (`haam.py config --backup-approvers`) en vertel die welke items zonder jou verder mogen.

---

## 10. De kosten van GitHub Actions laag houden

Elke pull request draait CI en twee AI-reviews op de machines van GitHub, en private repositories hebben een maandelijks tegoed aan minuten. Agents werken snel, dus het tegoed kan binnen een paar dagen op zijn. Wat het meest helpt, op volgorde:
1. **Kijk eerst:** `python3 tools/haam/haam.py ci-usage` laat zien welke workflows en jobs de minuten gebruikt hebben.
2. **Minder pull requests:** bundel de kleine items van een epic in één (`/work epic #9`), en houd de limiet voor open PR's laag (`max_open_prs` in `haam.config.json`).
3. **Reviews op je computer:** `haam.py settings --set review=local --apply --human` (of `/haam-settings`). De AI-reviews gebruiken dan je Claude-abonnement in plaats van minuten; beschermde gebieden (`human-review`) worden nog steeds op GitHub gereviewd. De afweging: op GitHub is het reviewresultaat bestand tegen manipulatie; lokaal niet. De reviews draaien in nieuwe, alleen-lezen sessies met de instructies van `main`, maar de agent die de wijziging bouwde, is degene die ze start, en alles wat jouw login gebruikt, zou een geslaagd resultaat kunnen posten. Voor meer scheiding voer je `haam.py review <ID>` zelf uit vanuit je eigen chat.
4. **Je eigen runner:** `haam.py settings --set runner=self-hosted --apply --human` nadat je een machine hebt geregistreerd die aan blijft staan (`docs/setup/GITHUB-SETUP.md` §8).
5. **Vraag om kleinere CI:** als het project losse onderdelen heeft (bijv. backend en mobiele app), laat dan een agent `make check` alleen de onderdelen laten draaien die een PR raakt.

## 11. Valkuilen

- **Alles is High.** Dan is niets het. Verlaag tot ongeveer een op de vijf items High of Urgent is.
- **Meer agents dan je kunt testen.** Werk stapelt zich op in UAT en veroudert. Minder en kleinere items gaan sneller.
- **"Bouw het nou maar gewoon" in een chat.** Maak eerst het issue aan (`/bug`, `/idea`): het kost een minuut en bewaart de geschiedenis, de prioriteit en de claim.
- **Een spec goedkeuren zonder de acceptatiecriteria te lezen.** Dat is wat de agent bouwt en waartegen jij test. Lees ze.
- **Prioriteiten alleen in je hoofd.** Als ze niet in `PRODUCT.md` en de tracker staan, kunnen agents ze niet volgen.
- **Fragmenten bouwen zonder het grote geheel.** Als meerdere issues eigenlijk één feature zijn, groepeer ze dan in een epic en geef die vorm voordat iemand de stukken specificeert.
- **Epics die nooit af zijn.** Als een epic al maanden openstaat, splits dan af wat klaar is en sluit hem.
- **Triage laten liggen voor "later".** De inbox groeit, en urgente bugs verstoppen zich erin.

---

## 12. Checklists

**Dagelijks**
- [ ] Alles in UAT getest met `/test`
- [ ] Triage-inbox leeg
- [ ] Op urgente bugs zit een agent
- [ ] Vragen van agents beantwoord

**Wekelijks**
- [ ] Losse issues in epics gegroepeerd; bovenste epic vormgegeven
- [ ] Over de Decision-wachtrij beslist
- [ ] Specs goedgekeurd of van commentaar voorzien
- [ ] Ready en Backlog opnieuw gerangschikt
- [ ] Vastgelopen werk nagejaagd (`/triage stale`)
- [ ] Parked-items opnieuw bekeken
- [ ] Vervolgissues van overrides gesloten
- [ ] Eén procesverbetering vastgelegd

**Maandelijks**
- [ ] Huidige prioriteiten in `PRODUCT.md` herschreven
- [ ] Oude Low-items geparkeerd
