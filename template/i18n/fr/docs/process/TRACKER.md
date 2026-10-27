# L'outil de suivi : Linear ou GitHub Projects

HAAM fonctionne de la même façon avec l'un ou l'autre outil de suivi. `haam.config.json` → `"tracker"` indique celui que ce projet utilise :

- **`github`** : des issues dans ce dépôt GitHub, sur un tableau GitHub Projects. Gratuit sur tous les plans GitHub. Les agents utilisent `python3 tools/haam/haam.py issue …` (voir ci-dessous), qui fonctionne depuis n'importe quel outil d'agent.
- **`linear`** : des issues dans une équipe Linear. Les agents utilisent la connexion Linear (MCP).

Les skills disent « dans l'outil de suivi » ; cette page explique comment faire chaque opération dans chaque outil. **Agents : vérifiez `tracker` dans `haam.config.json` une fois par session, puis utilisez la colonne correspondante.**

## Notions

| Notion | GitHub Projects | Linear |
|---|---|---|
| Identifiant d'issue (à écrire ainsi) | `#123` | `APP-123` |
| Nom de branche | `123-short-title` | `app-123-short-title` (le nom de branche de Linear) |
| Message de commit | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Titre de PR | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Lien PR → issue | **`Refs #123`** dans la description de la PR (pas `Closes` : l'issue est close au moment de `/release`, après le déploiement) | Identifiant de l'issue dans le titre de la PR |
| Fichiers de l'issue | `docs/specs/GH-123-slug.md` (de même pour les évaluations et l'UAT) | `docs/specs/APP-123-slug.md` |
| 12 statuts | Champ **Status** du tableau | Statuts du workflow de l'équipe |
| Priorité | Champ **Priority** du tableau (Urgent/High/Medium/Low) | Priorité intégrée |
| Flux, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Labels d'issue | Labels d'issue |
| Epic (regroupe les issues d'une fonctionnalité) | Issue avec le label `epic` ; ses issues sont des **sub-issues** GitHub | Issue avec le label `epic` ; ses issues sont des **sub-issues** (parent défini) |
| Qui travaille dessus | Statut In Progress (construction) ou label `claimed` (évaluation, rédaction de spec, construction d'un prototype), plus le commentaire de réservation. L'assignation seule ne permet pas de distinguer deux conversations de la même personne | Pareil |
| Changements de statut à l'ouverture/la fusion d'une PR | Workflow `tracker-sync.yml` : uniquement les issues en cours de livraison (pas les epics, ni les PR de documentation seule ou les spikes) | L'intégration GitHub de Linear |

## Opérations

Les commandes de la colonne GitHub se lancent depuis la racine du dépôt. Ajoutez `--json` pour une sortie lisible par une machine.

| Opération | GitHub Projects | Linear (via MCP) |
|---|---|---|
| **Trouver du travail** (files d'attente de `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (ajoutez `--label agent-ready` pour les fonctionnalités, `--label stream:bug` pour les bugs) | Lister les issues de l'équipe par statut, label, assignation |
| **Lire une issue** | `haam.py issue view 123` | Récupérer l'issue |
| **Créer une idée** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (arrive en Triage) | Créer l'issue, statut Triage, label `stream:idea` |
| **Signaler un bug** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Créer l'issue, statut Triage, label `stream:bug` |
| **Créer une epic** | `haam.py issue create --epic --stream idea --title "…"` | Créer une issue avec le label `epic` |
| **Mettre une issue dans une epic** | `haam.py issue link 14 --parent 9` | Définir l'epic comme parent de l'issue |
| **Créer une issue dans une epic** (par exemple des tranches de spec, des manques) | `haam.py issue create --stream feature --parent 9 --title "…"` | Créer une sous-issue de l'epic |
| **Les champs propres au tableau** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` les liste avec leurs options. Renseignez-les avec `--field NAME=VALUE` sur `issue create` ou `issue edit` (répétable ; une valeur vide en efface un ; `Sprint=@current` est l'itération en cours aujourd'hui), et filtrez avec `issue list --field Area=Billing`. Un nom ou une valeur erronés sont refusés avant tout changement | Les champs propres à l'équipe, via la connexion Linear |
| **Sortir une issue d'une epic** | `haam.py issue unlink 14` | Retirer le parent de l'issue |
| **Réécrire une issue** (titre, description) | `haam.py issue edit 14 --title "…" --body-file new.md` | Mettre à jour l'issue |
| **Les issues d'une epic** | `haam.py issue children 9` (avec l'avancement) | Lister les sous-issues de l'epic |
| **Issues hors de toute epic** | `haam.py issue list --open-only --no-parent --no-label epic` | Lister les issues sans parent |
| **Réserver** (avant de construire, d'évaluer ou de rédiger une spec) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (construction : refuse si l'issue est déjà réservée ou pas en Ready ; `--force` pour les bugs corrigés directement depuis Triage, seulement si l'humain l'a demandé). Évaluation : ajoutez `--for assess` ; rédaction de spec : `--for spec`. La commande affiche un identifiant de réservation : gardez-le | Récupérer à nouveau l'issue ; si elle est In Progress, a le label `claimed` ou est assignée à quelqu'un d'autre, arrêtez-vous ; sinon, assignez-la-vous, passez-la en In Progress (construction) ou ajoutez le label `claimed` (évaluation, spec), commentez avec un identifiant de réservation, relisez les commentaires (AGENTS.md §6) |
| **Construire un prototype** (`/spike`) | `haam.py issue claim 123 --for spike` (idées de Triage à Decision, fonctionnalités en Backlog), puis une fois poussé : `issue label 123 --add spike-ready` et `issue release 123 --claim <id> --status Decision` (une fonctionnalité en Backlog : sans `--status`) | Réserver comme ci-dessus (label `claimed`, un commentaire de réservation qui dit « pour construire un prototype »), label `spike-ready`, libérer |
| **Code de production dans une modification** | `haam.py production` (les fichiers modifiés par une branche qui tournent pour les utilisateurs) | Pareil |
| **Libérer une réservation** (évaluation ou spec poussée ; ou la conversation s'arrête) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` à la place de l'identifiant, seulement dans `/triage stale` ou `/test`) | Retirer l'assignation, retirer `claimed`, fixer le statut, commenter `🔓 Claim released` |
| **Changer de statut** | `haam.py issue status 123 "UAT"` | Mettre à jour le statut de l'issue |
| **Statut réservé aux humains** (Done, Parked, Canceled, Decision→Backlog) | Pareil, plus `--human`, **uniquement** dans `/triage`, `/epic`, `/decide`, `/test`, `/release` ou `/override` tapés par un humain | Même règle |
| **Priorité** | `haam.py issue priority 123 High` | Mettre à jour la priorité |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` demande aussi `--human`, après que l'humain a approuvé la spec) | Mettre à jour les labels |
| **Commenter** | `haam.py issue comment 123 --body "…"` ou `--body-file` | Créer un commentaire |
| **Rejeter ou marquer comme doublon** (dans `/triage`, `/epic` ou `/decide`) | `haam.py issue status 123 Canceled --human` (clôt aussi l'issue comme non planifiée) ; indiquez en commentaire la raison ou l'identifiant de l'original | Statut Canceled, commentaire |
| **Tester une modification** (humain, dans `/test`) | `haam.py checkout-pr 123`, puis `haam.py checkout-pr --back` | Pareil (le code est dans GitHub dans les deux cas) |
| **Ouvrir la PR après une validation** (test d'abord, l'humain a dit `pass`) | `haam.py publish 123 --human` : pousse le commit testé, ouvre la PR avec le label `uat-passed`, passe l'issue en In Review | `haam.py publish APP-123 --human` (`--label human-review` si l'issue l'a), puis passer l'issue en In Review et commenter, comme indiqué par la commande |
| **Consigner un test en échec** (l'humain a dit que ça a échoué) | `haam.py test-failed 123 --human`, puis label `uat-failed`, statut Ready, sans assignation | `haam.py test-failed APP-123 --human`, puis la même chose dans Linear |
| **Livrer après une validation** (l'humain a dit `ship`) | `haam.py ship 123 --human` : fusionner, approuver le déploiement, attendre, clore | `haam.py ship APP-123 --human`, puis passer en Done dans Linear |
| **Livrer tout ce qui est prêt, en un seul déploiement** | `haam.py ship --all --human` (ou `ship 12 13 14 --human`) : fusionne chacune, n'approuve que le déploiement le plus récent, les clôt toutes | `haam.py ship APP-12 APP-13 --human` (listez-les : `--all` ne sait pas lire Linear) |
| **Voir ou changer le fonctionnement de HAAM** (product owner) | `/haam-settings` ; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (uniquement au choix du product owner) | Pareil |
| **Lancer la CI ici** (paramètre `ci: local`) | `haam.py local-ci 123` (ship la lance pour vous) | Pareil |
| **Pas d'UAT pour cette issue** (décision du product owner) | `haam.py issue label 123 --add uat:skip --human` | Label `uat:skip` |
| **De la place pour du nouveau travail ?** (`/next` vérifie d'abord) | `haam.py capacity` (la file UAT et les PR prêtes face à `max_in_uat`, `max_open_prs`, ou au relèvement d'une fenêtre de lot ; les brouillons et les PR de documentation seule ne comptent pas) | Même commande, avec `--in-uat <count>` |
| **Le nouveau travail va-t-il entrer en collision avec ce qui attend ?** | `haam.py overlap --files src/auth/,src/api/users.py` (les branches en UAT qui modifient les mêmes fichiers) | Pareil, avec `--branch <name>` pour chaque branche en UAT |
| **PR groupée** (les bugs d'une epic) | Titre `#12 #13 #14: …`, une ligne `Refs #n` par issue ; `ship` les clôt toutes | Titre `APP-12 APP-13: …` |
| **Clore après la release** | `haam.py issue close 123 --human` (passe en Done et clôt ; `/release` uniquement) | Statut Done |

## Règles valables pour les deux

- Chaque travail a une issue dans l'outil de suivi ; rien n'est suivi ailleurs.
- Si l'outil de suivi est injoignable, arrêtez-vous et prévenez l'humain.
- Le protocole de réservation est ce qui empêche deux conversations d'agent (ou deux machines) de construire, d'évaluer ou de spécifier la même chose. Ne le sautez jamais.
- Les changements réservés aux humains n'ont lieu que dans les skills réservés aux humains, et l'outil demande `--human` sur GitHub en guise de rappel. Les agents agissent sous la propre connexion du product owner, si bien que GitHub ne peut pas savoir qui a posé un label du product owner (`uat:skip`, `mode:prototype`, `mode:epic-build`) : c'est une règle, vérifiée par l'outil sur GitHub Projects et par rien du tout sur Linear. Un agent qui l'enfreindrait avec un simple `gh` pourrait, avec `uat:skip`, faire sauter votre test à une modification hors des zones protégées ; la CI et les deux revues IA tournent quand même, et les déploiements vous attendent toujours là où votre plan le permet.

## Configuration de GitHub Projects (admin, une fois)

1. `gh auth refresh -s project` (permet à votre connexion GitHub d'utiliser Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plan), puis `--apply` : crée le tableau au nom du produit, le lie au dépôt, définit les 12 statuts et le champ Priority, crée les labels.
4. **Token d'automatisation** (pour `tracker-sync.yml`, et l'auto-merge de la voie sans UAT) : créez un token classique sur github.com/settings/tokens avec les scopes `project` et `repo` (`public_repo` suffit pour un dépôt public), puis `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Sans lui, tout fonctionne, mais les cartes ne bougent pas toutes seules quand des PR s'ouvrent ou sont fusionnées, et la voie sans UAT ne peut pas activer l'auto-merge (la porte utilise ce token, parce qu'une fusion faite avec le token propre au workflow ne déclencherait pas le déploiement). Sur les projets Linear, la voie sans UAT ne fait jamais d'auto-merge, le token n'est donc pas nécessaire pour elle.
5. **Dans le navigateur**, sur le tableau : créez les vues enregistrées que la configuration liste (Board grouped by Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics), et activez le workflow intégré **Auto-add to project** du tableau pour ce dépôt (tableau → Workflows). Il met sur le tableau, gratuitement, les issues créées sur le site de GitHub ; `haam.py issue create` ajoute lui-même les siennes. **Désactivez** le workflow intégré **Item closed → Status: Done** : il écrase `Canceled` après qu'`issue status … Canceled` ferme l'issue, et `ship` met déjà Done lui-même.
6. Chaque développeur lance `gh auth refresh -s project` une fois ; `/haam-onboard` le vérifie.

## Changer d'outil de suivi plus tard

Définissez `"tracker"` avec `haam.py config --tracker …`, lancez la configuration du nouvel outil de suivi, puis demandez à votre agent de recopier les issues ouvertes (il sait lire un outil et écrire dans l'autre). Gardez l'ancien outil de suivi en lecture seule pour l'historique.
