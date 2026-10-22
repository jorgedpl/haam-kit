# Configuration de Linear (une seule fois, ~30 minutes, admin de l'espace de travail)

> **Uniquement si votre outil de suivi est Linear** (`"tracker": "linear"` dans `haam.config.json`). Vous utilisez GitHub Projects ? Lancez plutôt `python3 tools/haam/haam.py github-project` et consultez `docs/process/TRACKER.md`.

Cela configure Linear pour qu'il corresponde à `docs/process/LIFECYCLE.md`. Faites-le une fois ; chaque développeur et chaque agent utilise ensuite la même structure.

> **Automatisé :** les sections 1–4 sont prises en charge par `python3 tools/haam/haam.py linear --apply`, que vous lancez dans votre propre terminal (la commande demande votre clé d'API personnelle Linear de façon sécurisée et ne la stocke jamais). Cette page en est l'équivalent manuel, plus les sections 5–9, qui n'existent que dans l'application web de Linear.

## 1. L'équipe
- Créez (ou réutilisez) une équipe au nom de votre produit, avec un identifiant court (les exemples utilisent **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` remplace `APP` dans tous les fichiers HAAM.
- Invitez chaque personne qui contribue, avec son propre compte Linear. Les agents agissent au nom de l'humain qui les fait tourner : pas besoin de places séparées pour les agents.

## 2. Les statuts du workflow
Team settings → **Workflow**. Créez ces statuts, dans cet ordre, dans la catégorie indiquée :

| Statut | Catégorie | Remarques |
|---|---|---|
| Triage | Triage | Activez Triage pour l'équipe |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | À définir comme statut par défaut des nouvelles issues hors triage |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Supprimez ou renommez les statuts par défaut de Linear (`Todo`, `Duplicate`, etc.) pour qu'il ne reste que ceux-là. Les noms doivent correspondre exactement ; les skills y font référence par leur nom.

## 3. Les labels
Team settings → **Labels**. Créez ces labels (labels simples, pas besoin de groupe) :
- `stream:idea`
- `stream:feature`
- `stream:bug`

Et ces labels indépendants :

| Label | Signification | Qui le pose |
|---|---|---|
| `agent-ready` | A passé G2 ; les agents peuvent la construire | L'agent, seulement après qu'un humain a approuvé la spec |
| `human-review` | Touche une zone protégée ; revue de code humaine obligatoire | Agent ou humain |
| `human-only` | Les agents ne doivent pas la prendre | Humain |
| `override-followup` | Créée après une dérogation à une porte | `/override` |
| `epic` | Issue parente qui regroupe les sous-issues d'une fonctionnalité | `/triage group`, `/epic`, ou un humain |
| `uat-failed` | A échoué au test humain ; les agents la reprennent en priorité | `/test`, `/uat-result` |
| `uat:skip` | Le product owner a décidé : pas de test de sa part | `/triage`, ou « spec approved, no UAT » |
| `claimed` | Une conversation d'agent est en train de l'évaluer, de rédiger sa spec ou de construire un prototype | L'agent, pendant qu'il travaille |
| `mode:prototype` | Le product owner a décidé : construire d'abord un prototype jetable (`/spike`) | `/triage` |
| `mode:epic-build` | Le product owner a décidé : un agent principal construit toute cette epic | `/decide` |
| `spike-ready` | Un prototype est prêt à être essayé par le product owner | `/spike` |

Facultatif : des labels de domaine (`area:onboarding`, `area:billing`, `area:checkout`…) pour filtrer le tableau.

## 4. Les priorités
Utilisez la priorité intégrée de Linear (Urgent / High / Medium / Low / No priority). Aucun champ personnalisé n'est nécessaire.

## 5. Les modèles d'issue
Team settings → **Templates** → créez trois modèles d'issue, en collant le corps depuis :
- **Idea** : `docs/templates/idea.md` · label par défaut `stream:idea` · statut Triage
- **Bug** : `docs/templates/bug.md` · label par défaut `stream:bug` · statut Triage
- **Feature** : un corps court avec un lien vers la spec · label par défaut `stream:feature` · statut Backlog

Les agents les remplissent eux-mêmes via `/idea` et `/bug` ; les modèles sont destinés aux humains qui créent des issues dans l'application Linear.

## 6. L'intégration GitHub
Settings → **Integrations → GitHub** → connectez l'organisation/le dépôt.

Puis dans les paramètres de l'équipe → **Workflow → Pull request automations** (la formulation peut varier légèrement) :

| Événement GitHub | Passer l'issue en |
|---|---|
| Branche créée / PR brouillon ouverte | In Progress |
| PR prête pour la revue (les agents ouvrent des brouillons et les marquent prêts quand ils sont complets) | In Review |
| PR prête à être fusionnée | *(aucun changement, les agents la passent en UAT)* |
| PR fusionnée | Deploying |

**Format des noms de branche :** `{issue-identifier}-{issue-title}` (en minuscules), par exemple `app-123-bulk-invite-users`. Retirez le préfixe du nom d'utilisateur pour que les branches soient identiques quelle que soit la personne qui les crée.

Activez **« link PRs by issue ID in title »** pour que les titres de PR du type `APP-123: ...` soient liés automatiquement.

## 7. Les vues (filtres enregistrés)
Créez ces vues d'équipe pour que les humains voient ce qui a besoin d'eux :

| Vue | Filtre |
|---|---|
| **Triage** | La boîte de réception Triage intégrée à Linear (la boîte de réception quotidienne du product owner ; voir `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Statut parmi (Decision, UAT), plus les issues en Backlog avec un commentaire `📝 Spec ready for review` |
| **Agent queue** | Statut = Ready, label `agent-ready` ou `stream:bug`, sans assignation |
| **Ideas inbox** | Statut parmi (Triage, Discovery), label `stream:idea` |
| **Bugs** | Label `stream:bug`, ni Done ni Canceled, triées par priorité |
| **Epics** | Label `epic`, ni Done ni Canceled (afficher l'avancement des sous-issues) |
| **Overrides to close** | Label `override-followup`, pas Done |

## 8. Les notifications
Chaque humain : Settings → Notifications → vérifiez que vous êtes prévenu pour les **mentions** et les **issues qui vous sont assignées**. `/uat` mentionne le product owner quand quelque chose est prêt à être testé.

## 9. Connecter l'outil d'agent de chaque personne à Linear
Chaque personne se connecte une fois depuis son propre outil (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Les étapes pour chaque outil : `docs/setup/AGENTS-SETUP.md`.
Test : demandez à l'agent *« listez mes issues Linear ouvertes dans l'équipe APP »*.

Si vous utilisez aussi une application de conversation (Claude, ChatGPT…) avec un connecteur Linear, connectez-la aussi pour pouvoir capturer des idées depuis votre téléphone.
