## Issue
<!-- GitHub Projects: Behalte die Zeile unten mit der Issue-Nummer (nutze Refs, nicht Closes: Das Issue wird bei /release geschlossen). Linear: Schreib die ID in den PR-Titel (APP-123: …). -->
Refs #

## Erstellt mit (Built with)
<!-- Agenten-Tool und Modell (z. B. Claude Code / Opus, Cursor / <model>, Codex, Grok Build) oder „Mensch“. -->

## Was und warum
<!-- 2–4 Sätze. Was sich für den Nutzer geändert hat, und warum. -->

## Akzeptanzkriterien → Tests
| AC | Test(s) | Status |
|---|---|---|
| AC1 | `test_…` | ✅ |

## So prüfst du es
- UAT-Plan: `docs/uat/<GH-123 or APP-123>-*.md` (von `/uat` hinzugefügt)
- Screenshots / Notizen:

## Risiko
- Berührte geschützte Bereiche: keine / <Liste> (falls ja → Label `human-review`)
- Migrationen: keine / <beschreiben + Rollback>
- Änderungen an Konfiguration / Umgebung: keine / <Liste>

## Checkliste (G3)
- [ ] `make check` läuft lokal durch
- [ ] Jedes Akzeptanzkriterium hat einen Test
- [ ] Keine fremden Änderungen
- [ ] Doku aktualisiert (ARCHITECTURE.md, .env.example, …) oder nicht nötig
- [ ] Keine Secrets oder echten personenbezogenen Daten

<!-- Release-Gate (G4): Dieser PR kann nur mit dem Label `uat-passed` gemergt werden, oder mit `gate-override` plus einem Kommentar „OVERRIDE: <reason>“. Reine Doku-PRs sind ausgenommen. -->
