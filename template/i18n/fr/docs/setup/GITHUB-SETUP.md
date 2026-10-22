# Configuration de GitHub (une seule fois, ~30 minutes, admin du dépôt)

Cela transforme les portes G3–G5, de simples conventions, en règles que GitHub impose.

> **Automatisé :** les labels (§1), les règles de branche (§2), l'environnement de production (§4) et les fonctions de sécurité (§3b–c) sont pris en charge par `python3 tools/haam/haam.py github --apply` (d'abord le plan, sans `--apply`). Cette page en est l'équivalent manuel, plus les étapes que GitHub ne propose que dans le navigateur. Le secret du relecteur est toujours ajouté par vous : `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (token obtenu par `claude setup-token`, votre plan Claude) ou `gh secret set ANTHROPIC_API_KEY -R owner/repo` (clé d'API, facturée à chaque revue). L'un des deux suffit à faire tourner les deux revues.

## 1. Les labels
Créez ces labels du dépôt (Issues → Labels), ou lancez :
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Protection de la branche `main`
Settings → **Rules → Rulesets** → New branch ruleset (ou la protection de branche classique), cible `main` :

- ✅ Restreindre les suppressions ; bloquer les force push
- ✅ Exiger une pull request avant la fusion
  - Approbations requises : **1** dès qu'il y a une deuxième personne ; **0** tant que vous êtes seul (le label UAT vaut approbation)
  - ✅ Annuler les approbations périmées quand de nouveaux commits sont poussés
- ✅ Exiger que les vérifications d'état passent (laissez « require branches to be up to date » désactivé : sinon la CI se relance sur chaque PR ouverte après chaque fusion)
  - Vérifications requises : **`ci`**, **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** et **`release-gate`** (elles apparaissent dans la liste une fois que les workflows ont tourné au moins une fois sur une PR)
- ✅ Exiger un historique linéaire (facultatif, garde l'historique propre)
- **Liste de contournement :** admins du dépôt uniquement, **pour les pull requests uniquement** (jamais « always » : les agents travaillent sous la connexion d'un humain, souvent un admin, et pourraient sinon pousser directement sur `main`). C'est le contournement d'urgence de niveau 2 décrit dans `docs/process/GATES.md`.

**Auto-merge** (Settings → General → Pull Requests → *Allow auto-merge* ; `haam.py github --apply` l'active) : utilisé uniquement par la voie sans UAT, pour les PR dont vous avez marqué les issues `uat:skip`. La porte l'active pour une telle PR avec le secret `HAAM_PROJECT_TOKEN` (`docs/process/TRACKER.md`), et GitHub ne fusionne qu'une fois toutes les vérifications requises passées. Si vous exigez des approbations, la voie sans UAT en attend une aussi.

## 3. Revue de code et sécurité

### 3a. Un secret Claude pour les agents relecteurs
Les relecteurs indépendants (`.github/workflows/review.yml`) font tourner Claude dans GitHub Actions. Un seul secret du dépôt fait tourner les deux revues (Settings → **Secrets and variables → Actions** → New repository secret). Choisissez l'un des deux :
- **`CLAUDE_CODE_OAUTH_TOKEN` :** lancez `claude setup-token` et utilisez le token qu'il affiche. Les revues sont alors décomptées de ce plan Claude.
- **`ANTHROPIC_API_KEY` :** une clé d'API dédiée à ce dépôt, créée sur console.anthropic.com, avec une limite de dépenses mensuelle. Elle est facturée à chaque revue, indépendamment de l'abonnement Claude de quiconque. Avec elle, la revue de sécurité utilise l'action de revue de sécurité d'Anthropic.

Les PR en brouillon et les PR de documentation seule n'appellent pas Claude. Les instructions de revue se trouvent dans `.github/review/REVIEWER.md` et `SECURITY-REVIEWER.md`, et sont toujours lues depuis `main`. Ajustez-les à mesure que vous apprenez.

### 3b. Analyse des secrets et protection des push
Settings → **Security** (Code security / Advanced Security, selon votre plan) :
- ✅ **Secret scanning**, ✅ **Push protection** : GitHub refuse les push qui contiennent des formats de secrets connus.
- Gratuit pour les dépôts publics. Pour les dépôts privés, cela peut demander l'option de sécurité payante de GitHub ; si vous ne l'avez pas, la vérification `secrets` propre au kit (gitleaks) et les hooks locaux vous couvrent quand même.

### 3c. Alertes sur les dépendances
Settings → **Security** : ✅ Dependabot alerts, ✅ Dependabot security updates. Décommentez ensuite votre écosystème dans `.github/dependabot.yml`. Les PR de Dependabot passent par les mêmes portes.

### 3d. Pull requests venant de forks
Settings → **Actions → General** → *Fork pull request workflows* : exigez une approbation pour tous les collaborateurs externes. (Les PR venant de forks n'ont pas accès aux secrets du dépôt, les revues IA ne peuvent donc pas tourner dessus ; un humain relit et passe outre si nécessaire.)

## 4. Environnement de production (porte G5)
Settings → **Environments** → New environment **`production`** :
- **Required reviewers :** le product owner (+ une personne suppléante si vous en avez une)
- ✅ Prevent self-review : laissez **désactivé** tant que vous êtes le seul approbateur, activez-le plus tard
- **Deployment branches and tags :** branches sélectionnées → `main` uniquement
- **Environment secrets :** les identifiants de déploiement en production vont ici et nulle part ailleurs
- **Environment variables :** `PRODUCTION_URL` (utilisée par le smoke test)

Désormais, chaque fusion dans `main` lance `deploy.yml`, qui se met en pause à *deploy-production* jusqu'à ce qu'un approbateur clique sur **Review deployments → Approve**. GitHub prévient les approbateurs par e-mail ou par notification.

Les relecteurs obligatoires fonctionnent sur les dépôts publics avec tous les plans, mais sur les dépôts privés seulement avec GitHub Enterprise Cloud. Sans eux, les déploiements démarrent à la fusion, et votre `ship` vaut décision de mise en production : réglez `deploy_approval: automatic` avec `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (facultatif mais recommandé dès qu'il y a deux personnes)
`.github/CODEOWNERS` :
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Activez ensuite « Require review from Code Owners » dans le ruleset.

## 6. Remplir le contrat de commandes
Modifiez le `Makefile` (y compris `audit`) et les étapes de configuration de l'environnement d'exécution dans `.github/workflows/ci.yml`, `security.yml` et `deploy.yml` (cherchez `TODO(setup)`). Ouvrez une PR. La vérification `ci` doit passer au vert sur cette PR avant que vous n'activiez les vérifications requises.

## 7. Facultatif : l'application GitHub de Claude
Si vous voulez mentionner un agent sur une PR pour une correction rapide (par exemple l'application GitHub de Claude via `/install-github-app` dans Claude Code, ou l'intégration GitHub de votre autre outil), installez-la. Une telle application est soumise aux mêmes protections de branche et aux mêmes vérifications, elle ne peut donc pas contourner les portes.

## 8. Limiter les minutes Actions

Les dépôts privés ont un quota mensuel de minutes Actions ; des agents qui ouvrent beaucoup de PR l'épuisent vite. Ce que le kit fait déjà : par défaut (test d'abord), les agents poussent des branches sans ouvrir de PR, et une PR ne s'ouvre qu'une fois que vous avez testé et validé la modification, si bien que les vérifications tournent une seule fois, sur du code testé (projets en vérifications d'abord : les PR en brouillon ne lancent rien, et les agents marquent une PR comme prête une seule fois, quand elle est complète) ; les PR de documentation seule sautent les vérifications ; `main` est vérifiée chaque nuit au lieu d'après chaque fusion ; les labels, les commentaires et les nouvelles issues ne démarrent pas de runners ; les agents mettent le nouveau travail en attente à partir de 10 PR ouvertes ou de 10 modifications qui attendent votre test (`max_open_prs`, `max_in_uat`).

Découvrez où passent les minutes : `python3 tools/haam/haam.py ci-usage` (7 derniers jours, par workflow, job, déclencheur et jour).

Deux des paramètres (`/haam-settings`, ou `python3 tools/haam/haam.py settings --set … --apply --human` ; ils deviennent des variables du dépôt que les workflows lisent) sont décrits ci-dessous. Les autres (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) font économiser davantage : voir `settings --explain`.

| Option | Ce qui change | Compromis |
|---|---|---|
| `--review local` | Les deux revues IA tournent sur votre ordinateur dans de nouvelles sessions Claude (`haam.py review`), avec votre plan Claude au lieu des minutes Actions. Les PR avec le label `human-review` sont toujours relues sur GitHub | Le résultat n'est plus infalsifiable : c'est l'agent qui construit qui lance la revue (sessions neuves, en lecture seule, instructions venant de `main`), et tout ce qui utilise votre connexion pourrait publier un résultat positif. Lancez `haam.py review` depuis votre propre conversation pour plus de séparation |
| `--runner self-hosted` | Tous les jobs sauf le déploiement tournent sur votre propre machine (enregistrée dans Settings → Actions → Runners) au lieu de celles de GitHub | La machine doit être allumée, avec git, make, Python 3, curl, gitleaks et les outils de votre projet ; dépôts privés uniquement. Vérifiez les tarifs actuels de GitHub pour les runners auto-hébergés |

À vérifier aussi : les jobs sur des runners macOS comptent 10 minutes pour chaque minute d'exécution (Windows : 2). Ne lancez les builds mobiles que lorsque le code mobile a changé (`make check` reçoit les fichiers modifiés dans `$CI_CHANGED_FILES`), ou la nuit.

## 9. Vérifier que tout fonctionne
1. Ouvrez une toute petite PR de test (par exemple la correction d'une faute de frappe dans le code). `ci`, `secrets` et `dependencies` tournent ; l'agent relecteur publie un commentaire et `ai-review` / `security-review` rendent leur résultat ; `release-gate` affiche **failure: waiting for UAT**.
   - **Test de secret :** sur une branche jetable, committez dans un fichier de code une fausse clé de type AWS, comme `AKIA` suivi de 16 lettres majuscules/chiffres. Le hook local doit bloquer le commit ; si vous le contournez avec `--no-verify`, la vérification `secrets` doit échouer. Supprimez la branche ensuite.
2. Ajoutez le label `uat-passed` → `release-gate` passe au vert → la fusion est autorisée.
3. Après la fusion, Actions → Deploy affiche **Waiting for review** sur `deploy-production`.
4. Ouvrez une PR de documentation seule → `release-gate` passe automatiquement.
