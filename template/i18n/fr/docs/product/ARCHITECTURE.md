# Carte de l'architecture

> Les agents lisent ce fichier au début de chaque session (importé par `AGENTS.md`). C'est une **carte**, pas une documentation complète : juste assez pour qu'un nouvel agent s'y retrouve en deux minutes.
> Les agents la tiennent à jour : si votre PR modifie la structure ou si vous découvrez un piège, mettez ce fichier à jour dans la même PR.
>
> **Première configuration :** demandez à votre agent de code : *« Explorez ce dépôt et remplissez docs/product/ARCHITECTURE.md en suivant ses titres de section. Restez sous 150 lignes. »* Puis relisez-le vous-même.

## Stack
- Langage / framework : `TODO`
- Base de données : `TODO`
- Hébergement / cible de déploiement : `TODO`
- Principaux services externes : `TODO` (API, e-mail, paiements, fournisseurs d'authentification…)

## Organisation du dépôt
```
TODO: top-level folders and what lives in each
```

## Modules principaux
| Module / chemin | Responsabilité | Zone protégée ? |
|---|---|---|
| `TODO` | | |

## Modèle de données (entités clés)
`TODO`

## Environnements
| Env | URL | Comment il est déployé |
|---|---|---|
| Local | http://localhost:`TODO` | `make dev` |
| Production | `TODO` | GitHub Actions `deploy.yml`, approbation requise |

## Configuration
- Les variables d'environnement sont documentées dans `.env.example` (ne committez jamais de vraies valeurs).

## Tests
- Les tests unitaires se trouvent dans `TODO` et se lancent avec `make test`.
- Fixtures de test synthétiques : `TODO` (n'utilisez jamais de vraies données personnelles).
- E2E / navigateur : `TODO`

## Pièges
- `TODO` : les choses qui ont déjà piégé des agents ou des développeurs.
