# Biblioteca Temporal – Ontologia e Queries SPARQL


# Exercícios SPARQL – Biblioteca Temporal

## 1. Liste todos os livros que existem na linha temporal original (`LinhaOriginal`) (LIVROS POR LINHA TEMPORAL)

```sparql
SELECT ?livro ?linha
WHERE {
  ?livro :existeEm ?linha .
  ?linha rdf:type :LinhaOriginal .
}
```

---

## 2. Identifique os livros que existem em mais do que uma linha temporal (LIVROS EM MÚLTIPLAS LINHAS TEMPORAIS)

```sparql
SELECT DISTINCT ?livro
WHERE {
  ?livro :existeEm ?linha1 .
  ?livro :existeEm ?linha2 .
  FILTER (?linha1 != ?linha2)
}
ORDER BY ?livro
```

---

## 3. Liste todos os livros classificados como `LivroParadoxal` (LIVROS PARADOXAIS)

```sparql
SELECT ?livro 
WHERE {
  ?livro rdf:type :LivroParadoxal .
}
```

---

## 4. Para cada `LivroHistórico`, indique os eventos históricos que esse livro refere (LIVROS HISTÓRICOS E EVENTOS)

```sparql
SELECT ?livro ?evento
WHERE {
  ?livro rdf:type :LivroHistorico .
  ?livro :refere ?evento .
    ?evento rdf:type :EventoHistorico.
}
ORDER BY ?livro
```

---

## 5. Identifique livros classificados como LivroHistorico que referem eventos futuros (INCONSISTÊNCIAS SEMÂNTICAS)

```sparql
SELECT ?livro ?evento
WHERE {
  ?livro rdf:type :LivroHistorico .
  ?livro :refere ?evento .
    ?evento rdf:type :EventoFuturo.
}
ORDER BY ?livro
```

---

## 6. Liste os autores e o número de livros que escreveram, ordenando o resultado por número de livros em ordem decrescente (AUTORES MAIS PROLÍFICOS)

```sparql
SELECT ?nomeAutor (COUNT(?livro) AS ?numLivros) WHERE {
    ?livro :escritoPor ?autor .
    ?autor :nome ?nomeAutor .
}
GROUP BY ?nomeAutor
ORDER BY DESC(?numLivros)
```

---

## 7. Identifique os autores que escreveram pelo menos um livro paradoxal (AUTORES DE LIVROS PARADOXAIS)

```sparql
SELECT ?nomeAutor WHERE {
    ?livro a :LivroParadoxal ;
             :escritoPor ?autor .
    ?autor :nome ?nomeAutor
}
GROUP BY ?nomeAutor
```

---

## 8. Liste todos os livros que existem em pelo menos uma linha temporal alternativa (`LinhaAlternativa`).

```sparql
SELECT ?livro WHERE {
    ?livro :existeEm ?nomeLinhaT .
    ?nomeLinhaT a :LinhaAlternativa .
}
ORDER BY ?livro
```

---

## 9. Indique todos os bibliotecários e a biblioteca onde trabalham (BIBLIOTECÁRIOS)

```sparql
SELECT ?nome ?biblioteca WHERE {
    ?nome a :Bibliotecário ;
          :trabalhaEm ?biblioteca .
    ?biblioteca a :Biblioteca .
}
```

---

## 10. Liste todos os livros escritos por Cronos e indique em que linhas temporais esses livros existem (LIVROS ESCRITOS POR CRONOS)

```sparql
SELECT ?livro ?linhaTemporal ?tipoLinhaTemporal WHERE {
    ?livro :escritoPor :Cronos ;
           :existeEm ?linhaTemporal .
    ?linhaTemporal a ?tipoLinhaTemporal
    
    FILTER(?tipoLinhaTemporal != owl:NamedIndividual)
    FILTER(?tipoLinhaTemporal IN (:LinhaOriginal, :LinhaAlternativa))
}
ORDER BY ?livro
```