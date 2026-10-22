# Spec: <ID> <título>

- **Issue:** <#123 ou APP-123> · **Avaliação:** docs/assessments/<FILE-ID>-*.md · **ADRs:** <links ou nenhum>
- **Status:** Rascunho / Aprovada · **Aprovada por:** <pessoa> em YYYY-MM-DD
- **Áreas protegidas:** nenhuma / <lista> → `human-review`

## 1. Objetivo
<!-- Um parágrafo: o que muda, para quem e por quê. -->

## 2. Histórias de usuário
- Como <papel>, eu quero <capacidade>, para <benefício>.

## 3. Critérios de aceitação
<!-- Cada critério precisa poder ser testado. Numere-os; os testes e os passos do UAT se referem a esses números. -->
**AC1:** <nome>
- Dado …
- Quando …
- Então …

**AC2:** …

## 4. Fora do escopo
- 

## 5. Notas de design
- **Arquivos / módulos que provavelmente serão alterados:** 
- **Modelo de dados / migrações:** nenhuma / <descreva, incluindo o preenchimento retroativo e a reversibilidade>
- **Configuração / variáveis de ambiente:** nenhuma / <nomes, e adicione ao .env.example>
- **APIs externas:** 
- **Notas de UI / textos:** 
- **Estados de erro e casos-limite:** 

## 6. Plano de testes
| AC | Teste(s) unitário(s) / de integração | Observações |
|---|---|---|
| AC1 | `test_…` | |

**Esboço do UAT:** <o que uma pessoa vai percorrer localmente>

## 7. Implantação e rollback
- **Feature flag:** nenhuma / <nome>
- **Implantação:** 
- **Rollback:** <basta um PR de revert? há dados a limpar?>

## 8. Partes (se dividida)
| Sub-issue | Escopo | Depende de |
|---|---|---|

## 9. Perguntas em aberto
1. 
