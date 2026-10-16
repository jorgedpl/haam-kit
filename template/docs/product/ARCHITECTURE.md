# Architecture map

> Agents read this at the start of every session (imported by `AGENTS.md`). It is a **map**, not full documentation: enough for a new agent to find its way in two minutes.
> Agents keep it current: if your PR changes structure or you discover a gotcha, update this file in the same PR.
>
> **First-time setup:** ask your coding agent: *"Explore this repository and fill in docs/product/ARCHITECTURE.md following its section headings. Keep it under 150 lines."* Then review it yourself.

## Stack
- Language / framework: `TODO`
- Database: `TODO`
- Hosting / deploy target: `TODO`
- Key external services: `TODO` (APIs, email, payments, auth providers…)

## Repository layout
```
TODO: top-level folders and what lives in each
```

## Main modules
| Module / path | Responsibility | Protected area? |
|---|---|---|
| `TODO` | | |

## Data model (key entities)
`TODO`

## Environments
| Env | URL | How it's deployed |
|---|---|---|
| Local | http://localhost:`TODO` | `make dev` |
| Production | `TODO` | GitHub Actions `deploy.yml`, approval required |

## Configuration
- Env vars are documented in `.env.example` (never commit real values).

## Testing
- Unit tests live in `TODO`, run with `make test`.
- Synthetic test fixtures: `TODO` (never use real personal data).
- E2E / browser: `TODO`

## Gotchas
- `TODO`: things that have bitten agents or developers before.
