# Decisões a tomar ao adotar o HAAM

Quem toma estas decisões é o product owner, junto com o administrador do projeto. O `/haam-setup` passa por elas nesta ordem, com uma recomendação para cada uma, e o `/haam-settings` as muda depois. Comece com a escolha recomendada e reveja depois da primeira semana movimentada. Até lá, `haam.py ci-usage` mostra para onde foram os minutos do Actions e `haam.py capacity` mostra o que está esperando por você.

**Alguns termos usados aqui:**
- **PR** (pull request): uma mudança proposta, esperando o merge na `main`.
- **CI:** as verificações automáticas (lint, tipos, testes, build) que rodam no GitHub para um PR. Elas usam minutos do Actions.
- **UAT** (teste de aceitação do usuário): o seu próprio teste de uma mudança, no seu computador, antes de ela ir para produção.
- **A via sem UAT:** as mudanças que você marca com `uat:skip` (atualizações de dependências, configuração, refatorações invisíveis). Elas pulam o seu teste e vão direto para as verificações.
- **Gate de release:** a verificação que impede o merge de um PR até que o seu teste tenha passado, ou até que você tenha escolhido a via sem UAT.
- **Worktree:** uma cópia separada da pasta do projeto para um chat de agente, para que os chats não sobrescrevam o trabalho uns dos outros.

## Visão geral

| Decisão | Comece com | Mude quando | Veja |
|---|---|---|---|
| Conta e plano do GitHub | Uma organização. Repositório público: Free. Privado: Team | O repositório é privado e você precisa de um aprovador nos deploys: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | A equipe já trabalha no Linear todos os dias | §2 |
| Quem é quem | Um product owner, um aprovador substituto | Vários produtos ou product owners | §3 |
| Idioma (`language`) | O idioma em que a sua equipe escreve | A equipe muda | §3 |
| Ordem dos testes (`flow`) | `test-first` | Você testa em um ambiente de staging compartilhado, e não localmente | §4 |
| O que você testa (`uat`) | `owner-decides` | Produto regulado: `always`. Muitas correções pequenas e bem testadas: `bugs-skip` | §4 |
| Agrupamento (`grouping`) | `per-issue` | Epics feitos de itens pequenos: `per-epic`. Minutos do Actions escassos: `release` | §4 |
| Verificações (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | Os minutos do Actions ficam curtos | §4 |
| Entrega (`deploy`, `deploy_approval`) | `github`, `each` | Você faz deploy de outra forma, ou o seu plano não consegue segurar deploys para aprovação | §4 |
| Limites | `settings --recommend` | O seu tempo para testar ou o número de agentes muda | §5 |
| Áreas protegidas | Os padrões, mais o seu código sensível | A arquitetura muda | §6 |
| Recursos de teste compartilhados (`heavy_runs`) | Nenhum | Os testes compartilham um banco de dados local, um simulador ou um dispositivo | §7 |
| Quanta liberdade os agentes têm | Protótipos e modo de construção por epic quando você pedir; código de produção é tudo, exceto protótipos, testes e documentação | Você quer que os agentes explorem mais, ou o seu código de produção fica em poucas pastas | §8 |

## 1. Conta, organização e plano do GitHub

### Contas
Cada pessoa cria e mantém a própria conta; nunca compartilhe um login.

1. **Cada pessoa** se cadastra em [github.com/signup](https://github.com/signup) com o e-mail de trabalho e ativa a autenticação de dois fatores (Settings → Password and authentication).
2. **Um administrador** cria uma organização ([github.com/organizations/plan](https://github.com/organizations/plan)) e convida a equipe. O plano gratuito basta para um repositório público; um privado precisa do Team (veja a tabela abaixo). A organização é dona dos repositórios, então nada depende da conta de uma única pessoa. Torne duas pessoas owners.
3. **O repositório** fica na organização: crie-o lá ou transfira um existente (Settings do repositório → General → Transfer ownership).
4. **Em cada computador**, instale o GitHub CLI ([cli.github.com](https://cli.github.com)) e rode `gh auth login`. Com o GitHub Projects como tracker, rode também `gh auth refresh -s project`.
5. **Nada de contas separadas para os agentes.** Os agentes agem com a conta da pessoa que está logada. Os gates partem do princípio de que a pessoa ao teclado responde pelo que os agentes dela fazem.

### De qual plano você precisa

| O que o HAAM usa | Repositório público, qualquer plano | Privado, Free | Privado, Pro | Privado, Team | Privado, Enterprise Cloud |
|---|---|---|---|---|---|
| Regras de branch e verificações obrigatórias ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Sim | Não | Sim | Sim | Sim |
| Um aprovador nos deploys para produção ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Sim | Não | Não | Não | Sim |
| Varredura de segredos e proteção de push do próprio GitHub ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Sim | Não | Não | Complemento pago | Complemento pago |
| Quadro do GitHub Projects | Sim | Sim | Sim | Sim | Sim |
| Minutos do Actions | Gratuitos nos runners padrão | Uma cota mensal | Uma cota maior | Uma cota maior | Uma cota maior |

O Pro é para uma conta pessoal; o Team e o Enterprise Cloud são para organizações.

O que significa cada peça que falta:
- **Sem regras de branch** (repositório privado no Free): o GitHub não impede um merge na `main` sem as verificações. Os agentes continuam instruídos a nunca fazer merge, e o `ship` continua passando por todos os gates, mas nada garante isso. Para qualquer produto privado, use o Team (organização) ou o Pro (conta pessoal).
- **Sem aprovador de deploy** (repositório privado abaixo do Enterprise Cloud): os deploys começam quando um PR entra na `main`. O seu `ship`, que faz o merge, passa a ser então a decisão de release. Defina `deploy_approval: automatic` para que o HAAM não espere uma aprovação que não pode acontecer, e mantenha `uat` em `owner-decides` ou `always` (§4).
- **Sem a varredura de segredos do GitHub:** tudo bem. A verificação `secrets` do próprio kit e o hook pre-commit rodam em todos os planos.

Os planos e as cotas mudam, então consulte [github.com/pricing](https://github.com/pricing) antes de escolher.

### O acesso dos revisores ao Claude
As duas revisões por IA rodam com um único segredo do repositório, adicionado pelo product owner no próprio terminal e nunca colado em um chat:
- `CLAUDE_CODE_OAUTH_TOKEN` (de `claude setup-token`): as revisões são descontadas do plano do Claude dessa pessoa.
- `ANTHROPIC_API_KEY`: cobrada por revisão, separadamente da assinatura de qualquer pessoa. Defina um limite de gastos mensal no console da Anthropic.

## 2. O tracker: GitHub Projects ou Linear

| | GitHub Projects | Linear |
|---|---|---|
| Custo | Gratuito em todos os planos do GitHub | Gratuito até 250 issues ativas (não arquivadas) e 2 times; os planos pagos, por usuário, removem o limite. Consulte [linear.app/pricing](https://linear.app/pricing) |
| Como os agentes o usam | `haam.py issue …` a partir de qualquer ferramenta de agente, com o login `gh` da pessoa | A conexão com o Linear (MCP), configurada em cada ferramenta de agente |
| Feito por você | Reservas que impedem que dois chats peguem a mesma tarefa; a fila de UAT contada para os limites; os campos próprios do quadro (`--field`); a via sem UAT fazendo merge sozinha; o `ship` fechando as issues | Os agentes fazem as mudanças pela conexão e contam a fila de UAT para `capacity --in-uat N`. A via sem UAT não faz merge sozinha: você coloca esses PRs em produção |
| Configuração | `haam.py github-project --apply` | `haam.py linear --apply` com a chave de API do product owner, mais os passos no navegador em `LINEAR-SETUP.md` |
| Ideal para | A maioria das equipes: tudo em um só lugar | Equipes que já vivem no Linear |

**Recomendação:** GitHub Projects, a não ser que a equipe já use o Linear todos os dias. A triagem e os agentes criam issues rapidamente, então o limite gratuito do Linear pode ser atingido em poucas semanas.

## 3. Quem é quem
- **Product owner:** uma pessoa, que decide, testa e coloca em produção. Só ela roda as skills exclusivas de pessoas: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` e `/haam-settings`.
- **Aprovadores substitutos:** uma ou duas pessoas que podem aprovar deploys quando o product owner estiver ausente (`config --backup-approvers a,b`). Isso exige um aprovador nos deploys, então não tem efeito em um repositório privado abaixo do Enterprise Cloud.
- **Construtores:** todas as pessoas que rodam chats de agente. Cada uma precisa da própria conta do GitHub com acesso de escrita e da própria ferramenta de agente. O administrador roda `haam.py invite --github USER` para ver o plano e depois o mesmo comando com `--apply`. Em seguida, cada construtor roda `/haam-onboard`.
- **Administrador:** configura o GitHub, o tracker e os segredos. Muitas vezes é o próprio product owner.
- **Quando duas pessoas trabalharem no código,** exija uma aprovação nas regras de branch (`GITHUB-SETUP.md` §2).
- **Idioma:** a documentação do kit está disponível em inglês, espanhol, francês, alemão, italiano, holandês e português (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`). Os agentes escrevem specs, issues, planos de UAT e mensagens no idioma que você escolher; comandos, labels, status e código continuam em inglês. Escolha na instalação (`install --language es`). Para mudar depois: `haam.py config --language fr` e, em seguida, o `update --target . --apply` do kit troca os documentos que você não editou.

## 4. Como o trabalho flui: as configurações
`python3 tools/haam/haam.py settings --explain` imprime cada opção com o seu custo-benefício. As escolhas que importam:

| Configuração | Comece com | Escolha outra quando | O que custa ou arrisca |
|---|---|---|---|
| `flow` | `test-first`: você testa a branch do agente, e depois o PR e as verificações rodam uma única vez | `checks-first`: você só quer testar código que passou pelas verificações, ou testa em um ambiente de staging compartilhado | Cada rodada de retrabalho roda as verificações de novo |
| `uat` | `owner-decides`: você testa tudo, exceto o que marcar com `uat:skip` | `always`: produtos regulados ou críticos para a segurança. `bugs-skip`: muitas correções pequenas com testes sólidos | `bugs-skip`: uma correção errada pode ir para produção sem que você a veja |
| `grouping` | `per-issue`: um PR por issue | `per-epic`: epics feitos de itens pequenos. `release` (só test-first): minutos escassos e releases em lote | Um item com falha segura o lote inteiro |
| `ci` | `every-pr`, no GitHub | `local`: os minutos acabam e o seu computador compila tudo. `off`: sem verificação `ci` no PR (os agentes continuam rodando `make check`; combine com uma verificação completa no release) | `local` não é à prova de adulteração; `off` precisa de um release gate em outro lugar |
| `review` | `github`: duas revisões por IA independentes por PR | `protected-only`: economiza a maior parte do custo de revisão. `local`: economiza minutos | Menos verificações independentes |
| `nightly` | `on` | `off`: quando os minutos estão muito escassos | Você descobre quebras e novas vulnerabilidades mais tarde |
| `runner` | `github` | `self-hosted`: um repositório privado com builds pesados e uma máquina que fica sempre ligada | Manutenção. Nunca para repositórios públicos |
| `deploy` | `github`: o `deploy.yml` faz deploy no merge | `manual`: você faz deploy de outra forma | O `ship` espera você dizer "live" |
| `deploy_approval` | `each`: todo deploy espera a sua aprovação | `automatic`: o seu plano não consegue segurar deploys (§1), ou você escolheu `uat: always` | Uma mudança integrada vai para o ar sem uma última olhada |
| `worktree_cleanup` | `after-ship` | `manual`: você prefere limpar os worktrees você mesmo | Espaço em disco |
| `worktree_dir` | `.claude/worktrees` | uma pasta irmã (por exemplo `../connect-wt`) quando você quer as cópias dos agentes fora do repositório | Os caminhos em `/work` e `doctor` a seguem |

A via sem UAT só faz merge sozinha no GitHub Projects, com o segredo `HAAM_PROJECT_TOKEN`, `ci: every-pr` e `review: github`. Caso contrário, você mesmo coloca esses PRs em produção.

Evite estas combinações, porque juntas elas removem a última verificação:
- `ci: off` com `review: off`: nada verifica o código antes do seu teste.
- `deploy_approval: automatic` com `uat: bugs-skip`: uma correção de bug pode chegar à produção sem que nenhuma pessoa olhe para ela. Os deploys são automáticos em um repositório privado abaixo do Enterprise Cloud, então não escolha `bugs-skip` nesse caso.

## 5. Limites: quanto trabalho pode ficar esperando
Os limites impedem que os agentes produzam mais do que você consegue testar, e mais PRs do que o seu orçamento de CI cobre. Quando um limite é atingido, os agentes param de começar novas construções. Eles continuam corrigindo retrabalho, escrevendo specs e avaliando ideias.

| Limite | O que conta | Como dimensionar |
|---|---|---|
| `max_in_uat` | Mudanças esperando o seu teste. O principal limite no test-first | O que você consegue testar de uma vez: minutos por sessão ÷ minutos por teste (um teste costuma levar de 5 a 10 minutos). Uma hora por dia, com cerca de 6 minutos por teste, dá 10 |
| `max_open_prs` | PRs prontos. Rascunhos, PRs só de documentação e PRs de bots (Dependabot) não contam | Test-first: os PRs duram pouco (da sua aprovação até o `ship`), então o dobro dos chats de agente rodando ao mesmo tempo é mais do que suficiente. Checks-first: toda mudança esperando o seu teste é um PR pronto, então defina pelo menos `max_in_uat` mais os chats rodando ao mesmo tempo |
| `max_review_rounds` | Rodadas de revisão por IA reprovadas antes de um agente parar e perguntar a você | 2. Aumente para 3 em áreas difíceis |
| `max_pr_lines` | Tamanho-alvo de um PR, em linhas alteradas | 400. PRs menores recebem revisões e testes melhores |

Calcule para a sua equipe:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
Ele imprime os limites sugeridos e avisa quando os agentes conseguem produzir mais do que você consegue testar. Depois, mostra o comando que os aplica. Ele parte de cerca de 6 minutos por teste e 2 mudanças por chat por dia; passe `--minutes-per-test` e `--changes-per-chat` com os seus próprios números. Ele lê o `flow` das configurações do projeto, ou recebe `--flow`.

Se os agentes produzirem mais do que você consegue testar:
- a fila enche e os agentes pausam as novas construções, que é o limite fazendo o seu trabalho;
- `/test all` com "pass all verified" libera as mudanças que os próprios agentes comprovaram;
- `uat: bugs-skip` manda as pequenas correções de bugs direto para as verificações;
- ou rode menos chats de agente.

Para um fim de semana de trabalho dos agentes testado de uma vez, abra uma **janela de lote**: um aumento que termina sozinho depois do último dia, por exemplo `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. O que proteger
**A regra:** proteja o código em que uma mudança errada pode prejudicar os usuários, causar perda de dinheiro ou de dados, violar a lei ou enfraquecer os próprios gates do HAAM. Toda mudança protegida precisa da sua revisão de código e do seu teste, e nunca usa a via sem UAT. Então proteja o que importa, não tudo.

| Área | Proteger | Caminhos típicos (exemplos) |
|---|---|---|
| Login, sessões, permissões, papéis | Sempre | `src/auth/**`, `**/permissions/**`, *o middleware de autenticação* |
| Pagamentos, cobrança, reembolsos, preços | Sempre | `src/billing/**`, `src/payments/**` |
| Dados pessoais: armazenamento, retenção, exclusão, exportações | Sempre que você guardar dados pessoais | `src/users/**`, `**/privacy/**` |
| Logs que podem capturar dados pessoais | Sempre que você guardar dados pessoais | *a configuração de logs e os módulos de auditoria* |
| Decisões sobre usuários: elegibilidade, verificação, aprovações, pontuação | Quando um resultado errado prejudica alguém | `src/verification/**`, `src/decisions/**` |
| Provedores externos que agem em nome dos usuários ou recebem os dados deles | Sim | `src/integrations/**` |
| Migrações de banco de dados | Sempre | `db/migrations/**`, `**/migrations/**` |
| Configuração de segurança: criptografia, CORS, CSP, tratamento de segredos | Sim | `**/security/**`, `**/crypto/**` |
| Infraestrutura como código | Sim | `infra/**`, `terraform/**` |
| Configuração de assinatura e release de aplicativos móveis | Se você publica aplicativos | *arquivos de entitlements, de assinatura e de build de release* |
| CI, deploy e scripts de build | Protegidos por padrão | `.github/**`, `Makefile`, `scripts/**` |
| O HAAM e a configuração dos agentes | Protegidos por padrão | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json` e outros: `haam.py settings` os lista |

Os caminhos em itálico descrevem o que procurar; transforme-os em padrões reais para o seu código.

Como configurar:
1. O `/haam-setup` propõe caminhos reais do seu código para cada área que se aplica. Você os confirma.
2. `config --protected "src/auth/**,db/migrations/**" --human` adiciona padrões, e `config --unprotected "…" --human` remove um. `**` significa quaisquer pastas, e `*` significa dentro de uma única pasta. Um simples nome de pasta cobre tudo o que está dentro dela.
3. `haam.py protected`, em qualquer branch, lista os arquivos protegidos que ela altera.
4. O gate de release decide a partir dos arquivos que um PR altera. Ele lê a lista da `main`, então um agente não consegue remover uma proteção no próprio PR.

Reveja a lista sempre que `docs/product/ARCHITECTURE.md` mudar.

## 7. Recursos de teste compartilhados
Alguns testes usam algo que o computador inteiro compartilha, como um banco de dados local que os testes clonam, um simulador de celular ou um dispositivo conectado. Dois chats de agente rodando esses testes ao mesmo tempo atrapalham um ao outro, e a falha parece uma mudança quebrada. Liste esses comandos como padrões: `config --heavy-run "make (check|test-integration)"`. Os agentes passam então a rodá-los um de cada vez, por meio de `haam.py exclusive`. Deixe a lista vazia quando os seus testes forem independentes.

## 8. Quanta liberdade os agentes têm
Os agentes podem construir partes grandes rapidamente, do jeito que as pessoas fazem "vibe coding" com IA, onde quer que um erro seja barato de jogar fora. Tudo o que roda para usuários reais fica atrás dos gates.

**Alguns termos usados aqui:**
- **Protótipo** (ou **spike**): uma versão rápida e descartável de uma ideia, que funciona, construída para ser experimentada e nunca colocada em produção como está.
- **Parte:** um pedaço de um epic que pode ir para produção, com a própria issue e a própria spec.
- **Agente líder:** o único chat de agente que constrói um epic inteiro. Ele pode passar partes independentes para agentes auxiliares (**subagentes**).
- **Feature flag:** um interruptor no código que mantém uma funcionalidade nova escondida até que alguém a ative.
- **Código de produção:** o código que roda para usuários reais.

Três escolhas:

| Escolha | O que faz | Quando usar |
|---|---|---|
| **Protótipo primeiro.** Digite `/spike`, ou escolha `prototype` no `/triage` | Um agente constrói um protótipo em uma branch `spike/`, sem spec, PR ou limite de tamanho. Você o experimenta com `/test`. Depois diz `discard`, `change: <what>`, `rebuild` (escrever a spec e construir do zero) ou `keep` (escrever a spec e construir a partir daquele código) | Quando experimentar a ideia diz mais do que ler sobre ela: uma tela nova, um fluxo, uma integração sobre a qual você tem dúvidas |
| **Modo de construção por epic.** Coloque a label `mode:epic-build` em um epic aprovado; o `/decide` e o `/triage backlog` oferecem essa opção | Um agente líder constrói todas as partes do epic em uma única branch, com um ponto de controle depois de cada parte. Você testa e coloca em produção a funcionalidade inteira de uma vez | Uma funcionalidade cujas partes só fazem sentido juntas, ou que você prefere avaliar como um todo |
| **O que conta como código de produção** (`production_paths`, `non_production_paths`) | Diz aos agentes e a você o que roda para os usuários, para que as notas de um protótipo e `haam.py production` mostrem o que uma mudança afetaria. Protótipos, testes e documentação ficam fora disso por padrão | Restrinja quando o seu produto fica em poucas pastas: `config --production "src/**,api/**" --human`. Adicione pastas que nunca rodam para os usuários com `config --not-production "…" --human`. Se a sua documentação é o que os usuários veem, tire-a da lista com `config --remove-not-production "docs/**" --human` |

Seja qual for o modo, toda mudança que entra passa por todos os gates. A proteção por trás disso:
- um protótipo nunca entra na `main`: o gate de release recusa as branches `spike/` e tudo o que estiver em `prototypes/`, e o `publish` recusa os spikes;
- o código de protótipo mantido só chega aos usuários por meio do `/spec`, de uma branch normal e do seu teste, atrás de uma feature flag desligada por padrão. Ele nunca usa a via sem UAT: o gate vê os commits `spike:` dele;
- o código de produção nunca importa de `prototypes/`, e o revisor de IA bloqueia se isso acontecer;
- um protótipo nunca altera áreas protegidas, e o `/test` mostra a você os arquivos protegidos alterados e as novas dependências dele antes de rodar qualquer coisa;
- as áreas protegidas sempre recebem a sua revisão de código;
- nenhum agente mexe em sistemas ou dados de produção, em nenhum modo.

## Fontes
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (planos que os incluem) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (revisores obrigatórios em repositórios privados) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
