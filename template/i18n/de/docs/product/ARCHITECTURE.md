# Architekturkarte

> Agenten lesen das zu Beginn jeder Sitzung (von `AGENTS.md` importiert). Es ist eine **Karte**, keine vollständige Dokumentation: genug, damit sich ein neuer Agent in zwei Minuten zurechtfindet.
> Agenten halten sie aktuell: Ändert dein PR die Struktur oder entdeckst du eine Stolperfalle, aktualisiere diese Datei im selben PR.
>
> **Erste Einrichtung:** Bitte deinen Coding-Agenten: *„Erkunde dieses Repository und fülle docs/product/ARCHITECTURE.md entlang seiner Abschnittsüberschriften aus. Bleib unter 150 Zeilen.“* Prüfe es dann selbst.

## Stack
- Sprache / Framework: `TODO`
- Datenbank: `TODO`
- Hosting / Deploy-Ziel: `TODO`
- Wichtige externe Dienste: `TODO` (APIs, E-Mail, Zahlungen, Auth-Anbieter…)

## Aufbau des Repositorys
```
TODO: top-level folders and what lives in each
```

## Hauptmodule
| Modul / Pfad | Verantwortung | Geschützter Bereich? |
|---|---|---|
| `TODO` | | |

## Datenmodell (wichtige Entitäten)
`TODO`

## Umgebungen
| Umgebung | URL | Wie deployt wird |
|---|---|---|
| Lokal | http://localhost:`TODO` | `make dev` |
| Produktion | `TODO` | GitHub Actions `deploy.yml`, Freigabe erforderlich |

## Konfiguration
- Umgebungsvariablen sind in `.env.example` dokumentiert (committe nie echte Werte).

## Tests
- Unit-Tests liegen in `TODO` und laufen mit `make test`.
- Synthetische Test-Fixtures: `TODO` (nutze nie echte personenbezogene Daten).
- E2E / Browser: `TODO`

## Stolperfallen
- `TODO`: Dinge, an denen sich Agenten oder Developer schon einmal die Finger verbrannt haben.
