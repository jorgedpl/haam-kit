## Issue
<!-- GitHub Projects: laat de regel hieronder staan met het issuenummer (gebruik Refs, niet Closes: het issue sluit bij /release). Linear: zet het ID in de PR-titel (APP-123: …). -->
Refs #

## Gebouwd met (Built with)
<!-- Agent-tool en model (bijv. Claude Code / Opus, Cursor / <model>, Codex, Grok Build), of "mens". -->

## Wat en waarom
<!-- 2–4 zinnen. Wat er voor de gebruiker veranderd is, en waarom. -->

## Acceptatiecriteria → tests
| AC | Test(s) | Status |
|---|---|---|
| AC1 | `test_…` | ✅ |

## Hoe te verifiëren
- UAT-plan: `docs/uat/<GH-123 or APP-123>-*.md` (toegevoegd door `/uat`)
- Screenshots / notities:

## Risico
- Geraakte beschermde gebieden: geen / <lijst> (als er een is → label `human-review`)
- Migraties: geen / <beschrijf + rollback>
- Wijzigingen in config / omgeving: geen / <lijst>

## Checklist (G3)
- [ ] `make check` slaagt lokaal
- [ ] Elk acceptatiecriterium heeft een test
- [ ] Geen wijzigingen die er niets mee te maken hebben
- [ ] Docs bijgewerkt (ARCHITECTURE.md, .env.example, …) of niet nodig
- [ ] Geen secrets of echte persoonsgegevens

<!-- Release-gate (G4): deze PR kan alleen gemerged worden met het label `uat-passed`, of `gate-override` plus een commentaar "OVERRIDE: <reason>". PR's met alleen docs zijn uitgezonderd. -->
