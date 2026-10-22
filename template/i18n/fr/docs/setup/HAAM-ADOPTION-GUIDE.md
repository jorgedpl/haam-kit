# Human-Agent Agile Methodology (HAAM)
## Guide d'adoption pour l'admin du projet

HAAM est une façon de développer des logiciels où **les humains décident et les agents exécutent**. Chaque travail va de l'idée à la production en passant par les mêmes étapes, avec des portes humaines aux moments qui comptent. Tout vit dans **Git** (connaissances et code) et dans l'**outil de suivi** (travail et statuts) : un tableau **GitHub Projects** (gratuit) ou **Linear**. Les membres de l'équipe peuvent utiliser des agents de code différents (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) avec leurs propres comptes et quand même travailler en parallèle.

Ce guide applique HAAM à un dépôt existant en **six phases, environ une demi-journée au total**. Vous pouvez vous arrêter après n'importe quelle phase et avoir déjà quelque chose d'utile.

---

## Récupérer le kit

Le kit est le dossier `template/` de https://github.com/jorgedpl/haam-kit. Utilisez toujours une version publiée :
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
ou téléchargez le zip depuis la page Releases. Dans la suite, `<path-to-kit>` désigne ce dossier `template/`.

## La voie rapide : laissez votre agent le faire

Placez le kit quelque part en dehors de votre projet, ouvrez votre agent de code **dans le dossier racine de votre projet** et dites :

> Lisez `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` et suivez-le pour mettre en place HAAM dans ce dépôt. Le kit se trouve dans `<path-to-kit>`.

L'agent pilote l'outil de configuration (`tools/haam/haam.py`) à travers chacune des phases ci-dessous. Il vous pose quelques questions, montre chaque modification avant de la faire et vous confie les quelques étapes qui demandent vos mots de passe ou vos clés, à lancer dans votre propre terminal. Servez-vous du reste de ce guide pour comprendre ce qu'il fait, ou pour le faire à la main.

### Qui fait quoi pendant la configuration

| Marqué | Signification |
|---|---|
| `[agent]` | Votre agent de code s'en charge (ou vous, si vous le faites à la main) |
| `[YOU, in your terminal]` | Vous lancez la commande vous-même : elle implique un secret (clé d'API, identifiants) qui ne doit jamais passer par la conversation d'un agent |
| `[YOU, in the browser]` | Un paramètre que GitHub ou Linear ne proposent que dans leur application web |

---

## Ce que vous obtenez

```
START-HERE.md                 Kit entry point (not copied into your repo)
AGENTS.md                     Rules every agent reads, whatever the tool
CLAUDE.md                     Pointer to AGENTS.md for Claude Code
haam.config.json              Project settings for the setup tool (created by `config`; no secrets)
haam.lock.json                Installed kit version and file fingerprints (used by `update`)
docs/changes/                 One release note per shipped change (added by /uat)
Makefile                      Command contract: setup, hooks, dev, test, check, audit, secrets, smoke, deploy
tools/haam/haam.py            Setup tool: install, config, agents, github, github-project, linear, issue, worktree, invite, dev, doctor
scripts/scan-secrets.sh       Secret scan (gitleaks) shared by all commit hooks
.githooks/pre-commit          Blocks commits containing secrets (any human, any agent using git)
.agents/skills/               One skill per stage, shared by all agent tools
.worktreeinclude              Local files (like .env) to copy into each agent's worktree
.claude/                      Claude Code: settings (guard-rails), hooks, skills link
.cursor/mcp.json              Cursor: Linear connection (Linear projects)
.grok/skills                  Grok Build: skills link
.gemini/settings.json         Gemini CLI: read AGENTS.md
.mcp.json                     Linear connection (Claude Code, Grok; Linear projects)
.github/
  pull_request_template.md    Includes "Built with" (agent tool and model)
  workflows/ci.yml            Gate G3: tests on every PR
  workflows/security.yml      Gate G3: secret scan of every commit + dependency audit
  workflows/review.yml        Gate G3: independent AI reviewers (spec/quality + security)
  workflows/tracker-sync.yml    Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/              Idea and bug forms (GitHub Projects)
  workflows/gates.yml         Gate G4: blocks merge until UAT passed or overridden
  workflows/deploy.yml        Gate G5: production deploy waits for human approval
  review/REVIEWER.md          Instructions for the reviewer agent
  dependabot.yml              Dependency update PRs
docs/
  process/LIFECYCLE.md        The methodology: streams, stages, statuses, roles
  process/GATES.md            Gate checklists, code review, overrides
  process/TRACKER.md          How each tracker operation works on GitHub Projects and on Linear
  product/PRODUCT.md          Your product context (you confirm it)
  product/ARCHITECTURE.md     Map of your codebase (the agent drafts it)
  setup/HAAM-ADOPTION-GUIDE.md  This guide
  setup/DECISIONS.md          Every choice to make (accounts and plan, tracker, settings, limits, what to protect), with recommendations
  setup/AGENTS-SETUP.md       Per-tool setup: Claude Code, Cursor, Codex, Grok, Gemini, Copilot
  setup/LINEAR-SETUP.md       Linear configuration in detail
  setup/GITHUB-SETUP.md       GitHub configuration in detail
  ONBOARDING.md               Guide for new developers
  templates/                  idea, bug, assessment, feature-spec, uat-plan, adr
  decisions/0001-adopt-haam.md
  assessments/ specs/ uat/    Filled in automatically as work flows
```

### Le cycle de vie en une image

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### Les commandes

Écrites `/name` ici (Claude Code, Cursor, Grok). Dans Codex, utilisez `$name`. Dans tout autre outil : *« suivez `.agents/skills/<name>/SKILL.md` »*.

| Commande | Étape | Qui |
|---|---|---|
| `/idea <text>` | Capturer une idée | N'importe qui |
| `/bug <text>` | Signaler un problème | N'importe qui |
| `/assess APP-12` | Évaluer la valeur, l'effort, le risque, la faisabilité | Agent |
| `/triage` | Trier la boîte de réception, regrouper les issues en epics (`group`), reclasser (`backlog`), relancer le travail bloqué (`stale`) | Humain uniquement |
| `/epic APP-9` | Mettre en forme une epic : brief, questions pour vous, rangement de ses issues | Humain uniquement |
| `/decide APP-12 approve` | Porte G1 | Humain uniquement |
| `/spec APP-12` | Rédiger une spec prête à construire | Agent |
| `/work bugs` | Lancer un agent dans une nouvelle fenêtre de conversation : son propre worktree, puis `/next` | N'importe qui |
| `/next` | Prendre l'élément suivant parmi les bugs, les fonctionnalités et les idées | Agent |
| `/build APP-12` | Implémenter avec des tests unitaires, ouvrir une PR | Agent |
| `/uat APP-12` | Rédiger votre plan de test local | Agent |
| `/test` | Tester une modification, puis `pass` → `ship`, ou dire ce qui ne va pas (G4 et G5) | Humain uniquement |
| `/uat-result APP-12 pass` | Enregistrer un résultat de test seul (G4) | Humain uniquement |
| `/override APP-12 "reason"` | Sauter l'UAT en cas d'urgence | Humain uniquement |
| `/release APP-12` | Clore après le déploiement | Humain uniquement |
| `/haam-setup` | Adopter HAAM dans un dépôt | Admin du projet |
| `/haam-onboard` | Préparer un nouveau développeur | Nouveau développeur |
| `/haam-update` | Passer à une nouvelle version du kit | Admin du projet |

### Comment fonctionne la revue de code

Aucun agent ne relit jamais son propre travail, et les secrets sont repérés par un scanner plutôt que par le jugement. Chaque modification passe par six couches :

| Couche | Quand | Ce qu'elle vérifie | Qui s'en charge |
|---|---|---|---|
| 1. Garde locale contre les secrets | Avant chaque commit | Clés, tokens, mots de passe dans les modifications ; le commit est bloqué s'il y en a | gitleaks via le hook git (tout le monde), plus les hooks de l'outil d'agent quand c'est possible |
| 2. Autovérification | Avant d'ouvrir une PR | Les tests passent ; autorevue de sécurité de son propre diff | L'agent qui l'a construite |
| 3. CI automatique | À chaque mise à jour d'une PR | Tests, lint, types (`ci`) ; secrets dans chaque commit (`secrets`) ; bibliothèques vulnérables (`dependencies`) | GitHub Actions |
| 4. Revue IA indépendante | À chaque mise à jour d'une PR (sauf brouillons et PR de documentation seule) | Conforme à la spec ? Tests honnêtes ? Bugs, dérive du périmètre, règles enfreintes (`ai-review`). Vulnérabilités de sécurité (`security-review`) | Un Claude distinct dans GitHub Actions qui n'a jamais vu le code s'écrire (un autre modèle quand le code vient d'un autre outil) |
| 5. Revue de code humaine | PR qui touchent des zones protégées | Logique métier centrale, authentification, paiements, données personnelles, migrations, infrastructure, configuration des agents | Le product owner ou un développeur désigné |
| 6. Acceptation humaine | Chaque PR de code | Ça marche vraiment (UAT de la porte G4) | Le product owner |

- Le relecteur publie un seul commentaire avec **Blocking / Should fix / Nits**. Les points bloquants empêchent la fusion.
- L'agent qui construit corrige les points Blocking et pousse ; les revues se relancent automatiquement. S'il n'est pas d'accord, il répond dans la PR et demande à un humain. Après **deux** tours en échec, il s'arrête et passe la main.
- Les relecteurs IA peuvent bloquer mais jamais approuver ni fusionner. Seul un humain peut passer outre, avec le label de PR `ai-review-overruled`.
- Si un vrai secret arrive un jour sur GitHub : révoquez-le et remplacez-le immédiatement, puis faites réécrire l'historique de la branche par un admin. Le supprimer dans un nouveau commit ne suffit pas.

Règles complètes : `docs/process/GATES.md`. Instructions du relecteur que vous pouvez ajuster : `.github/review/REVIEWER.md`.

---

## Avant de commencer

Il vous faut :
- [ ] Un accès admin au dépôt GitHub. S'il est privé, les règles de branche demandent GitHub Pro ou Team, et un approbateur pour les déploiements en production demande Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Un outil de suivi : **GitHub Projects** (rien de plus ; gratuit sur tous les plans) ou un accès admin à un espace de travail **Linear**
- [ ] Un agent de code installé et connecté, avec votre propre compte
- [ ] Python 3, Git, Make, et la GitHub CLI connectée (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, ou depuis sa page de releases sur GitHub)
- [ ] Un secret Claude pour les agents relecteurs : un token de plan Claude (`claude setup-token`) ou une clé d'API Anthropic avec une limite de dépenses mensuelle (console.anthropic.com)
- [ ] Votre projet tourne en local aujourd'hui

Décidez maintenant :
1. **Outil de suivi :** GitHub Projects (gratuit, tout dans GitHub) ou Linear (plus agréable à utiliser, plan gratuit limité). Vous pourrez changer plus tard.
2. **Clé produit :** un code court, par exemple `ACM`, `SHOP`, `CRM` (la clé d'équipe Linear si vous utilisez Linear). Le kit utilise `APP` comme espace réservé jusqu'à ce que `config` le remplace partout.
3. **Product owner :** la seule personne qui approuve les idées, les specs, l'UAT et les déploiements (plus un approbateur suppléant facultatif).
4. **Les outils d'agent** que votre équipe va utiliser.

Vérifiez votre machine à tout moment avec : `python3 <kit>/tools/haam/haam.py dev`

---

## Phase 1 : installer le kit (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

La documentation est en anglais, sauf si vous ajoutez `--language es` (ou `fr`, `de`, `it`, `nl`, `pt`) aux deux commandes. Les agents rédigent alors aussi les specs, les issues, les plans UAT et les messages dans cette langue ; les commandes, les labels et le code restent en anglais. Vous pourrez la changer plus tard avec `haam.py config --language <code>`, puis le `update --target . --apply` du kit.

L'installateur **n'écrase jamais** vos fichiers :
- Les nouveaux fichiers sont ajoutés.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` et `.claude/settings.json` sont **fusionnés** automatiquement.
- `.gitignore` reçoit une seule fois un bloc HAAM ajouté à la fin.
- Tout autre fichier que vous avez déjà est laissé tel quel, et la version du kit est enregistrée dans `.haam/incoming/` pour que vous (ou l'agent) fassiez la fusion.

Comment fusionner les conflits habituels :

| Si votre dépôt contient déjà… | Faites ceci |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Déplacez les connaissances propres au projet (conventions, pièges, commandes) dans `docs/product/ARCHITECTURE.md` ou dans une section « Project specifics » à la fin d'`AGENTS.md`. Utilisez ensuite les `AGENTS.md` et `CLAUDE.md` du kit. Ne gardez les règles Cursor `.mdc` que pour les détails limités à certains globs |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` déplace vos skills dans `.agents/skills/` et crée le lien vers le dossier. Renommez d'abord ceux qui entrent en conflit avec les noms des skills HAAM |
| `Makefile` | Ajoutez les cibles du kit aux vôtres |
| `.github/workflows/` avec une CI | Gardez votre CI, mais assurez-vous qu'un job nommé **`ci`** lance toute votre suite de tests sur les PR. Ajoutez `gates.yml`, `security.yml`, `review.yml`. Comparez votre déploiement avec `deploy.yml` (phase 4) |
| `.github/pull_request_template.md` | Intégrez « Réalisé avec (Built with) », « Critères d'acceptation → tests » et « Liste de contrôle (G3) » |
| `.pre-commit-config.yaml` ou Husky | Gardez-le et appelez-y `scripts/scan-secrets.sh` au lieu d'utiliser `.githooks/` |
| `CHANGELOG.md`, `.github/dependabot.yml` | Gardez les vôtres (ajoutez l'écosystème `github-actions` à Dependabot s'il manque) |

Supprimez `.haam/incoming/` une fois terminé.

---

## Phase 2 : configurer et lui apprendre votre projet (45 min)

1. **Paramètres du projet** `[agent]` (avec vos réponses) :
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Cela écrit `haam.config.json` et remplace l'espace réservé `APP` et le nom du produit dans tous les fichiers HAAM.

2. **Outils d'agent** `[agent]` : `python3 tools/haam/haam.py agents --apply`. Cela relie les skills partagés pour Claude Code et Grok, vérifie les fichiers de Cursor/Codex/Gemini/Copilot et liste les éventuelles étapes à faire par chaque personne. Détails : `docs/setup/AGENTS-SETUP.md`.

3. **Contrat de commandes** `[agent]` : remplissez chaque `TODO(setup)` du `Makefile` (setup, dev, test, lint, typecheck, build, audit) et les étapes d'exécution dans les workflows, à partir des vraies commandes de votre projet. Ensuite, `make check` doit passer sur le code actuel. Si des tests échouent déjà sur `main`, corrigez-les ou marquez-les d'abord : HAAM repose sur le fait que vert veut dire vert. Si `make audit` signale d'anciennes vulnérabilités de niveau élevé ou critique, corrigez-les ou consignez-les comme bugs et relevez temporairement le seuil.

4. **Carte de l'architecture** `[agent]` : remplissez `docs/product/ARCHITECTURE.md` à partir du code (moins de 150 lignes) et proposez de vrais chemins pour les zones protégées dans `AGENTS.md` §4. Vous relisez.

5. **Contexte produit** `[agent drafts, you confirm]` : `docs/product/PRODUCT.md` : ce que c'est, les utilisateurs, les parcours qui ne doivent jamais casser, les non-négociables, les priorités actuelles. C'est ce que chaque agent lit pour trancher quand il doit juger.

6. **Document d'onboarding** `[agent]` : remplissez les éléments `TODO(setup)` de `docs/ONBOARDING.md` (URL de clonage, environnement d'exécution, URL locale).

7. **Hygiène des secrets** `[agent]` : `make hooks`, puis analysez une fois l'historique : `gitleaks git --redact -v .` Tout ce qui est réel doit être **révoqué et remplacé** auprès du fournisseur : c'est déjà exposé à quiconque a accès au dépôt. C'est vous qui approuvez les empreintes de faux positifs ajoutées à `.gitleaksignore`.

8. **Conversations en parallèle** `[agent]` : listez dans `.worktreeinclude` les fichiers purement locaux dont l'application a besoin (comme `.env`), excluez `.claude/worktrees/` de tout outil qui parcourt tout le dossier (lanceur de tests, linter, watcher), et essayez un worktree neuf : `python3 tools/haam/haam.py worktree new setup-check`, puis `make setup && make check` dedans, puis `git worktree remove .claude/worktrees/setup-check`. À partir de là, chaque nouvelle conversation d'agent commence par `/work`.

9. **Vérification :** `python3 tools/haam/haam.py doctor` montre ce qu'il reste à faire.

---

## Phase 3 : ouvrir la PR d'adoption (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Cela fait exister les vérifications dans GitHub, pour qu'elles puissent être rendues obligatoires. Le premier commentaire de revue IA apparaîtra sur cette PR.

---

## Phase 4 : les portes GitHub (20 min)

1. **Planifier, puis appliquer** `[agent, with your OK]` :
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Cela crée les labels, un ruleset sur la branche par défaut (PR obligatoire, les six vérifications requises, pas de force push ; les admins ne peuvent contourner les règles qu'en fusionnant une PR, pour les urgences, jamais en poussant sur main ; « à jour avant la fusion » désactivé, pour économiser des exécutions de CI). Si le ruleset existe déjà, l'outil ajoute seulement ce qui manque et garde vos réglages (`--reset` le remplace). Il crée aussi l'environnement `production` avec vos approbateurs et la variable `PRODUCTION_URL`, et active l'analyse des secrets, la protection des push et Dependabot quand votre plan le permet.
2. **Clé du relecteur** `[YOU, in your terminal]` : un seul secret fait tourner les deux revues. Soit `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` avec le token obtenu par `claude setup-token` (utilise votre plan Claude), soit `gh secret set ANTHROPIC_API_KEY -R owner/repo` avec une clé d'API dédiée (facturée à chaque revue ; avec elle, la revue de sécurité utilise l'action de revue de sécurité d'Anthropic). Les deux commandes demandent la valeur sans l'afficher.
3. **PR venant de forks** `[YOU, in the browser]` : Settings → Actions → General → exiger une approbation pour les collaborateurs externes.
4. **Déploiements :**
   - *Vous déployez déjà depuis GitHub Actions ?* Ajoutez `environment: production` à votre job de déploiement : cela suffit à vous donner la porte G5. Supprimez le `deploy.yml` du kit ou gardez-le comme référence.
   - *Vous déployez autrement* (intégration Git d'une plateforme d'hébergement, à la main) ? Soit vous déplacez les déploiements dans `deploy.yml` (remplissez `make deploy`), soit vous gardez votre méthode et traitez G5 comme une étape manuelle : le product owner déploie après la fusion, puis lance `/release`. Désactivez le déploiement automatique à chaque push s'il contournait l'approbation.
5. **Dépôts privés :** les règles de branche demandent GitHub Pro ou Team, et un approbateur pour les déploiements en production demande Enterprise Cloud ; l'outil vous dit ce que votre plan permet. Sans approbateur, votre `ship` vaut décision de mise en production : réglez `deploy_approval: automatic` (`docs/setup/DECISIONS.md` §1).

Détails et équivalents manuels : `docs/setup/GITHUB-SETUP.md`.

---

## Phase 5 : l'outil de suivi (20 min)

### Option A : GitHub Projects (gratuit)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (permet à votre connexion GitHub d'utiliser Projects).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` token d'automatisation, pour que les cartes bougent quand des PR s'ouvrent et sont fusionnées : créez un token classique sur github.com/settings/tokens avec les scopes `project` et `repo` (`public_repo` suffit pour un dépôt public), puis `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` sur le tableau, créez les vues que l'outil liste : Board grouped by Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Test : `python3 tools/haam/haam.py issue list`.

Les agents utilisent `python3 tools/haam/haam.py issue …` pour toutes les opérations sur le tableau (`docs/process/TRACKER.md`), si bien que cela fonctionne de la même façon depuis Claude Code, Cursor, Codex, Grok ou n'importe quoi d'autre.

### Option B : Linear
1. **Statuts, labels, équipe** `[YOU, in your terminal]` (demande votre clé d'API personnelle Linear, qui ne passe jamais par un agent) :
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Cela crée l'équipe si nécessaire, active Triage, crée les 12 statuts (en renommant le statut par défaut « Todo » de Linear en « Ready ») et les 9 labels. Cela ne supprime jamais rien ; les statuts en trop sont listés pour que vous les archiviez.
2. **Paramètres disponibles seulement dans le navigateur** `[YOU, in the browser]` : connecter GitHub, automatisations des PR (PR brouillon → In Progress, PR prête pour la revue → In Review, fusionnée → Deploying), format de nom de branche `{issue-identifier}-{issue-title}`, vues enregistrées. Voir `docs/setup/LINEAR-SETUP.md`.
3. **Connectez votre agent** à Linear (`docs/setup/AGENTS-SETUP.md`) et testez : *« Listez les issues de l'équipe Linear ACM. »*

**Un backlog existant ?** Demandez à votre agent de le faire entrer dans l'outil de suivi (les issues GitHub peuvent simplement être ajoutées au tableau). Mettez tout en **Triage**, triez une fois (`stream:bug`, `stream:idea`, ou `stream:feature` + Backlog), et ne rédigez des specs que pour les cinq premiers.

---

## Phase 6 : fusion, boucle d'essai et équipe

### Fusionner la PR d'adoption
Quand les vérifications sont au vert, ajoutez vous-même `uat-passed` (la porte est active maintenant, donc même cette PR y passe) et fusionnez. Si les agents relecteurs pinaillent sur le kit lui-même, passez outre avec `ai-review-overruled`. Lancez `python3 tools/haam/haam.py doctor --role admin` pour une dernière vérification.

### Faire une boucle complète (45–60 min)
Choisissez quelque chose de petit et de réel. Faites-le passer une fois par chaque étape :

| Étape | Vous tapez | Ce qui doit se passer |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Nouvelle issue en Triage, label `stream:idea` (sur GitHub : `#1` ; sur Linear : `ACM-1`) |
| 2 | `/assess #1` | Évaluation commitée sur la branche de l'issue (sans PR) ; l'issue passe en Decision |
| 3 | `/decide #1 approve medium` | L'issue passe en Backlog, le label devient `stream:feature` |
| 4 | `/spec #1` | Spec avec critères d'acceptation, sur la même branche |
| 5 | Lisez la spec (lien dans l'issue), dites à l'agent « spec approved » | L'issue reçoit `agent-ready` et passe en Ready |
| 6 | `/build #1` | Réserve l'issue, crée la branche, code, écrit les tests, fait son autorevue, rédige le plan UAT et pousse la branche. Pas encore de PR (test d'abord, le mode par défaut) |
| 7 | `/uat #1` (`/build` le lance) | L'issue passe en UAT ; vous êtes prévenu |
| 8 | `/test #1` | L'agent met la modification sur votre machine, démarre l'application et vous donne une courte liste de contrôle |
| 9 | Essayez, répondez `pass` | L'agent ouvre la PR avec le label `uat-passed` ; `ci`, `secrets`, `dependencies` et les agents relecteurs tournent une fois ; `release-gate` passe au vert ; l'agent demande « On livre ? » |
| 10 | Répondez `ship` | L'agent fusionne, approuve pour vous le déploiement en production, attend et clôt l'issue : Done |
| 11 | (à essayer une fois) `/test` sur une modification, en décrivant plutôt un problème | Elle repart aux agents avec vos notes (`uat-failed`) et vous revient une fois corrigée |

(Sur Linear, les identifiants ressemblent à `ACM-1`.)

Essayez ensuite une fois les cas limites : demandez à l'agent de committer une fausse clé sur une branche jetable (`AKIA` + 16 lettres majuscules/chiffres) : le commit doit être bloqué. Puis faites échouer une UAT, et utilisez une dérogation. Ajustez les skills dans `.agents/skills/` ou le processus dans `docs/process/LIFECYCLE.md` là où quelque chose vous a semblé mal fonctionner.

**Essayez aussi un deuxième outil d'agent sur la boucle d'essai** (par exemple Cursor ou Codex pour l'étape 6). Cela confirme que les règles et les skills partagés fonctionnent au-delà de votre outil principal.

### Ajouter des développeurs
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply` : droit d'écriture GitHub (pas admin), accès au tableau GitHub Projects, ou une invitation Linear.
2. Envoyez-leur le lien du dépôt et les identifiants de test (gestionnaire de mots de passe ou lien à usage unique, jamais par conversation ni par e-mail).
3. Ils ouvrent leur propre agent dans le dépôt et lancent `/haam-onboard` (Codex : `$haam-onboard`).
4. Dès que vous êtes deux : l'outil active « 1 approbation requise » quand vous ajoutez des approbateurs suppléants (`config --backup-approvers`, puis `github --apply`), et vous pouvez ajouter `.github/CODEOWNERS` pour les zones protégées.

### Laisser les agents travailler en semi-autonomie

| Niveau | Comment | Quand |
|---|---|---|
| **1. Supervisé** | Vous tapez `/next` ou `/build`, vous approuvez chaque push et chaque PR | Les 2–3 premières semaines |
| **2. Par lots** | 2–3 fenêtres de conversation (n'importe quel mélange d'outils et d'ordinateurs), chacune lancée avec `/work`, qui lui donne son propre worktree ; vous relisez les PR par lots | Dès que les specs sont régulièrement bonnes |
| **3. Planifié** | Une tâche planifiée fait tourner un agent sans interface avec `/next` et s'arrête à l'UAT | Dès que vous faites confiance aux portes |

À chaque niveau, les agents s'arrêtent aux portes humaines.

### Coûts de fonctionnement
En dehors de GitHub, de Linear (si vous l'utilisez) et de l'abonnement d'agent de chaque personne, le seul coût à l'usage vient des agents relecteurs : deux appels à Claude par push relu sur une PR, facturés sur `ANTHROPIC_API_KEY` ou décomptés de votre plan Claude (`CLAUDE_CODE_OAUTH_TOKEN`). Gardez la limite de dépenses activée et les PR petites.

### Rester à jour
Les nouvelles versions du kit sont publiées sur https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` vous dit quand il y en a une. Lancez `/haam-update` (Codex : `$haam-update`) sur une branche : les fichiers que vous n'avez jamais modifiés sont mis à jour, vos personnalisations sont conservées et, là où les deux ont changé, l'agent les fusionne. Le CHANGELOG liste les éventuelles étapes de migration.

### Votre rythme de product owner
Tous les jours (10–15 min) : tester **UAT**, vider **Triage** (`/triage`). Toutes les semaines (30–45 min) : décider de tout ce qui est en **Decision**, reclasser le backlog (`/triage backlog`), relancer le travail bloqué (`/triage stale`), revoir **Parked**, clore les **dérogations**. Le guide complet, avec les règles de priorité et les listes de contrôle : `docs/process/PRODUCT-MANAGER.md`.

---

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| Vous ne savez pas ce qu'il reste à faire | – | `python3 tools/haam/haam.py doctor --role admin` |
| L'agent ne suit pas les règles | L'outil ne lit pas `AGENTS.md` | Vérification du premier lancement dans `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` dit que la connexion ne peut pas utiliser Projects | La connexion gh n'a pas le scope `project` | `gh auth refresh -s project` |
| Les cartes du tableau ne bougent pas quand des PR s'ouvrent ou sont fusionnées | `HAAM_PROJECT_TOKEN` manquant, ou la PR n'indique pas `Refs #123` | Ajoutez le secret (phase 5) ; vérifiez la description de la PR |
| L'agent ne voit pas Linear | MCP non connecté ou pas authentifié | Étapes par outil dans `docs/setup/AGENTS-SETUP.md` |
| Les skills apparaissent en double dans Cursor | Cursor lit à la fois `.agents/skills` et `.claude/skills` | Désactivez la compatibilité avec les skills Claude dans les paramètres de Cursor |
| `.claude/skills` ou `.grok/skills` manquent après le clonage (Windows) | Liens symboliques Git désactivés | `git config core.symlinks true` puis reclonez, ou `haam.py agents --apply` (copie à la place) |
| `haam.py github` dit que les rulesets/approbations ne sont pas disponibles | Dépôt privé sur un plan gratuit | Changez de plan, ou protégez à la main et appuyez-vous sur les vérifications |
| `haam.py linear` échoue à une étape | Changement d'API ou droits insuffisants | Terminez cette étape à la main avec `docs/setup/LINEAR-SETUP.md` |
| Deux conversations ont modifié les mêmes fichiers ou la même branche | Elles partageaient un dossier | Commencez chaque conversation d'agent par `/work` (son propre worktree) |
| Les tests ou le linter trouvent des fichiers en double sous `.claude/worktrees/` | L'outil parcourt tout le dossier | Excluez `.claude/worktrees/` dans la configuration de cet outil |
| Un worktree n'arrive pas à lancer l'application | Fichiers locaux manquants | Ajoutez-les à `.worktreeinclude`, puis `haam.py worktree prep` dans le worktree |
| `/build` refuse de démarrer | L'issue n'est pas en Ready, ou il manque `agent-ready` | `/spec` puis approuvez-la, ou passez vous-même l'issue en Ready |
| Les statuts Linear ne bougent pas lors des événements de PR | Intégration GitHub ou automatisations non configurées | Team settings → Workflow → PR automations ; le titre de la PR doit commencer par l'identifiant de l'issue |
| `release-gate` reste rouge après `uat-passed` | Le workflow ne s'est pas relancé | Retirez puis remettez le label |
| Une vérification requise manque dans la liste | Elle n'a pas encore tourné | Ouvrez d'abord une PR, n'importe laquelle |
| Commits bloqués : « gitleaks is not installed » | gitleaks absent sur cette machine | Installez-le, puis `make hooks` |
| Commit bloqué pour un secret qui n'en est pas un | Faux positif | Un humain ajoute l'empreinte à `.gitleaksignore` dans un commit relu |
| `ai-review` ou `security-review` en attente ou en erreur | Pas de secret pour le relecteur (`CLAUDE_CODE_OAUTH_TOKEN` ou `ANTHROPIC_API_KEY`), PR venant d'un fork, ou plus de tours disponibles | Ajoutez le secret ; relancez ; augmentez `--max-turns` ; ou `ai-review-overruled` |
| Relecteur trop strict | Instructions pas ajustées | Modifiez `.github/review/REVIEWER.md` |
| `dependencies` échoue sur chaque PR | Anciennes vulnérabilités | Corrigez-les, ou relevez temporairement le seuil et suivez-les comme des bugs |
| Specs trop vagues, les constructions tournent mal | G2 trop laxiste | Resserrez la Definition of Ready dans `docs/process/GATES.md` |

---

## Principes

1. **Les humains décident, les agents exécutent.**
2. **Ce qui n'est pas dans Git ou dans l'outil de suivi n'existe pas** pour la personne ou l'agent suivant.
3. **De petites tranches :** une issue, une branche, une PR, relisible en 15 minutes.
4. **Les portes coûtent peu à passer et cher à sauter.** Les dérogations sont autorisées, toujours enregistrées, toujours suivies.
5. **Vert veut dire vert.** N'affaiblissez jamais un test pour passer une porte.
6. **Personne ne corrige sa propre copie.** L'agent qui écrit le code ne le relit jamais ; les secrets sont repérés par des outils, pas par le jugement.
7. **N'importe quel agent, les mêmes règles.** Les outils sont interchangeables ; le processus et les portes ne le sont pas.
