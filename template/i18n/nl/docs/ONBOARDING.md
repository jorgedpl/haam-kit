# Onboarding voor developers

Welkom. Deze repo wordt gebouwd door mensen en coding agents die samenwerken volgens de **Human-Agent Agile Methodology (HAAM)**. Je kunt de agent-tool gebruiken die je het liefst hebt: Claude Code, Cursor, Codex, Grok, Gemini of Copilot. Met deze gids ga je in ongeveer een uur van nul naar je eerste issue.

## De snelle manier: laat je agent je onboarden

1. Clone de repo en open je agent-tool in de hoofdmap ervan:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Zeg tegen je agent:
   - Claude Code, Cursor of Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Elke andere tool: *"Lees `.agents/skills/haam-onboard/SKILL.md` en volg het."*

Hij controleert je machine, je toegang en de koppeling met de tracker, zet je lokale hooks en `.env` op, draait de checks van het project, legt uit hoe we werken en stelt een eerste issue voor. Stappen waarvoor je wachtwoord of sleutels nodig zijn, doe je zelf, in je eigen terminal of editor. Je plakt nooit secrets in de chat.

Doe je het liever met de hand? De secties hieronder behandelen hetzelfde.

---

## 1. Eerst lezen (15 minuten)
1. `AGENTS.md`: de regels die elke agent volgt, welke tool ook. Ze gelden ook voor jou.
2. `docs/process/LIFECYCLE.md`: stromen, statussen, gates, wie wat doet.
3. `docs/process/GATES.md`: checklists, code review en overrides.
4. `docs/product/PRODUCT.md` en `docs/product/ARCHITECTURE.md`: wat we bouwen en hoe het in elkaar zit.

## 2. Accounts die je nodig hebt
| Account | Waarom | Vraag om |
|---|---|---|
| GitHub | Code, PR's, CI | Schrijfrechten op de repo |
| Tracker | Backlog en status | **GitHub Projects:** toegang tot het board (komt met de uitnodiging voor de repo). **Linear:** lidmaatschap van team **APP** |
| Je agent-tool | Coding agent | Je **eigen** account (Claude, Cursor, OpenAI, xAI…). Deel nooit accounts |
| Testdiensten | Lokaal draaien | Alleen testgegevens, van de product owner |

De projectadmin nodigt je uit met één commando: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. Je krijgt **geen** productiegegevens; deploys gaan via GitHub, met goedkeuring.

## 3. Tools installeren
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (verplicht; zonder gitleaks worden commits geblokkeerd): macOS `brew install gitleaks`; andere: https://github.com/gitleaks/gitleaks/releases
- De runtime van de taal van deze repo: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Je agent-tool

Controleer alles met: `python3 tools/haam/haam.py dev`

## 4. De code aan de praat krijgen
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Koppelen met de tracker
Controleer `"tracker"` in `haam.config.json`:
- **GitHub Projects:** voer één keer `gh auth refresh -s project` uit en test daarna: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** volg de sectie van je tool in `docs/setup/AGENTS-SETUP.md` (één keer inloggen) en vraag daarna je agent: *"Toon de Ready-issues in het Linear-team APP."*

## 6. Je persoonlijke instellingen (niet gedeeld)
Persoonlijke notities en voorkeuren horen in bestanden die git negeert: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, of de gebruikersinstellingen van je tool. Zet daar nooit gedeelde regels in. Als iets voor iedereen moet gelden, stel dan via een PR een wijziging aan `AGENTS.md` voor.

## 7. Dagelijkse werkwijze
Commando's worden hieronder geschreven als `/name`; in Codex gebruik je `$name`.

| Je wilt… | Doe dit |
|---|---|
| Zien wat er wacht | Weergave **Agent queue** in de tracker (om te bouwen) of **Waiting on me** |
| Een agent starten in een nieuw chatvenster | `/work` (of `/work bugs`) |
| In deze chat aan het werk gaan | `/next`, of `/build APP-123` |
| Triëren en prioriteren (product owner) | `/triage`, `/triage group`, `/epic`, en `docs/process/PRODUCT-MANAGER.md` |
| Een idee vastleggen | `/idea …` |
| Een bug melden | `/bug …` |
| Van een goedgekeurd idee een spec maken | `/spec APP-123` |
| Een wijziging testen (product owner) | `/test`, daarna `pass` → `ship`, of zeg wat er mis is |
| De wijziging van iemand anders testen (developer) | Volg `docs/uat/APP-123-*.md` en laat het de product owner weten |
| Je setup controleren | `python3 tools/haam/haam.py doctor` |

### Agents parallel draaien
Open één nieuw chatvenster per agent en typ `/work` (of `/work bugs`, `/work features`, `/work specs`, `/work ideas`; Codex: `$work`). De agent krijgt een eigen kopie van het project (een git worktree onder `.claude/worktrees/`), kopieert de lokale bestanden uit `.worktreeinclude` (zoals `.env`), pakt het bovenste item en werkt het af tot aan de overdracht. Houd je eigen chat in de hoofdmap voor ideeën, beslissingen en testen.

- **Claude Code in VS Code:** nieuw chattabblad met Cmd+Shift+Esc (Mac) of Ctrl+Shift+Esc (Windows/Linux). In een terminal: `claude --worktree`.
- **Andere tools:** als de tool een eigen optie voor worktrees of parallelle agents heeft, gebruik die; anders maakt `/work` de worktree aan en vertelt het je welke map je in een nieuw venster moet openen.
- **Een andere computer:** precies hetzelfde. De claim in de tracker voorkomt dat twee agents hetzelfde issue oppakken; geef de naam van de machine op als daarom gevraagd wordt, zodat het claimcommentaar laat zien waar het draait.
- **Ruim** afgeronde worktrees af en toe **op**: `python3 tools/haam/haam.py worktree clean` (plan), daarna `--apply`.
- **De branch van een agent testen:** het UAT-plan gebruikt `git switch --detach origin/<branch>`, wat werkt terwijl de worktree van de agent de branch nog heeft.

### Agents semi-autonoom draaien
- **Met toezicht:** typ `/next`, bekijk de keuze en laat hem werken. Je tool moet het vragen voordat hij pusht of PR's opent (zie de veilige instellingen in `docs/setup/AGENTS-SETUP.md`).
- **Zonder toezicht:** een geplande taak of cron draait je agent headless met de prompt `/next` (Codex: `$next`). Hij neemt alleen werk dat door de gate is gekomen, en stopt bij UAT voor een mens.
- Agents stoppen bewust bij elke menselijke gate. Jouw taak is de weergave **Waiting on me** kort te houden.

## 8. Hoe je werk gereviewd wordt
Elke PR wordt gecontroleerd door tests, een secret-scan, een dependency-audit en twee onafhankelijke AI-reviewers (spec/kwaliteit en security) die de code nooit hebben zien schrijven. Los hun **Blocking**-bevindingen op; als je denkt dat er een niet klopt, antwoord dan op de PR en vraag het de product owner, die kan overrulen met het label `ai-review-overruled`. Beschermde gebieden krijgen ook een menselijke review. Details: `docs/process/GATES.md` § Hoe code review werkt.

**Als je ooit een echte secret commit:** zeg het direct tegen de product owner. Hij moet worden ingetrokken en vervangen, ook als je hem in de volgende commit verwijdert.

## 9. Regels die het herhalen waard zijn
- Geen pushes naar `main`, geen merges, geen deploys door agents.
- Geen secrets of echte persoonsgegevens in code, tests, fixtures, de tracker of de chat. Persoonsgegevens zijn wettelijk beschermd (bijv. AVG/GDPR).
- Eén issue → één branch → één PR, klein genoeg om in 15 minuten te reviewen.
- Vul bij elke PR **Gebouwd met (Built with)** in (je tool en model).
- Wat niet in Git of in de tracker staat, bestaat niet voor de volgende persoon.

## 10. Hulp krijgen
- Vragen over het proces: vraag je agent *"wat hoort er volgens LIFECYCLE.md te gebeuren als…"*
- Toegang en inloggegevens: de product owner.
- Het proces verbeteren: open een `/idea` met het label `area:process`. Wijzigingen aan `AGENTS.md`, `.agents/`, configuratiemappen van agents en `.github/` hebben een review van de product owner nodig.
