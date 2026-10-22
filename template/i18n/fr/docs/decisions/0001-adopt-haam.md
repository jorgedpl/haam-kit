# ADR 0001 : adopter la Human-Agent Agile Methodology (HAAM)

- **Statut :** Accepté
- **Date :** YYYY-MM-DD
- **Décideurs :** Product owner

## Contexte
Le travail sur ce produit est de plus en plus fait par des agents de code (Claude Code, Cursor, Codex, Grok et d'autres). Sans processus partagé, le contexte vit dans des conversations individuelles, les priorités sont implicites, et un deuxième développeur avec son propre compte Claude ne peut pas travailler en parallèle. Il nous faut aussi que les modifications en production soient vérifiées par un humain avant la mise en production, avec un moyen d'aller vite en cas d'urgence.

## Décision
- L'outil de suivi (GitHub Projects ou Linear, choisi par projet dans `haam.config.json`) est le système de référence pour les éléments de travail, les statuts et les priorités. Git est le système de référence pour les specs, les décisions, les plans UAT et le code.
- Le travail suit HAAM tel que décrit dans `docs/process/LIFECYCLE.md`, avec cinq portes (`docs/process/GATES.md`).
- Les agents, quel que soit l'outil, suivent `AGENTS.md` et les skills partagés dans `.agents/skills/`.
- Les portes G3–G5 sont imposées par GitHub (protection de branche, vérifications requises, un environnement `production` protégé). G1–G2 sont imposées par convention et par le statut dans l'outil de suivi.
- Les humains peuvent déroger aux portes avec une raison consignée et une issue de suivi automatique.

## Conséquences
- Un peu plus de formalités pour les petites modifications, compensées par le fait que les agents font l'essentiel de la paperasse.
- N'importe qui peut reprendre n'importe quelle issue à partir de l'outil de suivi et de Git, sans rien d'autre.
- Demande un outil de suivi (un tableau GitHub Projects, ou un espace de travail Linear avec son intégration GitHub) et une protection de branche GitHub sur `main`.

## Alternatives envisagées
- **GitHub Issues + Projects uniquement :** moins d'outils, mais un tri, des priorités et des vues de planification plus faibles.
- **Jira :** plus puissant, mais plus lourd que ce dont une petite équipe a besoin.
- **Pas de processus formel :** le plus rapide aujourd'hui, mais ne tient pas à l'échelle avec des agents en parallèle ou un deuxième développeur.
