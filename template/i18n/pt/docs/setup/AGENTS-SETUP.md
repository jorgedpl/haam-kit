# Ferramentas de agente: configuração por ferramenta

O HAAM funciona com qualquer agente de programação. Todas as ferramentas leem as **mesmas regras** (`AGENTS.md`) e as **mesmas skills** (`.agents/skills/`) e trabalham no **mesmo tracker**: um quadro do GitHub Projects (por meio de `python3 tools/haam/haam.py issue …`, que qualquer agente consegue rodar) ou o Linear (por meio do servidor MCP dele, `https://mcp.linear.app/mcp`). Só a parte técnica muda.

Rode `python3 tools/haam/haam.py agents` para ver o que está conectado neste repo, e `python3 tools/haam/haam.py dev` para verificar a sua máquina.

## Como cada ferramenta carrega o HAAM

| | Regras | Skills | Chamar uma skill | MCP do Linear (só projetos com Linear) | Skills exclusivas de pessoas |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → importa `AGENTS.md` | `.claude/skills` (link para `.agents/skills`) | `/build APP-1` | `.mcp.json` (no repo) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (no repo) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | por usuário: `codex mcp add` | `agents/openai.yaml` em cada skill |
| **Grok Build** | verificar na primeira execução (veja abaixo) | `.grok/skills` (link para `.agents/skills`) | `/build APP-1` | lê `.mcp.json` | conforme o texto da skill |
| **Gemini CLI** | `AGENTS.md` via `.gemini/settings.json` | seguir o `SKILL.md` pelo nome | "siga .agents/skills/build" | por usuário | conforme o texto da skill |
| **GitHub Copilot** | `AGENTS.md` | seguir o `SKILL.md` pelo nome | "siga .agents/skills/build" | por usuário | conforme o texto da skill |

Se uma ferramenta não carregar as skills, diga a ela: *"Abra `.agents/skills/<name>/SKILL.md` e siga as instruções."* As skills são Markdown simples.

## Conectar ao tracker (uma vez por pessoa)

**GitHub Projects:** nada a instalar no seu agente. Rode `gh auth refresh -s project` uma vez e teste com `python3 tools/haam/haam.py issue list`. O resto desta seção é para projetos com **Linear**.

O Linear faz o seu login com a sua própria conta (OAuth). Os agentes agem como você.

- **Claude Code:** abra o `claude` no repo → aprove o servidor `linear` → `/mcp` → **linear** → faça login.
- **Cursor:** Settings → MCP → o `linear` aparece a partir de `.cursor/mcp.json` → ative → faça login.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp` e depois siga o pedido de login.
- **Grok Build:** ele lê o `.mcp.json`; se não ler, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Faça login quando for pedido.
- **Gemini CLI / Copilot / outros:** adicione um servidor MCP remoto chamado `linear`, com a URL `https://mcp.linear.app/mcp`, nas configurações de MCP da ferramenta.

**Teste:** peça ao seu agente *"Liste as issues em Ready do time APP no Linear."*

## Rodar vários agentes ao mesmo tempo

Todo chat de agente que altera arquivos precisa da própria pasta (um git worktree), ou os chats sobrescrevem o trabalho uns dos outros. Comece cada chat de agente com `/work` (Codex: `$work`): ele verifica onde está e cria um worktree se necessário. O seu próprio chat fica na pasta principal.

| Ferramenta | Novo chat de agente |
|---|---|
| **Claude Code (VS Code)** | Nova aba de chat: Cmd+Shift+Esc (Mac) / Ctrl+Shift+Esc (Windows/Linux), ou Command Palette → "Claude Code: Open in New Tab". Digite `/work`; o Claude se move sozinho para um worktree. |
| **Claude Code (terminal)** | `claude --worktree` (ou `-w <name>`) e depois `/work`. |
| **Aplicativo de desktop do Claude** | Inicie uma sessão com a opção **worktree** e depois `/work`. |
| **Codex, Cursor, outros** | Use a opção de worktree ou de agentes em paralelo da própria ferramenta, se houver, e depois `/work`. Se não houver, digite `/work` na pasta principal: ele cria um worktree com `haam.py worktree new` e diz qual pasta abrir em uma nova janela. |

Os arquivos locais que não estão no Git (como `.env`) são copiados para cada novo worktree a partir da lista em `.worktreeinclude`. Limpe os worktrees concluídos com `python3 tools/haam/haam.py worktree clean` (plano) e depois `--apply`.

## Configurações seguras por ferramenta

As proteções principais ficam no GitHub e no git, então elas protegem você **seja o que for que a ferramenta faça**: nada de push na `main`, verificações obrigatórias, label de UAT, aprovação de deploy, o hook de segredos no commit (`make hooks`) e a varredura de segredos no CI. As configurações das ferramentas são uma segunda camada, que impede erros mais cedo. Recomendado:

| Ferramenta | Configurações recomendadas |
|---|---|
| **Claude Code** | Já configurado em `.claude/settings.json`: pergunta antes de pushes/PRs, bloqueia merges/deploys/leituras de `.env`, hook de varredura de segredos antes dos commits. Mantenha assim. |
| **Cursor** | Execução automática do agente: use uma lista de permissões (targets do make, git status/diff/log, `gh pr view/checks`) e exija confirmação para `git push`, `gh pr create/edit/merge` e qualquer coisa com `deploy`. Adicione `.env*` à lista de arquivos ignorados do Cursor, para que o agente não consiga lê-los. |
| **Codex** | Sandbox *workspace-write* e política de aprovação *on-request* (pergunta antes de ações de rede e de pushes). Evite os modos de "acesso total" neste repo. |
| **Grok Build** | Use as regras de permissão dele (permitidas no nível do repo) para exigir aprovação para `git push`, `gh pr merge` e comandos de deploy; negue a leitura de `.env*`. Ele aceita hooks `PreToolUse`: você pode chamar `bash scripts/scan-secrets.sh` antes do `git commit`, como faz o hook do Claude. Evite `--always-approve` fora do CI. |
| **Gemini CLI / Copilot** | Mantenha as confirmações ativadas para comandos de shell; nunca aprove automaticamente pushes ou merges. |

Nunca dê a nenhuma ferramenta de agente as suas credenciais de produção nem um token do GitHub com direitos de administrador.

## Verificação da primeira execução, para todas as ferramentas

Pergunte ao agente, no repo:
1. *"Quais são as regras rígidas deste repositório?"* Ele deve listar as regras de `AGENTS.md` §3. Se não listar, diga a ele que leia primeiro o `AGENTS.md` e verifique, nas configurações da ferramenta, o nome do arquivo de instruções.
2. *"Quais skills você tem para este projeto?"* Ele deve listar idea, bug, assess, spec, next, work, build, uat… Se não listar, veja a tabela acima.
3. *"Liste as issues em Ready do time APP no Linear."* Isso verifica a conexão com o Linear.

## Registrar qual ferramenta fez o trabalho
O comentário de reserva na issue e o campo **Feito com (Built with)** do PR registram a ferramenta e o modelo. Depois de algumas semanas, você pode comparar os apontamentos das revisões e as falhas no UAT por ferramenta.

## Revisão com outro modelo
Os agentes revisores do CI usam o Claude. Quando o código é escrito com uma ferramenta diferente (Codex, Grok, Cursor com outro modelo), a revisão também é feita por outro modelo, o que é uma verificação extra útil.
