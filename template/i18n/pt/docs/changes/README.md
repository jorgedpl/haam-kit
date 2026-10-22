# changes

Um arquivo pequeno por mudança colocada em produção, com o nome `<FILE-ID>.md` (por exemplo, `GH-12.md`), adicionado pelo `/uat` na própria branch da mudança, para que vá para produção junto com ela. Um arquivo por mudança significa que PRs em paralelo nunca entram em conflito aqui.

Cada arquivo tem uma ou duas linhas que um usuário entenderia:

```
- #12: Export to CSV now works on mobile.
```

Para escrever notas de release ou atualizar o `CHANGELOG.md`, peça a um agente que reúna os arquivos adicionados desde a última release.
