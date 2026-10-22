# ADR 0001: Die Human-Agent Agile Methodology (HAAM) einführen

- **Status:** Angenommen
- **Datum:** YYYY-MM-DD
- **Entschieden von:** Product Owner

## Kontext
Die Arbeit an diesem Produkt wird zunehmend von Coding-Agenten erledigt (Claude Code, Cursor, Codex, Grok und andere). Ohne einen gemeinsamen Prozess liegt der Kontext in einzelnen Chats, Prioritäten sind nur implizit, und ein zweiter Developer mit eigenem Claude-Konto kann nicht parallel arbeiten. Außerdem müssen Änderungen an der Produktion vor dem Release von einem Menschen geprüft werden, mit einer Möglichkeit, im Notfall schnell zu handeln.

## Entscheidung
- Der Tracker (GitHub Projects oder Linear, pro Projekt in `haam.config.json` gewählt) ist das maßgebliche System für Arbeitseinträge, Status und Priorität. Git ist das maßgebliche System für Specs, Entscheidungen, UAT-Pläne und Code.
- Die Arbeit folgt HAAM, wie in `docs/process/LIFECYCLE.md` beschrieben, mit fünf Gates (`docs/process/GATES.md`).
- Agenten folgen, egal mit welchem Tool, `AGENTS.md` und den gemeinsamen Skills in `.agents/skills/`.
- Die Gates G3–G5 setzt GitHub durch (Branch-Schutz, erforderliche Checks, ein geschütztes Environment `production`). G1–G2 werden durch Konvention und den Status im Tracker durchgesetzt.
- Menschen können Gates übergehen, mit einer festgehaltenen Begründung und einem automatischen Folge-Issue.

## Konsequenzen
- Etwas mehr Formalität bei kleinen Änderungen, ausgeglichen dadurch, dass Agenten den Großteil des Papierkrams erledigen.
- Jede Person kann jedes Issue allein aus Tracker + Git übernehmen.
- Erfordert einen Tracker (ein GitHub-Projects-Board oder einen Linear-Workspace mit seiner GitHub-Integration) und GitHub-Branch-Schutz auf `main`.

## Erwogene Alternativen
- **Einfache GitHub Issues, ohne Board oder Status:** weniger bewegliche Teile, aber nichts, woraus Agenten sich Arbeit in der richtigen Reihenfolge holen können, und kein Nachweis, wo jeder Eintrag gerade steht.
- **Jira:** leistungsfähiger, aber schwerfälliger, als ein kleines Team es braucht.
- **Kein formaler Prozess:** heute am schnellsten, skaliert aber nicht auf parallele Agenten oder einen zweiten Developer.
