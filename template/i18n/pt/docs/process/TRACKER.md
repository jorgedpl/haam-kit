# O tracker: Linear ou GitHub Projects

O HAAM funciona da mesma forma com qualquer um dos dois trackers. `haam.config.json` → `"tracker"` diz qual deles este projeto usa:

- **`github`**: issues neste repositório do GitHub, em um quadro do GitHub Projects. Gratuito em todos os planos do GitHub. Os agentes usam `python3 tools/haam/haam.py issue …` (abaixo), que funciona a partir de qualquer ferramenta de agente.
- **`linear`**: issues em um time do Linear. Os agentes usam a conexão com o Linear (MCP).

As skills dizem "no tracker"; esta página explica como fazer cada operação em cada tracker. **Agentes: verifiquem `tracker` em `haam.config.json` uma vez por sessão e depois usem a coluna correspondente.**

## Conceitos

| Conceito | GitHub Projects | Linear |
|---|---|---|
| ID da issue (escreva assim) | `#123` | `APP-123` |
| Nome da branch | `123-short-title` | `app-123-short-title` (o nome de branch do Linear) |
| Mensagem de commit | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Título do PR | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Vínculo PR → issue | **`Refs #123`** na descrição do PR (não `Closes`: a issue é fechada no `/release`, depois do deploy) | ID da issue no título do PR |
| Arquivos da issue | `docs/specs/GH-123-slug.md` (o mesmo vale para avaliações e UAT) | `docs/specs/APP-123-slug.md` |
| 12 status | Campo **Status** do quadro | Status do workflow do time |
| Prioridade | Campo **Priority** do quadro (Urgent/High/Medium/Low) | Prioridade nativa |
| Fluxos, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Labels da issue | Labels da issue |
| Epic (agrupa as issues de uma funcionalidade) | Issue com a label `epic`; as issues dele são **sub-issues** do GitHub | Issue com a label `epic`; as issues dele são **sub-issues** (com o pai definido) |
| Quem está trabalhando nela | Status In Progress (construindo) ou label `claimed` (avaliando, escrevendo uma spec, construindo um protótipo), mais o comentário de reserva. Só a pessoa atribuída não permite distinguir dois chats da mesma pessoa | Igual |
| Mudança de status ao abrir/fazer merge de um PR | Workflow `tracker-sync.yml`: só as issues sendo entregues (não os epics, nem PRs só de documentação, nem spikes) | Integração do Linear com o GitHub |

## Operações

Os comandos da coluna GitHub rodam a partir da raiz do repositório. Adicione `--json` para uma saída legível por máquina.

| Operação | GitHub Projects | Linear (via MCP) |
|---|---|---|
| **Encontrar trabalho** (filas do `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (adicione `--label agent-ready` para funcionalidades, `--label stream:bug` para bugs) | Listar as issues do time por status, label, pessoa atribuída |
| **Ler uma issue** | `haam.py issue view 123` | Obter a issue |
| **Criar uma ideia** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (cai em Triage) | Criar a issue, status Triage, label `stream:idea` |
| **Relatar um bug** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Criar a issue, status Triage, label `stream:bug` |
| **Criar um epic** | `haam.py issue create --epic --stream idea --title "…"` | Criar uma issue com a label `epic` |
| **Colocar uma issue em um epic** | `haam.py issue link 14 --parent 9` | Definir o epic como pai da issue |
| **Criar uma issue dentro de um epic** (por exemplo, partes de uma spec, lacunas) | `haam.py issue create --stream feature --parent 9 --title "…"` | Criar uma sub-issue do epic |
| **Os campos próprios do quadro** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` os lista, com as opções. Defina-os com `--field NAME=VALUE` em `issue create` ou `issue edit` (pode repetir; um valor vazio limpa o campo; `Sprint=@current` é a iteração em andamento hoje) e filtre com `issue list --field Area=Billing`. Um nome ou valor errado é recusado antes de qualquer mudança | Os campos próprios do time, com a conexão com o Linear |
| **Tirar uma issue de um epic** | `haam.py issue unlink 14` | Remover o pai da issue |
| **Reescrever uma issue** (título, descrição) | `haam.py issue edit 14 --title "…" --body-file new.md` | Atualizar a issue |
| **As issues de um epic** | `haam.py issue children 9` (com o progresso) | Listar as sub-issues do epic |
| **Issues fora de qualquer epic** | `haam.py issue list --open-only --no-parent --no-label epic` | Listar as issues sem pai |
| **Reservar** (antes de construir, avaliar ou escrever uma spec) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (construção: recusa se já estiver reservada ou não estiver em Ready; `--force` para bugs corrigidos direto a partir de Triage, só quando a pessoa pediu). Avaliar: adicione `--for assess`; escrever uma spec: `--for spec`. O comando imprime um id de reserva: guarde-o | Buscar de novo; se estiver In Progress, com a label `claimed` ou atribuída a outra pessoa, parar; caso contrário, atribuir a você, definir In Progress (construção) ou adicionar a label `claimed` (avaliação, spec), comentar com um id de reserva, reler os comentários (AGENTS.md §6) |
| **Construir um protótipo** (`/spike`) | `haam.py issue claim 123 --for spike` (ideias de Triage a Decision, funcionalidades em Backlog) e, depois do push: `issue label 123 --add spike-ready` e `issue release 123 --claim <id> --status Decision` (uma funcionalidade em Backlog: sem `--status`) | Reservar como acima (label `claimed`, um comentário de reserva dizendo "para construir um protótipo"), label `spike-ready`, liberar |
| **Código de produção em uma mudança** | `haam.py production` (os arquivos alterados por uma branch que rodam para os usuários) | Igual |
| **Liberar uma reserva** (avaliação ou spec enviada; ou o chat parou) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` em vez do id, só no `/triage stale` ou no `/test`) | Remover a pessoa atribuída, remover `claimed`, definir o status, comentar `🔓 Claim released` |
| **Mudar o status** | `haam.py issue status 123 "UAT"` | Atualizar o status da issue |
| **Status exclusivos de pessoas** (Done, Parked, Canceled, Decision→Backlog) | Igual, mais `--human`, **somente** dentro de `/triage`, `/epic`, `/decide`, `/test`, `/release` ou `/override` digitados por uma pessoa | Mesma regra |
| **Prioridade** | `haam.py issue priority 123 High` | Atualizar a prioridade |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` também exige `--human`, depois que a pessoa aprovou a spec) | Atualizar as labels |
| **Comentar** | `haam.py issue comment 123 --body "…"` ou `--body-file` | Criar um comentário |
| **Rejeitar ou marcar como duplicada** (no `/triage`, `/epic` ou `/decide`) | `haam.py issue status 123 Canceled --human` (também fecha a issue como não planejada); comente o motivo ou o ID da original | Status Canceled, comentário |
| **Testar uma mudança** (pessoa, no `/test`) | `haam.py checkout-pr 123` e depois `haam.py checkout-pr --back` | Igual (o código está no GitHub em qualquer caso) |
| **Abrir o PR depois de uma aprovação** (test-first, a pessoa disse `pass`) | `haam.py publish 123 --human`: faz push do commit testado, abre o PR com a label `uat-passed`, move a issue para In Review | `haam.py publish APP-123 --human` (`--label human-review` se a issue tiver essa label) e depois mover a issue para In Review e comentar, como o comando indica |
| **Registrar um teste reprovado** (a pessoa disse que falhou) | `haam.py test-failed 123 --human` e depois label `uat-failed`, status Ready, sem pessoa atribuída | `haam.py test-failed APP-123 --human` e depois o mesmo no Linear |
| **Colocar em produção depois de uma aprovação** (a pessoa disse `ship`) | `haam.py ship 123 --human`: merge, aprovação do deploy, espera, fechamento | `haam.py ship APP-123 --human` e depois definir Done no Linear |
| **Colocar em produção tudo o que está pronto, com um deploy** | `haam.py ship --all --human` (ou `ship 12 13 14 --human`): faz o merge de cada uma, aprova só o deploy mais novo, fecha todas | `haam.py ship APP-12 APP-13 --human` (liste-as: `--all` não consegue ler o Linear) |
| **Ver ou mudar como o HAAM roda** (product owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (só por escolha do product owner) | Igual |
| **Rodar o CI aqui** (configuração `ci: local`) | `haam.py local-ci 123` (o ship roda isso por você) | Igual |
| **Sem UAT para esta issue** (decisão do product owner) | `haam.py issue label 123 --add uat:skip --human` | Label `uat:skip` |
| **Há espaço para trabalho novo?** (o `/next` verifica primeiro) | `haam.py capacity` (a fila de UAT e os PRs prontos em comparação com `max_in_uat`, `max_open_prs` ou o aumento de uma janela de lote; rascunhos e PRs só de documentação não contam) | O mesmo comando, com `--in-uat <count>` |
| **O trabalho novo vai colidir com o que está esperando?** | `haam.py overlap --files src/auth/,src/api/users.py` (branches em UAT que alteram os mesmos arquivos) | Igual, com `--branch <name>` para cada branch em UAT |
| **PR em lote** (os bugs de um epic) | Título `#12 #13 #14: …`, uma linha `Refs #n` por issue; o `ship` fecha todas | Título `APP-12 APP-13: …` |
| **Fechar depois da release** | `haam.py issue close 123 --human` (define Done e fecha; só no `/release`) | Status Done |

## Regras que valem para os dois

- Todo trabalho tem uma issue no tracker; nada é acompanhado em outro lugar.
- Se não for possível acessar o tracker, pare e avise a pessoa.
- O protocolo de reserva é o que impede que dois chats de agente (ou duas máquinas) construam, avaliem ou especifiquem a mesma coisa. Nunca o pule.
- As mudanças exclusivas de pessoas só acontecem dentro das skills exclusivas de pessoas, e a ferramenta pede `--human` no GitHub como lembrete. Os agentes agem com o próprio login do product owner, então o GitHub não consegue saber quem colocou uma label que é decisão do product owner (`uat:skip`, `mode:prototype`, `mode:epic-build`): isso é uma regra, verificada pela ferramenta no GitHub Projects e por nada no Linear. Um agente que a quebrasse usando `gh` diretamente poderia, com `uat:skip`, deixar uma mudança fora das áreas protegidas pular o seu teste; o CI e as duas revisões por IA continuam rodando, e os deploys continuam esperando por você onde o seu plano permite.

## Configuração do GitHub Projects (admin, uma vez)

1. `gh auth refresh -s project` (permite que o seu login do GitHub use o Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plano) e depois `--apply`: cria o quadro com o nome do produto, vincula o repo, define os 12 status e o campo Priority e cria as labels.
4. **Token de automação** (para o `tracker-sync.yml` e para o auto-merge na via sem UAT): crie um token clássico em github.com/settings/tokens com os escopos `project` e `repo` (`public_repo` basta para um repositório público) e depois rode `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Sem ele tudo funciona, mas os cartões não se movem sozinhos quando os PRs são abertos ou integrados, e a via sem UAT não consegue ativar o auto-merge (o gate usa esse token porque um merge feito com o token do próprio workflow não iniciaria o deploy). Nos projetos com Linear, a via nunca faz auto-merge, então o token não é necessário para ela.
5. **No navegador**, no quadro: crie as visualizações salvas que a configuração lista (Board agrupado por Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics) e ative o workflow nativo **Auto-add to project** do quadro para este repositório (quadro → Workflows). Ele coloca no quadro, de graça, as issues criadas no site do GitHub; o `haam.py issue create` adiciona as dele. **Desative** o workflow nativo **Item closed → Status: Done**: ele sobrescreve `Canceled` depois que `issue status … Canceled` fecha a issue, e o `ship` já define Done sozinho.
6. Cada desenvolvedor roda `gh auth refresh -s project` uma vez; o `/haam-onboard` verifica isso.

## Trocar de tracker depois

Defina `"tracker"` com `haam.py config --tracker …`, rode a configuração do novo tracker e depois peça ao seu agente que copie as issues abertas de um para o outro (ele consegue ler um tracker e escrever no outro). Mantenha o tracker antigo como somente leitura, para o histórico.
