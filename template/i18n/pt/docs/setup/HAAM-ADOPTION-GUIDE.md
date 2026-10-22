# Human-Agent Agile Methodology (HAAM)
## Guia de adoção para o administrador do projeto

O HAAM é uma forma de construir software em que **os humanos decidem e os agentes executam**. Todo trabalho vai da ideia à produção passando pelas mesmas etapas, com gates humanos nos pontos que importam. Tudo fica no **Git** (conhecimento e código) e no **tracker** (trabalho e status): um quadro do **GitHub Projects** (gratuito) ou o **Linear**. As pessoas podem usar agentes de programação diferentes (Claude Code, Cursor, Codex, Grok, Gemini, Copilot), com as próprias contas, e ainda assim trabalhar em paralelo.

Este guia aplica o HAAM a um repositório existente em **seis fases, cerca de meio dia no total**. Você pode parar depois de qualquer fase e já terá algo útil.

---

## Obter o kit

O kit é a pasta `template/` de https://github.com/jorgedpl/haam-kit. Use sempre uma versão publicada:
```bash
git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
ou baixe o zip na página de Releases. A seguir, `<path-to-kit>` significa essa pasta `template/`.

## O caminho rápido: deixe o seu agente fazer

Coloque o kit em algum lugar fora do seu projeto, abra o seu agente de programação **na pasta raiz do seu projeto** e diga:

> Leia `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` e siga as instruções para configurar o HAAM neste repositório. O kit está em `<path-to-kit>`.

O agente conduz a ferramenta de configuração (`tools/haam/haam.py`) por todas as fases abaixo. Ele faz algumas perguntas, mostra cada mudança antes de fazê-la e entrega a você os poucos passos que precisam das suas senhas ou chaves para rodar no seu próprio terminal. Use o resto deste guia para entender o que ele está fazendo, ou para fazer tudo à mão.

### Quem faz o quê durante a configuração

| Marcado como | Significa |
|---|---|
| `[agent]` | O seu agente de programação faz (ou você, se estiver fazendo à mão) |
| `[YOU, in your terminal]` | Você mesmo roda o comando: ele envolve um segredo (chave de API, login) que nunca deve passar pelo chat de um agente |
| `[YOU, in the browser]` | Uma configuração que o GitHub ou o Linear só oferecem no aplicativo web |

---

## O que você recebe

```
START-HERE.md                 Kit entry point (not copied into your repo)
AGENTS.md                     Rules every agent reads, whatever the tool
CLAUDE.md                     Pointer to AGENTS.md for Claude Code
haam.config.json              Project settings for the setup tool (created by `config`; no secrets)
haam.lock.json                Installed kit version and file fingerprints (used by `update`)
docs/changes/                 One release note per shipped change (added by /uat)
Makefile                      Command contract: setup, hooks, dev, test, check, audit, secrets, smoke, deploy
tools/haam/haam.py            Setup tool: install, config, agents, github, github-project, linear, issue, worktree, invite, dev, doctor
scripts/scan-secrets.sh       Secret scan (gitleaks) shared by all commit hooks
.githooks/pre-commit          Blocks commits containing secrets (any human, any agent using git)
.agents/skills/               One skill per stage, shared by all agent tools
.worktreeinclude              Local files (like .env) to copy into each agent's worktree
.claude/                      Claude Code: settings (guard-rails), hooks, skills link
.cursor/mcp.json              Cursor: Linear connection (Linear projects)
.grok/skills                  Grok Build: skills link
.gemini/settings.json         Gemini CLI: read AGENTS.md
.mcp.json                     Linear connection (Claude Code, Grok; Linear projects)
.github/
  pull_request_template.md    Includes "Built with" (agent tool and model)
  workflows/ci.yml            Gate G3: tests on every PR
  workflows/security.yml      Gate G3: secret scan of every commit + dependency audit
  workflows/review.yml        Gate G3: independent AI reviewers (spec/quality + security)
  workflows/tracker-sync.yml  Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/             Idea and bug forms (GitHub Projects)
  workflows/gates.yml         Gate G4: blocks merge until UAT passed or overridden
  workflows/deploy.yml        Gate G5: production deploy waits for human approval
  review/REVIEWER.md          Instructions for the reviewer agent
  dependabot.yml              Dependency update PRs
docs/
  process/LIFECYCLE.md        The methodology: streams, stages, statuses, roles
  process/GATES.md            Gate checklists, code review, overrides
  process/TRACKER.md          How each tracker operation works on GitHub Projects and on Linear
  product/PRODUCT.md          Your product context (you confirm it)
  product/ARCHITECTURE.md     Map of your codebase (the agent drafts it)
  setup/HAAM-ADOPTION-GUIDE.md  This guide
  setup/DECISIONS.md          Every choice to make (accounts and plan, tracker, settings, limits, what to protect), with recommendations
  setup/AGENTS-SETUP.md       Per-tool setup: Claude Code, Cursor, Codex, Grok, Gemini, Copilot
  setup/LINEAR-SETUP.md       Linear configuration in detail
  setup/GITHUB-SETUP.md       GitHub configuration in detail
  ONBOARDING.md               Guide for new developers
  templates/                  idea, bug, assessment, feature-spec, uat-plan, adr
  decisions/0001-adopt-haam.md
  assessments/ specs/ uat/    Filled in automatically as work flows
```

### O ciclo de vida em uma imagem

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### Os comandos

Escritos aqui como `/name` (Claude Code, Cursor, Grok). No Codex, use `$name`. Em qualquer outra ferramenta: *"siga `.agents/skills/<name>/SKILL.md`"*.

| Comando | Etapa | Quem |
|---|---|---|
| `/idea <text>` | Capturar uma ideia | Qualquer pessoa |
| `/bug <text>` | Relatar um problema | Qualquer pessoa |
| `/assess APP-12` | Avaliar valor, esforço, risco, viabilidade | Agente |
| `/triage` | Fazer a triagem da caixa de entrada, agrupar issues em epics (`group`), reordenar (`backlog`), cobrar o trabalho parado (`stale`) | Só pessoas |
| `/epic APP-9` | Definir um epic: briefing, perguntas para você, limpeza das issues dele | Só pessoas |
| `/decide APP-12 approve` | Gate G1 | Só pessoas |
| `/spec APP-12` | Escrever uma spec pronta para construção | Agente |
| `/work bugs` | Iniciar um agente em uma nova janela de chat: worktree próprio e depois `/next` | Qualquer pessoa |
| `/next` | Pegar o próximo item entre bugs, funcionalidades e ideias | Agente |
| `/build APP-12` | Implementar com testes unitários, abrir um PR | Agente |
| `/uat APP-12` | Escrever o seu plano de teste local | Agente |
| `/test` | Testar uma mudança e depois `pass` → `ship`, ou dizer o que está errado (G4 e G5) | Só pessoas |
| `/uat-result APP-12 pass` | Registrar só o resultado de um teste (G4) | Só pessoas |
| `/override APP-12 "reason"` | Pular o UAT em uma emergência | Só pessoas |
| `/release APP-12` | Encerrar depois do deploy | Só pessoas |
| `/haam-setup` | Adotar o HAAM em um repo | Administrador do projeto |
| `/haam-onboard` | Preparar um novo desenvolvedor | Novo desenvolvedor |
| `/haam-update` | Atualizar para uma nova versão do kit | Administrador do projeto |

### Como funciona a revisão de código

Nenhum agente revisa o próprio trabalho, e os segredos são pegos por um scanner, não por julgamento. Toda mudança passa por seis camadas:

| Camada | Quando | O que verifica | Quem faz |
|---|---|---|---|
| 1. Proteção local contra segredos | Antes de cada commit | Chaves, tokens, senhas nas mudanças; o commit é bloqueado se algo for encontrado | gitleaks pelo hook do git (todo mundo), mais hooks da ferramenta do agente onde houver suporte |
| 2. Autoverificação | Antes de abrir um PR | Os testes passam; revisão de segurança feita pelo próprio agente sobre o próprio diff | O agente que construiu |
| 3. CI automático | A cada atualização do PR | Testes, lint, tipos (`ci`); segredos em cada commit (`secrets`); bibliotecas vulneráveis (`dependencies`) | GitHub Actions |
| 4. Revisão independente por IA | A cada atualização do PR (exceto rascunhos ou PRs só de documentação) | Atende à spec? Os testes são honestos? Bugs, aumento de escopo, violações de regras (`ai-review`). Vulnerabilidades de segurança (`security-review`) | Um Claude separado no GitHub Actions, que nunca viu o código ser escrito (com outro modelo quando o código veio de outra ferramenta) |
| 5. Revisão de código humana | PRs que alteram áreas protegidas | Lógica central, autenticação, pagamentos, dados pessoais, migrações, infraestrutura, configuração dos agentes | Product owner ou um desenvolvedor designado |
| 6. Aceitação humana | Todo PR de código | Funciona de verdade (UAT do gate G4) | Product owner |

- O revisor publica um comentário com **Blocking / Should fix / Nits**. Os apontamentos Blocking impedem o merge.
- O agente que construiu corrige os itens Blocking e faz push; as revisões rodam de novo automaticamente. Se discordar, ele responde no PR e pergunta a uma pessoa. Depois de **duas** rodadas reprovadas, ele para e passa a vez.
- Os revisores de IA podem bloquear, mas nunca aprovar nem fazer merge. Só uma pessoa pode anulá-los, com a label `ai-review-overruled` no PR.
- Se um segredo real chegar ao GitHub: revogue-o e troque-o imediatamente e depois peça a um administrador que reescreva o histórico da branch. Apagá-lo em um novo commit não basta.

Regras completas: `docs/process/GATES.md`. Instruções do revisor que você pode ajustar: `.github/review/REVIEWER.md`.

---

## Antes de começar

Você precisa de:
- [ ] Acesso de administrador ao repositório do GitHub. Se ele for privado, as regras de branch exigem GitHub Pro ou Team, e um aprovador nos deploys para produção exige Enterprise Cloud (`docs/setup/DECISIONS.md` §1)
- [ ] Um tracker: **GitHub Projects** (nada a mais; gratuito em todos os planos) ou acesso de administrador a um workspace do **Linear**
- [ ] Um agente de programação instalado e com login feito, na sua própria conta
- [ ] Python 3, Git, Make e o GitHub CLI com login feito (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, ou pela página de releases dele no GitHub)
- [ ] Um segredo do Claude para os agentes revisores: um token de um plano do Claude (`claude setup-token`) ou uma chave de API da Anthropic com um limite de gastos mensal (console.anthropic.com)
- [ ] O seu projeto roda localmente hoje

Decida agora:
1. **Tracker:** GitHub Projects (gratuito, tudo no GitHub) ou Linear (mais agradável de usar, plano gratuito limitado). Você pode trocar depois.
2. **Chave do produto:** um código curto, por exemplo `ACM`, `SHOP`, `CRM` (a chave do time no Linear, se você usar o Linear). O kit usa `APP` como marcador até que o `config` o substitua em todo lugar.
3. **Product owner:** a única pessoa que aprova ideias, specs, UAT e deploys (mais um aprovador substituto opcional).
4. **Ferramentas de agente** que a sua equipe vai usar.

Verifique a sua máquina a qualquer momento com: `python3 <kit>/tools/haam/haam.py dev`

---

## Fase 1: Instalar o kit (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

A documentação fica em inglês, a não ser que você adicione `--language es` (ou `fr`, `de`, `it`, `nl`, `pt`) aos dois comandos. Os agentes então também escrevem specs, issues, planos de UAT e mensagens nesse idioma; comandos, labels e código continuam em inglês. Mude depois com `haam.py config --language <code>` e, em seguida, o `update --target . --apply` do kit.

O instalador **nunca sobrescreve** os seus arquivos:
- Os arquivos novos são adicionados.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` e `.claude/settings.json` são **mesclados** automaticamente.
- O `.gitignore` recebe um bloco do HAAM no final, uma única vez.
- Qualquer outro arquivo que você já tenha é deixado como está, e a versão do kit é salva em `.haam/incoming/` para que você (ou o agente) faça o merge.

Como resolver os conflitos mais comuns:

| Se o seu repo já tem… | Faça isto |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Mova o conhecimento específico do projeto (convenções, armadilhas, comandos) para `docs/product/ARCHITECTURE.md` ou para uma seção "Particularidades do projeto" no final do `AGENTS.md`. Depois use o `AGENTS.md` e o `CLAUDE.md` do kit. Mantenha as regras `.mdc` do Cursor só para detalhes restritos a padrões de arquivos |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` move as suas skills para `.agents/skills/` e cria o link da pasta. Antes, renomeie as que tiverem o mesmo nome de skills do HAAM |
| `Makefile` | Adicione os targets do kit ao seu |
| `.github/workflows/` com CI | Mantenha o seu CI, mas garanta que um job chamado **`ci`** rode a sua suíte de testes completa nos PRs. Adicione `gates.yml`, `security.yml`, `review.yml`. Compare o seu deploy com o `deploy.yml` (Fase 4) |
| `.github/pull_request_template.md` | Incorpore as seções "Feito com (Built with)", "Critérios de aceitação → testes" e "Checklist (G3)" |
| `.pre-commit-config.yaml` ou Husky | Mantenha-o e chame `scripts/scan-secrets.sh` a partir dele, em vez de usar `.githooks/` |
| `CHANGELOG.md`, `.github/dependabot.yml` | Mantenha os seus (adicione o ecossistema `github-actions` ao Dependabot, se faltar) |

Apague `.haam/incoming/` quando terminar.

---

## Fase 2: Configurar e ensinar o seu projeto ao kit (45 min)

1. **Configurações do projeto** `[agent]` (com as suas respostas):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   Isso escreve o `haam.config.json` e substitui o marcador `APP` e o nome do produto em todos os arquivos do HAAM.

2. **Ferramentas de agente** `[agent]`: `python3 tools/haam/haam.py agents --apply`. Isso cria os links das skills compartilhadas para o Claude Code e o Grok, verifica os arquivos do Cursor/Codex/Gemini/Copilot e lista os passos que cada pessoa precisa fazer. Detalhes: `docs/setup/AGENTS-SETUP.md`.

3. **Contrato de comandos** `[agent]`: preencha cada `TODO(setup)` do `Makefile` (setup, dev, test, lint, typecheck, build, audit) e os passos de runtime nos workflows, a partir dos comandos reais do seu projeto. Depois, o `make check` precisa passar no código atual. Se os testes já falham na `main`, corrija-os ou marque-os primeiro: o HAAM depende de verde significar verde. Se o `make audit` relatar vulnerabilidades antigas de severidade alta/crítica, corrija-as ou registre-as como bugs e aumente o limite temporariamente.

4. **Mapa da arquitetura** `[agent]`: preencha `docs/product/ARCHITECTURE.md` a partir do código (menos de 150 linhas) e proponha caminhos reais para as áreas protegidas em `AGENTS.md` §4. Você revisa.

5. **Contexto do produto** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: o que é, usuários, jornadas que nunca podem quebrar, inegociáveis, prioridades atuais. É isso que todo agente lê para fazer julgamentos.

6. **Documento de onboarding** `[agent]`: preencha os itens `TODO(setup)` em `docs/ONBOARDING.md` (URL de clone, runtime, URL local).

7. **Higiene de segredos** `[agent]`: `make hooks` e depois varra o histórico uma vez: `gitleaks git --redact -v .` Qualquer coisa real precisa ser **revogada e trocada** junto ao provedor: ela já está exposta a qualquer pessoa com acesso ao repo. Você aprova as impressões digitais de falsos positivos adicionadas ao `.gitleaksignore`.

8. **Chats em paralelo** `[agent]`: liste em `.worktreeinclude` os arquivos só locais de que o aplicativo precisa (como `.env`), exclua `.claude/worktrees/` de qualquer ferramenta que varra a pasta inteira (executor de testes, linter, watcher) e experimente um worktree novo: `python3 tools/haam/haam.py worktree new setup-check`, depois `make setup && make check` dentro dele e então `git worktree remove .claude/worktrees/setup-check`. A partir daí, todo novo chat de agente começa com `/work`.

9. **Verificação:** `python3 tools/haam/haam.py doctor` mostra o que falta.

---

## Fase 3: Abrir o PR de adoção (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
Isso faz as verificações passarem a existir no GitHub, para que possam ser exigidas. O primeiro comentário de revisão por IA vai aparecer neste PR.

---

## Fase 4: Gates do GitHub (20 min)

1. **Planejar e depois aplicar** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   Ele cria as labels, um ruleset na branch padrão (PR obrigatório, as seis verificações obrigatórias, sem force push; os administradores só podem contornar ao fazer o merge de um PR, para emergências, nunca fazendo push na main; "up to date before merging" desligado, para economizar execuções de CI). Se o ruleset já existir, ele só adiciona o que falta e mantém as suas configurações (`--reset` o substitui). Ele também cria o ambiente `production` com os seus aprovadores e a variável `PRODUCTION_URL`, e ativa a varredura de segredos, a proteção de push e o Dependabot onde o seu plano permitir.
2. **Chave do revisor** `[YOU, in your terminal]`: um único segredo roda as duas revisões. Ou `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` com o token de `claude setup-token` (usa o seu plano do Claude), ou `gh secret set ANTHROPIC_API_KEY -R owner/repo` com uma chave de API dedicada (cobrada por revisão; com ela, a revisão de segurança usa a action de revisão de segurança da Anthropic). Os dois comandos pedem o valor sem mostrá-lo.
3. **PRs de forks** `[YOU, in the browser]`: Settings → Actions → General → exigir aprovação para colaboradores externos.
4. **Deploys:**
   - *Já faz deploy pelo GitHub Actions?* Adicione `environment: production` ao seu job de deploy: só isso já dá a você o gate G5. Apague o `deploy.yml` do kit ou guarde-o como referência.
   - *Faz deploy de outra forma* (a integração com o Git de uma plataforma de hospedagem, manual)? Ou passe os deploys para o `deploy.yml` (preencha o `make deploy`), ou mantenha o seu método e trate o G5 como um passo manual: o product owner faz o deploy depois do merge e então roda `/release`. Desligue o deploy automático a cada push se ele contornar a aprovação.
5. **Repositórios privados:** as regras de branch exigem GitHub Pro ou Team, e um aprovador nos deploys para produção exige Enterprise Cloud; a ferramenta informa o que o seu plano permite. Sem um aprovador, o seu `ship` é a decisão de release: defina `deploy_approval: automatic` (`docs/setup/DECISIONS.md` §1).

Detalhes e equivalentes manuais: `docs/setup/GITHUB-SETUP.md`.

---

## Fase 5: O tracker (20 min)

### Opção A: GitHub Projects (gratuito)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (permite que o seu login do GitHub use o Projects).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` token de automação, para que os cartões se movam quando os PRs são abertos e integrados: crie um token clássico em github.com/settings/tokens com os escopos `project` e `repo` (`public_repo` basta para um repositório público) e depois rode `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` no quadro, crie as visualizações que a ferramenta lista: Board agrupado por Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Teste: `python3 tools/haam/haam.py issue list`.

Os agentes usam `python3 tools/haam/haam.py issue …` para todas as operações no quadro (`docs/process/TRACKER.md`), então funciona do mesmo jeito a partir do Claude Code, do Cursor, do Codex, do Grok ou de qualquer outra ferramenta.

### Opção B: Linear
1. **Status, labels, time** `[YOU, in your terminal]` (exige a sua chave de API pessoal do Linear, que nunca passa por um agente):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   Ele cria o time se necessário, ativa o Triage, cria os 12 status (renomeando o "Todo" padrão do Linear para "Ready") e as 14 labels. Ele nunca apaga nada; lista os status a mais para que você os arquive.
2. **Configurações só do navegador** `[YOU, in the browser]`: conectar o GitHub, automações de PR (PR em rascunho → In Progress, PR pronto para revisão → In Review, merge feito → Deploying), formato do nome de branch `{issue-identifier}-{issue-title}`, visualizações salvas. Veja `docs/setup/LINEAR-SETUP.md`.
3. **Conecte o seu agente** ao Linear (`docs/setup/AGENTS-SETUP.md`) e teste: *"Liste as issues do time ACM no Linear."*

**Já tem um backlog?** Peça ao seu agente que o traga para o tracker (as issues do GitHub podem simplesmente ser adicionadas ao quadro). Coloque tudo em **Triage**, faça a triagem uma vez (`stream:bug`, `stream:idea`, ou `stream:feature` + Backlog) e escreva specs só para as cinco primeiras.

---

## Fase 6: Merge, ciclo de teste e pessoas

### Fazer o merge do PR de adoção
Quando as verificações estiverem verdes, adicione você mesmo a label `uat-passed` (o gate já está ativo, então até este PR passa por ele) e faça o merge. Se os agentes revisores implicarem com detalhes do próprio kit, anule-os com `ai-review-overruled`. Rode `python3 tools/haam/haam.py doctor --role admin` para uma verificação final.

### Rodar um ciclo completo (45–60 min)
Escolha algo pequeno e real. Passe com ele por todas as etapas uma vez:

| Passo | Você digita | O que deve acontecer |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | Nova issue em Triage, label `stream:idea` (no GitHub: `#1`; no Linear: `ACM-1`) |
| 2 | `/assess #1` | Avaliação commitada na branch da issue (sem PR); a issue passa para Decision |
| 3 | `/decide #1 approve medium` | A issue passa para Backlog, a label vira `stream:feature` |
| 4 | `/spec #1` | Spec com critérios de aceitação, na mesma branch |
| 5 | Leia a spec (link na issue), diga ao agente "spec aprovada" | A issue recebe `agent-ready` e passa para Ready |
| 6 | `/build #1` | Reserva a issue, cria a branch, programa, escreve os testes, faz a autorrevisão, escreve o plano de UAT e faz push da branch. Ainda sem PR (test-first, o padrão) |
| 7 | `/uat #1` (o `/build` roda isso) | A issue passa para UAT; você é notificado |
| 8 | `/test #1` | O agente coloca a mudança na sua máquina, inicia o aplicativo e dá a você uma checklist curta |
| 9 | Experimente, responda `pass` | O agente abre o PR com a label `uat-passed`; `ci`, `secrets`, `dependencies` e os agentes revisores rodam uma vez; o `release-gate` fica verde; o agente pergunta "Colocar em produção?" |
| 10 | Responda `ship` | O agente faz o merge, aprova o deploy para produção por você, espera e fecha a issue: Done |
| 11 | (experimente uma vez) `/test` em uma mudança, descrevendo um problema em vez de aprovar | Ela volta para os agentes com as suas notas (`uat-failed`) e retorna para você quando estiver corrigida |

(No Linear, os IDs têm a forma `ACM-1`.)

Depois, experimente os casos-limite uma vez: peça ao agente que faça commit de uma chave falsa em uma branch descartável (`AKIA` + 16 letras maiúsculas/dígitos): o commit precisa ser bloqueado. Depois reprove um UAT e use um override. Ajuste as skills em `.agents/skills/` ou o processo em `docs/process/LIFECYCLE.md` onde algo pareceu errado.

**Experimente também uma segunda ferramenta de agente no ciclo de teste** (por exemplo, o Cursor ou o Codex para o passo 6). Isso confirma que as regras e as skills compartilhadas funcionam além da sua ferramenta principal.

### Adicionar desenvolvedores
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: acesso de escrita no GitHub (não de administrador), acesso ao quadro do GitHub Projects ou um convite para o Linear.
2. Envie a eles o link do repo e as credenciais de teste (por um gerenciador de senhas ou um link de uso único, nunca por chat ou e-mail).
3. Eles abrem o próprio agente no repo e rodam `/haam-onboard` (Codex: `$haam-onboard`).
4. Quando vocês forem duas pessoas: a ferramenta define "1 approval required" quando você adiciona aprovadores substitutos (`config --backup-approvers` e depois `github --apply`), e você pode adicionar um `.github/CODEOWNERS` para as áreas protegidas.

### Deixar os agentes trabalharem de forma semiautônoma

| Nível | Como | Quando |
|---|---|---|
| **1. Supervisionado** | Você digita `/next` ou `/build` e aprova cada push e cada PR | Primeiras 2–3 semanas |
| **2. Em lote** | 2–3 janelas de chat (qualquer combinação de ferramentas e computadores), cada uma iniciada com `/work`, que dá a ela o próprio worktree; você revisa os PRs em lote | Quando as specs forem boas de forma consistente |
| **3. Agendado** | Uma tarefa agendada roda um agente sem interface com `/next` e para no UAT | Quando você confiar nos gates |

Em todos os níveis, os agentes param nos gates humanos.

### Custos de operação
Além do GitHub, do Linear (se você o usar) e da assinatura de agente de cada pessoa, o único custo baseado em uso são os agentes revisores: duas chamadas ao Claude por push revisado em um PR, cobradas na `ANTHROPIC_API_KEY` ou descontadas do seu plano do Claude (`CLAUDE_CODE_OAUTH_TOKEN`). Mantenha o limite de gastos ativado e os PRs pequenos.

### Manter-se atualizado
As novas versões do kit são publicadas em https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` avisa quando sai uma. Rode `/haam-update` (Codex: `$haam-update`) em uma branch: os arquivos que você nunca alterou são atualizados, as suas personalizações são mantidas e, onde os dois lados mudaram, o agente faz o merge. O CHANGELOG lista os passos de migração, se houver.

### O seu ritmo como product owner
Diário (10–15 min): testar o que está em **UAT**, esvaziar **Triage** (`/triage`). Semanal (30–45 min): decidir tudo o que está em **Decision**, reordenar o backlog (`/triage backlog`), cobrar o trabalho parado (`/triage stale`), rever **Parked**, fechar os **overrides**. O guia completo, com regras de prioridade e checklists: `docs/process/PRODUCT-MANAGER.md`.

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| Não sabe o que falta | – | `python3 tools/haam/haam.py doctor --role admin` |
| O agente não segue as regras | A ferramenta não está lendo o `AGENTS.md` | Verificação da primeira execução em `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` diz que o login não pode usar o Projects | O login do gh não tem o escopo `project` | `gh auth refresh -s project` |
| Os cartões do quadro não se movem quando os PRs são abertos/integrados | Falta o `HAAM_PROJECT_TOKEN`, ou o PR não diz `Refs #123` | Adicione o segredo (Fase 5); verifique a descrição do PR |
| O agente não vê o Linear | MCP não conectado ou sem login | Passos por ferramenta em `docs/setup/AGENTS-SETUP.md` |
| As skills aparecem duas vezes no Cursor | O Cursor lê tanto `.agents/skills` quanto `.claude/skills` | Desative a compatibilidade com skills do Claude nas configurações do Cursor |
| `.claude/skills` ou `.grok/skills` faltando depois do clone (Windows) | Links simbólicos do Git desativados | `git config core.symlinks true` e clone de novo, ou `haam.py agents --apply` (copia em vez de criar links) |
| `haam.py github` diz que rulesets/aprovações não estão disponíveis | Repo privado em um plano gratuito | Faça upgrade, ou proteja manualmente e confie nas verificações |
| `haam.py linear` dá erro em um passo | Mudança na API ou permissões | Termine esse passo à mão com `docs/setup/LINEAR-SETUP.md` |
| Dois chats alteraram os mesmos arquivos ou a mesma branch | Eles compartilhavam uma pasta | Comece todo chat de agente com `/work` (worktree próprio) |
| Os testes ou o linter encontram arquivos duplicados em `.claude/worktrees/` | A ferramenta varre a pasta inteira | Exclua `.claude/worktrees/` na configuração dessa ferramenta |
| Um worktree não consegue rodar o aplicativo | Faltam arquivos locais | Adicione-os ao `.worktreeinclude` e depois rode `haam.py worktree prep` no worktree |
| O `/build` se recusa a começar | A issue não está em Ready, ou falta `agent-ready` | `/spec` e aprove a spec, ou mova você mesmo a issue para Ready |
| Os status do Linear não mudam com os eventos de PR | Integração com o GitHub ou automações não configuradas | Configurações do time → Workflow → automações de PR; o título do PR precisa começar com o ID da issue |
| O `release-gate` continua vermelho depois de `uat-passed` | O workflow não rodou de novo | Remova e adicione a label de novo |
| Falta uma verificação obrigatória na lista | Ela ainda não rodou | Abra algum PR primeiro |
| Commits bloqueados: "gitleaks is not installed" | Falta o gitleaks nessa máquina | Instale-o e depois rode `make hooks` |
| Commit bloqueado por um segredo que não é segredo | Falso positivo | Uma pessoa adiciona a impressão digital ao `.gitleaksignore` em um commit revisado |
| `ai-review` ou `security-review` pendente ou com erro | Sem segredo do revisor (`CLAUDE_CODE_OAUTH_TOKEN` ou `ANTHROPIC_API_KEY`), PR de fork, ou acabaram os turnos | Adicione o segredo; rode de novo; aumente `--max-turns`; ou `ai-review-overruled` |
| Revisor rigoroso demais | Instruções não ajustadas | Edite `.github/review/REVIEWER.md` |
| `dependencies` falha em todo PR | Vulnerabilidades antigas | Corrija, ou aumente o limite temporariamente e acompanhe como bugs |
| Specs vagas demais, construções dão errado | G2 frouxo demais | Endureça a Definition of Ready em `docs/process/GATES.md` |

---

## Princípios

1. **Os humanos decidem, os agentes executam.**
2. **Se não está no Git ou no tracker, não existe** para a próxima pessoa ou o próximo agente.
3. **Partes pequenas:** uma issue, uma branch, um PR, revisável em 15 minutos.
4. **Os gates são baratos de passar e caros de pular.** Os overrides são permitidos, sempre registrados e sempre acompanhados.
5. **Verde significa verde.** Nunca enfraqueça um teste para passar por um gate.
6. **Ninguém corrige a própria prova.** O agente que escreve o código nunca o revisa; os segredos são pegos por ferramentas, não por julgamento.
7. **Qualquer agente, as mesmas regras.** As ferramentas são intercambiáveis; o processo e os gates, não.
