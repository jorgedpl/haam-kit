# Gates e overrides

Cinco gates ficam entre uma ideia e a produção. Cada um tem um responsável claro, uma checklist e, sempre que possível, um ponto de controle automático, para que a regra não dependa de alguém se lembrar dela.

| Gate | Entre | Responsável | Garantido por |
|---|---|---|---|
| **G1 Decisão** | Discovery → Backlog | Pessoa (PO) | Status no tracker: só pessoas rodam `/decide` |
| **G2 Ready** | Backlog → Ready | Uma pessoa aprova a spec | Label `agent-ready`; os agentes só constroem issues `agent-ready` |
| **G3 Verificado** | In Progress → UAT | Verificações automáticas + agente revisor independente (+ uma pessoa para áreas protegidas) | Verificações obrigatórias `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Aceito** | UAT → merge | Pessoa que testa | Verificação obrigatória `release-gate` (exige a label `uat-passed` ou `gate-override` no PR) |
| **G5 Lançado** | merge → produção | Pessoa (PO) | Ambiente `production` do GitHub com revisor obrigatório |

---

## Checklist do G1 Decisão

A avaliação (ou, para uma ideia construída como protótipo, as notas do protótipo geradas por `/spike`) deve conter:
- [ ] Descrição do problema e para quem ele é
- [ ] Estimativa de valor com evidências (ou um "ainda sem evidências" explícito)
- [ ] Tamanho do esforço, com justificativa baseada no código
- [ ] Riscos: segurança, proteção de dados (por exemplo, LGPD ou RGPD), regulatórios, operacionais
- [ ] Pelo menos duas opções, mais "não fazer nada"
- [ ] Uma recomendação

A pessoa responde com uma destas opções: **aprovar** (com prioridade), **estacionar** (com um gatilho para rever), **rejeitar** (com o motivo). No caso de um protótipo, ela o experimenta primeiro (`/test`), para que a decisão se baseie no uso e não só na leitura.

## G2 Definition of Ready

Uma issue só pode receber `agent-ready` quando:
- [ ] A spec existe em `docs/specs/` e está vinculada na issue
- [ ] Os critérios de aceitação estão escritos no formato Dado / Quando / Então e cada um pode ser testado
- [ ] O escopo e o que está **fora do escopo** estão explícitos
- [ ] Os arquivos/módulos que provavelmente serão alterados estão listados
- [ ] O impacto em dados, migrações e configuração está descrito (ou "nenhum")
- [ ] O plano de testes unitários e um esboço do UAT estão incluídos
- [ ] Tamanho ≤ 1 dia de trabalho de agente (~400 linhas alteradas); caso contrário, dividir em sub-issues
- [ ] As áreas protegidas afetadas estão sinalizadas (label `human-review` adicionada)
- [ ] A prioridade está definida
- [ ] Uma pessoa aprovou a spec

## G3 Verificado (Definition of Done do código)

- [ ] Cada critério de aceitação tem pelo menos um teste automatizado
- [ ] `make check` passa localmente e no CI (lint, tipos, testes unitários, build)
- [ ] Nenhuma mudança não relacionada no diff
- [ ] A documentação afetada pela mudança está atualizada (`ARCHITECTURE.md`, documentação da API, lista de variáveis de ambiente)
- [ ] Nenhum segredo e nenhum dado pessoal real no código, nos testes ou nas fixtures
- [ ] A descrição do PR segue o modelo e vincula a issue (`Refs #123` no GitHub Projects, o ID no título no Linear)
- [ ] Verificação `secrets` verde: nenhuma chave, token ou senha em nenhum commit do PR
- [ ] Verificação `dependencies` verde: nenhuma vulnerabilidade conhecida de severidade alta/crítica
- [ ] `ai-review` verde: o agente revisor independente não encontrou problemas bloqueantes
- [ ] `security-review` verde: a revisão de segurança do Claude não encontrou vulnerabilidades
- [ ] Revisão de código humana feita, se a label `human-review` estiver presente

### Como funciona a revisão de código

A revisão é feita em camadas para que **nenhum agente revise o próprio trabalho** e para que **os segredos sejam pegos por ferramentas determinísticas, não por julgamento**.

| Camada | Quando | O quê | Quem / o que faz |
|---|---|---|---|
| 1. Proteção local contra segredos | Antes de cada commit | Bloqueia commits que contêm chaves/tokens | gitleaks pelo hook pre-commit do git (todo mundo, qualquer ferramenta), mais hooks da ferramenta do agente onde houver suporte (Claude Code; Grok) |
| 2. Autoverificação | Antes de abrir um PR | `make check` + `/security-review` sobre as próprias mudanças | O agente que constrói |
| 3. CI determinístico | A cada push no PR | Testes, lint, tipos, varredura de segredos em cada commit, auditoria de dependências | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Revisão independente por IA | A cada push no PR (exceto rascunhos ou PRs só de documentação) | Conformidade com a spec, testes honestos, correção, regras do projeto; vulnerabilidades de segurança | Um Claude separado no GitHub Actions, que nunca viu o código ser escrito (`ai-review`, `security-review`) |
| 5. Revisão humana | PRs com a label `human-review` | Áreas protegidas: lógica central, autenticação, pagamentos, dados pessoais, migrações, infraestrutura | Product owner ou um desenvolvedor designado |
| 6. Aceitação humana | Todo PR de código | O comportamento funciona de verdade (UAT do G4) | Product owner |

**Regras do ciclo de revisão**
- O agente que constrói lê o comentário do revisor, corrige cada item **Blocking** e faz push; as revisões rodam de novo automaticamente.
- Se o agente que constrói achar que um apontamento está errado, ele responde no PR explicando por quê e pergunta à pessoa. Ele nunca discute em círculos: **depois de duas rodadas de revisão** que ainda falham, ele para e passa a vez para a pessoa.
- Só uma pessoa pode anular uma revisão por IA, com a label `ai-review-overruled` no PR. Isso fica registrado no PR.
- Os revisores de IA não podem aprovar nem fazer merge. Eles só podem bloquear.

### Se um segredo chegar ao GitHub
1. **Revogue e troque o segredo imediatamente** junto ao provedor. Considere que ele foi comprometido; removê-lo do código não desfaz o vazamento.
2. Remova-o do código; use uma variável de ambiente documentada em `.env.example`.
3. Um administrador do repo reescreve o histórico da branch antes do merge (um novo commit não basta).
4. Registre um `/bug` com prioridade Urgent para documentar o que aconteceu e o que foi trocado (nunca inclua o segredo em si).

**As configurações do product owner mudam a forma como o G3 roda, não quem decide** (`/haam-settings`):
- `ci`: em todo PR, local (`ci-local`, publicado por `haam.py local-ci` no computador do product owner) ou desligado.
- `review`: GitHub, local, só áreas protegidas ou desligado.
- `nightly`.

As verificações obrigatórias seguem as configurações (`settings --apply`). A varredura de segredos sempre roda.

## G4 Aceito (UAT)

No fluxo padrão test-first, o G4 vem antes do G3: o product owner testa a branch que o agente enviou antes de existir um PR, e o G3 então verifica exatamente o commit que ele aprovou (`haam.py publish`, depois `ship`, que recusa qualquer outra coisa).

**Via sem UAT:** nesse caso, o G4 é decidido de antemão. Quando o product owner marca uma issue com `uat:skip` (no `/triage`, ou com "spec aprovada, sem UAT"), o agente abre o PR com a mesma label, e o `release-gate` passa quando todas as issues do PR têm essa label (GitHub Projects: o gate lê as issues; Linear: ele confia na label do PR). Nunca quando o PR altera uma área protegida: o gate compara os arquivos alterados com `protected_paths` em `haam.config.json` na `main` (por padrão, a configuração dos agentes e do CI, mais as áreas do próprio projeto), adiciona `human-review` e mantém a via fechada, digam o que disserem as labels. Por isso, uma atualização do kit nunca usa essa via: ela altera a configuração dos agentes, e você mesmo a revisa e a coloca em produção. O G3 continua valendo por completo, e o auto-merge (exige `HAAM_PROJECT_TOKEN`) só faz merge quando todas as verificações obrigatórias passam. Não há auto-merge no Linear, nem quando o CI ou alguma das revisões por IA roda em outro lugar que não seja o GitHub, em todo PR (o auto-merge exige `ci: every-pr` e `review: github`): resultados locais não são à prova de adulteração e verificações reduzidas não bastam sozinhas, então o product owner coloca em produção esses PRs da via (`ship`), o que continua sendo uma única decisão para muitos. Só a decisão de uma pessoa adiciona `uat:skip` a uma issue (`issue create` e `issue label` recusam sem `--human`).

- [ ] O plano de UAT existe em `docs/uat/`, com passos numerados e resultados esperados
- [ ] Uma pessoa o executou localmente na branch (test-first: a branch enviada pelo agente, antes de qualquer PR; checks-first: a branch do PR)
- [ ] Todos os passos passaram, ou as falhas estão registradas e aceitas como issues de acompanhamento
- [ ] A aprovação da pessoa (`/test` ou `/uat-result <ID> pass`) adiciona a label `uat-passed` ao PR (test-first: `publish` também a registra no commit testado como o status `uat`)
- [ ] A aprovação cobre o código que entra: um push depois dela remove `uat-passed` (`gates.yml`), a não ser que o novo head seja o commit testado; `ship` só faz merge desse commit

## G5 Lançado

- [ ] PR com merge na `main` feito por uma pessoa, ou por `haam.py ship --human` depois que a pessoa disse `ship`
- [ ] Deploy para produção aprovado (ambiente `production`): no GitHub, ou pelo `ship` com a palavra da pessoa
- [ ] Smoke check pós-deploy aprovado (`make smoke`, se definido)
- [ ] A issue está marcada como Done (`ship`, ou `/release` para mudanças que entraram de outra forma); a nota de release em `docs/changes/` foi junto com ela

---

## Overrides

Às vezes a produção está pegando fogo ou um prazo não pode esperar. Os overrides existem para isso e são **exclusivos de pessoas**.

### Nível 1: pular o UAT (o mais comum)
Use quando a correção é urgente e está verificada por testes, mas não há tempo para um ciclo completo de UAT.

1. A pessoa roda `/override <ID> "<reason>"` (para um PR sem issue: `/override PR <number> "<reason>"`), ou comenta manualmente `OVERRIDE: <reason>` no PR (o comentário deve começar com `OVERRIDE:`) e adiciona a label `gate-override` ao PR.
2. A verificação `release-gate` passa por causa da label de override.
3. O CI (verificação `ci`) **ainda precisa passar**.
4. Quando o PR tem uma issue, o agente cria uma issue de acompanhamento no tracker: `Post-override UAT for <ID>` (prioridade High, label `stream:bug`, `override-followup`), para que a verificação pulada aconteça mesmo assim, depois.

### Nível 2: bypass de emergência (raro)
Use somente quando o próprio CI estiver quebrado ou bloqueando uma correção em produção.

1. Um administrador do repositório faz o merge com "bypass branch protections" no GitHub.
2. O administrador comenta `EMERGENCY BYPASS: <reason>` no PR.
3. Uma issue de acompanhamento é criada como acima, mais uma segunda para corrigir o que bloqueou o CI.

### Regras de override
- Os agentes **nunca** adicionam `gate-override`, nunca contornam as proteções e nunca sugerem um override, a não ser que a pessoa levante o assunto primeiro.
- Todo override precisa ter um motivo por escrito no PR.
- Os overrides são revisados na revisão semanal do backlog: filtre o tracker pela label `override-followup`.
