# Les décisions à prendre quand vous adoptez HAAM

C'est le product owner qui les prend, avec l'admin du projet. `/haam-setup` les passe en revue dans cet ordre, avec une recommandation pour chacune, et `/haam-settings` permet de les changer plus tard. Commencez par le choix recommandé, puis revenez-y après la première semaine chargée. À ce moment-là, `haam.py ci-usage` montre où sont passées les minutes Actions et `haam.py capacity` montre ce qui vous attend.

**Quelques mots utilisés ici :**
- **PR** (pull request) : une modification proposée, en attente de fusion dans `main`.
- **CI :** les vérifications automatiques (lint, types, tests, build) qui tournent sur GitHub pour une PR. Elles consomment des minutes Actions.
- **UAT** (test d'acceptation utilisateur) : votre propre test d'une modification, sur votre ordinateur, avant qu'elle soit livrée.
- **La voie sans UAT :** les modifications que vous marquez `uat:skip` (mises à jour de dépendances, configuration, refactorisations invisibles). Elles sautent votre test et passent directement aux vérifications.
- **Porte de release :** la vérification qui empêche une PR d'être fusionnée tant que votre test n'est pas validé, ou que vous n'avez pas choisi la voie sans UAT.
- **Worktree :** une copie séparée du dossier du projet pour une conversation d'agent, pour que les conversations n'écrasent pas le travail des autres.

## En un coup d'œil

| Décision | Commencez par | Changez quand | Voir |
|---|---|---|---|
| Compte et plan GitHub | Une organisation. Dépôt public : Free. Privé : Team | Le dépôt est privé et il vous faut un approbateur pour les déploiements : Enterprise Cloud | §1 |
| Outil de suivi | GitHub Projects | L'équipe travaille déjà tous les jours dans Linear | §2 |
| Qui fait quoi | Un product owner, un approbateur suppléant | Plusieurs produits ou product owners | §3 |
| Langue (`language`) | La langue dans laquelle votre équipe écrit | L'équipe change | §3 |
| Ordre des tests (`flow`) | `test-first` | Vous testez sur un site de préproduction partagé plutôt qu'en local | §4 |
| Ce que vous testez (`uat`) | `owner-decides` | Produit réglementé : `always`. Beaucoup de petites corrections bien testées : `bugs-skip` | §4 |
| Regroupement (`grouping`) | `per-issue` | Des epics faites de petits éléments : `per-epic`. Les minutes Actions sont rares : `release` | §4 |
| Vérifications (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | Les minutes Actions viennent à manquer | §4 |
| Livraison (`deploy`, `deploy_approval`) | `github`, `each` | Vous déployez autrement, ou votre plan ne permet pas de retenir les déploiements pour approbation | §4 |
| Limites | `settings --recommend` | Votre temps de test ou le nombre d'agents change | §5 |
| Zones protégées | Les valeurs par défaut, plus votre code sensible | L'architecture change | §6 |
| Ressources de test partagées (`heavy_runs`) | Aucune | Les tests partagent une base de données locale, un simulateur ou un appareil | §7 |
| Liberté laissée aux agents | Prototypes et mode de construction par epic quand vous les demandez ; le code de production, c'est tout sauf les prototypes, les tests et la documentation | Vous voulez que les agents explorent davantage, ou votre code de production tient dans quelques dossiers | §8 |

## 1. Compte GitHub, organisation et plan

### Les comptes
Chaque personne crée et garde son propre compte ; ne partagez jamais des identifiants.

1. **Chaque personne** s'inscrit sur [github.com/signup](https://github.com/signup) avec son e-mail professionnel et active l'authentification à deux facteurs (Settings → Password and authentication).
2. **Un admin** crée une organisation ([github.com/organizations/plan](https://github.com/organizations/plan)) et y invite l'équipe. Le plan gratuit suffit pour un dépôt public ; un dépôt privé demande Team (voir le tableau ci-dessous). L'organisation possède les dépôts, si bien que rien ne dépend du compte d'une seule personne. Désignez deux propriétaires.
3. **Le dépôt** vit dans l'organisation : créez-le là, ou transférez-y un dépôt existant (Settings du dépôt → General → Transfer ownership).
4. **Sur chaque ordinateur**, installez la GitHub CLI ([cli.github.com](https://cli.github.com)) et lancez `gh auth login`. Si l'outil de suivi est GitHub Projects, lancez aussi `gh auth refresh -s project`.
5. **Pas de comptes séparés pour les agents.** Les agents agissent sous le compte de la personne connectée. Les portes partent du principe que la personne au clavier répond de ce que font ses agents.

### Le plan dont vous avez besoin

| Ce qu'utilise HAAM | Dépôt public, n'importe quel plan | Privé, Free | Privé, Pro | Privé, Team | Privé, Enterprise Cloud |
|---|---|---|---|---|---|
| Règles de branche et vérifications requises ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Oui | Non | Oui | Oui | Oui |
| Un approbateur pour les déploiements en production ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Oui | Non | Non | Non | Oui |
| L'analyse des secrets et la protection des push propres à GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Oui | Non | Non | Option payante | Option payante |
| Tableau GitHub Projects | Oui | Oui | Oui | Oui | Oui |
| Minutes Actions | Gratuites sur les runners standard | Un quota mensuel | Un quota plus important | Un quota plus important | Un quota plus important |

Pro est destiné à un compte personnel ; Team et Enterprise Cloud aux organisations.

Ce que signifie chaque élément manquant :
- **Pas de règles de branche** (dépôt privé sur Free) : GitHub n'empêche pas une fusion dans `main` sans les vérifications. Les agents ont toujours pour consigne de ne jamais fusionner, et `ship` fait toujours passer toutes les portes, mais rien ne l'impose. Pour tout produit privé, utilisez Team (organisation) ou Pro (compte personnel).
- **Pas d'approbateur pour les déploiements** (dépôt privé en dessous d'Enterprise Cloud) : les déploiements démarrent quand une PR est fusionnée. Votre `ship`, qui fait la fusion, vaut alors décision de mise en production. Réglez `deploy_approval: automatic` pour que HAAM n'attende pas une approbation qui ne peut pas arriver, et gardez `uat` sur `owner-decides` ou `always` (§4).
- **Pas d'analyse des secrets de GitHub :** ce n'est pas grave. La vérification `secrets` du kit et le hook pre-commit tournent sur tous les plans.

Les plans et les quotas changent : vérifiez [github.com/pricing](https://github.com/pricing) avant de choisir.

### L'accès des relecteurs à Claude
Les deux revues IA tournent avec un seul secret du dépôt, ajouté par le product owner dans son propre terminal et jamais collé dans une conversation :
- `CLAUDE_CODE_OAUTH_TOKEN` (obtenu par `claude setup-token`) : les revues sont décomptées du plan Claude de cette personne.
- `ANTHROPIC_API_KEY` : facturé à chaque revue, indépendamment de l'abonnement de quiconque. Fixez une limite de dépenses mensuelle dans la console Anthropic.

## 2. L'outil de suivi : GitHub Projects ou Linear

| | GitHub Projects | Linear |
|---|---|---|
| Coût | Gratuit sur tous les plans GitHub | Gratuit jusqu'à 250 issues actives (non archivées) et 2 équipes ; les plans payants par utilisateur lèvent le plafond. Vérifiez [linear.app/pricing](https://linear.app/pricing) |
| Comment les agents l'utilisent | `haam.py issue …` depuis n'importe quel outil d'agent, avec la connexion `gh` de la personne | La connexion Linear (MCP) configurée dans chaque outil d'agent |
| Fait pour vous | Des réservations qui empêchent deux conversations de prendre la même tâche ; la file UAT comptée pour les limites ; les champs propres au tableau (`--field`) ; la voie sans UAT qui fusionne toute seule ; `ship` qui clôt les issues | Les agents font les changements via la connexion, et comptent la file UAT pour `capacity --in-uat N`. La voie sans UAT ne fusionne pas toute seule : c'est vous qui livrez ces PR |
| Configuration | `haam.py github-project --apply` | `haam.py linear --apply` avec la clé d'API du product owner, plus les étapes dans le navigateur décrites dans `LINEAR-SETUP.md` |
| Idéal pour | La plupart des équipes : tout au même endroit | Les équipes qui vivent déjà dans Linear |

**Recommandation :** GitHub Projects, sauf si l'équipe utilise déjà Linear tous les jours. Le tri et les agents créent vite des issues, si bien que le plafond gratuit de Linear peut être atteint en quelques semaines.

## 3. Qui fait quoi
- **Product owner :** une seule personne, qui décide, teste et livre. Elle seule lance les skills réservés aux humains : `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` et `/haam-settings`.
- **Approbateurs suppléants :** une ou deux personnes qui peuvent approuver les déploiements quand le product owner est absent (`config --backup-approvers a,b`). Cela demande un approbateur pour les déploiements, donc cela n'a aucun effet sur un dépôt privé en dessous d'Enterprise Cloud.
- **Constructeurs :** toutes les personnes qui font tourner des conversations d'agent. Chacune a besoin de son propre compte GitHub avec droit d'écriture, et de son propre outil d'agent. L'admin lance `haam.py invite --github USER` pour voir le plan, puis la même commande avec `--apply`. Chaque constructeur lance ensuite `/haam-onboard`.
- **Admin :** configure GitHub, l'outil de suivi et les secrets. C'est souvent le product owner.
- **Dès que deux personnes travaillent sur le code,** exigez une approbation dans les règles de branche (`GITHUB-SETUP.md` §2).
- **Langue :** la documentation du kit existe en anglais, espagnol, français, allemand, italien, néerlandais et portugais (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Les agents rédigent les specs, les issues, les plans UAT et les messages dans la langue choisie ; les commandes, les labels, les statuts et le code restent en anglais. Choisissez-la à l'installation (`install --language es`). Pour la changer plus tard : `haam.py config --language fr`, puis le `update --target . --apply` du kit bascule les documents que vous n'avez pas modifiés.

## 4. Comment le travail circule : les paramètres
`python3 tools/haam/haam.py settings --explain` affiche chaque option avec son compromis. Les choix qui comptent :

| Paramètre | Commencez par | Choisissez autre chose quand | Ce que cela coûte ou risque |
|---|---|---|---|
| `flow` | `test-first` : vous testez la branche de l'agent, puis la PR et les vérifications tournent une fois | `checks-first` : vous ne voulez tester que du code qui a passé les vérifications, ou vous testez sur un site de préproduction partagé | Chaque tour de reprise relance les vérifications |
| `uat` | `owner-decides` : vous testez tout sauf ce que vous marquez `uat:skip` | `always` : produits réglementés ou critiques pour la sécurité. `bugs-skip` : beaucoup de petites corrections avec de bons tests | `bugs-skip` : une mauvaise correction peut être livrée sans que vous l'ayez vue |
| `grouping` | `per-issue` : une PR par issue | `per-epic` : des epics faites de petits éléments. `release` (test d'abord uniquement) : minutes rares et releases par lots | Un élément en échec retient tout le lot |
| `ci` | `every-pr`, sur GitHub | `local` : les minutes s'épuisent et votre ordinateur sait tout construire. `off` : prototypes en solo uniquement | `local` n'est pas infalsifiable |
| `review` | `github` : deux revues IA indépendantes par PR | `protected-only` : économise l'essentiel du coût des revues. `local` : économise des minutes | Moins de vérifications indépendantes |
| `nightly` | `on` | `off` : quand les minutes sont très rares | Vous découvrez plus tard les régressions et les nouvelles vulnérabilités |
| `runner` | `github` | `self-hosted` : un dépôt privé avec des builds lourds et une machine qui reste allumée | De l'entretien. Jamais pour les dépôts publics |
| `deploy` | `github` : `deploy.yml` déploie à la fusion | `manual` : vous déployez autrement | `ship` attend que vous disiez « live » |
| `deploy_approval` | `each` : chaque déploiement attend votre approbation | `automatic` : votre plan ne permet pas de retenir les déploiements (§1), ou vous avez choisi `uat: always` | Une modification fusionnée est mise en ligne sans dernier coup d'œil |
| `worktree_cleanup` | `after-ship` | `manual` : vous préférez ranger les worktrees vous-même | Espace disque |

La voie sans UAT ne fusionne toute seule que sur GitHub Projects, avec le secret `HAAM_PROJECT_TOKEN`, `ci: every-pr` et `review: github`. Sinon, c'est vous qui livrez ces PR.

Évitez ces combinaisons, car ensemble elles suppriment le dernier contrôle :
- `ci: off` avec `review: off` : rien ne vérifie le code avant votre test.
- `deploy_approval: automatic` avec `uat: bugs-skip` : une correction de bug peut arriver en production sans que personne ne l'ait regardée. Les déploiements sont automatiques sur un dépôt privé en dessous d'Enterprise Cloud, donc n'y choisissez pas `bugs-skip`.

## 5. Les limites : combien de travail peut attendre
Les limites empêchent les agents de produire plus que ce que vous pouvez tester, et plus de PR que votre budget de CI ne le permet. Quand une limite est atteinte, les agents cessent de lancer de nouvelles constructions. Ils continuent de faire les reprises, de rédiger des specs et d'évaluer des idées.

| Limite | Ce qu'elle compte | Comment la dimensionner |
|---|---|---|
| `max_in_uat` | Les modifications qui attendent votre test. La principale limite en mode test d'abord | Ce que vous pouvez tester en une session : minutes par session ÷ minutes par test (un test prend souvent 5 à 10 minutes). Une heure par jour à environ 6 minutes par test, cela fait 10 |
| `max_open_prs` | Les PR prêtes. Les brouillons, les PR de documentation seule et les PR des bots (Dependabot) ne comptent pas | Test d'abord : les PR vivent peu de temps (de votre validation à `ship`), donc deux fois le nombre de conversations d'agent simultanées suffit largement. Vérifications d'abord : chaque modification qui attend votre test est une PR prête, donc réglez-la au moins à `max_in_uat` plus le nombre de conversations simultanées |
| `max_review_rounds` | Les tours de revue IA en échec avant qu'un agent s'arrête et vous demande | 2. Passez à 3 pour les zones difficiles |
| `max_pr_lines` | La taille visée pour une PR, en lignes modifiées | 400. Les petites PR sont mieux relues et mieux testées |

Faites le calcul pour votre équipe :
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
La commande affiche les limites suggérées et vous avertit quand les agents peuvent produire plus que ce que vous pouvez tester. Elle donne ensuite la commande qui les applique. Elle suppose environ 6 minutes par test et 2 modifications par conversation et par jour ; passez `--minutes-per-test` et `--changes-per-chat` avec vos propres chiffres. Elle lit `flow` dans les paramètres du projet, ou prend `--flow`.

Si les agents produisent plus que ce que vous testez :
- la file se remplit et les agents mettent en pause les nouvelles constructions : c'est la limite qui fait son travail ;
- `/test all` avec « pass all verified » libère les modifications que les agents ont prouvées eux-mêmes ;
- `uat: bugs-skip` envoie les petites corrections de bugs directement aux vérifications ;
- ou faites tourner moins de conversations d'agent.

Pour un week-end de travail des agents testé en une seule session, ouvrez une **fenêtre de lot** : un relèvement qui se termine tout seul après son dernier jour, par exemple `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. Ce qu'il faut protéger
**La règle :** protégez le code où une mauvaise modification pourrait nuire aux utilisateurs, faire perdre de l'argent ou des données, enfreindre la loi, ou affaiblir les portes de HAAM elles-mêmes. Chaque modification protégée demande votre revue de code et votre test, et ne passe jamais par la voie sans UAT. Protégez donc ce qui compte, pas tout.

| Zone | Protéger | Chemins typiques (exemples) |
|---|---|---|
| Connexion, sessions, droits, rôles | Toujours | `src/auth/**`, `**/permissions/**`, *le middleware d'authentification* |
| Paiements, facturation, remboursements, tarifs | Toujours | `src/billing/**`, `src/payments/**` |
| Données personnelles : stockage, conservation, suppression, exports | Dès que vous détenez des données personnelles | `src/users/**`, `**/privacy/**` |
| Journalisation susceptible de capter des données personnelles | Dès que vous détenez des données personnelles | *la configuration de la journalisation et les modules d'audit* |
| Décisions concernant les utilisateurs : éligibilité, vérification, approbations, scoring | Quand un mauvais résultat nuit à quelqu'un | `src/verification/**`, `src/decisions/**` |
| Fournisseurs externes qui agissent pour les utilisateurs ou reçoivent leurs données | Oui | `src/integrations/**` |
| Migrations de base de données | Toujours | `db/migrations/**`, `**/migrations/**` |
| Configuration de sécurité : cryptographie, CORS, CSP, gestion des secrets | Oui | `**/security/**`, `**/crypto/**` |
| Infrastructure as code | Oui | `infra/**`, `terraform/**` |
| Signature et configuration de release mobiles | Si vous livrez des applications | *fichiers d'entitlements, de signature et de build de release* |
| CI, déploiement et scripts de build | Protégé par défaut | `.github/**`, `Makefile`, `scripts/**` |
| HAAM et la configuration des agents | Protégé par défaut | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json`, et d'autres : `haam.py settings` les liste |

Les chemins en italique décrivent ce qu'il faut chercher ; transformez-les en vrais motifs pour votre code.

Comment le mettre en place :
1. `/haam-setup` propose de vrais chemins tirés de votre code pour chaque zone concernée. Vous les confirmez.
2. `config --protected "src/auth/**,db/migrations/**" --human` ajoute des motifs, et `config --unprotected "…" --human` en retire un. `**` veut dire n'importe quels dossiers et `*` veut dire à l'intérieur d'un seul dossier. Un simple nom de dossier couvre tout ce qu'il contient.
3. `haam.py protected` sur n'importe quelle branche liste les fichiers protégés qu'elle modifie.
4. La porte de release décide d'après les fichiers que modifie une PR. Elle lit la liste depuis `main`, si bien qu'un agent ne peut pas retirer une protection dans sa propre PR.

Revoyez la liste chaque fois que `docs/product/ARCHITECTURE.md` change.

## 7. Les ressources de test partagées
Certains tests utilisent quelque chose que tout l'ordinateur partage, comme une base de données locale que les tests clonent, un simulateur de téléphone ou un appareil connecté. Deux conversations d'agent qui les lancent en même temps se gênent mutuellement, et l'échec ressemble à une modification cassée. Listez ces commandes sous forme de motifs : `config --heavy-run "make (check|test-integration)"`. Les agents les lancent alors une à la fois via `haam.py exclusive`. Laissez la liste vide si vos tests sont autonomes.

## 8. La liberté laissée aux agents
Les agents peuvent construire vite de gros morceaux, à la manière dont on fait du « vibe-coding » avec l'IA, partout où une erreur ne coûte pas grand-chose à jeter. Tout ce qui tourne pour de vrais utilisateurs reste derrière les portes.

**Quelques mots utilisés ici :**
- **Prototype** (ou **spike**) : une version fonctionnelle rapide et jetable d'une idée, construite pour être essayée, jamais livrée telle quelle.
- **Tranche :** un morceau livrable d'une epic, avec sa propre issue et sa propre spec.
- **Agent principal :** la conversation d'agent unique qui construit toute une epic. Il peut confier des tranches indépendantes à des agents auxiliaires (**sous-agents**).
- **Feature flag :** un interrupteur dans le code qui garde une nouvelle fonctionnalité cachée jusqu'à ce que quelqu'un l'active.
- **Code de production :** le code qui tourne pour de vrais utilisateurs.

Trois choix :

| Choix | Ce qu'il fait | Quand l'utiliser |
|---|---|---|
| **Le prototype d'abord.** Tapez `/spike`, ou choisissez `prototype` dans `/triage` | Un agent construit un prototype sur une branche `spike/`, sans spec, sans PR ni limite de taille. Vous l'essayez avec `/test`. Puis vous répondez `discard`, `change: <what>`, `rebuild` (le spécifier et le reconstruire à neuf) ou `keep` (le spécifier et construire à partir de ce code) | Quand essayer l'idée vous en apprend plus que de lire à son sujet : un nouvel écran, un parcours, une intégration dont vous n'êtes pas sûr |
| **Le mode de construction par epic.** Mettez le label `mode:epic-build` sur une epic approuvée ; `/decide` et `/triage backlog` le proposent | Un agent principal construit toutes les tranches de l'epic sur une seule branche, avec un point d'étape après chaque tranche. Vous testez et livrez toute la fonctionnalité en une fois | Une fonctionnalité dont les tranches n'ont de sens qu'ensemble, ou que vous préférez juger dans son ensemble |
| **Ce qui compte comme code de production** (`production_paths`, `non_production_paths`) | Indique aux agents et à vous ce qui tourne pour les utilisateurs, pour que les notes d'un prototype et `haam.py production` montrent ce qu'une modification toucherait. Les prototypes, les tests et la documentation en sont exclus par défaut | Restreignez-le quand votre produit tient dans quelques dossiers : `config --production "src/**,api/**" --human`. Ajoutez les dossiers qui ne tournent jamais pour les utilisateurs avec `config --not-production "…" --human`. Si votre documentation est ce que voient les utilisateurs, retirez-la de la liste avec `config --remove-not-production "docs/**" --human` |

Quel que soit le mode, toute modification fusionnée passe toutes les portes. Le garde-fou derrière cela :
- un prototype n'est jamais fusionné : la porte de release refuse les branches `spike/` et tout ce qui se trouve sous `prototypes/`, et `publish` refuse les spikes ;
- le code de prototype conservé n'arrive aux utilisateurs que par `/spec`, une branche normale et votre test, derrière un feature flag désactivé par défaut. Il ne passe jamais par la voie sans UAT : la porte voit ses commits `spike:` ;
- le code de production n'importe jamais rien de `prototypes/`, et le relecteur IA bloque s'il le fait ;
- un prototype ne modifie jamais les zones protégées, et `/test` vous montre les fichiers protégés qu'il modifie et ses nouvelles dépendances avant de lancer quoi que ce soit ;
- les zones protégées ont toujours droit à votre revue de code ;
- aucun agent ne touche aux systèmes ni aux données de production, dans aucun mode.

## Sources
- GitHub : [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (plans qui les incluent) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (relecteurs obligatoires sur les dépôts privés) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear : [Pricing](https://linear.app/pricing)
