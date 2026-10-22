# Travailler en tant que product manager

*Un guide pour la personne qui décide de ce qui est construit. Les agents n'ont pas besoin de le lire ; vous, si.*

Dans HAAM, vous décidez du **quoi** et du **pourquoi** ; les agents trouvent le **comment** et le font. Les agents sont rapides : la vitesse de tout le système dépend donc de la rapidité avec laquelle vous triez, décidez, approuvez et testez. Votre travail principal consiste à garder la file **Waiting on me** courte et l'**Agent queue** orientée vers les bonnes choses.

Les exemples utilisent les identifiants de GitHub Projects (`#12`) ; sur Linear, le même élément s'appelle `APP-12`. Les commandes sont écrites `/name` ; dans Codex, utilisez `$name`.

---

## 1. Votre travail en une page

| Ce que vous seul faites | À quelle fréquence | Avec l'IA | Directement dans l'outil de suivi |
|---|---|---|---|
| Tenir `docs/product/PRODUCT.md` à jour : priorités actuelles, non-négociables, parcours essentiels | Tous les mois | « Mettez à jour PRODUCT.md : nos priorités sont maintenant… » | Modifier le fichier (via une PR) |
| Trier les nouvelles idées et les nouveaux bugs | Tous les jours | `/triage` | Vue Triage : priorité, statut, labels |
| Regrouper les issues liées en epics et répondre aux questions de l'agent sur chacune | Toutes les semaines | `/triage group`, puis `/epic #9` | Issue d'epic (label `epic`) avec des sous-issues |
| Fixer et changer les priorités | Tous les jours et toutes les semaines | `/triage`, `/triage backlog` | Champ Priority |
| Décider des idées évaluées (G1) | Toutes les semaines | `/decide #12 approve high` | Statut, labels, commentaire (§7–8) |
| Approuver les specs (G2) | Au fil de l'eau | Lire la spec (liée dans l'issue), puis « spec de #12 approuvée » | Commenter « spec approved » ; statut Ready, label `agent-ready` |
| Tester les modifications (G4) et les livrer (G5) | Tous les jours | `/test`, puis répondre `pass` → `ship`, ou dire ce qui ne va pas | GitHub : label `uat-passed`, fusion, approbation du déploiement |
| Clore les suivis de dérogation | Toutes les semaines | « Montrez-moi les suivis de dérogation ouverts » | Vue : label `override-followup` |

Tout ce que vous décidez va dans l'outil de suivi ou dans Git, jamais seulement dans une conversation. Si ce n'est pas écrit là, l'agent suivant ne le sait pas.

---

## 2. Votre rythme

### Tous les jours (10–15 minutes)
1. **Testez d'abord.** Tapez `/test all` : l'agent vous fait passer en revue chaque modification qui vous attend, l'une après l'autre (§2a), puis livre tout ce qui a été validé en un seul déploiement. Les agents ne peuvent pas terminer tant que vous ne l'avez pas fait, et leur contexte devient obsolète.
2. **Videz la boîte de réception Triage** (`/triage`, ou la vue Triage). Rien ne devrait y rester plus de deux jours ouvrés.
3. **Bugs urgents :** s'il y en a un, lancez tout de suite un agent dessus : nouvelle fenêtre de conversation, `/work bugs`.
4. Parcourez les commentaires de passation et de blocage des agents et répondez à leurs questions.

### 2a. Tester une modification : la boucle complète
1. Tapez **`/test`** (ou `/test #12`). L'agent met la modification sur votre ordinateur, démarre l'application et vous donne le lien et une courte liste de contrôle : *faites ceci → vous devriez voir cela*.
2. Essayez-la. Puis répondez en un mot ou en une phrase :
   - **`pass`** → l'agent ouvre la pull request (jusque-là il n'y en avait pas : vous avez testé la branche de l'agent), les vérifications tournent une seule fois sur exactement ce que vous avez testé, et il vous demande *« On livre quand les vérifications passent ? »* Répondez **`ship`** : il les attend, fusionne, approuve pour vous le déploiement en production et clôt l'issue. Vous recevez *« #12 est en ligne. »* Répondez `later` pour la mettre en attente.
   - Si votre projet **déploie à la main** (`"deploy": "manual"`), l'agent fusionne puis vous demande de déployer ; répondez **`live`** une fois le déploiement fait et il clôt l'issue.
   - Si les vérifications ou les revues trouvent ensuite un problème, l'issue repart aux agents comme un test en échec, et vous revient une fois corrigée.
   - **Ce qui n'a pas marché** (*« étape 3 : le bouton d'export manque toujours sur mobile »*) → l'agent le consigne dans l'issue, lui met le label `uat-failed` et la renvoie aux agents, qui la corrigent en priorité. Une fois corrigée, elle revient dans `/test`.
3. C'est tout. Vous n'avez pas besoin de toucher aux branches, aux labels ni au tableau.

**Le fonctionnement de HAAM, c'est vous qui le choisissez.** Tapez `/haam-settings` : il passe en revue chaque paramètre avec vos propres chiffres (minutes Actions, file UAT), recommande une option et applique ce que vous choisissez :
- quand la CI et les revues IA tournent (à chaque PR, sur votre ordinateur, seulement pour les zones protégées, ou jamais) ;
- ce que vous testez vous-même (tout, ce que vous décidez issue par issue, ou tout sauf les bugs) ;
- comment les modifications sont regroupées (par issue, par epic, ou dans une seule PR de release pour tout ce que vous avez validé) ;
- si les déploiements attendent votre approbation ;
- les limites.

`python3 tools/haam/haam.py settings --explain` les liste tous.

**Les modifications que vous ne pouvez pas tester vous-même** (mises à jour du kit ou de la configuration, mises à jour de dépendances, refactorisations que vous ne remarqueriez pas, CI) : marquez-les `uat:skip` quand vous les triez, ou dites « spec approved, no UAT ». Elles ne passent jamais par `/test` : leur PR est fusionnée toute seule dès que la CI et les deux revues IA passent (GitHub Projects), et votre prochain `ship` les déploie avec tout le reste et les clôt. Si vous ne livrez rien pendant un moment, lancez quand même `/test` et répondez `ship`, ou `ship --all` : leur déploiement attend votre approbation. Sur Linear, livrez-les par leur nom (`ship APP-12 --human`). Réservez cette voie aux modifications qu'aucun utilisateur ne remarquerait ; jamais pour les zones protégées.

### Toutes les semaines (30–45 minutes)
1. **Regroupez** les issues éparses en epics (`/triage group`) et mettez en forme l'epic prioritaire avec l'agent (`/epic #9`).
2. **Décidez** de tout ce qui est en **Decision** (G1).
3. **Relisez les specs** (liées dans chaque issue) et approuvez-les ou commentez-les (G2).
4. **Reclassez** Ready et Backlog en fonction des priorités actuelles (`/triage backlog`).
5. **Repérez le travail bloqué :** `/triage stale` (réservé mais silencieux, UAT en attente depuis trop longtemps, décisions en retard).
6. **Revoyez les éléments Parked** dont le « à revoir quand » s'est réalisé.
7. **Clôturez les suivis de dérogation** (label `override-followup`).
8. Améliorez une chose dans le processus (une `/idea` avec le label `area:process`).

### Tous les mois ou tous les trimestres (30 minutes)
1. Réécrivez les **priorités actuelles** dans `PRODUCT.md` : 3 à 5 résultats, dans l'ordre. Les agents s'en servent pour proposer des priorités et départager, c'est donc la chose la plus utile que vous puissiez tenir à jour.
2. **Élaguez :** tout ce qui est Low et attend depuis plus de deux mois → mettez-le en Parked avec un « à revoir quand ». Un backlog court est un backlog utilisable.

---

## 3. Le tri : décider ce qu'est chaque nouvel élément

Le statut **Triage** est votre boîte de réception. Les idées et les bugs y arrivent depuis `/idea`, `/bug`, les formulaires d'issue, d'autres personnes et les agents. Visez une boîte vide à la fin de chaque journée.

Si plusieurs éléments semblent liés, ou si la plupart manquent de contexte, **regroupez-les d'abord** (§4) : trier une fonctionnalité à la fois est plus rapide et donne de meilleurs résultats que trier des fragments.

Pour chaque élément, répondez à quatre questions :

1. **Est-ce clair et nouveau ?** Doublon → clôturez-le et liez l'original. Pas assez d'informations → posez votre question en commentaire et laissez-le en Triage.
2. **Qu'est-ce que c'est ?** Un **bug**, c'est quelque chose qui ne fonctionne pas comme prévu. Une **idée**, c'est un comportement nouveau ou modifié. « Fonctionne comme prévu, mais l'utilisateur s'attendait à autre chose » est une idée, pas un bug. Corrigez le label de flux s'il est faux.
3. **Quelle importance ?** Fixez la priorité (§5).
4. **Que se passe-t-il ensuite ?**

| Élément | Votre décision | Statut ensuite | Ce qui suit |
|---|---|---|---|
| Bug avec des étapes de reproduction claires | **Ready** | Ready, avec une priorité | Un agent le prend (`/work bugs`) |
| Bug sans assez d'éléments pour avancer | **Besoin d'infos** | Reste en Triage, avec votre question en commentaire | Vous ou la personne qui l'a signalé répondez, puis on trie à nouveau |
| Bug urgent | **Ready, à lancer tout de suite** | Ready, Urgent | Lancez un agent maintenant ; `/override` est disponible si le déploiement ne peut pas attendre |
| Idée qui mérite d'être explorée | **Évaluer** | Discovery, avec une priorité | Un agent rédige l'évaluation (`/work ideas` ou `/assess #12`) |
| Idée que vous comprendriez mieux en l'essayant | **Prototype** | Discovery, label `mode:prototype` | Un agent construit une version fonctionnelle jetable (`/spike #12`) ; vous l'essayez avec `/test` et décidez |
| Bonne idée, mauvais moment | **Mettre de côté** | Parked, avec un commentaire « à revoir quand… » | Revient lors d'une revue hebdomadaire |
| Idée que vous ne ferez pas | **Rejeter** | Canceled, avec une raison en une ligne | Close |
| Doublon | **Doublon** | Canceled, lié à l'original | Close |

Les petites idées passent quand même par l'évaluation. Demandez-en une rapide (« évaluez #12, faites court »). C'est dans l'évaluation que l'agent vérifie le code et les risques, et sa lecture vous prend une minute.

---

## 4. Les epics : regrouper les issues en fonctionnalités

Les issues isolées manquent souvent de contexte. « Bouton d'export absent sur mobile », « Export en CSV » et « Rapports planifiés » sont trois fragments d'une même fonctionnalité, et triés un par un, chacun paraît petit et flou. Une **epic** est une issue parente (label `epic`) qui regroupe les issues visant un même résultat et porte le contexte qui leur manque : pour qui, à quoi ressemble le succès, ce qui est dans le périmètre et en dehors, et l'ordre des tranches. Ce contexte vit dans un court **brief d'epic** dans `docs/epics/`.

**Utilisez une epic pour :** trois issues ou plus qui visent le même résultat ; une idée trop grosse pour une seule spec (taille L ou XL) ; une demande qui touche plusieurs écrans ou modules.
**N'en utilisez pas pour :** un bug isolé ; un fourre-tout de choses sans rapport ; un thème qui ne finit jamais (« performance », « finitions UX ») : ce sont des priorités, pas des epics. Une epic doit pouvoir se terminer, en semaines plutôt qu'en trimestres.

### Comment une epic avance
1. **Regrouper.** `/triage group` examine les issues éparses et propose des epics : un titre, le résultat en une ligne, quelles issues en font partie et pourquoi. Vous répondez `ok` ou vous ajustez (`merge 2 and 3`, `#40 out`). Ou partez d'un thème : `/epic "reporting"`.
2. **Mettre en forme.** `/epic #9` : l'agent lit chaque issue de l'epic, le contexte produit et le code concerné, rédige un brouillon de brief, puis **vous pose jusqu'à cinq questions par tour** : pour qui, à quoi ressemble le succès, l'indispensable et le souhaitable, les contraintes, ce qui ne doit pas changer, son rang. Ensuite il propose un rangement : doublons à clore, manques à ajouter sous forme de nouvelles issues, issues floues à réécrire, grosses issues à découper, un ordre. Rien ne change tant que vous n'avez pas confirmé.
3. **Décider une fois (G1).** `/assess #9` ajoute l'effort et la faisabilité pour toute l'epic ; `/decide #9 approve high` l'approuve, ainsi que les idées qu'elle contient, en une seule fois.
4. **Spécifier et construire tranche par tranche.** Chaque sous-issue a sa propre spec et passe G2 séparément. Les agents construisent les sous-issues, jamais l'epic elle-même.
5. **Terminer.** Quand la dernière sous-issue est livrée, l'agent propose de clore l'epic.

**Priorités :** donnez une priorité à l'epic ; ses issues prennent la même, sauf indication contraire de votre part. Un bug dans une epic peut quand même être plus urgent que l'epic.

**Répondre aux questions de l'agent :** des réponses courtes conviennent. « Je ne sais pas encore » est une réponse valable : la question reste ouverte dans le brief. Répondez sur ce dont les utilisateurs ont besoin et pourquoi ; laissez le comment aux agents.

### Les epics directement dans l'outil de suivi
- **GitHub Projects :** créez une issue et ajoutez-lui le label `epic` ; puis, dans la section des sous-issues de l'epic, ajoutez les issues qui en font partie (ou définissez le parent depuis chaque issue). Sur le tableau, utilisez la vue **Epics**, et affichez les champs *Parent issue* et *Sub-issues progress* dans les vues en tableau pour que chaque carte montre son epic.
- **Linear :** créez une issue avec le label `epic` et faites des issues liées ses sous-issues (définissez leur parent). Pour une très grosse initiative qui couvre plusieurs epics, un projet Linear peut contenir les epics.

---

## 5. Prioriser

### 5.1 Les quatre niveaux

| Priorité | Critère | Traitement attendu |
|---|---|---|
| **Urgent** | La production est cassée pour un parcours essentiel, des données pourraient être perdues ou exposées, une faille de sécurité, ou une échéance légale/de conformité est menacée | On commence aujourd'hui. On peut déroger aux portes, avec un suivi |
| **High** | Fait avancer directement une des priorités actuelles de `PRODUCT.md`, ou un bug dans un parcours essentiel sans solution de contournement | À faire ensuite, cette semaine |
| **Medium** | Utile, mais hors des priorités actuelles, ou les preuves sont minces | Dans l'ordre, quand il n'y a plus de High |
| **Low** | Bien d'avoir, cosmétique, cas limite | Quand il n'y a rien d'autre ; à élaguer après deux mois |
| *(aucune)* | Pas encore trié | Les agents ne le construiront pas |

Restez honnête : si plus d'environ un élément ouvert sur cinq est High ou Urgent, les niveaux ne veulent plus rien dire. Rétrogradez quelque chose.

### 5.2 Les bugs : impact × portée

| | La plupart des utilisateurs, ou un parcours essentiel | Certains utilisateurs | Quelques utilisateurs, ou un cas limite |
|---|---|---|---|
| **Bloque la tâche, perd ou expose des données, sécurité, aspect légal** | Urgent | Urgent | High |
| **Résultat faux, mais il existe une solution de contournement** | High | Medium | Low |
| **Agaçant ou cosmétique** | Medium | Low | Low |

### 5.3 Les idées et les fonctionnalités : valeur, confiance, taille

Après une évaluation, vous avez trois éléments : la **valeur** (à quel point cela fait avancer une priorité actuelle), la **confiance** (la qualité des preuves) et la **taille** (XS–XL, d'après le code). Quelques règles empiriques :
- **High :** valeur claire pour une priorité actuelle, bonnes preuves, taille S–M.
- **Medium :** bonne valeur mais preuves plus faibles ; ou forte valeur mais taille L–XL (demandez un découpage).
- **Low :** faible valeur, quelle que soit la taille.
- **Hors des priorités actuelles ?** Medium au maximum, sauf si vous changez d'abord les priorités.

Pour comparer rapidement deux idées : valeur (1–3) × confiance (0,5 / 0,8 / 1) ÷ taille (XS 1, S 2, M 3, L 5, XL 8). Le score le plus élevé passe en premier. C'est un moyen de départager, pas une formule à laquelle obéir.

### 5.4 L'ordre au sein d'une priorité
Les agents prennent **les bugs avant les fonctionnalités, les plus anciens avant les plus récents, les plus petits avant les plus gros**. Ils lisent la priorité, pas la position d'une carte sur le tableau. Si X doit se faire avant Y, donnez à X une priorité plus haute, ou écrivez `Blocked by #X` dans la description de Y.

### 5.5 Garder des files d'attente saines

| File | Taille saine | Sinon |
|---|---|---|
| **Agent queue** (Ready) | 3–10 éléments | Vide : les agents n'ont rien à faire, rédigez donc plus de specs. Plus de 10 : les priorités deviennent obsolètes, reclassez donc |
| **Decision** | 5 ou moins | Réservez 20 minutes et décidez |
| **UAT** | `max_in_uat` (10 par défaut) | Les agents mettent en attente les nouvelles constructions à la limite (`haam.py capacity`) : c'est votre temps de test, la principale limite en mode test d'abord. Testez avec `/test all` ; les éléments que les agents ont entièrement vérifiés se valident en une réponse (`pass all verified`). Pour un week-end de travail des agents, ouvrez une fenêtre de lot dans `/haam-settings` : un relèvement qui se termine tout seul |
| **Agents en cours** | Pas plus que ce que vous pouvez tester demain | Moins d'agents, des éléments plus petits |
| **PR prêtes** | `max_open_prs` dans `haam.config.json` (10 par défaut) | Les agents mettent en attente les nouvelles constructions à la limite : chaque PR prête coûte des minutes de CI à chaque push. Les brouillons et les PR de documentation seule ne comptent pas. Les specs et les évaluations continuent. Testez et livrez ce qui est ouvert |

### 5.6 Changer les priorités
Changez-les dès que les faits changent, mais expliquez pourquoi dans un commentaire. Les agents et vos collègues lisent l'historique. Ne rétrogradez jamais discrètement un élément Urgent : commentez, et prévenez la personne qui l'a signalé.

---

## 6. Le faire avec l'IA

Utilisez **votre propre conversation dans le dossier principal du projet**, pas l'une des conversations d'agent qui tournent avec `/work`.

| Vous voulez… | Tapez |
|---|---|
| Regrouper des issues éparses en epics | `/triage group` |
| Mettre en forme une epic : brief, questions pour vous, rangement | `/epic #9` (ou `/epic "reporting"` pour partir d'un thème) |
| Trier la boîte de réception | `/triage` |
| Reclasser Ready et Backlog en fonction des priorités | `/triage backlog` |
| Repérer le travail bloqué ou oublié | `/triage stale` |
| Capturer une idée ou un bug depuis n'importe où | `/idea …`, `/bug …` |
| Faire évaluer une idée | `/assess #12` (ou laissez `/work ideas` la prendre) |
| Décider (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Approuver une spec (G2) | Lisez-la (liée dans l'issue), puis : « spec de #12 approuvée » |
| Tester une modification, puis la livrer ou la renvoyer (G4, G5) | `/test` (ou `/test #12`), puis `pass` → `ship`, ou dites ce qui ne va pas |
| Clore quelque chose qui a été fusionné autrement | `/release #12` |
| Urgence | `/override #12 "<reason>"` |

**Comment fonctionne `/triage`.** L'agent lit `PRODUCT.md` et les éléments, puis vous montre un seul tableau : flux proposé, priorité, étape suivante et une courte raison pour chacun. Répondez `ok` pour tout appliquer, ou avec des changements (`#14 Low, #9 park until Q3`). Il ne change rien tant que vous n'avez pas répondu, applique exactement ce que vous avez confirmé et commente chaque élément pour que la raison reste consignée. Il n'approuve jamais d'idées à votre place ; pour cela, il vous renvoie vers `/decide`.

**Des questions qui valent la peine d'être posées à votre agent :**
- « Qu'est-ce qui m'attend ? »
- « Qu'est-ce que les agents ont terminé depuis hier, et qu'est-ce qui est bloqué ? »
- « Quels éléments Ready ne correspondent pas à nos priorités actuelles ? »
- « #12 est trop gros. Proposez un découpage en morceaux de taille S. »
- « Comparez #12 et #15 : lequel doit passer en premier, et pourquoi ? »
- « Rédigez de nouvelles priorités actuelles pour PRODUCT.md à partir de ce que nous avons livré et de ce qui est dans le backlog. »

Les suggestions de l'agent sont des brouillons, et les décisions vous appartiennent. Quand `/bug` enregistre un bug, il remplit une priorité suggérée ; vous la confirmez ou la changez au moment du tri.

---

## 7. Le faire directement dans GitHub Projects

Tout ce qui précède peut se faire à la main sur le tableau. Les vues enregistrées (créées avec `haam.py github-project`) sont votre espace de travail :

| Vue | À utiliser pour |
|---|---|
| **Triage** (statut : Triage) | Votre boîte de réception quotidienne |
| **Epics** (label : epic) | Chaque fonctionnalité et l'avancement de ses sous-issues |
| **Waiting on me** (statut : Decision, UAT) | Décisions et tests |
| **Agent queue** (statut : Ready, sans assignation) | Ce que les agents vont prendre ensuite, par priorité |
| **Bugs** | Tous les bugs ouverts par priorité |
| **Ideas inbox** | Les idées en cours de tri ou d'évaluation |
| **Board** | Tout le flux, regroupé par statut |

| Tâche | Sur le tableau |
|---|---|
| Trier un élément | Ouvrez-le. Renseignez **Priority** et **Status** ; corrigez le label de flux dans la barre latérale de l'issue ; commentez votre raison |
| Mettre de côté | Statut **Parked**, et un commentaire : « à revoir quand… » |
| Rejeter ou marquer comme doublon | Statut **Canceled**, puis clôturez l'issue comme *not planned* ou *duplicate* |
| Approuver une idée (G1) | Statut **Backlog** ; remplacez le label `stream:idea` par `stream:feature` ; renseignez Priority ; commentez « Approved » |
| Approuver une spec (G2) | Commentez « spec approved » dans l'issue ; puis statut **Ready** et label `agent-ready` |
| Regrouper des issues en epic | Créez une issue avec le label `epic` ; ajoutez les autres comme ses sous-issues |
| Reclasser beaucoup d'éléments | Disposition en tableau, groupée ou triée par Priority ; modifiez les cellules (vous pouvez copier une valeur et la coller dans plusieurs cellules sélectionnées) |

Laissez ceci aux skills : la réservation (**In Progress**) est le travail des agents. Tester et livrer est plus simple avec `/test` ; à la main, cela donne : ajoutez le label `uat-passed` à la PR (cela débloque la fusion), fusionnez-la, approuvez le déploiement (Actions → l'exécution → Review deployments), puis passez l'issue en **Done** et clôturez-la. Si le test a échoué, commentez dans l'issue ce qui ne va pas, ajoutez le label `uat-failed`, repassez-la en **Ready** et retirez l'assignation.

---

## 8. Le faire directement dans Linear

| Tâche | Dans Linear |
|---|---|
| Trier | Utilisez la boîte de réception **Triage** de l'équipe. Vous pouvez accepter, refuser, marquer comme doublon ou reporter. Après avoir accepté, **fixez vous-même le statut HAAM** (Ready pour un bug, Discovery pour une idée à évaluer), car accepter place l'élément dans le statut par défaut de l'équipe. Fixez la priorité |
| Mettre de côté ou rejeter | Statut **Parked** ou **Canceled**, avec un commentaire |
| Regrouper des issues en epic | Créez une issue avec le label `epic` ; définissez-la comme parent des issues liées |
| Approuver une idée (G1) | Statut **Backlog**, remplacez le label `stream:idea` par `stream:feature`, fixez la priorité, commentez |
| Approuver une spec (G2) | Commentez « spec approved » dans l'issue ; puis statut **Ready** et label `agent-ready` |
| Reclasser | Les vues de `docs/setup/LINEAR-SETUP.md` §7, triées par priorité ; le menu de commandes (Cmd/Ctrl+K) change rapidement la priorité ou le statut |

Comme sur GitHub, les agents suivent le champ de priorité, pas l'ordre manuel d'une liste.

---

## 9. Travailler avec d'autres personnes

- **Un seul product owner par produit** fixe les priorités et fait passer les portes. Tous les autres proposent : `/idea`, `/bug`, commentaires.
- Demandez à vos collègues de suggérer une priorité quand ils signalent quelque chose. Vous la confirmez au moment du tri.
- **Les désaccords se règlent dans l'issue,** pas dans des conversations privées. Le product owner décide et explique pourquoi dans un commentaire.
- Si vous êtes absent, désignez un approbateur suppléant (`haam.py config --backup-approvers`) et dites-lui quels éléments peuvent avancer sans vous.

---

## 10. Limiter les coûts de GitHub Actions

Chaque pull request fait tourner la CI et deux revues IA sur les machines de GitHub, et les dépôts privés ont un quota mensuel de minutes. Les agents travaillent vite, si bien que le quota peut être épuisé en quelques jours. Ce qui aide le plus, dans l'ordre :
1. **Regardez d'abord :** `python3 tools/haam/haam.py ci-usage` montre quels workflows et quels jobs ont consommé les minutes.
2. **Moins de pull requests :** regroupez les petits éléments d'une epic en une seule (`/work epic #9`), et gardez une limite basse de PR ouvertes (`max_open_prs` dans `haam.config.json`).
3. **Les revues sur votre ordinateur :** `haam.py settings --set review=local --apply --human` (ou `/haam-settings`). Les revues IA utilisent alors votre plan Claude au lieu des minutes ; les zones protégées (`human-review`) sont toujours relues sur GitHub. Le compromis : sur GitHub, le résultat de la revue est infalsifiable ; en local, il ne l'est pas. Les revues tournent dans de nouvelles sessions en lecture seule avec les instructions de `main`, mais c'est l'agent qui a construit la modification qui les lance, et tout ce qui utilise votre connexion pourrait publier un résultat positif. Pour plus de séparation, lancez vous-même `haam.py review <ID>` depuis votre propre conversation.
4. **Votre propre runner :** `haam.py settings --set runner=self-hosted --apply --human` après avoir enregistré une machine qui reste allumée (`docs/setup/GITHUB-SETUP.md` §8).
5. **Demandez une CI plus légère :** si le projet a des parties séparées (par exemple un backend et une application mobile), demandez à un agent de faire en sorte que `make check` ne lance que les parties touchées par une PR.

## 11. Les pièges à éviter

- **Tout est High.** Alors rien ne l'est. Rétrogradez jusqu'à ce qu'environ un élément sur cinq soit High ou Urgent.
- **Plus d'agents que vous ne pouvez en tester.** Le travail s'accumule en UAT et devient obsolète. Moins d'éléments, et plus petits, avancent plus vite.
- **« Construisez-le, c'est tout » dans une conversation.** Créez d'abord l'issue (`/bug`, `/idea`) : cela prend une minute et conserve l'historique, la priorité et la réservation.
- **Approuver une spec sans lire les critères d'acceptation.** C'est ce que l'agent construit et ce sur quoi vous testez. Lisez-les.
- **Des priorités seulement dans votre tête.** Si elles ne sont pas dans `PRODUCT.md` et dans l'outil de suivi, les agents ne peuvent pas les suivre.
- **Construire des fragments sans vue d'ensemble.** Si plusieurs issues forment en réalité une seule fonctionnalité, regroupez-les en une epic et mettez-la en forme avant que quiconque ne spécifie les morceaux.
- **Des epics qui ne finissent jamais.** Si une epic est ouverte depuis des mois, détachez ce qui est fait et clôturez-la.
- **Laisser Triage « pour plus tard ».** La boîte de réception grossit, et les bugs urgents s'y cachent.

---

## 12. Listes de contrôle

**Tous les jours**
- [ ] Tout ce qui est en UAT a été testé avec `/test`
- [ ] Boîte de réception Triage vide
- [ ] Chaque bug urgent a un agent dessus
- [ ] Questions des agents répondues

**Toutes les semaines**
- [ ] Issues éparses regroupées en epics ; epic prioritaire mise en forme
- [ ] File Decision tranchée
- [ ] Specs approuvées ou commentées
- [ ] Ready et Backlog reclassés
- [ ] Travail en souffrance relancé (`/triage stale`)
- [ ] Éléments Parked revus
- [ ] Suivis de dérogation clos
- [ ] Une amélioration du processus consignée

**Tous les mois**
- [ ] Priorités actuelles de `PRODUCT.md` réécrites
- [ ] Anciens éléments Low mis en Parked
