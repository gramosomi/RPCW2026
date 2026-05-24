# Biblioteca Temporal
 
### Novas Rotas
 
| Rota | Descrição |
|------|-----------|
| `GET /linhas` | Lista todas as linhas temporais |
| `GET /linha/<id_linha>` | Página de detalhe de uma linha temporal |
 
### Página `/linhas`
Lista todas as linhas temporais registadas na ontologia, com o seu tipo em tag colorida (verde = `LinhaOriginal`, laranja = `LinhaAlternativa`). Cada linha tem link para a sua página de detalhe.
 
### Página `/linha/<id_linha>`
Página de detalhe de uma linha temporal com:
- ID e tipo da linha
- Tabela com os livros que existem nessa linha (id, título com link, tipo com tag colorida)
- Botão **Voltar às Linhas Temporais** (`/linhas`)
- Botão **Página Inicial** (`/livros`)

 
### Novos Templates
 
- `linhas.html` — lista de todas as linhas temporais
- `linha.html` — detalhe de uma linha temporal
