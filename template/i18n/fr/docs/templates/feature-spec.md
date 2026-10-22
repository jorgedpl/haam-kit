# Spec : <ID> <titre>

- **Issue :** <#123 ou APP-123> · **Évaluation :** docs/assessments/<FILE-ID>-*.md · **ADR :** <liens ou aucun>
- **Statut :** Brouillon / Approuvée · **Approuvée par :** <humain> le YYYY-MM-DD
- **Zones protégées :** aucune / <liste> → `human-review`

## 1. Objectif
<!-- Un paragraphe : ce qui change, pour qui, et pourquoi. -->

## 2. User stories
- En tant que <rôle>, je veux <capacité>, afin de <bénéfice>.

## 3. Critères d'acceptation
<!-- Chaque critère doit être testable. Numérotez-les ; les tests et les étapes d'UAT font référence à ces numéros. -->
**AC1 :** <nom>
- Étant donné …
- Quand …
- Alors …

**AC2 :** …

## 4. Hors périmètre
- 

## 5. Notes de conception
- **Fichiers / modules probablement touchés :** 
- **Modèle de données / migrations :** aucune / <décrire, y compris le remplissage des données existantes et la réversibilité>
- **Configuration / variables d'environnement :** aucune / <noms, et les ajouter à .env.example>
- **API externes :** 
- **Notes d'interface / textes :** 
- **États d'erreur et cas limites :** 

## 6. Plan de test
| AC | Test(s) unitaire(s) / d'intégration | Remarques |
|---|---|---|
| AC1 | `test_…` | |

**Grandes lignes de l'UAT :** <ce sur quoi un humain va cliquer en local>

## 7. Déploiement progressif et retour arrière
- **Feature flag :** aucun / <nom>
- **Déploiement progressif :** 
- **Retour arrière :** <une PR de revert suffit ? des données à nettoyer ?>

## 8. Tranches (en cas de découpage)
| Sous-issue | Périmètre | Dépend de |
|---|---|---|

## 9. Questions ouvertes
1. 
