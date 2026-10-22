# ADR 0001: Adotar a Human-Agent Agile Methodology (HAAM)

- **Status:** Aceita
- **Data:** YYYY-MM-DD
- **Quem decidiu:** Product owner

## Contexto
O trabalho neste produto é feito cada vez mais por agentes de programação (Claude Code, Cursor, Codex, Grok e outros). Sem um processo compartilhado, o contexto fica em chats individuais, as prioridades ficam implícitas, e um segundo desenvolvedor com a própria conta do Claude não consegue trabalhar em paralelo. Também precisamos que as mudanças em produção sejam verificadas por uma pessoa antes da release, com uma maneira de agir rápido em emergências.

## Decisão
- O tracker (GitHub Projects ou Linear, escolhido para cada projeto em `haam.config.json`) é o sistema de registro dos itens de trabalho, dos status e das prioridades. O Git é o sistema de registro das specs, das decisões, dos planos de UAT e do código.
- O trabalho segue o HAAM, conforme descrito em `docs/process/LIFECYCLE.md`, com cinco gates (`docs/process/GATES.md`).
- Os agentes, seja qual for a ferramenta, seguem o `AGENTS.md` e as skills compartilhadas em `.agents/skills/`.
- Os gates G3–G5 são garantidos pelo GitHub (proteção de branch, verificações obrigatórias, um ambiente `production` protegido). Os gates G1–G2 são garantidos por convenção e pelo status no tracker.
- As pessoas podem contornar os gates com um motivo registrado e uma issue de acompanhamento automática.

## Consequências
- Um pouco mais de cerimônia para mudanças pequenas, compensada pelos agentes, que fazem a maior parte da papelada.
- Qualquer pessoa pode pegar qualquer issue só com o tracker + o Git.
- Exige um tracker (um quadro do GitHub Projects, ou um workspace do Linear com a integração com o GitHub) e a proteção de branch do GitHub na `main`.

## Alternativas consideradas
- **Só GitHub Issues + Projects:** menos ferramentas, mas triagem, prioridades e visualizações de planejamento mais fracas.
- **Jira:** mais poderoso, mas mais pesado do que uma equipe pequena precisa.
- **Nenhum processo formal:** o mais rápido hoje, mas não escala para agentes em paralelo nem para um segundo desenvolvedor.
