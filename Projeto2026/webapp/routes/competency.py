from flask import Blueprint, render_template, request

from services.graphdb_client import run_select
from services.queries import (
    get_recipe_ingredients_query,
    get_mobs_that_drop_item_query,
    get_biomes_for_mob_query,
    get_tool_for_block_query,
    get_items_for_enchantment_query,
    get_structures_for_biome_query,
    get_material_progression_query,
    get_fire_immune_mobs_query,
    get_sunlight_burn_mobs_query,
    get_required_items_for_dimension_query,
    get_gravity_blocks_query,
    get_top_foods_by_saturation_query,
    get_incompatible_enchantments_query,
    get_recipes_using_item_query,
)

QUERY_OPTIONS = {
    "ingredients": {
        "label": "Ingredientes de receita",
        "placeholder": "Ex.: torch",
        "builder": get_recipe_ingredients_query,
        "needs_input": True,
    },
    "drops": {
        "label": "Mobs que dropam item",
        "placeholder": "Ex.: gunpowder",
        "builder": get_mobs_that_drop_item_query,
        "needs_input": True,
    },
    "biomes": {
        "label": "Biomas de spawn de mob",
        "placeholder": "Ex.: creeper",
        "builder": get_biomes_for_mob_query,
        "needs_input": True,
    },
    "tool": {
        "label": "Ferramenta para minerar bloco",
        "placeholder": "Ex.: diamond_ore",
        "builder": get_tool_for_block_query,
        "needs_input": True,
    },
    "enchantment": {
        "label": "Items aplicáveis a encantamento",
        "placeholder": "Ex.: fortune",
        "builder": get_items_for_enchantment_query,
        "needs_input": True,
    },
    "structures": {
        "label": "Estruturas por bioma",
        "placeholder": "Ex.: desert",
        "builder": get_structures_for_biome_query,
        "needs_input": True,
    },
    "material_progression": {
        "label": "Progressão de tiers",
        "placeholder": "",
        "builder": get_material_progression_query,
        "needs_input": False,
    },
    "fire_immune": {
        "label": "Mobs imunes ao fogo",
        "placeholder": "",
        "builder": get_fire_immune_mobs_query,
        "needs_input": False,
    },
    "sunlight_burn": {
        "label": "Mobs que ardem à luz do sol",
        "placeholder": "",
        "builder": get_sunlight_burn_mobs_query,
        "needs_input": False,
    },
    "dimension_items": {
        "label": "Items necessários para dimensão",
        "placeholder": "Ex.: nether",
        "builder": get_required_items_for_dimension_query,
        "needs_input": True,
    },
    "gravity_blocks": {
        "label": "Blocos afetados pela gravidade",
        "placeholder": "",
        "builder": get_gravity_blocks_query,
        "needs_input": False,
    },
    "top_foods": {
        "label": "Alimentos com maior saturação",
        "placeholder": "",
        "builder": get_top_foods_by_saturation_query,
        "needs_input": False,
    },
    "incompatible": {
        "label": "Encantamentos incompatíveis",
        "placeholder": "Ex.: fortune",
        "builder": get_incompatible_enchantments_query,
        "needs_input": True,
    },
    "recipe_output": {
        "label": "Qual é o resultado desta receita?",
        "needs_input": True,
        "placeholder": "Ex.: recipe_985_13"
    },
    "recipes_using_item": {
        "label": "Receitas que usam item",
        "placeholder": "Ex.: stick",
        "builder": get_recipes_using_item_query,
        "needs_input": True,
    },
}

competency_bp = Blueprint("competency", __name__)


def fetch_resource_names():
    """Busca todos os nomes locais de recursos da ontologia."""
    query = """
    PREFIX : <http://rpcw.di.uminho.pt/2026/minecraft/>

    SELECT DISTINCT ?name WHERE {
        ?s a ?type .
        FILTER(STRSTARTS(STR(?s), STR(:)))
        BIND(STRAFTER(STR(?s), STR(:)) AS ?name)
        FILTER(?name != "")
    }
    ORDER BY ?name
    """
    try:
        result = run_select(query)
        return [row["name"]["value"] for row in result["results"]["bindings"]]
    except Exception:
        return []


@competency_bp.route("/", methods=["GET", "POST"])
def competency():
    result = None
    selected_query = None
    input_value = ""
    error = None

    if request.method == "POST":
        selected_query = request.form.get("query_type")
        input_value = (request.form.get("input_value") or "").strip()

        option = QUERY_OPTIONS.get(selected_query)

        if not option:
            error = "Tipo de query inválido."
        elif selected_query == "recipe_output":
            if not input_value:
                error = "Por favor, indica o nome da receita."
            else:
                from services.queries import get_recipe_output_query
                query = get_recipe_output_query(input_value)
                try:
                    result = run_select(query)
                except Exception as e:
                    error = str(e)
        else:
            try:
                query = option["builder"](input_value)
                result = run_select(query)
            except Exception as e:
                error = str(e)

    resource_names = fetch_resource_names()

    return render_template(
        "competency.html",
        result=result,
        selected_query=selected_query,
        input_value=input_value,
        query_options=QUERY_OPTIONS,
        error=error,
        resource_names=resource_names,
    )


@competency_bp.route("/sparql", methods=["GET", "POST"])
def sparql_livre():
    query = request.form.get("sparql_query", "").strip()
    result = None
    error = None

    if request.method == "GET":
        query = """PREFIX : <http://rpcw.di.uminho.pt/2026/minecraft/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 20"""

    if request.method == "POST":
        if not query:
            error = "O bloco de comandos não pode executar uma query vazia."
        else:
            try:
                result = run_select(query)
            except Exception as e:
                error = str(e)

    return render_template(
        "sparql.html",
        query=query,
        result=result,
        error=error
    )