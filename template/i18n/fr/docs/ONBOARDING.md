# Onboarding des développeurs

Bienvenue. Ce dépôt est construit par des humains et des agents de code qui travaillent ensemble selon la **Human-Agent Agile Methodology (HAAM)**. Vous pouvez utiliser l'outil d'agent que vous préférez : Claude Code, Cursor, Codex, Grok, Gemini ou Copilot. Ce guide vous amène de zéro à votre première issue en une heure environ.

## La voie rapide : laissez votre agent vous intégrer

1. Clonez le dépôt et ouvrez votre outil d'agent dans son dossier racine :
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Dites à votre agent :
   - Claude Code, Cursor ou Grok : `/haam-onboard`
   - Codex : `$haam-onboard`
   - Tout autre outil : *« Lisez `.agents/skills/haam-onboard/SKILL.md` et suivez-le. »*

Il vérifie votre machine, vos accès et la connexion à l'outil de suivi, met en place vos hooks locaux et votre `.env`, lance les vérifications du projet, explique comment nous travaillons et vous suggère une première issue. Les étapes qui demandent votre mot de passe ou vos clés, c'est vous qui les faites, dans votre propre terminal ou éditeur. Vous ne collez jamais de secrets dans la conversation.

Vous préférez le faire à la main ? Les sections ci-dessous couvrent le même terrain.

---

## 1. À lire d'abord (15 minutes)
1. `AGENTS.md` : les règles que suit chaque agent, quel que soit l'outil. Elles s'appliquent aussi à vous.
2. `docs/process/LIFECYCLE.md` : flux, statuts, portes, qui fait quoi.
3. `docs/process/GATES.md` : listes de contrôle, revue de code et dérogations.
4. `docs/product/PRODUCT.md` et `docs/product/ARCHITECTURE.md` : ce que nous construisons et comment c'est structuré.

## 2. Les comptes dont vous avez besoin
| Compte | Pourquoi | Ce qu'il faut demander |
|---|---|---|
| GitHub | Code, PR, CI | Un droit d'écriture sur le dépôt |
| Outil de suivi | Backlog et statuts | **GitHub Projects :** un accès au tableau (fourni avec l'invitation au dépôt). **Linear :** être membre de l'équipe **APP** |
| Votre outil d'agent | Agent de code | Votre **propre** compte (Claude, Cursor, OpenAI, xAI…). Ne partagez jamais de comptes |
| Services de test | Faire tourner le projet en local | Uniquement des identifiants de test, fournis par le product owner |

L'admin du projet vous invite avec une seule commande : `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. Vous **n'aurez pas** d'identifiants de production ; les déploiements passent par GitHub, avec approbation.

## 3. Installer les outils
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (obligatoire ; les commits sont bloqués sans lui) : macOS `brew install gitleaks` ; autres : https://github.com/gitleaks/gitleaks/releases
- L'environnement d'exécution du langage de ce dépôt : `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Votre outil d'agent

Vérifiez tout avec : `python3 tools/haam/haam.py dev`

## 4. Faire tourner le code
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Se connecter à l'outil de suivi
Regardez `"tracker"` dans `haam.config.json` :
- **GitHub Projects :** lancez une fois `gh auth refresh -s project`, puis testez : `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear :** suivez la section de votre outil dans `docs/setup/AGENTS-SETUP.md` (une seule connexion), puis demandez à votre agent : *« Listez les issues Ready de l'équipe Linear APP. »*

## 6. Vos paramètres personnels (non partagés)
Les notes et préférences personnelles vont dans des fichiers ignorés par git : `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, ou les paramètres utilisateur de votre outil. N'y mettez jamais de règles partagées. Si quelque chose doit s'appliquer à tout le monde, proposez une modification d'`AGENTS.md` via une PR.

## 7. Le travail au quotidien
Les commandes sont écrites `/name` ci-dessous ; dans Codex, utilisez `$name`.

| Vous voulez… | Faites ceci |
|---|---|
| Voir ce qui attend | Vue **Agent queue** de l'outil de suivi (à construire) ou **Waiting on me** |
| Lancer un agent dans une nouvelle fenêtre de conversation | `/work` (ou `/work bugs`) |
| Commencer à travailler dans cette conversation | `/next`, ou `/build APP-123` |
| Trier et prioriser (product owner) | `/triage`, `/triage group`, `/epic`, et `docs/process/PRODUCT-MANAGER.md` |
| Consigner une idée | `/idea …` |
| Signaler un bug | `/bug …` |
| Transformer une idée approuvée en spec | `/spec APP-123` |
| Tester une modification (product owner) | `/test`, puis `pass` → `ship`, ou dites ce qui ne va pas |
| Tester la modification de quelqu'un (développeur) | Suivez `docs/uat/APP-123-*.md`, puis prévenez le product owner |
| Vérifier votre configuration | `python3 tools/haam/haam.py doctor` |

### Faire tourner des agents en parallèle
Ouvrez une nouvelle fenêtre de conversation par agent et tapez `/work` (ou `/work bugs`, `/work features`, `/work specs`, `/work ideas` ; Codex : `$work`). L'agent reçoit sa propre copie du projet (un worktree git sous `.claude/worktrees/`), copie les fichiers locaux listés dans `.worktreeinclude` (comme `.env`), prend l'élément en tête de liste et le mène jusqu'à la passation. Gardez votre propre conversation dans le dossier principal pour les idées, les décisions et les tests.

- **Claude Code dans VS Code :** nouvel onglet de conversation avec Cmd+Shift+Esc (Mac) ou Ctrl+Shift+Esc (Windows/Linux). Dans un terminal : `claude --worktree`.
- **Autres outils :** si l'outil a sa propre option de worktree ou d'agents en parallèle, utilisez-la ; sinon, `/work` crée le worktree et vous dit quel dossier ouvrir dans une nouvelle fenêtre.
- **Un autre ordinateur :** même chose. La réservation dans l'outil de suivi empêche deux agents de prendre la même issue ; donnez le nom de la machine quand on vous le demande, pour que le commentaire de réservation indique où l'agent tourne.
- **Rangez** de temps en temps les worktrees terminés : `python3 tools/haam/haam.py worktree clean` (plan), puis `--apply`.
- **Tester la branche d'un agent :** le plan UAT utilise `git switch --detach origin/<branch>`, qui fonctionne même tant que le worktree de l'agent a encore la branche.

### Faire tourner des agents en semi-autonomie
- **Avec surveillance :** tapez `/next`, vérifiez son choix, laissez-le tourner. Votre outil devrait demander avant de pousser ou d'ouvrir des PR (voir les paramètres sûrs dans `docs/setup/AGENTS-SETUP.md`).
- **Sans surveillance :** une tâche planifiée ou un cron fait tourner votre agent sans interface avec le prompt `/next` (Codex : `$next`). Il ne prend que du travail qui a passé sa porte, et s'arrête à l'UAT pour un humain.
- Les agents s'arrêtent à chaque porte humaine, par conception. Votre travail est de garder la vue **Waiting on me** courte.

## 8. Comment votre travail est relu
Chaque PR est vérifiée par des tests, une analyse des secrets, un audit des dépendances et deux relecteurs IA indépendants (spec/qualité et sécurité) qui n'ont jamais vu le code s'écrire. Corrigez leurs points **Blocking** ; si vous pensez que l'un d'eux est faux, répondez dans la PR et demandez au product owner, qui peut passer outre avec le label `ai-review-overruled`. Les zones protégées ont aussi droit à une revue humaine. Détails : `docs/process/GATES.md` § Comment fonctionne la revue de code.

**Si vous committez un jour un vrai secret :** prévenez immédiatement le product owner. Il doit être révoqué et remplacé, même si vous le supprimez dans le commit suivant.

## 9. Des règles qu'il vaut la peine de répéter
- Pas de push sur `main`, pas de fusions, pas de déploiements par les agents.
- Pas de secrets ni de données personnelles réelles dans le code, les tests, les fixtures, l'outil de suivi ou la conversation. Les données personnelles sont protégées par la loi (par exemple le RGPD).
- Une issue → une branche → une PR, assez petite pour être relue en 15 minutes.
- Remplissez **Réalisé avec (Built with)** dans chaque PR (votre outil et votre modèle).
- Ce qui n'est pas dans Git ou dans l'outil de suivi n'existe pas pour la personne suivante.

## 10. Obtenir de l'aide
- Questions sur le processus : demandez à votre agent *« d'après LIFECYCLE.md, que doit-il se passer quand… »*
- Accès et identifiants : le product owner.
- Améliorer le processus : ouvrez une `/idea` avec le label `area:process`. Les modifications d'`AGENTS.md`, de `.agents/`, des dossiers de configuration des agents et de `.github/` demandent une revue du product owner.
