# Trabalhar como gerente de produto

*Um guia para a pessoa que decide o que é construído. Os agentes não precisam lê-lo; você precisa.*

No HAAM, você decide **o quê** e **por quê**; os agentes descobrem **como** e fazem. Os agentes são rápidos, então a velocidade do sistema todo é definida pela rapidez com que você faz a triagem, decide, aprova e testa. Seu trabalho principal é manter curta a fila **Waiting on me** e apontar a **Agent queue** para as coisas certas.

Os exemplos usam IDs do GitHub Projects (`#12`); no Linear, o mesmo item é `APP-12`. Os comandos estão escritos como `/name`; no Codex, use `$name`.

---

## 1. Seu trabalho em uma página

| O que só você faz | Com que frequência | Com IA | Diretamente no tracker |
|---|---|---|---|
| Manter `docs/product/PRODUCT.md` atualizado: prioridades atuais, inegociáveis, jornadas principais | Mensal | "Atualize o PRODUCT.md: nossas prioridades agora são…" | Editar o arquivo (por meio de um PR) |
| Fazer a triagem de novas ideias e bugs | Diária | `/triage` | Visualização Triage: prioridade, status, labels |
| Agrupar issues relacionadas em epics e responder às perguntas do agente sobre cada um | Semanal | `/triage group` e depois `/epic #9` | Issue de epic (label `epic`) com sub-issues |
| Definir e mudar prioridades | Diária e semanal | `/triage`, `/triage backlog` | Campo Priority |
| Decidir sobre ideias avaliadas (G1) | Semanal | `/decide #12 approve high` | Status, labels, comentário (§7–8) |
| Aprovar specs (G2) | À medida que chegam | Ler a spec (vinculada na issue) e depois "spec da #12 aprovada" | Comentar "spec aprovada"; Status Ready, label `agent-ready` |
| Testar mudanças (G4) e colocá-las em produção (G5) | Diária | `/test` e depois responder `pass` → `ship`, ou dizer o que está errado | GitHub: label `uat-passed`, merge, aprovar o deploy |
| Fechar os acompanhamentos de override | Semanal | "Mostre os acompanhamentos de override abertos" | Visualização: label `override-followup` |

Tudo o que você decide vai para o tracker ou para o Git, nunca só para um chat. Se não estiver escrito lá, o próximo agente não sabe.

---

## 2. Seu ritmo

### Diário (10–15 minutos)
1. **Teste primeiro.** Digite `/test all`: o agente conduz você por todas as mudanças que estão esperando por você, uma depois da outra (§2a), e depois coloca em produção tudo o que passou, com um único deploy. Os agentes não conseguem terminar enquanto você não terminar, e o contexto deles fica desatualizado.
2. **Esvazie a caixa de entrada de Triage** (`/triage`, ou a visualização Triage). Nada deve ficar ali por mais de dois dias úteis.
3. **Bugs urgentes:** se houver algum, coloque um agente nele agora: nova janela de chat, `/work bugs`.
4. Dê uma olhada nos comentários de passagem e de "bloqueado" dos agentes e responda às perguntas deles.

### 2a. Testar uma mudança: o ciclo completo
1. Digite **`/test`** (ou `/test #12`). O agente coloca a mudança no seu computador, inicia o aplicativo e dá a você o link e uma checklist curta: *faça isto → você deve ver aquilo*.
2. Experimente. Depois responda com uma palavra ou uma frase:
   - **`pass`** → o agente abre o pull request (até agora não havia nenhum: você testou a branch do agente), as verificações rodam uma única vez exatamente sobre o que você testou, e ele pergunta *"Coloco em produção quando as verificações passarem?"* Responda **`ship`**: ele espera as verificações, faz o merge, aprova o deploy para produção por você e fecha a issue. Você recebe *"A #12 está no ar."* Responda `later` para segurar.
   - Se o seu projeto **faz deploy à mão** (`"deploy": "manual"`), o agente faz o merge e depois pede que você faça o deploy; responda **`live`** quando estiver no ar, e ele fecha a issue.
   - Se as verificações ou as revisões encontrarem um problema depois disso, a mudança volta para os agentes como um teste reprovado e retorna para você quando estiver corrigida.
   - **O que deu errado** (*"passo 3: o botão de exportar continua faltando no celular"*) → o agente registra isso na issue, coloca a label `uat-failed` e a manda de volta para os agentes, que a corrigem primeiro. Quando estiver corrigida, ela volta para o `/test`.
3. É só isso. Você não precisa mexer em branches, labels nem no quadro.

**A forma como o HAAM roda é escolha sua.** Digite `/haam-settings`: ele passa por cada configuração com os seus próprios números (minutos do Actions, a fila de UAT), recomenda uma opção e aplica o que você escolher:
- quando o CI e as revisões por IA rodam (em todo PR, no seu computador, só para áreas protegidas ou nunca);
- o que você mesmo testa (tudo, o que você decidir para cada issue, ou bugs sem teste);
- como as mudanças são agrupadas (por issue, por epic ou em um único PR de release para tudo o que você aprovou);
- se os deploys esperam a sua aprovação;
- os limites.

`python3 tools/haam/haam.py settings --explain` lista todas elas.

**Mudanças que você não consegue testar** (atualizações do kit ou de configuração, atualizações de dependências, refatorações que você não perceberia, CI): marque-as com `uat:skip` ao fazer a triagem, ou diga "spec aprovada, sem UAT". Elas nunca chegam ao `/test`: o PR delas faz merge sozinho quando o CI e as duas revisões por IA passam (GitHub Projects), e o seu próximo `ship` faz o deploy delas junto com todo o resto e as fecha. Se você ficar um tempo sem colocar nada em produção, rode `/test` e responda `ship` mesmo assim, ou `ship --all`: o deploy delas espera a sua aprovação. No Linear, coloque-as em produção pelo nome (`ship APP-12 --human`). Use isso só para mudanças que nenhum usuário perceberia; nunca para áreas protegidas.

### Semanal (30–45 minutos)
1. **Agrupe** as issues soltas em epics (`/triage group`) e defina com o agente o epic do topo (`/epic #9`).
2. **Decida** tudo o que está em **Decision** (G1).
3. **Revise as specs** (vinculadas em cada issue) e aprove ou comente (G2).
4. **Reordene** Ready e Backlog de acordo com as prioridades atuais (`/triage backlog`).
5. **Encontre o trabalho parado:** `/triage stale` (reservado mas sem movimento, UAT esperando há tempo demais, decisões atrasadas).
6. **Reveja os itens em Parked** cujo "rever quando" já aconteceu.
7. **Feche os acompanhamentos de override** (label `override-followup`).
8. Melhore uma coisa no processo (uma `/idea` com a label `area:process`).

### Mensal ou trimestral (30 minutos)
1. Reescreva as **Prioridades atuais** no `PRODUCT.md`: 3–5 resultados, em ordem. Os agentes as usam para sugerir prioridades e desempatar, então essa é a coisa mais útil que você pode manter atualizada.
2. **Pode:** tudo o que é Low e está esperando há mais de dois meses → coloque em Parked com um "rever quando". Um backlog curto é um backlog utilizável.

---

## 3. Triagem: decidir o que é cada item novo

O status **Triage** é a sua caixa de entrada. Ideias e bugs chegam ali pelo `/idea`, pelo `/bug`, pelos formulários de issue, por outras pessoas e pelos agentes. Tente terminar cada dia com a caixa de entrada vazia.

Se vários itens parecerem relacionados, ou se a maioria deles não tiver contexto, **agrupe-os primeiro** (§4): fazer a triagem de uma funcionalidade de cada vez é mais rápido e melhor do que fazer a triagem de fragmentos.

Para cada item, responda a quatro perguntas:

1. **Está claro e é novo?** Duplicado → feche-o e vincule o original. Informação insuficiente → comente com a sua pergunta e deixe-o em Triage.
2. **O que é?** Um **bug** significa que algo não funciona como deveria. Uma **ideia** significa um comportamento novo ou alterado. "Funciona como foi projetado, mas o usuário esperava outra coisa" é uma ideia, não um bug. Corrija a label de fluxo se estiver errada.
3. **Qual é a importância?** Defina a prioridade (§5).
4. **O que acontece em seguida?**

| Item | Sua decisão | Status depois | O que vem em seguida |
|---|---|---|---|
| Bug com passos claros para reproduzir | **Ready** | Ready, com uma prioridade | Um agente o pega (`/work bugs`) |
| Bug sem informação suficiente | **Precisa de informação** | Continua em Triage, com a sua pergunta como comentário | Você ou quem relatou responde, e depois você faz a triagem de novo |
| Bug urgente | **Ready, começar agora** | Ready, Urgent | Coloque um agente nele agora; o `/override` está disponível se o deploy não puder esperar |
| Ideia que vale a pena explorar | **Avaliar** | Discovery, com uma prioridade | Um agente escreve a avaliação (`/work ideas` ou `/assess #12`) |
| Ideia que você entenderia melhor experimentando | **Protótipo** | Discovery, label `mode:prototype` | Um agente constrói uma versão descartável que funciona (`/spike #12`); você a experimenta com `/test` e decide |
| Boa ideia, hora errada | **Estacionar** | Parked, com um comentário "rever quando…" | Volta em uma revisão semanal |
| Ideia que você não vai fazer | **Rejeitar** | Canceled, com um motivo de uma linha | Fechada |
| Duplicada | **Duplicada** | Canceled, vinculada à original | Fechada |

Ideias pequenas também passam pela avaliação. Peça uma rápida ("avalie a #12, de forma breve"). A avaliação é onde o agente verifica o código e os riscos, e ela custa a você um minuto de leitura.

---

## 4. Epics: agrupar issues em funcionalidades

Issues isoladas muitas vezes não têm contexto. "Botão de exportar faltando no celular", "Exportar para CSV" e "Relatórios agendados" são três fragmentos de uma mesma funcionalidade e, triados um a um, cada um parece pequeno e pouco claro. Um **epic** é uma issue pai (label `epic`) que agrupa as issues de um mesmo resultado e traz o contexto que falta a elas: para quem é, como é o sucesso, o que está dentro e fora do escopo e a ordem das partes. Esse contexto fica em um **briefing do epic** curto em `docs/epics/`.

**Use um epic para:** três ou mais issues sobre o mesmo resultado; uma ideia grande demais para uma única spec (tamanho L ou XL); um pedido que afeta várias telas ou módulos.
**Não use um epic para:** um único bug; um balaio de "diversos" com coisas não relacionadas; um tema que nunca acaba ("desempenho", "polimento de UX"): esses são prioridades, não epics. Um epic deve poder ser concluído, em semanas e não em trimestres.

### Como um epic avança
1. **Agrupar.** `/triage group` olha as issues soltas e propõe epics: um título, o resultado em uma linha, quais issues pertencem a ele e por quê. Você diz `ok` ou ajusta (`merge 2 and 3`, `#40 out`). Ou comece por um tema: `/epic "reporting"`.
2. **Definir.** `/epic #9`: o agente lê todas as issues do epic, o contexto do produto e o código relevante, faz um rascunho do briefing e depois **faz até cinco perguntas a você por rodada**: para quem é, como é o sucesso, o que é obrigatório e o que é desejável, restrições, o que não pode mudar, qual a posição na fila. Depois ele propõe uma limpeza: duplicatas a fechar, lacunas a adicionar como novas issues, issues pouco claras a reescrever, issues grandes a dividir, uma ordem. Nada muda até você confirmar.
3. **Decidir uma vez (G1).** `/assess #9` adiciona o esforço e a viabilidade do epic inteiro; `/decide #9 approve high` aprova o epic e as ideias dentro dele de uma só vez.
4. **Spec e construção parte por parte.** Cada sub-issue recebe a própria spec e passa pelo G2 separadamente. Os agentes constroem as sub-issues, nunca o epic em si.
5. **Concluir.** Quando a última sub-issue vai para produção, o agente se oferece para fechar o epic.

**Prioridades:** dê uma prioridade ao epic; as issues dele recebem a mesma, a não ser que você diga o contrário. Um bug dentro de um epic ainda pode ser mais urgente do que o epic.

**Responder às perguntas do agente:** respostas curtas estão ótimas. "Ainda não sei" é uma resposta válida: a questão fica em aberto no briefing. Responda sobre o que os usuários precisam e por quê; deixe o como para os agentes.

### Epics diretamente no tracker
- **GitHub Projects:** crie uma issue e adicione a label `epic`; depois, na seção de sub-issues do epic, adicione as issues que pertencem a ele (ou defina o pai a partir de cada issue). No quadro, use a visualização **Epics** e mostre os campos *Parent issue* e *Sub-issues progress* nas visualizações de tabela, para que cada cartão mostre o seu epic.
- **Linear:** crie uma issue com a label `epic` e transforme as issues relacionadas em sub-issues dela (defina o pai delas). Para uma iniciativa muito grande, que abrange vários epics, um projeto do Linear pode reunir os epics.

---

## 5. Priorizar

### 5.1 Os quatro níveis

| Prioridade | Critério | Tratamento esperado |
|---|---|---|
| **Urgent** | A produção está quebrada em uma jornada principal, dados podem ser perdidos ou expostos, há uma falha de segurança ou um prazo legal/de conformidade está em risco | Começar hoje. Os gates podem ser contornados, com um acompanhamento |
| **High** | Faz avançar diretamente uma das prioridades atuais do `PRODUCT.md`, ou é um bug em uma jornada principal sem alternativa de contorno | É o próximo, nesta semana |
| **Medium** | Útil, mas fora das prioridades atuais, ou as evidências são fracas | Na ordem, quando não houver nada High |
| **Low** | Seria bom ter, cosmético, caso-limite | Quando não houver outra coisa; podar depois de dois meses |
| *(nenhuma)* | Ainda sem triagem | Os agentes não vão construir |

Seja honesto: se mais de cerca de um em cada cinco itens abertos for High ou Urgent, os níveis deixaram de significar alguma coisa. Rebaixe algo.

### 5.2 Bugs: impacto × alcance

| | A maioria dos usuários, ou uma jornada principal | Alguns usuários | Poucos usuários, ou um caso-limite |
|---|---|---|---|
| **Bloqueia a tarefa, perde ou expõe dados, segurança, questão legal** | Urgent | Urgent | High |
| **Resultado errado, mas há uma alternativa de contorno** | High | Medium | Low |
| **Incômodo ou cosmético** | Medium | Low | Low |

### 5.3 Ideias e funcionalidades: valor, confiança, tamanho

Depois de uma avaliação, você tem três coisas: **valor** (quanto isso faz avançar uma prioridade atual), **confiança** (quão boas são as evidências) e **tamanho** (XS–XL, a partir do código). Regras práticas:
- **High:** valor claro para uma prioridade atual, boas evidências, tamanho S–M.
- **Medium:** bom valor, mas evidências mais fracas; ou valor alto, mas tamanho L–XL (peça para dividir).
- **Low:** pouco valor, seja qual for o tamanho.
- **Fora das prioridades atuais?** No máximo Medium, a não ser que você mude as prioridades primeiro.

Para comparar duas ideias rapidamente: valor (1–3) × confiança (0,5 / 0,8 / 1) ÷ tamanho (XS 1, S 2, M 3, L 5, XL 8). A maior pontuação vai primeiro. É um critério de desempate, não uma fórmula a ser obedecida.

### 5.4 Ordem dentro de uma prioridade
Os agentes pegam **bugs antes de funcionalidades, os mais antigos antes dos mais novos, os menores antes dos maiores**. Eles leem a prioridade, não a posição de um cartão no quadro. Se X precisa acontecer antes de Y, dê a X uma prioridade maior ou escreva `Blocked by #X` na descrição de Y.

### 5.5 Mantenha as filas saudáveis

| Fila | Tamanho saudável | Se não for |
|---|---|---|
| **Agent queue** (Ready) | 3–10 itens | Vazia: os agentes ficam parados, então escreva mais specs. Mais de 10: as prioridades ficam desatualizadas, então reordene |
| **Decision** | 5 ou menos | Reserve 20 minutos e decida |
| **UAT** | `max_in_uat` (padrão 10) | Os agentes seguram novas construções no limite (`haam.py capacity`): é o seu tempo para testar, o principal limite no test-first. Teste com `/test all`; os itens que os agentes verificaram por completo passam com uma única resposta (`pass all verified`). Para um fim de semana de trabalho dos agentes, abra uma janela de lote no `/haam-settings`: um aumento que termina sozinho |
| **Agentes rodando** | Não mais do que você consegue testar amanhã | Menos agentes, itens menores |
| **PRs prontos** | `max_open_prs` em `haam.config.json` (padrão 10) | Os agentes seguram novas construções no limite: cada PR pronto gasta minutos de CI a cada push. Rascunhos e PRs só de documentação não contam. Specs e avaliações continuam. Teste e coloque em produção o que está aberto |

### 5.6 Mudar prioridades
Mude-as sempre que os fatos mudarem, mas diga por quê em um comentário. Os agentes e os colegas leem o histórico. Nunca rebaixe um item Urgent em silêncio: comente e avise quem o relatou.

---

## 6. Fazer com IA

Use **o seu próprio chat na pasta principal do projeto**, não um dos chats de agente que estão rodando `/work`.

| Você quer… | Digite |
|---|---|
| Agrupar issues soltas em epics | `/triage group` |
| Definir um epic: briefing, perguntas para você, limpeza | `/epic #9` (ou `/epic "reporting"` para começar por um tema) |
| Fazer a triagem da caixa de entrada | `/triage` |
| Reordenar Ready e Backlog de acordo com as prioridades | `/triage backlog` |
| Encontrar trabalho parado ou esquecido | `/triage stale` |
| Capturar uma ideia ou um bug de qualquer lugar | `/idea …`, `/bug …` |
| Pedir a avaliação de uma ideia | `/assess #12` (ou deixe que `/work ideas` a pegue) |
| Decidir (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Aprovar uma spec (G2) | Leia-a (vinculada na issue) e depois: "spec da #12 aprovada" |
| Testar uma mudança e depois colocá-la em produção ou devolvê-la (G4, G5) | `/test` (ou `/test #12`) e depois `pass` → `ship`, ou diga o que está errado |
| Fechar algo que entrou de outra forma | `/release #12` |
| Emergência | `/override #12 "<reason>"` |

**Como o `/triage` funciona.** O agente lê o `PRODUCT.md` e os itens e depois mostra a você uma tabela: fluxo proposto, prioridade, próximo passo e um motivo curto para cada um. Responda `ok` para aplicar tudo, ou com mudanças (`#14 Low, #9 park until Q3`). Ele não muda nada até você responder, aplica exatamente o que você confirmou e comenta em cada item, para que o motivo fique registrado. Ele nunca aprova ideias por você; para isso, ele indica o `/decide`.

**Perguntas que vale a pena fazer ao seu agente:**
- "O que está esperando por mim?"
- "O que os agentes terminaram desde ontem, e o que está bloqueado?"
- "Quais itens em Ready não se encaixam nas nossas prioridades atuais?"
- "A #12 é grande demais. Proponha uma divisão em partes de tamanho S."
- "Compare a #12 e a #15: qual deve ir primeiro, e por quê?"
- "Faça um rascunho de novas prioridades atuais para o PRODUCT.md, com base no que já colocamos em produção e no que está no backlog."

As sugestões do agente são rascunhos, e as decisões são suas. Quando o `/bug` registra um bug, ele preenche uma prioridade sugerida; você a confirma ou muda quando faz a triagem.

---

## 7. Fazer diretamente no GitHub Projects

Tudo o que foi descrito acima pode ser feito à mão no quadro. As visualizações salvas (criadas com `haam.py github-project`) são o seu espaço de trabalho:

| Visualização | Use para |
|---|---|
| **Triage** (status: Triage) | A sua caixa de entrada diária |
| **Epics** (label: epic) | Cada funcionalidade e até onde as sub-issues dela chegaram |
| **Waiting on me** (status: Decision, UAT) | Decisões e testes |
| **Agent queue** (status: Ready, sem pessoa atribuída) | O que os agentes vão pegar em seguida, por prioridade |
| **Bugs** | Todos os bugs abertos, por prioridade |
| **Ideas inbox** | Ideias em triagem ou em avaliação |
| **Board** | O fluxo inteiro, agrupado por status |

| Tarefa | No quadro |
|---|---|
| Fazer a triagem de um item | Abra-o. Defina **Priority** e **Status**; corrija a label de fluxo na barra lateral da issue; comente o seu motivo |
| Estacionar | Status **Parked** e um comentário: "rever quando…" |
| Rejeitar ou marcar como duplicada | Status **Canceled** e depois feche a issue como *not planned* ou *duplicate* |
| Aprovar uma ideia (G1) | Status **Backlog**; substitua a label `stream:idea` por `stream:feature`; defina Priority; comente "Aprovada" |
| Aprovar uma spec (G2) | Comente "spec aprovada" na issue; depois Status **Ready** e label `agent-ready` |
| Agrupar issues em um epic | Crie uma issue com a label `epic`; adicione as outras como sub-issues dela |
| Reordenar muitos itens | Layout de tabela, agrupado ou ordenado por Priority; edite as células (você pode copiar um valor e colá-lo em várias células selecionadas) |

Deixe isto para as skills: a reserva (**In Progress**) é trabalho dos agentes. Testar e colocar em produção é mais fácil com o `/test`; à mão, é assim: adicione a label `uat-passed` ao PR (isso libera o merge), faça o merge, aprove o deploy (Actions → a execução → Review deployments) e depois defina a issue como **Done** e feche-a. Se o teste falhou, comente na issue o que está errado, adicione a label `uat-failed`, volte-a para **Ready** e remova a pessoa atribuída.

---

## 8. Fazer diretamente no Linear

| Tarefa | No Linear |
|---|---|
| Triagem | Use a caixa de entrada **Triage** do time. Você pode aceitar, recusar, marcar como duplicada ou adiar. Depois de aceitar, **defina você mesmo o status do HAAM** (Ready para um bug, Discovery para uma ideia a avaliar), porque aceitar move o item para o status padrão do time. Defina a prioridade |
| Estacionar ou rejeitar | Status **Parked** ou **Canceled**, com um comentário |
| Agrupar issues em um epic | Crie uma issue com a label `epic`; defina-a como pai das issues relacionadas |
| Aprovar uma ideia (G1) | Status **Backlog**, substitua a label `stream:idea` por `stream:feature`, defina a prioridade, comente |
| Aprovar uma spec (G2) | Comente "spec aprovada" na issue; depois status **Ready** e label `agent-ready` |
| Reordenar | As visualizações de `docs/setup/LINEAR-SETUP.md` §7, ordenadas por prioridade; o menu de comandos (Cmd/Ctrl+K) muda a prioridade ou o status rapidamente |

Assim como no GitHub, os agentes seguem o campo de prioridade, não a ordem manual de uma lista.

---

## 9. Trabalhar com outras pessoas

- **Um product owner por produto** define as prioridades e aprova os gates. Todas as outras pessoas propõem: `/idea`, `/bug`, comentários.
- Peça aos colegas que sugiram uma prioridade quando relatarem algo. Você a confirma na triagem.
- **As discordâncias ficam na issue,** não em chats privados. O product owner decide e diz por quê em um comentário.
- Se você for se ausentar, indique um aprovador substituto (`haam.py config --backup-approvers`) e diga a ele quais itens podem avançar sem você.

---

## 10. Manter baixos os custos do GitHub Actions

Todo pull request roda o CI e duas revisões por IA nas máquinas do GitHub, e os repositórios privados têm uma cota mensal de minutos. Os agentes trabalham rápido, então a cota pode acabar em poucos dias. O que mais ajuda, em ordem:
1. **Olhe primeiro:** `python3 tools/haam/haam.py ci-usage` mostra quais workflows e jobs usaram os minutos.
2. **Menos pull requests:** junte os itens pequenos de um epic em um só (`/work epic #9`) e mantenha baixo o limite de PRs abertos (`max_open_prs` em `haam.config.json`).
3. **Revisões no seu computador:** `haam.py settings --set review=local --apply --human` (ou `/haam-settings`). As revisões por IA passam a usar o seu plano do Claude em vez de minutos; as áreas protegidas (`human-review`) continuam sendo revisadas no GitHub. O custo-benefício: no GitHub, o resultado da revisão é à prova de adulteração; localmente, não. As revisões rodam em sessões novas e somente leitura, com as instruções da `main`, mas quem as inicia é o agente que construiu a mudança, e qualquer coisa que use o seu login poderia publicar um resultado aprovado. Para mais separação, rode você mesmo `haam.py review <ID>` a partir do seu próprio chat.
4. **O seu próprio runner:** `haam.py settings --set runner=self-hosted --apply --human` depois de registrar uma máquina que fica sempre ligada (`docs/setup/GITHUB-SETUP.md` §8).
5. **Peça um CI menor:** se o projeto tiver partes separadas (por exemplo, backend e aplicativo móvel), peça a um agente que faça o `make check` rodar só as partes que um PR altera.

## 11. Armadilhas a evitar

- **Tudo é High.** Então nada é. Rebaixe até que cerca de um item em cada cinco seja High ou Urgent.
- **Mais agentes do que você consegue testar.** O trabalho se acumula em UAT e fica desatualizado. Itens menores e em menor número andam mais rápido.
- **"Só construa" em um chat.** Crie a issue primeiro (`/bug`, `/idea`): leva um minuto e preserva o histórico, a prioridade e a reserva.
- **Aprovar uma spec sem ler os critérios de aceitação.** É isso que o agente constrói e é com base nisso que você testa. Leia-os.
- **Prioridades só na sua cabeça.** Se não estiverem no `PRODUCT.md` e no tracker, os agentes não conseguem segui-las.
- **Construir fragmentos sem a visão geral.** Se várias issues forem, na verdade, uma única funcionalidade, agrupe-as em um epic e defina-o antes que alguém escreva as specs das partes.
- **Epics que nunca terminam.** Se um epic está aberto há meses, separe o que já está feito e feche-o.
- **Deixar Triage para "depois".** A caixa de entrada cresce, e os bugs urgentes se escondem nela.

---

## 12. Checklists

**Diária**
- [ ] Tudo o que está em UAT testado com `/test`
- [ ] Caixa de entrada de Triage vazia
- [ ] Os bugs urgentes têm um agente trabalhando neles
- [ ] As perguntas dos agentes respondidas

**Semanal**
- [ ] Issues soltas agrupadas em epics; o epic do topo definido
- [ ] Fila de Decision decidida
- [ ] Specs aprovadas ou comentadas
- [ ] Ready e Backlog reordenados
- [ ] Trabalho parado cobrado (`/triage stale`)
- [ ] Itens em Parked revistos
- [ ] Acompanhamentos de override fechados
- [ ] Uma melhoria de processo registrada

**Mensal**
- [ ] Prioridades atuais do `PRODUCT.md` reescritas
- [ ] Itens Low antigos estacionados
