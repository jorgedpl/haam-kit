# Configuração do Linear (uma vez, ~30 minutos, administrador do workspace)

> **Só se o seu tracker for o Linear** (`"tracker": "linear"` em `haam.config.json`). Usa o GitHub Projects? Rode `python3 tools/haam/haam.py github-project` em vez disto e veja `docs/process/TRACKER.md`.

Isto configura o Linear de acordo com `docs/process/LIFECYCLE.md`. Faça uma vez; depois, todos os desenvolvedores e agentes usam a mesma estrutura.

> **Automatizado:** as seções 1–4 são feitas por `python3 tools/haam/haam.py linear --apply`, que você mesmo roda no seu próprio terminal (ele pede a sua chave de API pessoal do Linear de forma segura e nunca a guarda). Esta página é o equivalente manual, mais as seções 5–9, que só existem no aplicativo web do Linear.

## 1. Time
- Crie (ou reaproveite) um time com o nome do seu produto e um identificador curto (os exemplos usam **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` substitui `APP` em todos os arquivos do HAAM.
- Convide cada pessoa que contribui, com a própria conta do Linear. Os agentes agem como a pessoa que os roda, então não são necessárias licenças separadas para agentes.

## 2. Status do workflow
Configurações do time → **Workflow**. Crie estes status, nesta ordem, na categoria indicada:

| Status | Categoria | Observações |
|---|---|---|
| Triage | Triage | Ative o Triage para o time |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Marque como padrão para as novas issues que não passam pela triagem |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Apague ou renomeie os padrões do Linear (`Todo`, `Duplicate` etc.) para que só estes fiquem. Os nomes precisam ser exatamente iguais; as skills se referem a eles pelo nome.

## 3. Labels
Configurações do time → **Labels**. Crie estas labels (labels simples, sem necessidade de grupo):
- `stream:idea`
- `stream:feature`
- `stream:bug`

E estas labels avulsas:

| Label | Significado | Quem a aplica |
|---|---|---|
| `agent-ready` | Passou pelo G2; os agentes podem construí-la | Agente, só depois que uma pessoa aprova a spec |
| `human-review` | Altera uma área protegida; exige revisão de código humana | Agente ou pessoa |
| `human-only` | Os agentes não devem pegar esta issue | Pessoa |
| `override-followup` | Criada depois de um override de gate | `/override` |
| `epic` | Issue pai que agrupa as sub-issues de uma funcionalidade | `/triage group`, `/epic` ou uma pessoa |
| `uat-failed` | Reprovada no teste da pessoa; os agentes a retrabalham primeiro | `/test`, `/uat-result` |
| `uat:skip` | O product owner decidiu: sem teste da parte dele | `/triage`, ou "spec aprovada, sem UAT" |
| `claimed` | Um chat de agente está avaliando a issue, escrevendo a spec dela ou construindo um protótipo | O agente, enquanto trabalha |
| `mode:prototype` | O product owner decidiu: construir primeiro um protótipo descartável (`/spike`) | `/triage` |
| `mode:epic-build` | O product owner decidiu: um agente líder constrói este epic inteiro | `/decide` |
| `spike-ready` | Um protótipo está pronto para o product owner experimentar | `/spike` |

Opcional: labels de área (`area:onboarding`, `area:billing`, `area:checkout`…) para filtrar o quadro.

## 4. Prioridades
Use a prioridade nativa do Linear (Urgent / High / Medium / Low / No priority). Não são necessários campos personalizados.

## 5. Modelos de issue
Configurações do time → **Templates** → crie três modelos de issue, colando o corpo a partir de:
- **Idea**: `docs/templates/idea.md` · label padrão `stream:idea` · status Triage
- **Bug**: `docs/templates/bug.md` · label padrão `stream:bug` · status Triage
- **Feature**: um corpo curto com um link para a spec · label padrão `stream:feature` · status Backlog

Os próprios agentes os preenchem por meio do `/idea` e do `/bug`; os modelos são para as pessoas que criam issues no aplicativo do Linear.

## 6. Integração com o GitHub
Settings → **Integrations → GitHub** → conecte a organização/o repo.

Depois, nas configurações do time → **Workflow → Pull request automations** (o texto pode variar um pouco):

| Evento do GitHub | Mover a issue para |
|---|---|
| Branch criada / PR em rascunho aberto | In Progress |
| PR pronto para revisão (os agentes abrem rascunhos e os marcam como prontos quando estão completos) | In Review |
| PR pronto para merge | *(sem mudança, os agentes a movem para UAT)* |
| Merge do PR feito | Deploying |

**Formato do nome de branch:** `{issue-identifier}-{issue-title}` (em minúsculas), por exemplo `app-123-bulk-invite-users`. Remova o prefixo com o nome de usuário, para que as branches sejam iguais seja quem for que as crie.

Ative **"link PRs by issue ID in title"** para que os títulos de PR no formato `APP-123: ...` sejam vinculados automaticamente.

## 7. Visualizações (filtros salvos)
Crie estas visualizações do time para que as pessoas vejam o que precisa delas:

| Visualização | Filtro |
|---|---|
| **Triage** | A caixa de entrada Triage nativa do Linear (a caixa de entrada diária do product owner; veja `docs/process/PRODUCT-MANAGER.md` §8) |
| **Waiting on me** | Status em (Decision, UAT), mais as issues em Backlog com um comentário `📝 Spec ready for review` |
| **Agent queue** | Status = Ready, label `agent-ready` ou `stream:bug`, sem pessoa atribuída |
| **Ideas inbox** | Status em (Triage, Discovery), label `stream:idea` |
| **Bugs** | Label `stream:bug`, não Done/Canceled, ordenadas por prioridade |
| **Epics** | Label `epic`, não Done/Canceled (mostrar o progresso das sub-issues) |
| **Overrides to close** | Label `override-followup`, não Done |

## 8. Notificações
Cada pessoa: Settings → Notifications → garanta que você é notificado em **menções** e em **issues atribuídas a você**. O `/uat` menciona o product owner quando algo está pronto para testar.

## 9. Conectar a ferramenta de agente de cada pessoa ao Linear
Cada pessoa faz login uma vez a partir da própria ferramenta (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Passos por ferramenta: `docs/setup/AGENTS-SETUP.md`.
Teste: peça ao agente *"liste as minhas issues abertas no Linear, no time APP"*.

Se você também usa um aplicativo de chat (Claude, ChatGPT…) com um conector do Linear, conecte-o também, para poder capturar ideias pelo celular.
