# Onboarding de desenvolvedores

Boas-vindas. Este repo é construído por pessoas e agentes de programação trabalhando juntos com a **Human-Agent Agile Methodology (HAAM)**. Você pode usar a ferramenta de agente que preferir: Claude Code, Cursor, Codex, Grok, Gemini ou Copilot. Este guia leva você do zero à sua primeira issue em cerca de uma hora.

## O jeito rápido: deixe o seu agente fazer o seu onboarding

1. Clone o repo e abra a sua ferramenta de agente na pasta raiz dele:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Diga ao seu agente:
   - Claude Code, Cursor ou Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Qualquer outra ferramenta: *"Leia `.agents/skills/haam-onboard/SKILL.md` e siga as instruções."*

Ele verifica a sua máquina, os seus acessos e a conexão com o tracker, configura os seus hooks locais e o `.env`, roda as verificações do projeto, explica como trabalhamos e sugere uma primeira issue. Os passos que precisam da sua senha ou das suas chaves são feitos por você, no seu próprio terminal ou editor. Você nunca cola segredos no chat.

Prefere fazer à mão? As seções abaixo cobrem o mesmo conteúdo.

---

## 1. Leia primeiro (15 minutos)
1. `AGENTS.md`: as regras que todo agente segue, seja qual for a ferramenta. Elas também valem para você.
2. `docs/process/LIFECYCLE.md`: fluxos de trabalho, status, gates, quem faz o quê.
3. `docs/process/GATES.md`: checklists, revisão de código e overrides.
4. `docs/product/PRODUCT.md` e `docs/product/ARCHITECTURE.md`: o que estamos construindo e como está estruturado.

## 2. Contas de que você precisa
| Conta | Para quê | O que pedir |
|---|---|---|
| GitHub | Código, PRs, CI | Acesso de escrita ao repo |
| Tracker | Backlog e status | **GitHub Projects:** acesso ao quadro (vem com o convite para o repo). **Linear:** participação no time **APP** |
| A sua ferramenta de agente | Agente de programação | A sua **própria** conta (Claude, Cursor, OpenAI, xAI…). Nunca compartilhe contas |
| Serviços de teste | Rodar localmente | Só credenciais de teste, fornecidas pelo product owner |

O administrador do projeto convida você com um único comando: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. Você **não** vai receber credenciais de produção; os deploys passam pelo GitHub, com aprovação.

## 3. Instalar as ferramentas
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (obrigatório; os commits são bloqueados sem ele): macOS `brew install gitleaks`; outros: https://github.com/gitleaks/gitleaks/releases
- Runtime da linguagem deste repo: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- A sua ferramenta de agente

Verifique tudo com: `python3 tools/haam/haam.py dev`

## 4. Colocar o código para rodar
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Conectar ao tracker
Verifique `"tracker"` em `haam.config.json`:
- **GitHub Projects:** rode `gh auth refresh -s project` uma vez e depois teste: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** siga a seção da sua ferramenta em `docs/setup/AGENTS-SETUP.md` (um único login) e depois peça ao seu agente: *"Liste as issues em Ready do time APP no Linear."*

## 6. As suas configurações pessoais (não compartilhadas)
Notas e preferências pessoais ficam em arquivos ignorados pelo git: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json` ou as configurações de usuário da sua ferramenta. Nunca coloque regras compartilhadas ali. Se algo deve valer para todo mundo, proponha uma mudança no `AGENTS.md` por meio de um PR.

## 7. O fluxo de trabalho do dia a dia
Os comandos estão escritos abaixo como `/name`; no Codex, use `$name`.

| Você quer… | Faça isto |
|---|---|
| Ver o que está esperando | Visualização **Agent queue** do tracker (para construir) ou **Waiting on me** |
| Iniciar um agente em uma nova janela de chat | `/work` (ou `/work bugs`) |
| Começar a trabalhar neste chat | `/next`, ou `/build APP-123` |
| Fazer a triagem e priorizar (product owner) | `/triage`, `/triage group`, `/epic` e `docs/process/PRODUCT-MANAGER.md` |
| Registrar uma ideia | `/idea …` |
| Relatar um bug | `/bug …` |
| Transformar uma ideia aprovada em uma spec | `/spec APP-123` |
| Testar uma mudança (product owner) | `/test` e depois `pass` → `ship`, ou dizer o que está errado |
| Testar a mudança de outra pessoa (desenvolvedor) | Siga `docs/uat/APP-123-*.md` e depois avise o product owner |
| Verificar a sua configuração | `python3 tools/haam/haam.py doctor` |

### Rodar agentes em paralelo
Abra uma nova janela de chat por agente e digite `/work` (ou `/work bugs`, `/work features`, `/work specs`, `/work ideas`; Codex: `$work`). O agente recebe a própria cópia do projeto (um git worktree em `.claude/worktrees/`), copia os arquivos locais listados em `.worktreeinclude` (como `.env`), pega o item do topo e trabalha nele até a passagem. Mantenha o seu próprio chat na pasta principal, para ideias, decisões e testes.

- **Claude Code no VS Code:** nova aba de chat com Cmd+Shift+Esc (Mac) ou Ctrl+Shift+Esc (Windows/Linux). Em um terminal: `claude --worktree`.
- **Outras ferramentas:** se a ferramenta tiver a própria opção de worktree ou de agentes em paralelo, use-a; caso contrário, o `/work` cria o worktree e diz qual pasta abrir em uma nova janela.
- **Outro computador:** a mesma coisa. A reserva no tracker impede que dois agentes peguem a mesma issue; informe o nome da máquina quando for pedido, para que o comentário de reserva mostre onde o agente está rodando.
- **Limpe** de vez em quando os worktrees concluídos: `python3 tools/haam/haam.py worktree clean` (plano) e depois `--apply`.
- **Testar a branch de um agente:** o plano de UAT usa `git switch --detach origin/<branch>`, que funciona enquanto o worktree do agente ainda tiver a branch.

### Rodar agentes de forma semiautônoma
- **Com acompanhamento:** digite `/next`, revise a escolha dele e deixe-o trabalhar. A sua ferramenta deve perguntar antes de fazer push ou abrir PRs (veja as configurações seguras em `docs/setup/AGENTS-SETUP.md`).
- **Sem acompanhamento:** uma tarefa agendada ou um cron roda o seu agente sem interface com o prompt `/next` (Codex: `$next`). Ele só pega trabalho que já passou pelo respectivo gate e para no UAT, à espera de uma pessoa.
- Os agentes param em todos os gates humanos, por design. O seu trabalho é manter curta a visualização **Waiting on me**.

## 8. Como o seu trabalho é revisado
Todo PR é verificado por testes, por uma varredura de segredos, por uma auditoria de dependências e por dois revisores de IA independentes (spec/qualidade e segurança) que nunca viram o código ser escrito. Corrija os apontamentos **Blocking** deles; se você achar que algum está errado, responda no PR e pergunte ao product owner, que pode anulá-lo com a label `ai-review-overruled`. As áreas protegidas também recebem uma revisão humana. Detalhes: `docs/process/GATES.md` § Como funciona a revisão de código.

**Se algum dia você fizer commit de um segredo real:** avise o product owner imediatamente. Ele precisa ser revogado e trocado, mesmo que você o apague no commit seguinte.

## 9. Regras que vale repetir
- Nada de push na `main`, nada de merges, nada de deploys feitos por agentes.
- Nenhum segredo ou dado pessoal real no código, nos testes, nas fixtures, no tracker ou no chat. Os dados pessoais são protegidos por lei (por exemplo, LGPD ou RGPD).
- Uma issue → uma branch → um PR, pequeno o suficiente para ser revisado em 15 minutos.
- Preencha o campo **Feito com (Built with)** em todo PR (a sua ferramenta e o modelo).
- Se não está no Git ou no tracker, não existe para a próxima pessoa.

## 10. Obter ajuda
- Dúvidas sobre o processo: pergunte ao seu agente *"de acordo com o LIFECYCLE.md, o que deve acontecer quando…"*
- Acessos e credenciais: o product owner.
- Melhorar o processo: abra uma `/idea` com a label `area:process`. Mudanças no `AGENTS.md`, em `.agents/`, nas pastas de configuração dos agentes e em `.github/` precisam da revisão do product owner.
