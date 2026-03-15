from flask import Flask, render_template
from mquery import execute_query
from datetime import datetime

app = Flask(__name__)

data_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

@app.route('/')
@app.route('/livros')
def index():
    q = """
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?livroID ?tituloLivro ?tipoID ?nomeAutor ?pais WHERE {
        ?livro a ?tipoLivro .
        FILTER(?tipoLivro in (:LivroParadoxal, :LivroFiccional, :LivroHistorico))
        OPTIONAL {?livro :titulo ?tituloLivro . }
        ?livro :escritoPor/:nome ?nomeAutor .
        ?livro :escritoPor/:paisOrigem ?pais .
        BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
        BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoID)
    }
    ORDER BY ?tituloLivro
"""

    res = execute_query(q)
    livros = []

    for livro in res["results"]["bindings"]:
        l = {
            "id": livro["livroID"]["value"],
            "tipo": livro["tipoID"]["value"],
            "autor": livro["nomeAutor"]["value"],
            "pais": livro["pais"]["value"]
        }
        if "tituloLivro" in livro:
            l["titulo"] = livro["tituloLivro"]["value"]
        else:
            l["titulo"] = "Título Desconhecido"

        livros.append(l)

    return render_template('lista.html', livros=livros)

@app.route('/livro/<id_livro>')
def rota_livro(id_livro):
    q = f"""
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?titulo ?tipoID ?nomeAutor ?pais ?linhaID ?eventoID ?eventoNome ?eventoDesc WHERE {{
        :{id_livro} a ?tipoLivro .
        OPTIONAL {{ :{id_livro} :titulo ?titulo . }}
        :{id_livro} :escritoPor/:nome ?nomeAutor .
        :{id_livro} :escritoPor/:paisOrigem ?pais .
        :{id_livro} :existeEm ?linha .
        OPTIONAL {{
            :{id_livro} :refereEvento ?evento .
            ?evento :designacao ?eventoNome .
            OPTIONAL {{ ?evento :descricao ?eventoDesc . }}
            BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
        }}
        BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoID)
        BIND(STRAFTER(STR(?linha), "#") AS ?linhaID)
    }}
"""
    res = execute_query(q)
    if not res or not res["results"]["bindings"]:
        return "Livro não encontrado", 404

    rows = res["results"]["bindings"]
    first = rows[0]

    livro = {
        "id": id_livro,
        "titulo": first.get("titulo", {}).get("value", "Título Desconhecido"),
        "tipo": first.get("tipoID", {}).get("value", ""),
        "autor": first.get("nomeAutor", {}).get("value", ""),
        "pais": first.get("pais", {}).get("value", ""),
        "linhas": set(),
        "eventos": {}
    }

    for row in rows:
        if "linhaID" in row:
            livro["linhas"].add(row["linhaID"]["value"])
        if "eventoID" in row:
            eid = row["eventoID"]["value"]
            if eid not in livro["eventos"]:
                livro["eventos"][eid] = {
                    "id": eid,
                    "nome": row.get("eventoNome", {}).get("value", eid),
                    "descricao": row.get("eventoDesc", {}).get("value", "")
                }

    livro["linhas"] = sorted(livro["linhas"])
    livro["eventos"] = list(livro["eventos"].values())

    return render_template('livro.html', livro=livro)


@app.route('/evento/<id_evento>')
def rota_evento(id_evento):
    q = f"""
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?designacao ?descricao ?livroID ?tituloLivro WHERE {{
        :{id_evento} :designacao ?designacao .
        OPTIONAL {{ :{id_evento} :descricao ?descricao . }}
        OPTIONAL {{
            ?livro :refereEvento :{id_evento} .
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
            OPTIONAL {{ ?livro :titulo ?tituloLivro . }}
        }}
    }}
"""
    res = execute_query(q)
    if not res or not res["results"]["bindings"]:
        return "Evento não encontrado", 404

    rows = res["results"]["bindings"]
    first = rows[0]

    evento = {
        "id": id_evento,
        "designacao": first.get("designacao", {}).get("value", id_evento),
        "descricao": first.get("descricao", {}).get("value", ""),
        "livros": {}
    }

    for row in rows:
        if "livroID" in row:
            lid = row["livroID"]["value"]
            if lid not in evento["livros"]:
                evento["livros"][lid] = {
                    "id": lid,
                    "titulo": row.get("tituloLivro", {}).get("value", "Título Desconhecido")
                }

    evento["livros"] = list(evento["livros"].values())

    return render_template('evento.html', evento=evento)


@app.route('/eventos')
def rota_eventos():
    q = """
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?eventoID ?designacao ?descricao ?livroID ?tituloLivro WHERE {
        ?evento a ?tipoEvento .
        FILTER(?tipoEvento IN (:EventoHistorico, :EventoFuturo, :Evento))
        ?evento :designacao ?designacao .
        OPTIONAL { ?evento :descricao ?descricao . }
        OPTIONAL {
            ?livro :refereEvento ?evento .
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
            OPTIONAL { ?livro :titulo ?tituloLivro . }
        }
        BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
    }
    ORDER BY ?designacao
"""
    res = execute_query(q)
    eventos = {}

    for row in res["results"]["bindings"]:
        eid = row["eventoID"]["value"]
        if eid not in eventos:
            eventos[eid] = {
                "id": eid,
                "designacao": row.get("designacao", {}).get("value", eid),
                "descricao": row.get("descricao", {}).get("value", ""),
                "livros": {}
            }
        if "livroID" in row:
            lid = row["livroID"]["value"]
            if lid not in eventos[eid]["livros"]:
                eventos[eid]["livros"][lid] = {
                    "id": lid,
                    "titulo": row.get("tituloLivro", {}).get("value", "Título Desconhecido")
                }

    for e in eventos.values():
        e["livros"] = list(e["livros"].values())

    return render_template('eventos.html', eventos=list(eventos.values()))


if __name__ == '__main__':
    app.run(debug=True)