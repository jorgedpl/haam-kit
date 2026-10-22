# ADR 0001: De Human-Agent Agile Methodology (HAAM) invoeren

- **Status:** Geaccepteerd
- **Datum:** YYYY-MM-DD
- **Besluitvormers:** Product owner

## Context
Werk aan dit product wordt steeds vaker gedaan door coding agents (Claude Code, Cursor, Codex, Grok en andere). Zonder een gedeeld proces zit de context in losse chats, zijn prioriteiten impliciet, en kan een tweede developer met een eigen Claude-account niet parallel werken. Ook moeten wijzigingen in productie vóór de release door een mens geverifieerd worden, met een manier om in noodgevallen snel te handelen.

## Beslissing
- De tracker (GitHub Projects of Linear, per project gekozen in `haam.config.json`) is het bronsysteem voor werkitems, status en prioriteit. Git is het bronsysteem voor specs, beslissingen, UAT-plannen en code.
- Het werk volgt HAAM zoals beschreven in `docs/process/LIFECYCLE.md`, met vijf gates (`docs/process/GATES.md`).
- Agents, welke tool ook, volgen `AGENTS.md` en de gedeelde skills in `.agents/skills/`.
- De gates G3–G5 worden afgedwongen door GitHub (branchbescherming, verplichte checks, een beschermde environment `production`). G1–G2 worden afgedwongen door afspraken en de status in de tracker.
- Mensen kunnen gates overrulen met een vastgelegde reden en een automatisch vervolgissue.

## Gevolgen
- Iets meer ceremonie voor kleine wijzigingen, gecompenseerd doordat agents het meeste papierwerk doen.
- Iedereen kan elk issue oppakken met alleen de tracker + Git.
- Vereist een tracker (een GitHub Projects-board, of een Linear-workspace met de GitHub-integratie) en GitHub-branchbescherming op `main`.

## Overwogen alternatieven
- **Gewone GitHub Issues, zonder board of statussen:** minder onderdelen, maar niets waaruit agents op volgorde werk kunnen halen, en geen overzicht van waar elk item staat.
- **Jira:** krachtiger, maar zwaarder dan een klein team nodig heeft.
- **Geen formeel proces:** vandaag het snelst, maar schaalt niet naar parallelle agents of een tweede developer.
