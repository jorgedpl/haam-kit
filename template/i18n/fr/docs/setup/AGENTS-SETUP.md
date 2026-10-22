# Outils d'agent : configuration outil par outil

HAAM fonctionne avec n'importe quel agent de code. Chaque outil lit les **mêmes règles** (`AGENTS.md`) et les **mêmes skills** (`.agents/skills/`), et travaille sur le **même outil de suivi** : un tableau GitHub Projects (via `python3 tools/haam/haam.py issue …`, que n'importe quel agent peut lancer) ou Linear (via son serveur MCP, `https://mcp.linear.app/mcp`). Seule la tuyauterie change.

Lancez `python3 tools/haam/haam.py agents` pour voir ce qui est branché dans ce dépôt, et `python3 tools/haam/haam.py dev` pour vérifier votre machine.

## Comment chaque outil prend en compte HAAM

| | Règles | Skills | Appeler un skill | MCP Linear (projets Linear uniquement) | Skills réservés aux humains |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importe `AGENTS.md` | `.claude/skills` (lien vers `.agents/skills`) | `/build APP-1` | `.mcp.json` (dans le dépôt) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (dans le dépôt) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | par utilisateur : `codex mcp add` | `agents/openai.yaml` dans chaque skill |
| **Grok Build** | à vérifier au premier lancement (voir ci-dessous) | `.grok/skills` (lien vers `.agents/skills`) | `/build APP-1` | lit `.mcp.json` | selon le texte du skill |
| **Gemini CLI** | `AGENTS.md` via `.gemini/settings.json` | suivre `SKILL.md` par son nom | « suivez .agents/skills/build » | par utilisateur | selon le texte du skill |
| **GitHub Copilot** | `AGENTS.md` | suivre `SKILL.md` par son nom | « suivez .agents/skills/build » | par utilisateur | selon le texte du skill |

Si un outil ne charge pas les skills, dites-lui : *« Ouvrez `.agents/skills/<name>/SKILL.md` et suivez-le. »* Les skills sont du simple Markdown.

## Se connecter à l'outil de suivi (une fois par personne)

**GitHub Projects :** rien à installer dans votre agent. Lancez une fois `gh auth refresh -s project`, et testez avec `python3 tools/haam/haam.py issue list`. Le reste de cette section concerne les projets **Linear**.

Linear vous connecte avec votre propre compte (OAuth). Les agents agissent en votre nom.

- **Claude Code :** ouvrez `claude` dans le dépôt → approuvez le serveur `linear` → `/mcp` → **linear** → connectez-vous.
- **Cursor :** Settings → MCP → `linear` apparaît grâce à `.cursor/mcp.json` → activez-le → connectez-vous.
- **Codex :** `codex mcp add linear --url https://mcp.linear.app/mcp`, puis suivez l'invite de connexion.
- **Grok Build :** il lit `.mcp.json` ; sinon, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Connectez-vous quand il vous le demande.
- **Gemini CLI / Copilot / autres :** ajoutez un serveur MCP distant nommé `linear` avec l'URL `https://mcp.linear.app/mcp` dans les paramètres MCP de l'outil.

**Test :** demandez à votre agent *« Listez les issues Ready de l'équipe Linear APP. »*

## Faire tourner plusieurs agents à la fois

Chaque conversation d'agent qui modifie des fichiers a besoin de son propre dossier (un worktree git), sinon les conversations écrasent le travail des autres. Commencez chaque conversation d'agent par `/work` (Codex : `$work`) : il vérifie où il se trouve et met en place un worktree si nécessaire. Votre propre conversation reste dans le dossier principal.

| Outil | Nouvelle conversation d'agent |
|---|---|
| **Claude Code (VS Code)** | Nouvel onglet de conversation : Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux), ou Command Palette → « Claude Code: Open in New Tab ». Tapez `/work` ; Claude se déplace tout seul dans un worktree. |
| **Claude Code (terminal)** | `claude --worktree` (ou `-w <name>`), puis `/work`. |
| **Application de bureau Claude** | Démarrez une session avec l'option **worktree**, puis `/work`. |
| **Codex, Cursor, autres** | Utilisez l'option de worktree ou d'agents en parallèle propre à l'outil s'il en a une, puis `/work`. Sinon, tapez `/work` dans le dossier principal : il crée un worktree avec `haam.py worktree new` et vous dit quel dossier ouvrir dans une nouvelle fenêtre. |

Les fichiers locaux qui ne sont pas dans Git (comme `.env`) sont copiés dans chaque nouveau worktree à partir de la liste de `.worktreeinclude`. Rangez les worktrees terminés avec `python3 tools/haam/haam.py worktree clean` (plan), puis `--apply`.

## Paramètres sûrs pour chaque outil

Les vrais garde-fous vivent dans GitHub et git, si bien qu'ils vous protègent **quoi que fasse l'outil** : pas de push sur `main`, vérifications requises, label UAT, approbation des déploiements, le hook de commit contre les secrets (`make hooks`) et l'analyse des secrets dans la CI. Les paramètres des outils sont une deuxième couche qui arrête les erreurs plus tôt. Recommandations :

| Outil | Paramètres recommandés |
|---|---|
| **Claude Code** | Déjà configuré dans `.claude/settings.json` : demande avant les push/PR, bloque les fusions, les déploiements et la lecture de `.env`, hook d'analyse des secrets avant les commits. Gardez-le. |
| **Cursor** | Exécution automatique de l'agent : utilisez une liste d'autorisations (cibles make, git status/diff/log, `gh pr view/checks`) et exigez une confirmation pour `git push`, `gh pr create/edit/merge`, et tout ce qui contient `deploy`. Ajoutez `.env*` aux fichiers ignorés par Cursor pour que l'agent ne puisse pas le lire. |
| **Codex** | Sandbox *workspace-write* et politique d'approbation *on-request* (demande avant les actions réseau et les push). Évitez les modes « full access » dans ce dépôt. |
| **Grok Build** | Utilisez ses règles de permissions (autorisées au niveau du dépôt) pour exiger une approbation pour `git push`, `gh pr merge` et les commandes de déploiement ; interdisez la lecture de `.env*`. Il prend en charge les hooks `PreToolUse` : vous pouvez appeler `bash scripts/scan-secrets.sh` avant `git commit`, comme le fait le hook de Claude. Évitez `--always-approve` en dehors de la CI. |
| **Gemini CLI / Copilot** | Gardez les confirmations activées pour les commandes shell ; n'approuvez jamais automatiquement les push ni les fusions. |

Ne donnez jamais à un outil d'agent vos identifiants de production ni un token GitHub avec des droits d'admin.

## Vérification au premier lancement, pour chaque outil

Demandez à l'agent, dans le dépôt :
1. *« Quelles sont les règles impératives de ce dépôt ? »* Il doit lister les règles de `AGENTS.md` §3. Sinon, dites-lui de lire d'abord `AGENTS.md`, et vérifiez dans les paramètres de l'outil le nom du fichier d'instructions.
2. *« Quels skills avez-vous pour ce projet ? »* Il doit lister idea, bug, assess, spec, next, work, build, uat… Sinon, voyez le tableau ci-dessus.
3. *« Listez les issues Ready de l'équipe Linear APP. »* Cela vérifie la connexion à Linear.

## Garder la trace de l'outil qui a fait le travail
Le commentaire de réservation dans l'issue et le champ **Réalisé avec (Built with)** de la PR enregistrent l'outil et le modèle. Au bout de quelques semaines, vous pouvez comparer les remarques des revues et les échecs d'UAT par outil.

## Revue croisée entre modèles
Les agents relecteurs de la CI utilisent Claude. Quand le code est écrit avec un autre outil (Codex, Grok, Cursor avec un autre modèle), la revue se fait aussi entre modèles différents, ce qui est un contrôle supplémentaire utile.
