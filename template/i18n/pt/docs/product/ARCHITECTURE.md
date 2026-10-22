# Mapa da arquitetura

> Os agentes leem este arquivo no início de cada sessão (importado pelo `AGENTS.md`). Ele é um **mapa**, não uma documentação completa: o suficiente para que um novo agente se oriente em dois minutos.
> Os agentes o mantêm atualizado: se o seu PR mudar a estrutura ou se você descobrir uma armadilha, atualize este arquivo no mesmo PR.
>
> **Primeira configuração:** peça ao seu agente de programação: *"Explore este repositório e preencha docs/product/ARCHITECTURE.md seguindo os títulos das seções. Mantenha-o com menos de 150 linhas."* Depois, revise-o você mesmo.

## Stack
- Linguagem / framework: `TODO`
- Banco de dados: `TODO`
- Hospedagem / destino do deploy: `TODO`
- Principais serviços externos: `TODO` (APIs, e-mail, pagamentos, provedores de autenticação…)

## Estrutura do repositório
```
TODO: top-level folders and what lives in each
```

## Módulos principais
| Módulo / caminho | Responsabilidade | Área protegida? |
|---|---|---|
| `TODO` | | |

## Modelo de dados (entidades principais)
`TODO`

## Ambientes
| Ambiente | URL | Como é feito o deploy |
|---|---|---|
| Local | http://localhost:`TODO` | `make dev` |
| Produção | `TODO` | GitHub Actions `deploy.yml`, com aprovação obrigatória |

## Configuração
- As variáveis de ambiente estão documentadas em `.env.example` (nunca faça commit de valores reais).

## Testes
- Os testes unitários ficam em `TODO` e rodam com `make test`.
- Fixtures de teste sintéticas: `TODO` (nunca use dados pessoais reais).
- E2E / navegador: `TODO`

## Armadilhas
- `TODO`: coisas que já pegaram agentes ou desenvolvedores de surpresa.
