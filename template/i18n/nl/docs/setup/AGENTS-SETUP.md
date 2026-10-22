# Agent-tools: setup per tool

HAAM werkt met elke coding agent. Elke tool leest **dezelfde regels** (`AGENTS.md`) en **dezelfde skills** (`.agents/skills/`), en werkt op **dezelfde tracker**: een GitHub Projects-board (via `python3 tools/haam/haam.py issue …`, dat elke agent kan uitvoeren) of Linear (via de MCP-server, `https://mcp.linear.app/mcp`). Alleen de bedrading verschilt.

Voer `python3 tools/haam/haam.py agents` uit om te zien wat er in deze repo gekoppeld is, en `python3 tools/haam/haam.py dev` om je machine te controleren.

## Hoe elke tool HAAM oppakt

| | Regels | Skills | Een skill aanroepen | Linear-MCP (alleen Linear-projecten) | Skills alleen voor mensen |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importeert `AGENTS.md` | `.claude/skills` (link naar `.agents/skills`) | `/build APP-1` | `.mcp.json` (in de repo) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (in de repo) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | per gebruiker: `codex mcp add` | `agents/openai.yaml` in elke skill |
| **Grok Build** | controleren bij de eerste run (zie hieronder) | `.grok/skills` (link naar `.agents/skills`) | `/build APP-1` | leest `.mcp.json` | volgens de tekst van de skill |
| **Gemini CLI** | `AGENTS.md` via `.gemini/settings.json` | `SKILL.md` op naam volgen | "volg .agents/skills/build" | per gebruiker | volgens de tekst van de skill |
| **GitHub Copilot** | `AGENTS.md` | `SKILL.md` op naam volgen | "volg .agents/skills/build" | per gebruiker | volgens de tekst van de skill |

Als een tool geen skills laadt, zeg dan: *"Open `.agents/skills/<name>/SKILL.md` en volg het."* De skills zijn gewone Markdown.

## Koppelen met de tracker (één keer per persoon)

**GitHub Projects:** je hoeft niets in je agent te installeren. Voer één keer `gh auth refresh -s project` uit en test met `python3 tools/haam/haam.py issue list`. De rest van deze sectie is voor projecten met **Linear**.

Linear logt je in met je eigen account (OAuth). Agents handelen als jou.

- **Claude Code:** open `claude` in de repo → keur de server `linear` goed → `/mcp` → **linear** → inloggen.
- **Cursor:** Settings → MCP → `linear` verschijnt vanuit `.cursor/mcp.json` → inschakelen → inloggen.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp`, en volg daarna de vraag om in te loggen.
- **Grok Build:** leest `.mcp.json`; zo niet, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Log in als daarom gevraagd wordt.
- **Gemini CLI / Copilot / andere:** voeg in de MCP-instellingen van de tool een externe MCP-server toe met de naam `linear` en de URL `https://mcp.linear.app/mcp`.

**Test:** vraag je agent *"Toon de Ready-issues in het Linear-team APP."*

## Meerdere agents tegelijk draaien

Elke agent-chat die bestanden wijzigt, heeft een eigen map nodig (een git worktree), anders overschrijven de chats elkaars werk. Begin elke agent-chat met `/work` (Codex: `$work`): die controleert waar hij is en zet zo nodig een worktree op. Je eigen chat blijft in de hoofdmap.

| Tool | Nieuwe agent-chat |
|---|---|
| **Claude Code (VS Code)** | Nieuw chattabblad: Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux), of Command Palette → "Claude Code: Open in New Tab". Typ `/work`; Claude verplaatst zichzelf naar een worktree. |
| **Claude Code (terminal)** | `claude --worktree` (of `-w <name>`), daarna `/work`. |
| **Claude-desktopapp** | Start een sessie met de optie **worktree**, daarna `/work`. |
| **Codex, Cursor, andere** | Gebruik de eigen optie van de tool voor worktrees of parallelle agents als die er is, daarna `/work`. Zo niet, typ dan `/work` in de hoofdmap: die maakt een worktree aan met `haam.py worktree new` en vertelt je welke map je in een nieuw venster moet openen. |

Lokale bestanden die niet in Git staan (zoals `.env`), worden naar elke nieuwe worktree gekopieerd vanuit de lijst in `.worktreeinclude`. Ruim afgeronde worktrees op met `python3 tools/haam/haam.py worktree clean` (plan), daarna `--apply`.

## Veilige instellingen per tool

De harde vangrails zitten in GitHub en git, dus ze beschermen je **wat de tool ook doet**: geen pushes naar `main`, verplichte checks, het UAT-label, goedkeuring van deploys, de secret-hook bij commits (`make hooks`) en de secret-scan in CI. De instellingen van een tool zijn een tweede laag die fouten eerder tegenhoudt. Aanbevolen:

| Tool | Aanbevolen instellingen |
|---|---|
| **Claude Code** | Al geconfigureerd in `.claude/settings.json`: vraagt het vóór pushes/PR's, blokkeert merges/deploys/het lezen van `.env`, secret-scan-hook vóór commits. Laat het zo. |
| **Cursor** | Auto-run van de agent: gebruik een allow-list (make-targets, git status/diff/log, `gh pr view/checks`) en vereis bevestiging voor `git push`, `gh pr create/edit/merge` en alles met `deploy`. Zet `.env*` in de ignore van Cursor, zodat de agent het niet kan lezen. |
| **Codex** | Sandbox *workspace-write* en approval policy *on-request* (vraagt het vóór netwerkacties en pushes). Vermijd modi met "full access" in deze repo. |
| **Grok Build** | Gebruik de permissieregels (op reponiveau toegestaan) om goedkeuring te vereisen voor `git push`, `gh pr merge` en deploycommando's; weiger het lezen van `.env*`. Het ondersteunt `PreToolUse`-hooks: je kunt `bash scripts/scan-secrets.sh` aanroepen vóór `git commit`, zoals de hook van Claude doet. Vermijd `--always-approve` buiten CI. |
| **Gemini CLI / Copilot** | Laat bevestigingen voor shellcommando's aan staan; keur pushes of merges nooit automatisch goed. |

Geef nooit een agent-tool je productiegegevens of een GitHub-token met adminrechten.

## Controle bij de eerste run, voor elke tool

Vraag de agent, in de repo:
1. *"Wat zijn de harde regels in deze repository?"* Hij moet de regels uit `AGENTS.md` §3 noemen. Zo niet, zeg dan dat hij eerst `AGENTS.md` moet lezen, en controleer in de instellingen van de tool de naam van het instructiebestand.
2. *"Welke skills heb je voor dit project?"* Hij moet idea, bug, assess, spec, next, work, build, uat… noemen. Zo niet, zie de tabel hierboven.
3. *"Toon de Ready-issues in het Linear-team APP."* Dit controleert de koppeling met Linear.

## Vastleggen welke tool het werk deed
Het claimcommentaar op het issue en het veld **Gebouwd met (Built with)** van de PR leggen de tool en het model vast. Na een paar weken kun je de bevindingen uit reviews en de mislukte UAT's per tool vergelijken.

## Review door een ander model
De reviewer-agents in CI gebruiken Claude. Als code met een andere tool geschreven is (Codex, Grok, Cursor met een ander model), wordt de review ook door een ander model gedaan, en dat is een nuttige extra controle.
