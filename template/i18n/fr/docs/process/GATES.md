# Portes et dérogations

Cinq portes séparent une idée de la production. Chacune a un responsable clair, une liste de contrôle et, quand c'est possible, un point de contrôle automatique, pour que la règle ne dépende pas de la mémoire de quelqu'un.

| Porte | Entre | Responsable | Imposée par |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Humain (PO) | Statut dans l'outil de suivi : seuls des humains lancent `/decide` |
| **G2 Ready** | Backlog → Ready | Un humain approuve la spec | Label `agent-ready` ; les agents ne construisent que les issues `agent-ready` |
| **G3 Verified** | In Progress → UAT | Vérifications automatiques + agent relecteur indépendant (+ humain pour les zones protégées) | Vérifications requises `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → fusion | Testeur humain | Vérification requise `release-gate` (demande le label de PR `uat-passed` ou `gate-override`) |
| **G5 Released** | fusion → production | Humain (PO) | Environnement GitHub `production` avec relecteur obligatoire |

---

## Liste de contrôle de G1 Decision

L'évaluation (ou, pour une idée construite sous forme de prototype, les notes du prototype produites par `/spike`) doit contenir :
- [ ] L'énoncé du problème et pour qui
- [ ] Une estimation de la valeur avec des preuves (ou un « pas encore de preuves » explicite)
- [ ] La taille de l'effort, justifiée à partir du code
- [ ] Les risques : sécurité, protection des données (par exemple le RGPD), réglementation, exploitation
- [ ] Au moins deux options, plus « ne rien faire »
- [ ] Une recommandation

L'humain répond par l'une de ces décisions : **approuver** (avec une priorité), **mettre de côté** (avec ce qui déclenchera un réexamen), **rejeter** (avec une raison). Pour un prototype, il l'essaie d'abord (`/test`), si bien que la décision repose sur l'usage plutôt que sur la lecture.

## G2 Definition of Ready

Une issue ne peut recevoir `agent-ready` que si :
- [ ] La spec existe dans `docs/specs/` et est liée depuis l'issue
- [ ] Les critères d'acceptation sont écrits au format Given / When / Then et chacun est testable
- [ ] Le périmètre et le **hors périmètre** sont explicites
- [ ] Les fichiers/modules probablement touchés sont listés
- [ ] L'impact sur les données, les migrations et la configuration est indiqué (ou « aucun »)
- [ ] Le plan de tests unitaires et les grandes lignes de l'UAT sont inclus
- [ ] Taille ≤ 1 jour de travail d'agent (~400 lignes modifiées) ; sinon, découpage en sous-issues
- [ ] Les zones protégées touchées sont signalées (label `human-review` ajouté)
- [ ] La priorité est fixée
- [ ] Un humain a approuvé la spec

## G3 Verified (Definition of Done pour le code)

- [ ] Chaque critère d'acceptation a au moins un test automatisé
- [ ] `make check` passe en local et dans la CI (lint, types, tests unitaires, build)
- [ ] Aucune modification sans rapport dans le diff
- [ ] La documentation touchée par la modification est à jour (`ARCHITECTURE.md`, documentation de l'API, liste des variables d'environnement)
- [ ] Aucun secret, aucune donnée personnelle réelle dans le code, les tests ou les fixtures
- [ ] La description de la PR suit le modèle et lie l'issue (`Refs #123` sur GitHub Projects, l'identifiant dans le titre sur Linear)
- [ ] Vérification `secrets` au vert : aucune clé, aucun token ni mot de passe dans aucun commit de la PR
- [ ] Vérification `dependencies` au vert : aucune vulnérabilité connue de niveau élevé ou critique
- [ ] `ai-review` au vert : l'agent relecteur indépendant n'a trouvé aucun point bloquant
- [ ] `security-review` au vert : la revue de sécurité de Claude n'a trouvé aucune vulnérabilité
- [ ] Revue de code humaine faite si le label `human-review` est présent

### Comment fonctionne la revue de code

La revue est organisée en couches pour qu'**aucun agent ne relise jamais son propre travail** et que **les secrets soient repérés par des outils déterministes, pas par le jugement**.

| Couche | Quand | Quoi | Qui ou quoi s'en charge |
|---|---|---|---|
| 1. Garde locale contre les secrets | Avant chaque commit | Bloque les commits qui contiennent des clés/tokens | gitleaks via le hook git pre-commit (tout le monde, n'importe quel outil), plus les hooks de l'outil d'agent quand c'est possible (Claude Code ; Grok) |
| 2. Autovérification | Avant d'ouvrir une PR | `make check` + `/security-review` sur ses propres modifications | L'agent qui construit |
| 3. CI déterministe | À chaque push sur une PR | Tests, lint, types, analyse des secrets de chaque commit, audit des dépendances | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Revue IA indépendante | À chaque push sur une PR (sauf brouillons et PR de documentation seule) | Conformité à la spec, tests honnêtes, exactitude, règles du projet ; vulnérabilités de sécurité | Un Claude distinct dans GitHub Actions qui n'a jamais vu le code s'écrire (`ai-review`, `security-review`) |
| 5. Revue humaine | PR avec le label `human-review` | Zones protégées : logique métier centrale, authentification, paiements, données personnelles, migrations, infrastructure | Le product owner ou un développeur désigné |
| 6. Acceptation humaine | Chaque PR de code | Le comportement fonctionne pour de vrai (UAT de G4) | Le product owner |

**Règles de la boucle de revue**
- L'agent qui construit lit le commentaire du relecteur, corrige chaque point **Blocking** et pousse ; les revues se relancent automatiquement.
- Si l'agent qui construit pense qu'une remarque est fausse, il répond dans la PR en expliquant pourquoi et demande à l'humain. Il ne tourne jamais en rond : **après deux tours de revue** toujours en échec, il s'arrête et passe la main à l'humain.
- Seul un humain peut passer outre une revue IA, avec le label de PR `ai-review-overruled`. Cela reste enregistré dans la PR.
- Les relecteurs IA ne peuvent ni approuver ni fusionner. Ils peuvent seulement bloquer.

### Si un secret arrive un jour sur GitHub
1. **Révoquez-le et remplacez-le immédiatement** auprès du fournisseur. Considérez qu'il est compromis ; le retirer du code n'annule pas la fuite.
2. Retirez-le du code ; utilisez une variable d'environnement documentée dans `.env.example`.
3. Un admin du dépôt réécrit l'historique de la branche avant la fusion (un nouveau commit ne suffit pas).
4. Ouvrez un `/bug` avec la priorité Urgent pour consigner ce qui s'est passé et ce qui a été remplacé (n'y mettez jamais le secret lui-même).

**Les paramètres du product owner changent la façon dont G3 tourne, pas qui décide** (`/haam-settings`) :
- `ci` : à chaque PR, en local (`ci-local`, publié par `haam.py local-ci` sur l'ordinateur du product owner), ou désactivée.
- `review` : GitHub, en local, zones protégées seulement, ou désactivée.
- `nightly`.

Les vérifications requises suivent les paramètres (`settings --apply`). L'analyse des secrets tourne toujours.

## G4 Accepted (UAT)

Dans le flux par défaut « test d'abord », G4 vient avant G3 : le product owner teste la branche poussée par l'agent avant qu'une PR n'existe, puis G3 vérifie exactement le commit qu'il a validé (`haam.py publish`, puis `ship`, qui refuse tout le reste).

**Voie sans UAT :** G4 est alors décidée à l'avance. Quand le product owner marque une issue `uat:skip` (dans `/triage`, ou avec « spec approved, no UAT »), l'agent ouvre la PR avec le même label et `release-gate` passe dès que toutes les issues couvertes par la PR le portent (GitHub Projects : la porte lit les issues ; Linear : elle se fie au label de la PR). Jamais quand la PR modifie une zone protégée : la porte compare les fichiers modifiés à `protected_paths` dans le `haam.config.json` de `main` (la configuration des agents et de la CI par défaut, plus les zones propres au projet), ajoute `human-review` et garde la voie fermée, quels que soient les labels. Une mise à jour du kit ne prend donc jamais cette voie : elle modifie la configuration des agents, et vous la relisez et la livrez vous-même. G3 s'applique toujours entièrement, et l'auto-merge (qui demande `HAAM_PROJECT_TOKEN`) ne fusionne que lorsque toutes les vérifications requises passent. Il n'y a pas d'auto-merge sur Linear, ni quand la CI ou l'une des revues IA tourne ailleurs que sur GitHub pour chaque PR (l'auto-merge demande `ci: every-pr` et `review: github`) : des résultats locaux ne sont pas infalsifiables et des vérifications réduites ne suffisent pas à elles seules, donc c'est le product owner qui livre ces PR de la voie sans UAT (`ship`), ce qui reste une seule décision pour beaucoup de PR. Seule la décision d'un humain ajoute `uat:skip` à une issue (`issue create` et `issue label` le refusent sans `--human`).

- [ ] Le plan UAT existe dans `docs/uat/` avec des étapes numérotées et des résultats attendus
- [ ] Un humain l'a déroulé en local sur la branche (test d'abord : la branche poussée par l'agent, avant toute PR ; vérifications d'abord : la branche de la PR)
- [ ] Toutes les étapes passent, ou les échecs sont consignés et acceptés comme issues de suivi
- [ ] La validation de l'humain (`/test` ou `/uat-result <ID> pass`) ajoute le label `uat-passed` à la PR (test d'abord : `publish` l'enregistre aussi sur le commit testé, sous forme de statut `uat`)
- [ ] La validation couvre le code qui est fusionné : un push après elle retire `uat-passed` (`gates.yml`), sauf si la nouvelle tête est le commit testé ; `ship` ne fusionne que ce commit

## G5 Released

- [ ] PR fusionnée dans `main` par un humain, ou par `haam.py ship --human` après que l'humain a dit `ship`
- [ ] Déploiement en production approuvé (environnement `production`) : dans GitHub, ou par `ship` sur la parole de l'humain
- [ ] Smoke test après déploiement réussi (`make smoke`, s'il est défini)
- [ ] L'issue est marquée Done (`ship`, ou `/release` pour les modifications fusionnées autrement) ; la note de version dans `docs/changes/` a été livrée avec elle

---

## Dérogations

Parfois la production est en feu ou une échéance ne peut pas attendre. Les dérogations existent pour cela et sont **réservées aux humains**.

### Niveau 1 : sauter l'UAT (le plus courant)
À utiliser quand la correction est urgente et vérifiée par des tests, mais qu'il n'y a pas le temps de faire un cycle UAT complet.

1. L'humain lance `/override <ID> "<reason>"` (pour une PR sans issue : `/override PR <number> "<reason>"`), ou commente à la main `OVERRIDE: <reason>` dans la PR (le commentaire doit commencer par `OVERRIDE:`) et ajoute le label de PR `gate-override`.
2. La vérification `release-gate` passe grâce au label de dérogation.
3. La CI (vérification `ci`) **doit toujours passer**.
4. Quand la PR a une issue, l'agent crée une issue de suivi dans l'outil de suivi : `Post-override UAT for <ID>` (priorité High, label `stream:bug`, `override-followup`), pour que la vérification sautée ait quand même lieu après coup.

### Niveau 2 : contournement d'urgence (rare)
À utiliser seulement quand la CI elle-même est cassée ou bloque une correction de production.

1. Un admin du dépôt fusionne avec « bypass branch protections » dans GitHub.
2. L'admin commente `EMERGENCY BYPASS: <reason>` dans la PR.
3. Une issue de suivi est créée comme ci-dessus, plus une deuxième pour réparer ce qui bloquait la CI.

### Règles des dérogations
- Les agents n'ajoutent **jamais** `gate-override`, ne contournent jamais les protections et ne suggèrent jamais de déroger, sauf si l'humain l'évoque en premier.
- Chaque dérogation doit avoir une raison écrite dans la PR.
- Les dérogations sont passées en revue lors de la revue hebdomadaire du backlog : filtrez l'outil de suivi sur le label `override-followup`.
