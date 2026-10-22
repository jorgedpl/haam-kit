# Agenten-Tools: Einrichtung pro Tool

HAAM funktioniert mit jedem Coding-Agenten. Jedes Tool liest **dieselben Regeln** (`AGENTS.md`) und **dieselben Skills** (`.agents/skills/`) und arbeitet auf **demselben Tracker**: einem GitHub-Projects-Board (über `python3 tools/haam/haam.py issue …`, das jeder Agent ausführen kann) oder Linear (über seinen MCP-Server, `https://mcp.linear.app/mcp`). Nur die Anbindung unterscheidet sich.

Führe `python3 tools/haam/haam.py agents` aus, um zu sehen, was in diesem Repo angebunden ist, und `python3 tools/haam/haam.py dev`, um deine Maschine zu prüfen.

## Wie jedes Tool HAAM aufnimmt

| | Regeln | Skills | Skill aufrufen | Linear-MCP (nur Linear-Projekte) | Skills nur für Menschen |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importiert `AGENTS.md` | `.claude/skills` (Link auf `.agents/skills`) | `/build APP-1` | `.mcp.json` (im Repo) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (im Repo) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | pro Nutzer: `codex mcp add` | `agents/openai.yaml` in jedem Skill |
| **Grok Build** | beim ersten Start prüfen (siehe unten) | `.grok/skills` (Link auf `.agents/skills`) | `/build APP-1` | liest `.mcp.json` | laut Text des Skills |
| **Gemini CLI** | `AGENTS.md` über `.gemini/settings.json` | `SKILL.md` per Name folgen | „folge .agents/skills/build“ | pro Nutzer | laut Text des Skills |
| **GitHub Copilot** | `AGENTS.md` | `SKILL.md` per Name folgen | „folge .agents/skills/build“ | pro Nutzer | laut Text des Skills |

Lädt ein Tool keine Skills, sag ihm: *„Öffne `.agents/skills/<name>/SKILL.md` und folge der Anleitung.“* Die Skills sind einfaches Markdown.

## Mit dem Tracker verbinden (einmal pro Person)

**GitHub Projects:** Du musst in deinem Agenten nichts installieren. Führe einmal `gh auth refresh -s project` aus und teste mit `python3 tools/haam/haam.py issue list`. Der Rest dieses Abschnitts gilt für **Linear**-Projekte.

Linear meldet dich mit deinem eigenen Konto an (OAuth). Agenten handeln als du.

- **Claude Code:** `claude` im Repo öffnen → den Server `linear` genehmigen → `/mcp` → **linear** → anmelden.
- **Cursor:** Settings → MCP → `linear` erscheint aus `.cursor/mcp.json` → aktivieren → anmelden.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp`, dann der Anmeldeaufforderung folgen.
- **Grok Build:** Es liest `.mcp.json`; falls nicht, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Melde dich an, wenn du dazu aufgefordert wirst.
- **Gemini CLI / Copilot / andere:** Füge in den MCP-Einstellungen des Tools einen Remote-MCP-Server namens `linear` mit der URL `https://mcp.linear.app/mcp` hinzu.

**Test:** Bitte deinen Agenten *„Liste die Ready-Issues im Linear-Team APP auf.“*

## Mehrere Agenten gleichzeitig laufen lassen

Jeder Agenten-Chat, der Dateien ändert, braucht seinen eigenen Ordner (einen Git-Worktree), sonst überschreiben sich die Chats gegenseitig die Arbeit. Starte jeden Agenten-Chat mit `/work` (Codex: `$work`): Es prüft, wo es ist, und richtet bei Bedarf einen Worktree ein. Dein eigener Chat bleibt im Hauptordner.

| Tool | Neuer Agenten-Chat |
|---|---|
| **Claude Code (VS Code)** | Neuer Chat-Tab: Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux) oder Command Palette → „Claude Code: Open in New Tab“. Tippe `/work`; Claude wechselt selbst in einen Worktree. |
| **Claude Code (Terminal)** | `claude --worktree` (oder `-w <name>`), dann `/work`. |
| **Claude-Desktop-App** | Starte eine Sitzung mit der Option **worktree**, dann `/work`. |
| **Codex, Cursor, andere** | Nutze die eigene Worktree- oder Parallel-Agenten-Option des Tools, falls es eine hat, dann `/work`. Falls nicht, tippe `/work` im Hauptordner: Es legt mit `haam.py worktree new` einen Worktree an und sagt dir, welchen Ordner du in einem neuen Fenster öffnen sollst. |

Lokale Dateien, die nicht in Git liegen (wie `.env`), werden laut der Liste in `.worktreeinclude` in jeden neuen Worktree kopiert. Räume fertige Worktrees mit `python3 tools/haam/haam.py worktree clean` (Plan) auf, dann mit `--apply`.

## Sichere Einstellungen pro Tool

Die harten Schutzmechanismen liegen in GitHub und Git, sie schützen dich also, **egal was das Tool tut**: keine Pushes auf `main`, erforderliche Checks, UAT-Label, Deploy-Freigabe, der Secret-Hook beim Commit (`make hooks`) und der Secret-Scan in der CI. Die Einstellungen des Tools sind eine zweite Schicht, die Fehler früher stoppt. Empfohlen:

| Tool | Empfohlene Einstellungen |
|---|---|
| **Claude Code** | Schon in `.claude/settings.json` konfiguriert: fragt vor Pushes/PRs nach, blockiert Merges, Deploys und das Lesen von `.env`, Secret-Scan-Hook vor Commits. Lass das so. |
| **Cursor** | Agent auto-run: Nutze eine Allow-List (Make-Targets, git status/diff/log, `gh pr view/checks`) und verlange eine Bestätigung für `git push`, `gh pr create/edit/merge` und alles mit `deploy`. Füge `.env*` zur Ignore-Liste von Cursor hinzu, damit der Agent es nicht lesen kann. |
| **Codex** | Sandbox *workspace-write* und Approval Policy *on-request* (fragt vor Netzwerkaktionen und Pushes nach). Vermeide in diesem Repo Modi mit „full access“. |
| **Grok Build** | Nutze seine Berechtigungsregeln (auf Repo-Ebene erlaubt), um für `git push`, `gh pr merge` und Deploy-Befehle eine Freigabe zu verlangen; verbiete das Lesen von `.env*`. Es unterstützt `PreToolUse`-Hooks: Du kannst vor `git commit` `bash scripts/scan-secrets.sh` aufrufen, so wie es der Claude-Hook tut. Vermeide `--always-approve` außerhalb der CI. |
| **Gemini CLI / Copilot** | Lass Bestätigungen für Shell-Befehle eingeschaltet; genehmige Pushes oder Merges nie automatisch. |

Gib keinem Agenten-Tool deine Zugangsdaten für die Produktion oder einen GitHub-Token mit Admin-Rechten.

## Prüfung beim ersten Start, für jedes Tool

Frag den Agenten, im Repo:
1. *„Was sind die harten Regeln in diesem Repository?“* Er sollte die Regeln aus `AGENTS.md` §3 auflisten. Falls nicht, sag ihm, er soll zuerst `AGENTS.md` lesen, und prüfe in den Einstellungen des Tools den Namen der Anweisungsdatei.
2. *„Welche Skills hast du für dieses Projekt?“* Er sollte idea, bug, assess, spec, next, work, build, uat… auflisten. Falls nicht, siehe die Tabelle oben.
3. *„Liste die Ready-Issues im Linear-Team APP auf.“* Das prüft die Linear-Verbindung.

## Festhalten, welches Tool die Arbeit gemacht hat
Der Claim-Kommentar im Issue und das Feld **Built with** im PR halten Tool und Modell fest. Nach ein paar Wochen kannst du Review-Befunde und fehlgeschlagene UATs nach Tool vergleichen.

## Modellübergreifendes Review
Die Reviewer-Agenten in der CI nutzen Claude. Wird Code mit einem anderen Tool geschrieben (Codex, Grok, Cursor mit einem anderen Modell), ist das Review auch modellübergreifend, was eine nützliche zusätzliche Prüfung ist.
