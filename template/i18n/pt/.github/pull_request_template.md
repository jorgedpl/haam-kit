## Issue
<!-- GitHub Projects: mantenha a linha abaixo com o número da issue (use Refs, não Closes: a issue é fechada no /release). Linear: coloque o ID no título do PR (APP-123: …). -->
Refs #

## Feito com (Built with)
<!-- Ferramenta de agente e modelo (por exemplo, Claude Code / Opus, Cursor / <model>, Codex, Grok Build), ou "pessoa". -->

## O quê e por quê
<!-- 2–4 frases. O que mudou para o usuário, e por quê. -->

## Critérios de aceitação → testes
| AC | Teste(s) | Status |
|---|---|---|
| AC1 | `test_…` | ✅ |

## Como verificar
- Plano de UAT: `docs/uat/<GH-123 or APP-123>-*.md` (adicionado pelo `/uat`)
- Capturas de tela / observações:

## Risco
- Áreas protegidas afetadas: nenhuma / <lista> (se houver alguma → label `human-review`)
- Migrações: nenhuma / <descreva + rollback>
- Mudanças de configuração / ambiente: nenhuma / <lista>

## Checklist (G3)
- [ ] `make check` passa localmente
- [ ] Todo critério de aceitação tem um teste
- [ ] Nenhuma mudança não relacionada
- [ ] Documentação atualizada (ARCHITECTURE.md, .env.example, …) ou não necessária
- [ ] Nenhum segredo ou dado pessoal real

<!-- Gate de release (G4): este PR só pode fazer merge com a label `uat-passed`, ou com `gate-override` mais um comentário "OVERRIDE: <reason>". PRs só de documentação estão isentos. -->
