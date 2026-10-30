# Configuração do GitHub (uma vez, ~30 minutos, administrador do repo)

Isto transforma os gates G3–G5 de convenções em regras que o GitHub garante.

> **Automatizado:** as labels (§1), as regras de branch (§2), o ambiente de produção (§4) e os recursos de segurança (§3b–c) são feitos por `python3 tools/haam/haam.py github --apply` (veja o plano primeiro, sem `--apply`). Esta página é o equivalente manual, mais os passos que o GitHub só oferece no navegador. O segredo do revisor é sempre adicionado por você: `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/repo` (token de `claude setup-token`, o seu plano do Claude) ou `gh secret set ANTHROPIC_API_KEY -R owner/repo` (chave de API, cobrada por revisão). Qualquer um dos dois roda as duas revisões.

## 1. Labels
Crie estas labels no repositório (Issues → Labels), ou rode:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Proteção da branch `main`
Settings → **Rules → Rulesets** → New branch ruleset (ou a Branch protection clássica), com alvo `main`:

- ✅ Restringir exclusões; bloquear force pushes
- ✅ Exigir um pull request antes do merge
  - Aprovações obrigatórias: **1** quando houver uma segunda pessoa; **0** enquanto você estiver sozinho (a label de UAT é a sua aprovação)
  - ✅ Descartar aprovações antigas quando novos commits forem enviados
- ✅ Exigir que as verificações de status passem (deixe "require branches to be up to date" desligado: ele roda o CI de novo em todos os PRs abertos depois de cada merge)
  - Verificações obrigatórias: **`ci`** (ou **`ci-local`** quando `ci` é `local`; omita quando `ci` é `off`), **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** e **`release-gate`** (elas aparecem na lista depois que os workflows rodarem uma vez em um PR). `haam.py settings --apply` / `github --apply` adiciona as verificações que as configurações pedem e remove as do HAAM que elas já não pedem (por exemplo `ci` quando você muda para `off`)
- ✅ Exigir histórico linear (opcional, mantém o histórico limpo)
- **Lista de bypass:** só administradores do repositório, **somente para pull requests** (nunca "always": os agentes trabalham com o login de uma pessoa, muitas vezes de um administrador, e poderiam, caso contrário, fazer push direto na `main`). Esse é o bypass de emergência de Nível 2 descrito em `docs/process/GATES.md`.

**Auto-merge** (Settings → General → Pull Requests → *Allow auto-merge*; `haam.py github --apply` o ativa): usado só pela via sem UAT, para PRs cujas issues você marcou com `uat:skip`. O gate o ativa nesse tipo de PR com o segredo `HAAM_PROJECT_TOKEN` (`docs/process/TRACKER.md`), e o GitHub só faz o merge quando todas as verificações obrigatórias passam. Se você exigir aprovações, a via também espera uma.

## 3. Revisão de código e segurança

### 3a. Um segredo do Claude para os agentes revisores
Os revisores independentes (`.github/workflows/review.yml`) rodam o Claude no GitHub Actions. Um único segredo do repositório roda as duas revisões (Settings → **Secrets and variables → Actions** → New repository secret). Escolha uma destas opções:
- **`CLAUDE_CODE_OAUTH_TOKEN`:** rode `claude setup-token` e use o token que ele imprime. As revisões passam então a ser descontadas daquele plano do Claude.
- **`ANTHROPIC_API_KEY`:** uma chave de API dedicada a este repo, criada em console.anthropic.com, com um limite de gastos mensal. Ela é cobrada por revisão, separadamente da assinatura do Claude de qualquer pessoa. Com ela, a revisão de segurança usa a action de revisão de segurança da Anthropic.

PRs em rascunho e PRs só de documentação não chamam o Claude. As instruções de revisão ficam em `.github/review/REVIEWER.md` e `SECURITY-REVIEWER.md` e são sempre lidas da `main`. Ajuste-as conforme for aprendendo.

### 3b. Varredura de segredos e proteção de push
Settings → **Security** (Code security / Advanced Security, dependendo do seu plano):
- ✅ **Secret scanning**, ✅ **Push protection**: o GitHub rejeita pushes que contêm formatos de segredos conhecidos.
- Gratuito para repositórios públicos. Para repositórios privados, pode exigir o complemento de segurança pago do GitHub; se você não o tiver, a verificação `secrets` do próprio kit (gitleaks) e os hooks locais continuam protegendo você.

### 3c. Alertas de dependências
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Depois, descomente o seu ecossistema em `.github/dependabot.yml`. Os PRs do Dependabot passam pelos mesmos gates.

### 3d. Pull requests de forks
Settings → **Actions → General** → *Fork pull request workflows*: exija aprovação para todos os colaboradores externos. (Os PRs de forks não recebem os segredos do repositório, então as revisões por IA não podem rodar neles; uma pessoa revisa e anula a revisão se necessário.)

## 4. Ambiente de produção (gate G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** o product owner (+ uma pessoa substituta, se houver)
- ✅ Prevent self-review: deixe **desligado** enquanto você for o único aprovador e ative depois
- **Deployment branches and tags:** selected branches → só a `main`
- **Environment secrets:** as credenciais de deploy para produção ficam aqui e em nenhum outro lugar
- **Environment variables:** `PRODUCTION_URL` (usada pelo smoke test)

Agora todo merge na `main` roda o `deploy.yml`, que pausa em *deploy-production* até que um aprovador clique em **Review deployments → Approve**. O GitHub envia e-mails/notificações aos aprovadores.

Os revisores obrigatórios funcionam em repositórios públicos em todos os planos, mas nos privados só com o GitHub Enterprise Cloud. Sem eles, os deploys começam no merge, e o seu `ship` é a decisão de release: defina `deploy_approval: automatic` com `/haam-settings` (`docs/setup/DECISIONS.md` §1).

## 5. CODEOWNERS (opcional, mas recomendado quando houver duas pessoas)
`.github/CODEOWNERS`:
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Depois, ative "Require review from Code Owners" no ruleset.

## 6. Preencher o contrato de comandos
Edite o `Makefile` (incluindo `audit`) e os passos de configuração do runtime em `.github/workflows/ci.yml`, `security.yml` e `deploy.yml` (procure `TODO(setup)`). Abra um PR. A verificação `ci` precisa ficar verde nesse PR antes que você ative as verificações obrigatórias.

## 7. Opcional: aplicativo do Claude para o GitHub
Se você quiser marcar um agente em um PR para uma correção rápida (por exemplo, o aplicativo do Claude para o GitHub, via `/install-github-app` no Claude Code, ou a integração com o GitHub da sua outra ferramenta), instale-o. Qualquer aplicativo desse tipo está sujeito à mesma proteção de branch e às mesmas verificações, então não consegue contornar os gates.

## 8. Economizar minutos do Actions

Os repositórios privados têm uma cota mensal de minutos do Actions; agentes que abrem muitos PRs a gastam rapidamente. O que o kit já faz: por padrão (test-first), os agentes fazem push das branches sem abrir PRs, e um PR só é aberto depois que você testou e aprovou a mudança, então as verificações rodam uma única vez, sobre código testado (projetos checks-first: PRs em rascunho não rodam nada, e os agentes marcam um PR como pronto uma única vez, quando ele está completo); PRs só de documentação pulam as verificações; a `main` é verificada todas as noites em vez de depois de cada merge; labels, comentários e novas issues não acionam runners; os agentes seguram trabalho novo quando há 10 PRs abertos ou 10 mudanças esperando o seu teste (`max_open_prs`, `max_in_uat`).

Descubra para onde vão os minutos: `python3 tools/haam/haam.py ci-usage` (últimos 7 dias, por workflow, job, gatilho e dia).

Duas configurações da tabela abaixo economizam minutos com poucas desvantagens. Mude-as com `/haam-settings`, ou com `python3 tools/haam/haam.py settings --set … --apply --human`; elas viram variáveis do repositório que os workflows leem. As outras (`ci: local | off`, `review: protected-only | off`, `nightly: off`, `grouping: release`) economizam mais: veja `settings --explain`. Com `ci: off`, as regras de branch deixam de exigir a verificação `ci`; mantenha a varredura de segredos, as revisões de IA e o release-gate, e rode uma verificação completa na hora do release (o seu script de deploy ou o workflow de CI no commit que você envia) para continuar pegando as falhas que só aparecem no Linux.

| Opção | O que muda | Custo-benefício |
|---|---|---|
| `--review local` | As duas revisões por IA rodam no seu computador, em sessões novas do Claude (`haam.py review`), usando o seu plano do Claude em vez de minutos do Actions. Os PRs com a label `human-review` continuam sendo revisados no GitHub | O resultado deixa de ser à prova de adulteração: o agente que construiu inicia a revisão (sessões novas, somente leitura, instruções da `main`), e qualquer coisa que use o seu login poderia publicar um resultado aprovado. Rode `haam.py review` a partir do seu próprio chat para mais separação |
| `--runner self-hosted` | Todos os jobs, exceto o deploy, rodam na sua própria máquina (registrada em Settings → Actions → Runners) em vez das do GitHub | A máquina precisa estar ligada, com git, make, Python 3, curl, gitleaks e as ferramentas do seu projeto; só para repositórios privados. Consulte os preços atuais do GitHub para runners self-hosted |

Também vale verificar: os jobs em runners macOS contam 10 minutos para cada minuto que rodam (Windows: 2). Rode os builds de aplicativos móveis só quando o código móvel mudou (o `make check` recebe os arquivos alterados em `$CI_CHANGED_FILES`), ou à noite.

## 9. Verificar se funciona
1. Abra um PR de teste minúsculo (por exemplo, a correção de um erro de digitação no código). `ci`, `secrets` e `dependencies` rodam; o agente revisor publica um comentário e `ai-review` / `security-review` dão o resultado; `release-gate` mostra **failure: waiting for UAT**.
   - **Teste de segredo:** em uma branch descartável, faça commit de uma chave falsa no estilo da AWS, como `AKIA` seguido de 16 letras maiúsculas/dígitos, em um arquivo de código. O hook local deve bloquear o commit; se você o contornar com `--no-verify`, a verificação `secrets` deve falhar. Apague a branch depois.
2. Adicione a label `uat-passed` → `release-gate` fica verde → o merge é permitido.
3. Depois do merge, Actions → Deploy mostra **Waiting for review** em `deploy-production`.
4. Abra um PR só de documentação → `release-gate` passa automaticamente.
