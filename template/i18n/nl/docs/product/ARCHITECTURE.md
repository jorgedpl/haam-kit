# Architectuurkaart

> Agents lezen dit aan het begin van elke sessie (geïmporteerd door `AGENTS.md`). Het is een **kaart**, geen volledige documentatie: genoeg voor een nieuwe agent om in twee minuten de weg te vinden.
> Agents houden hem actueel: als je PR de structuur verandert of je een valkuil ontdekt, werk dit bestand dan in dezelfde PR bij.
>
> **Eerste setup:** vraag je coding agent: *"Verken deze repository en vul docs/product/ARCHITECTURE.md in volgens de sectiekoppen. Houd het onder de 150 regels."* Review het daarna zelf.

## Stack
- Taal / framework: `TODO`
- Database: `TODO`
- Hosting / deploydoel: `TODO`
- Belangrijkste externe diensten: `TODO` (API's, e-mail, betalingen, auth-providers…)

## Opbouw van de repository
```
TODO: top-level folders and what lives in each
```

## Belangrijkste modules
| Module / pad | Verantwoordelijkheid | Beschermd gebied? |
|---|---|---|
| `TODO` | | |

## Datamodel (belangrijkste entiteiten)
`TODO`

## Omgevingen
| Omgeving | URL | Hoe het gedeployd wordt |
|---|---|---|
| Lokaal | http://localhost:`TODO` | `make dev` |
| Productie | `TODO` | GitHub Actions `deploy.yml`, goedkeuring vereist |

## Configuratie
- Omgevingsvariabelen zijn gedocumenteerd in `.env.example` (commit nooit echte waarden).

## Testen
- Unittests staan in `TODO` en draai je met `make test`.
- Synthetische testfixtures: `TODO` (gebruik nooit echte persoonsgegevens).
- E2E / browser: `TODO`

## Valkuilen
- `TODO`: dingen waar agents of developers al eerder last van hebben gehad.
