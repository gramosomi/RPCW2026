from flask import Blueprint, render_template, request
from services.graphdb_client import run_select
from services.queries import (
    get_classes_query,
    get_instances_of_class_query,
    get_resource_details_query,
    get_resource_inverse_query
)
from collections import defaultdict

ontology_bp = Blueprint("ontology", __name__)

def extract_local_name(uri: str) -> str:
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.rstrip("/").split("/")[-1]

@ontology_bp.route("/classes")
def list_classes():
    data = run_select(get_classes_query())
    classes = [extract_local_name(b["class"]["value"]) for b in data["results"]["bindings"]]
    return render_template("classes.html", classes=classes)

@ontology_bp.route("/classes/<class_name>")
def class_detail(class_name):
    data = run_select(get_instances_of_class_query(class_name))
    instances = [extract_local_name(b["instance"]["value"]) for b in data["results"]["bindings"]]
    return render_template("class_detail.html", class_name=class_name, instances=instances)

@ontology_bp.route("/resource/<resource_name>")
def resource_detail(resource_name):
    page = int(request.args.get("page", 1))
    per_page = 25

    direct = run_select(get_resource_details_query(resource_name))
    inverse = run_select(get_resource_inverse_query(resource_name))

    direct_rows = direct["results"]["bindings"]
    inverse_rows = inverse["results"]["bindings"]

    def is_blank_node_value(value: str) -> bool:
        if not value:
            return False
        value = str(value)
        return value.startswith("node") or "/.well-known/genid/" in value

    clean_direct = []
    for row in direct_rows:
        o_value = row.get("o", {}).get("value", "")
        if not is_blank_node_value(o_value):
            clean_direct.append(row)

    clean_inverse = []
    for row in inverse_rows:
        s_value = row.get("s", {}).get("value", "")
        if not is_blank_node_value(s_value):
            clean_inverse.append(row)

    grouped_direct = defaultdict(list)

    for row in clean_direct:
        predicate = row["p"]["value"]
        grouped_direct[predicate].append(row)

    grouped_direct = dict(sorted(grouped_direct.items(), key=lambda item: item[0]))

    grouped_inverse = defaultdict(list)

    for row in clean_inverse:
        predicate = row["p"]["value"]
        grouped_inverse[predicate].append(row)

    grouped_inverse = dict(sorted(grouped_inverse.items(), key=lambda item: item[0]))

    # Paginação
    group_items = list(grouped_inverse.items())
    total_groups = len(group_items)
    total_pages = max((total_groups + per_page - 1) // per_page, 1)

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    paginated_inverse_groups = group_items[start:end]

    # RELHA 3x3 BASEADA EM COORDENADAS ===
    grid_map = {}
    output_item = None
    
    if "recipe" in resource_name.lower() and "slot" not in resource_name.lower():

        query = f"""
        PREFIX : <http://rpcw.di.uminho.pt/2026/minecraft/>
        SELECT ?slotRow ?slotColumn ?item ?outputItem
        WHERE {{
            :{resource_name} :hasSlot ?slot .
            ?slot :slotRow ?slotRow .
            ?slot :slotColumn ?slotColumn .
            ?slot :slotItem ?item .
            OPTIONAL {{ :{resource_name} :produces ?outputItem . }}
        }}
        """
        grid_data = run_select(query)
        
        for row in grid_data["results"]["bindings"]:
            r = int(row["slotRow"]["value"])
            c = int(row["slotColumn"]["value"])
            uri = row["item"]["value"]
            item_name = uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
            grid_map[(r, c)] = item_name


            if not output_item and "outputItem" in row:
                out_uri = row["outputItem"]["value"]
                output_item = out_uri.split('#')[-1] if '#' in out_uri else out_uri.split('/')[-1]


    return render_template(
        "resource_detail.html",
        resource_name=resource_name,
        direct=clean_direct,
        inverse=clean_inverse,
        grouped_direct=grouped_direct.items(),
        grouped_inverse=paginated_inverse_groups,
        page=page,
        total_pages=total_pages,
        total_direct=len(clean_direct),
        total_inverse=len(clean_inverse),
        grid_map=grid_map,
        output_item=output_item
    )


    

