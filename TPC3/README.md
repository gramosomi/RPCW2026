# TPC3 - Querrys Sparql

# Alterações à Ontologia

- Classe `PratocomPolvo` movida de `owl:Thing` para `PratoCarnívoro`
- Removido indivíduo `PolvoIngrediente`
- Substituída propriedade `:temIngrediente PolvoIngrediente` por `:temIngrediente IngredientePolvo` no indivíduo `EnsopadoCanibal`
- Removidas as propriedades `come EnsopadoCanibal` e `come PratoDoDia` do indivíduo `Aristóteles` pois ambos os pratos continham `Polvo` como `Ingrediente` e `Aristóteles` sendo um `Polvo` não pode comer `PratoComPolvo`

# Queries

1. Quem foram os clientes?

Query

```sparql
PREFIX : <http://example.org/polvo-filosofico#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select * where {
    ?s rdf:type :Cliente .
}
```

Lista de Cliente Obtida:

```text
1 :Ana
2 :Bruno
3 :Carla
4 :Daniel
5 :Eva
6 :Schrodinger
```

2. Que pratos serve o restaurante?

Query

```sparql
PREFIX : <http://example.org/polvo-filosofico#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select * where {
    ?s rdf:type :Prato .
}
```

Lista de Pratos Obtida:

```text
1 :PratoDoDia
2 :SaladaExistencial
3 :TofuMetafisico
4 :BifeDeterminista
5 :PeixeDoLivreArbitrio
6 :PratoDoObservador
7 :DilemaDoSer
8 :EnsopadoCanibal
```

3. Quais os ingredientes necessários à confeção dos pratos?

Query

```sparql
PREFIX : <http://example.org/polvo-filosofico#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select DISTINCT ?ing where {
    ?s rdf:type :Prato;
       :temIngrediente ?ing .
}
```

Lista de Ingredientes obtida:

```text
1 :IngredientePolvo
2 :Alface
3 :Tomate
4 :Tofu
5 :Cogumelos
6 :CarneVaca
7 :Peixe
8 :PolvoIngrediente
```

4. Há funcionários que também sejam clientes?

Query

```sparql
PREFIX : <http://example.org/polvo-filosofico#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?nome where {
    ?nome a :Funcionario;
          a :Cliente .
}  
```

Lista de Funcionários que também são clientes obtida:

```text
1 :Schrodinger
```