# HAAM: Human-Agent Agile Methodology

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Nederlands](README.nl.md) · **Português**

**Os humanos decidem. Os agentes executam. Tudo fica no Git e no seu tracker.**

HAAM é uma metodologia e um kit abertos para desenvolver software com agentes de programação de IA, da ideia à produção, sem perder o controle. Ela dá a todos os agentes as mesmas regras, os mesmos comandos e os mesmos gates, seja qual for a ferramenta em que rodam: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI ou GitHub Copilot**. O trabalho é acompanhado em um quadro do **GitHub Projects** (gratuito) ou no **Linear**, como você preferir. Várias pessoas, cada uma com o próprio agente e a própria conta, podem trabalhar no mesmo produto em paralelo.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## O que você recebe

- **Um ciclo de vida com cinco gates humanos**: decidir sobre a ideia, aprovar a spec, verificações automáticas com revisão independente por IA, teste de aceitação feito por uma pessoa e aprovação para produção. Todo gate pode ser contornado em uma emergência, e todo override fica registrado e é acompanhado depois.
- **Três fluxos de trabalho** dos quais os agentes puxam tarefas: bugs, funcionalidades prontas e ideias a avaliar. O tracker (GitHub Projects ou Linear) guarda o backlog, as prioridades e os status.
- **20 skills compartilhadas** (`/idea`, `/bug`, `/assess`, `/spike`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), no formato aberto Agent Skills.
- **Suas configurações, suas escolhas:** `/haam-settings` permite que o product owner escolha quando o CI e as revisões por IA rodam (em todo PR, localmente, só para áreas protegidas ou nunca), o que ele mesmo testa, como o trabalho é agrupado (por issue, por epic ou em um único PR de release), se os deploys esperam aprovação e quais são os limites, cada um com o seu custo-benefício e os números do próprio projeto.
- **Testar com uma palavra, antes que algo gaste minutos de CI**: digite `/test`, experimente a mudança do agente no seu computador e responda `pass` (só então o pull request é aberto e verificado, uma única vez, exatamente sobre o que você testou) e depois `ship` (o agente faz o merge, o deploy e fecha a issue), ou simplesmente diga o que está errado (a mudança volta direto para os agentes e retorna para você quando estiver corrigida). `/test all` pega tudo o que está esperando de uma vez, e `ship --all` faz o deploy de tudo com uma única aprovação.
- **Uma via sem UAT** para mudanças que você não tem como testar de forma útil (configuração, atualização de dependências, refatorações invisíveis): marque a issue com `uat:skip` uma vez, e o PR dela faz merge sozinho quando o CI e as duas revisões por IA passam.
- **Epics com um agente que faz as perguntas certas**: `/triage group` transforma uma pilha de issues soltas em epics (um por funcionalidade); `/epic` lê cada um, escreve um briefing curto, faz algumas perguntas objetivas e depois organiza as issues: duplicatas, lacunas, divisões, ordem.
- **Espaço para os agentes construírem partes grandes rapidamente, com uma proteção:**
  - `/spike` constrói um protótipo descartável que funciona, para você experimentar antes de decidir;
  - o modo de construção por epic permite que um único agente construa uma funcionalidade inteira, parte por parte, com pontos de controle, um único teste e uma única release;
  - toda mudança que entra passa por todos os gates, e os protótipos nunca entram.
- **Um guia de decisões** ([DECISIONS.md](template/i18n/pt/docs/setup/DECISIONS.md)): todas as escolhas que uma equipe faz ao adotar o HAAM, com uma recomendação para cada uma. Ele cobre as contas do GitHub e o plano de que você precisa, GitHub Projects ou Linear, as configurações, como dimensionar os limites de acordo com o seu tempo para testar e o que proteger. `/haam-setup` conduz você por ele.
- **Um guia para o gerente de produto** ([PRODUCT-MANAGER.md](template/i18n/pt/docs/process/PRODUCT-MANAGER.md)): ritmo diário e semanal, como fazer a triagem, regras de prioridade com uma matriz de impacto × alcance para bugs, tamanhos saudáveis de fila, tudo isso com um agente (`/triage`) ou diretamente no GitHub Projects ou no Linear.
- **Agentes em paralelo sem colisões**: abra uma nova janela de chat, digite `/work bugs`, e o agente recebe a própria cópia do projeto (um git worktree), pega o bug do topo e trabalha nele até chegar ao seu teste. Rode quantos quiser, em um computador ou em vários.
- **Revisão de código em que ninguém corrige a própria prova**: varredura de segredos antes de cada commit e no CI, auditoria de dependências e dois revisores de IA independentes (spec/qualidade e segurança) que nunca viram o código ser escrito. Pessoas revisam as áreas protegidas e podem ter a palavra final.
- **Gates garantidos pelo GitHub**, não pela confiança: regras de branch, verificações obrigatórias, um gate de label de UAT e aprovações de deploy, que valem seja qual for o agente ou a pessoa que está fazendo push.
- **Documentação em sete idiomas:** inglês, espanhol, francês, alemão, italiano, holandês e português. Escolha um na instalação (`install --language es`) e os agentes também escreverão nele as specs, issues, planos de UAT e mensagens; comandos, labels e código continuam em inglês.
- **Uma ferramenta de configuração** (`haam.py`, Python 3, sem dependências) que instala o kit em um repo existente sem sobrescrever nada, configura o GitHub e o tracker (GitHub Projects ou Linear), dá aos agentes um único conjunto de comandos para o quadro, faz o onboarding de desenvolvedores, verifica a configuração e atualiza os projetos para novas versões do kit.

## Início rápido

### Adotar o HAAM no seu projeto (administrador do projeto, cerca de meio dia)

1. Obtenha uma versão publicada do kit:
   ```bash
   git clone --depth 1 --branch v1.16.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (ou baixe o zip em [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Abra o seu agente de programação **na pasta raiz do seu projeto** e diga:
   > Leia `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` e siga as instruções para configurar o HAAM neste repositório. O kit está em `~/haam-kit/template`.

O agente instala o kit em uma branch, faz algumas perguntas, preenche o conhecimento do projeto a partir do seu código e conduz você pela configuração do GitHub e do seu tracker. Ele mostra cada mudança antes de fazê-la. Tudo o que envolve uma senha ou uma chave de API é feito por você, no seu próprio terminal, nunca pelo chat do agente.

Prefere fazer à mão? Siga [o guia de adoção](template/i18n/pt/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Entrar em um projeto que já usa o HAAM (desenvolvedor, cerca de uma hora)

Clone o projeto, abra o seu agente nele e rode `/haam-onboard` (Codex: `$haam-onboard`; outras ferramentas: *"siga `.agents/skills/haam-onboard/SKILL.md`"*).

### Atualizar um projeto para uma nova versão do kit

Obtenha a nova versão do kit e, no seu projeto, rode `/haam-update`, ou:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Os arquivos que você nunca alterou são atualizados; os que você personalizou são mantidos e, onde os dois lados mudaram, a nova versão é deixada de lado para o seu agente fazer o merge. Nada é apagado.

## A ferramenta de configuração

| Comando | Quem | O quê |
|---|---|---|
| `install --target DIR` | admin | Copia o kit para um repo. Nunca sobrescreve; mescla os arquivos de configuração dos agentes; guarda os conflitos em `.haam/incoming/`; registra a versão em `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Atualiza um projeto para esta versão do kit, mantendo as personalizações |
| `config` | admin | Nome do produto, chave do time no Linear, repo, aprovadores → `haam.config.json`; aplica-os a todos os arquivos do HAAM |
| `agents [--apply]` | admin | Conecta as skills e o Linear para Claude Code, Cursor, Codex, Grok, Gemini, Copilot |
| `github [--apply]` | admin | Labels, ruleset de branch com verificações obrigatórias, aprovação para produção, recursos de segurança |
| `github-project [--apply]` | admin | Quadro do GitHub Projects: 12 status, campo Priority, labels, vínculo com o repo |
| `linear [--apply]` | admin, no próprio terminal | Time do Linear, triagem, 12 status, 9 labels |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agentes | Trabalha no quadro do GitHub Projects a partir de qualquer ferramenta de agente |
| `exclusive "<who>" -- <command>` | agentes | Roda uma execução de testes pesada (que usa um recurso compartilhado por toda a máquina) quando nenhuma outra está rodando nesta máquina |
| `capacity` | agentes | Segura trabalho novo quando há PRs demais abertos ou esperando o seu teste (limites em `haam.config.json`) |
| `ci-usage [--days 7]` | admin | Para onde foram os minutos do GitHub Actions, por workflow, job, gatilho e dia |
| `settings [--explain] [--set key=value] [--apply]` | owner/admin | Suas escolhas: quando o CI e as revisões por IA rodam, o que você testa, agrupamento, entrega, limites (`/haam-settings` conduz você por elas) |
| `local-ci ISSUE` | owner | Com `ci: local`: roda `make check` aqui sobre o commit do PR e publica o resultado (o ship faz isso por você) |
| `review ISSUE` | agentes | As duas revisões por IA em sessões locais novas, publicadas como status do PR (quando as revisões são locais) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Coloca uma mudança nesta máquina para testar; depois de `pass` + `ship`: merge, aprovação do deploy (uma para vários), espera, fechamento |
| `worktree status\|new\|prep\|list\|clean` | agentes, qualquer pessoa | Um worktree por chat de agente; copia arquivos locais de `.worktreeinclude`; limpa os que terminaram |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Convida um desenvolvedor (escrita no GitHub, não admin; acesso ao quadro ou ao time do Linear) |
| `dev [--apply] [--run-checks]` | desenvolvedor | Verificação da máquina, hook de commit, `.env` a partir do exemplo, verificações do projeto |
| `doctor [--role admin] [--check-updates]` | qualquer pessoa | O que está feito, o que falta e quem precisa fazer |
| `version [--check]` | qualquer pessoa | Versões da ferramenta, do projeto e do último kit publicado |

Todo comando mostra primeiro um plano e só muda algo com `--apply`. Adicione `--json` para uma saída legível por máquina.

## Rodar vários agentes ao mesmo tempo

Cada chat de agente recebe a própria pasta, para que os chats nunca sobrescrevam o trabalho uns dos outros:

1. Abra uma nova janela de chat (Claude Code no VS Code: Cmd/Ctrl+Shift+Esc).
2. Digite `/work bugs` (ou `/work features`, `/work specs`, `/work ideas`, ou apenas `/work`; Codex: `$work`).
3. O agente passa para o próprio git worktree, copia arquivos locais como `.env`, reserva o item do topo do quadro, constrói e testa, abre o PR e entrega a você um plano de teste.

Repita para quantos agentes quiser, em qualquer computador com o projeto clonado. A reserva no quadro impede que dois agentes peguem a mesma issue, seja para construí-la, avaliá-la ou escrever a spec dela. O seu próprio chat fica na pasta principal, para ideias, decisões, testes e releases.

## Escolher um tracker

| | GitHub Projects | Linear |
|---|---|---|
| Custo | Gratuito em todos os planos do GitHub | Plano gratuito com limites; pago por usuário |
| Onde | Junto do seu código, um único login | Aplicativo separado |
| Os agentes usam | `haam.py issue …` (qualquer agente) | O servidor MCP do Linear |
| Ideal para | Pessoas sozinhas e times pequenos, mantendo tudo no GitHub | Backlogs mais movimentados, vários times, planejamento mais rico |

O mesmo ciclo de vida, os mesmos gates e as mesmas skills nos dois casos, e você pode trocar depois. Veja [TRACKER.md](template/i18n/pt/docs/process/TRACKER.md).

## Compatibilidade com agentes

| | Regras | Skills | Chamar uma skill | Linear (se usado) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | verificar na primeira execução | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` via `.gemini/settings.json` | por arquivo | por arquivo | por usuário |
| GitHub Copilot | `AGENTS.md` | por arquivo | por arquivo | por usuário |

No GitHub Projects, todos os agentes usam os mesmos comandos `haam.py issue`, então não há nada a conectar por ferramenta. Detalhes e configurações seguras recomendadas para cada ferramenta: [AGENTS-SETUP.md](template/i18n/pt/docs/setup/AGENTS-SETUP.md).

## Requisitos

- Um repositório no GitHub. Repositórios públicos têm tudo no plano gratuito. Nos **privados**, as regras de branch exigem GitHub Pro ou Team, e um aprovador obrigatório nos deploys para produção exige GitHub Enterprise Cloud (sem ele, o seu `ship` é a decisão de release). O [DECISIONS.md](template/i18n/pt/docs/setup/DECISIONS.md) traz os detalhes.
- Um tracker: um quadro do GitHub Projects (gratuito, em qualquer plano do GitHub) ou um workspace do Linear (qualquer plano)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- Um segredo do Claude para os agentes revisores do CI: um token de um plano do Claude (`claude setup-token`) ou uma chave de API da Anthropic (cobrada por uso; defina um limite de gastos)
- Qualquer agente de programação compatível

## Estrutura do repositório

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  i18n/          The same docs in other languages
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Versionamento

O HAAM segue o [versionamento semântico](https://semver.org):
- **Patch** (1.0.x): correções e ajustes de texto; o `update` se aplica sem conflitos.
- **Minor** (1.x.0): novas skills, verificações ou documentos; compatível com versões anteriores.
- **Major** (x.0.0): mudanças que exigem um passo de migração (por exemplo, status do Linear ou verificações obrigatórias renomeados). O [CHANGELOG](CHANGELOG.md) lista os passos.

Instale sempre a partir de uma tag ou de uma release, nunca a partir de `main`.

## Como contribuir

Ideias, relatos de bugs e pull requests são bem-vindos. Veja [CONTRIBUTING.md](CONTRIBUTING.md). Problemas de segurança: veja [SECURITY.md](SECURITY.md).

## Licença

[MIT](LICENSE) © 2026 Jorge del Prado
