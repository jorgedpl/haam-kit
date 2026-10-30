# HAAM : Human-Agent Agile Methodology

[English](README.md) · [Español](README.es.md) · **Français** · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Nederlands](README.nl.md) · [Português](README.pt.md)

**Les humains décident. Les agents exécutent. Tout vit dans Git et dans votre outil de suivi.**

HAAM est une méthodologie et un kit ouverts pour développer des logiciels avec des agents de code IA, de l'idée à la production, sans perdre le contrôle. Il donne à chaque agent les mêmes règles, les mêmes commandes et les mêmes portes, quel que soit l'outil dans lequel il tourne : **Claude Code, Cursor, Codex, Grok Build, Gemini CLI ou GitHub Copilot**. Le travail est suivi sur un tableau **GitHub Projects** (gratuit) ou dans **Linear**, au choix. Plusieurs personnes, chacune avec son propre agent et son propre compte, peuvent travailler en parallèle sur le même produit.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## Ce que vous obtenez

- **Un cycle de vie avec cinq portes humaines** : décider de l'idée, approuver la spec, vérifications automatiques avec revue IA indépendante, test d'acceptation par une personne, approbation de la mise en production. On peut déroger à chaque porte en cas d'urgence, et chaque dérogation est enregistrée et suivie.
- **Trois flux de travail** dans lesquels les agents puisent : les bugs, les fonctionnalités prêtes et les idées à évaluer. L'outil de suivi (GitHub Projects ou Linear) contient le backlog, les priorités et les statuts.
- **20 skills partagés** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), au format ouvert Agent Skills.
- **Vos paramètres, vos compromis :** `/haam-settings` permet au product owner de choisir quand la CI et les revues IA tournent (à chaque PR, en local, seulement pour les zones protégées, ou jamais), ce qu'il teste lui-même, comment le travail est regroupé (par issue, par epic ou dans une seule PR de release), si les déploiements attendent une approbation, et les limites, chaque option avec son compromis et les chiffres du projet.
- **Tester en un mot, avant que quoi que ce soit ne coûte des minutes de CI** : tapez `/test`, essayez la modification de l'agent sur votre ordinateur, répondez `pass` (c'est seulement à ce moment que la pull request est ouverte et vérifiée, une seule fois, sur exactement ce que vous avez testé) puis `ship` (l'agent fusionne, déploie et clôt), ou dites simplement ce qui ne va pas (cela repart directement aux agents et vous revient une fois corrigé). `/test all` traite tout ce qui attend en une seule session, et `ship --all` le déploie avec une seule approbation.
- **Une voie sans UAT** pour les modifications que vous ne pouvez pas vraiment tester (configuration, mises à jour de dépendances, refactorisations invisibles) : marquez une fois l'issue `uat:skip`, et sa PR est fusionnée toute seule quand la CI et les deux revues IA passent.
- **Des epics avec un agent qui pose les bonnes questions** : `/triage group` transforme un tas d'issues éparses en epics (une par fonctionnalité) ; `/epic` lit chacune d'elles, rédige un brief court, vous pose quelques questions ciblées, puis range les issues : doublons, manques, découpages, ordre.
- **De la place pour que les agents construisent vite de gros morceaux, avec un garde-fou :**
  - `/spike` construit un prototype fonctionnel jetable que vous essayez avant de décider ;
  - le mode de construction par epic permet à un seul agent de construire toute une fonctionnalité, tranche par tranche, avec des points d'étape, un seul test et une seule release ;
  - toute modification fusionnée passe toutes les portes, et les prototypes ne sont jamais fusionnés.
- **Un guide des décisions** ([DECISIONS.md](template/i18n/fr/docs/setup/DECISIONS.md)) : chaque choix qu'une équipe fait en adoptant HAAM, avec une recommandation pour chacun. Il couvre les comptes GitHub et le plan dont vous avez besoin, GitHub Projects ou Linear, les paramètres, comment dimensionner les limites selon votre temps de test, et ce qu'il faut protéger. `/haam-setup` vous guide.
- **Un guide pour le product manager** ([PRODUCT-MANAGER.md](template/i18n/fr/docs/process/PRODUCT-MANAGER.md)) : rythme quotidien et hebdomadaire, comment trier, règles de priorité avec une matrice impact × portée pour les bugs, tailles saines des files d'attente, le tout avec un agent (`/triage`) ou directement dans GitHub Projects ou Linear.
- **Des agents en parallèle sans collisions** : ouvrez une nouvelle fenêtre de conversation, tapez `/work bugs`, et l'agent reçoit sa propre copie du projet (un worktree git), prend le bug en tête de liste et le mène jusqu'à votre test. Lancez-en autant que vous voulez, sur un ou plusieurs ordinateurs.
- **Une revue de code où personne ne corrige sa propre copie** : une analyse des secrets avant chaque commit et dans la CI, un audit des dépendances, et deux relecteurs IA indépendants (spec/qualité et sécurité) qui n'ont jamais vu le code s'écrire. Des humains relisent les zones protégées et peuvent trancher contre eux.
- **Des portes imposées par GitHub**, pas par la confiance : règles de branche, vérifications requises, une porte par label UAT et des approbations de déploiement, pour qu'elles tiennent quel que soit l'agent ou la personne qui pousse.
- **Une documentation en sept langues :** anglais, espagnol, français, allemand, italien, néerlandais et portugais. Choisissez-en une à l'installation (`install --language es`) et les agents rédigent aussi dans cette langue les specs, les issues, les plans UAT et les messages ; les commandes, les labels et le code restent en anglais.
- **Un outil de configuration** (`haam.py`, Python 3, sans dépendances) qui installe le kit dans un dépôt existant sans rien écraser, configure GitHub et l'outil de suivi (GitHub Projects ou Linear), donne aux agents un même jeu de commandes pour le tableau, intègre les développeurs, vérifie la configuration et met les projets à niveau vers les nouvelles versions du kit.

## Démarrage rapide

### Adopter HAAM dans votre projet (admin du projet, environ une demi-journée)

1. Récupérez une version publiée du kit :
   ```bash
   git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (ou téléchargez le zip depuis les [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Ouvrez votre agent de code **dans le dossier racine de votre projet** et dites :
   > Lisez `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` et suivez-le pour mettre en place HAAM dans ce dépôt. Le kit se trouve dans `~/haam-kit/template`.

L'agent installe le kit sur une branche, vous pose quelques questions, remplit les connaissances du projet à partir de votre code et vous guide dans la configuration de GitHub et de votre outil de suivi. Il montre chaque modification avant de la faire. Tout ce qui implique un mot de passe ou une clé d'API, c'est vous qui le faites, dans votre propre terminal, jamais via la conversation avec l'agent.

Vous préférez le faire à la main ? Suivez [le guide d'adoption](template/i18n/fr/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Rejoindre un projet qui utilise déjà HAAM (développeur, environ une heure)

Clonez le projet, ouvrez votre agent dedans et lancez `/haam-onboard` (Codex : `$haam-onboard` ; autres outils : *« suivez `.agents/skills/haam-onboard/SKILL.md` »*).

### Mettre un projet à niveau vers une nouvelle version du kit

Récupérez la nouvelle version du kit, puis lancez `/haam-update` dans votre projet, ou :
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Les fichiers que vous n'avez jamais modifiés sont mis à jour ; ceux que vous avez personnalisés sont conservés et, quand les deux côtés ont changé, la nouvelle version est mise de côté pour que votre agent fasse la fusion. Rien n'est supprimé.

## L'outil de configuration

| Commande | Qui | Quoi |
|---|---|---|
| `install --target DIR` | admin | Copie le kit dans un dépôt. N'écrase jamais rien ; fusionne les fichiers de paramètres des agents ; met les conflits de côté dans `.haam/incoming/` ; enregistre la version dans `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Met un projet à niveau vers cette version du kit, en gardant les personnalisations |
| `config` | admin | Nom du produit, clé d'équipe Linear, dépôt, approbateurs → `haam.config.json` ; les applique à tous les fichiers HAAM |
| `agents [--apply]` | admin | Branche les skills et Linear pour Claude Code, Cursor, Codex, Grok, Gemini, Copilot |
| `github [--apply]` | admin | Labels, ruleset de branche avec vérifications requises, approbation de production, fonctions de sécurité |
| `github-project [--apply]` | admin | Tableau GitHub Projects : 12 statuts, champ Priority, labels, lien vers le dépôt |
| `linear [--apply]` | admin, dans son propre terminal | Équipe Linear, triage, 12 statuts, 14 labels |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agents | Travailler sur le tableau GitHub Projects depuis n'importe quel outil d'agent |
| `exclusive "<who>" -- <command>` | agents | Lancer une exécution de tests lourde (qui utilise une ressource partagée par toute la machine) quand aucune autre ne tourne sur cette machine |
| `capacity` | agents | Retenir le nouveau travail quand trop de PR sont ouvertes ou attendent votre test (limites dans `haam.config.json`) |
| `ci-usage [--days 7]` | admin | Où sont passées les minutes GitHub Actions, par workflow, job, déclencheur et jour |
| `metrics [--days 30] [--save]` | owner | Comment le travail circule : temps jusqu'à Done, temps dans chaque file (décision, spec, construction, votre test, livraison), reprises, défauts trouvés en UAT contre ceux trouvés après, reverts. `--save` garde les chiffres dans `docs/metrics/` |
| `settings [--explain] [--set key=value] [--apply]` | product owner/admin | Vos choix : quand la CI et les revues IA tournent, ce que vous testez, le regroupement, la livraison, les limites (`/haam-settings` vous guide) |
| `local-ci ISSUE` | product owner | Avec `ci: local` : lance `make check` ici sur le commit de la PR et publie le résultat (ship le fait pour vous) |
| `review ISSUE` | agents | Les deux revues IA dans de nouvelles sessions locales, publiées comme statuts de la PR (quand les revues sont locales) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Mettre une modification sur cette machine pour la tester ; après `pass` + `ship` : fusionner, approuver le déploiement (un seul pour plusieurs), attendre, clore |
| `worktree status\|new\|prep\|list\|clean` | agents, tout le monde | Un worktree par conversation d'agent ; copie les fichiers locaux listés dans `.worktreeinclude` ; range ceux qui sont terminés |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Inviter un développeur (droit d'écriture GitHub, pas admin ; accès au tableau ou à l'équipe Linear) |
| `dev [--apply] [--run-checks]` | développeur | Vérification de la machine, hook de commit, `.env` à partir de l'exemple, vérifications du projet |
| `doctor [--role admin] [--check-updates]` | tout le monde | Ce qui est fait, ce qui manque et qui doit le faire |
| `version [--check]` | tout le monde | Versions de l'outil, du projet et de la dernière release du kit |

Chaque commande montre d'abord un plan et ne change quelque chose qu'avec `--apply`. Ajoutez `--json` pour une sortie lisible par une machine.

## Faire tourner plusieurs agents à la fois

Chaque conversation d'agent a son propre dossier, si bien que les conversations n'écrasent jamais le travail des autres :

1. Ouvrez une nouvelle fenêtre de conversation (Claude Code dans VS Code : Cmd/Ctrl+Shift+Esc).
2. Tapez `/work bugs` (ou `/work features`, `/work specs`, `/work ideas`, ou simplement `/work` ; Codex : `$work`).
3. L'agent passe dans son propre worktree git, copie les fichiers locaux comme `.env`, réserve l'élément en tête du tableau, le construit et le teste, ouvre la PR et vous remet un plan de test.

Répétez pour autant d'agents que vous voulez, sur n'importe quel ordinateur où le projet est cloné. La réservation sur le tableau empêche deux agents de prendre la même issue, que ce soit pour la construire, l'évaluer ou écrire sa spec. Votre propre conversation reste dans le dossier principal pour les idées, les décisions, les tests et les releases.

## Choisir un outil de suivi

| | GitHub Projects | Linear |
|---|---|---|
| Coût | Gratuit sur tous les plans GitHub | Plan gratuit avec limites ; payant par utilisateur |
| Où | À côté de votre code, une seule connexion | Application séparée |
| Utilisation par les agents | `haam.py issue …` (n'importe quel agent) | Le serveur MCP de Linear |
| Idéal pour | Personnes seules et petites équipes, tout garder dans GitHub | Backlogs plus chargés, plusieurs équipes, planification plus riche |

Le cycle de vie, les portes et les skills sont les mêmes dans les deux cas, et vous pouvez changer plus tard. Voir [TRACKER.md](template/i18n/fr/docs/process/TRACKER.md).

## Compatibilité des agents

| | Règles | Skills | Appeler un skill | Linear (si utilisé) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | à vérifier au premier lancement | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` via `.gemini/settings.json` | par fichier | par fichier | par utilisateur |
| GitHub Copilot | `AGENTS.md` | par fichier | par fichier | par utilisateur |

Sur GitHub Projects, tous les agents utilisent les mêmes commandes `haam.py issue`, il n'y a donc rien à connecter outil par outil. Détails et paramètres sûrs recommandés pour chaque outil : [AGENTS-SETUP.md](template/i18n/fr/docs/setup/AGENTS-SETUP.md).

## Prérequis

- Un dépôt GitHub. Les dépôts publics ont tout avec le plan gratuit. Sur les dépôts **privés**, les règles de branche demandent GitHub Pro ou Team, et un approbateur obligatoire pour les déploiements en production demande GitHub Enterprise Cloud (sans lui, votre `ship` vaut décision de mise en production). [DECISIONS.md](template/i18n/fr/docs/setup/DECISIONS.md) donne les détails.
- Un outil de suivi : un tableau GitHub Projects (gratuit, sur n'importe quel plan GitHub) ou un espace de travail Linear (n'importe quel plan)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Un secret Claude pour les agents relecteurs de la CI : un token de plan Claude (`claude setup-token`) ou une clé d'API Anthropic (facturée à l'usage ; fixez une limite de dépenses)
- N'importe quel agent de code pris en charge

## Organisation du dépôt

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  i18n/          The same docs in other languages
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Gestion des versions

HAAM suit le [versionnage sémantique](https://semver.org) :
- **Patch** (1.0.x) : corrections et formulations ; `update` s'applique sans accroc.
- **Mineure** (1.x.0) : nouveaux skills, vérifications ou docs ; rétrocompatible.
- **Majeure** (x.0.0) : changements qui demandent une étape de migration (par exemple des statuts Linear ou des vérifications requises renommés). Le [CHANGELOG](CHANGELOG.md) liste les étapes.

Installez toujours à partir d'un tag ou d'une release, pas à partir de `main`.

## Contribuer

Les idées, les rapports de bug et les pull requests sont les bienvenus. Voir [CONTRIBUTING.md](CONTRIBUTING.md). Problèmes de sécurité : voir [SECURITY.md](SECURITY.md).

## Licence

[MIT](LICENSE) © 2026 Jorge del Prado
