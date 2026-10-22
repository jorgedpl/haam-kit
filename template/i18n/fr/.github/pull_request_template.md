## Issue
<!-- GitHub Projects : gardez la ligne ci-dessous avec le numéro de l'issue (utilisez Refs, pas Closes : l'issue est close au moment de /release). Linear : mettez l'identifiant dans le titre de la PR (APP-123: …). -->
Refs #

## Réalisé avec (Built with)
<!-- Outil d'agent et modèle (par exemple Claude Code / Opus, Cursor / <model>, Codex, Grok Build), ou « humain ». -->

## Quoi et pourquoi
<!-- 2 à 4 phrases. Ce qui a changé pour l'utilisateur, et pourquoi. -->

## Critères d'acceptation → tests
| AC | Test(s) | Statut |
|---|---|---|
| AC1 | `test_…` | ✅ |

## Comment vérifier
- Plan UAT : `docs/uat/<GH-123 or APP-123>-*.md` (ajouté par `/uat`)
- Captures d'écran / remarques :

## Risques
- Zones protégées touchées : aucune / <liste> (s'il y en a → label `human-review`)
- Migrations : aucune / <décrire + retour arrière>
- Changements de configuration / d'environnement : aucun / <liste>

## Liste de contrôle (G3)
- [ ] `make check` passe en local
- [ ] Chaque critère d'acceptation a un test
- [ ] Aucune modification sans rapport
- [ ] Documentation mise à jour (ARCHITECTURE.md, .env.example, …) ou pas nécessaire
- [ ] Aucun secret ni donnée personnelle réelle

<!-- Porte de release (G4) : cette PR ne peut être fusionnée qu'avec le label `uat-passed`, ou `gate-override` plus un commentaire « OVERRIDE: <reason> ». Les PR de documentation seule en sont dispensées. -->
