from flask import Blueprint, render_template

from config import PREFIXES, ONTOLOGY_NS
from services.graphdb_client import run_select, run_update, run_ask
from services.queries import (
    get_classes_query,
    get_insertable_properties_query,
    ask_resource_exists_query,
    ask_class_exists_query,
    ask_property_exists_query,
    ask_instance_of_query,
    get_property_metadata_query,
)
from services.validation import (
    require_local_name,
    sparql_literal,
    sparql_string_literal,
    parse_boolean,
    literal_type_for_xsd_uri,
)
from flask import request

admin_bp = Blueprint("admin", __name__)


def local_name(uri):
    return str(uri).rstrip("/").split("/")[-1].split("#")[-1]


def is_internal_uri(uri):
    return str(uri).startswith(ONTOLOGY_NS)


def get_class_options():
    result = run_select(get_classes_query())
    classes = []

    for row in result.get("results", {}).get("bindings", []):
        classes.append(local_name(row["class"]["value"]))

    return sorted(classes)


def get_property_options():
    result = run_select(get_insertable_properties_query())
    properties = []

    for row in result.get("results", {}).get("bindings", []):
        prop_uri = row["property"]["value"]
        prop_type = row["type"]["value"]

        properties.append({
            "name": local_name(prop_uri),
            "type": local_name(prop_type),
        })

    return properties


def resource_exists(resource_name):
    return run_ask(ask_resource_exists_query(resource_name))


def class_exists(class_name):
    return run_ask(ask_class_exists_query(class_name))


def ensure_resource_exists(resource_name, field_name):
    if not resource_exists(resource_name):
        raise ValueError(f"{field_name} não existe na ontologia: {resource_name}")


def ensure_class_exists(class_name):
    if not class_exists(class_name):
        raise ValueError(f"Classe não existe na ontologia: {class_name}")


def ensure_instance_of(resource_name, class_name, field_name):
    ensure_resource_exists(resource_name, field_name)

    if not run_ask(ask_instance_of_query(resource_name, class_name)):
        raise ValueError(f"{field_name} deve ser instância de {class_name}: {resource_name}")


def get_property_metadata(property_name):
    result = run_select(get_property_metadata_query(property_name))

    types = set()
    domains = set()
    ranges = set()
    xsd_ranges = set()

    for row in result.get("results", {}).get("bindings", []):
        if "type" in row:
            types.add(local_name(row["type"]["value"]))

        if "domain" in row:
            domain_value = row["domain"]["value"]
            if is_internal_uri(domain_value):
                domains.add(local_name(domain_value))

        if "range" in row:
            range_value = row["range"]["value"]

            if is_internal_uri(range_value):
                ranges.add(local_name(range_value))
            elif range_value.startswith("http://www.w3.org/2001/XMLSchema#"):
                xsd_ranges.add(range_value)

    return {
        "types": types,
        "domains": sorted(domains),
        "ranges": sorted(ranges),
        "xsd_ranges": sorted(xsd_ranges),
    }


def validate_single_domain_range(resource_name, classes, field_name):
    # Se houver vários domínios/ranges explícitos, não se força validação.
    # Em OWL, múltiplos rdfs:domain não significam alternativa simples.
    if len(classes) != 1:
        return

    required_class = classes[0]

    if not run_ask(ask_instance_of_query(resource_name, required_class)):
        raise ValueError(f"{field_name} deve ser compatível com {required_class}: {resource_name}")


def validate_relation(subject, predicate, object_kind, object_value, literal_type):
    if not run_ask(ask_property_exists_query(predicate)):
        raise ValueError("Predicado não existe como ObjectProperty ou DatatypeProperty.")

    ensure_resource_exists(subject, "Sujeito")

    metadata = get_property_metadata(predicate)
    property_types = metadata["types"]

    validate_single_domain_range(subject, metadata["domains"], "Sujeito")

    if "ObjectProperty" in property_types:
        if object_kind != "resource":
            raise ValueError("Esta propriedade é ObjectProperty, por isso o objeto deve ser um recurso.")

        obj = require_local_name(object_value, "Objeto")
        ensure_resource_exists(obj, "Objeto")
        validate_single_domain_range(obj, metadata["ranges"], "Objeto")

        return f"mc:{obj}"

    if "DatatypeProperty" in property_types:
        if object_kind != "literal":
            raise ValueError("Esta propriedade é DatatypeProperty, por isso o objeto deve ser um literal.")

        expected_types = [
            literal_type_for_xsd_uri(uri)
            for uri in metadata["xsd_ranges"]
            if literal_type_for_xsd_uri(uri)
        ]

        expected_types = sorted(set(expected_types))

        if len(expected_types) == 1 and literal_type != expected_types[0]:
            raise ValueError(
                f"Tipo de literal inválido para {predicate}. "
                f"Esperado: {expected_types[0]}."
            )

        return sparql_literal(object_value, literal_type)

    raise ValueError("Tipo de propriedade não suportado.")


@admin_bp.route("/add-relation", methods=["GET", "POST"])
def add_relation():
    message = None
    properties = get_property_options()

    if request.method == "POST":
        try:
            subject = require_local_name(request.form.get("subject"), "Sujeito")
            predicate = require_local_name(request.form.get("predicate"), "Predicado")
            object_kind = request.form.get("object_kind")
            object_value = request.form.get("object")
            literal_type = request.form.get("literal_type", "string")

            object_expr = validate_relation(
                subject=subject,
                predicate=predicate,
                object_kind=object_kind,
                object_value=object_value,
                literal_type=literal_type,
            )

            update_query = PREFIXES + f"""
            INSERT DATA {{
              mc:{subject} mc:{predicate} {object_expr} .
            }}
            """

            run_update(update_query)
            message = "Triple inserida com sucesso."

        except Exception as e:
            message = f"Erro: {e}"

    return render_template(
        "add_relation.html",
        message=message,
        properties=properties,
    )


@admin_bp.route("/add-resource", methods=["GET", "POST"])
def add_resource():
    message = None
    classes = get_class_options()

    if request.method == "POST":
        try:
            resource_name = require_local_name(request.form.get("resource_name"), "Nome local")
            class_name = require_local_name(request.form.get("class_name"), "Classe")
            display_name = (request.form.get("display_name") or resource_name).strip()
            description = (request.form.get("description") or "").strip()

            ensure_class_exists(class_name)

            if resource_exists(resource_name):
                raise ValueError(f"Já existe um recurso com o nome: {resource_name}")

            triples = [
                f"mc:{resource_name} rdf:type mc:{class_name} .",
                f"mc:{resource_name} rdfs:label {sparql_string_literal(display_name)} .",
            ]

            if description:
                triples.append(
                    f"mc:{resource_name} rdfs:comment {sparql_string_literal(description)} ."
                )

            update_query = PREFIXES + """
            INSERT DATA {
            """ + "\n".join(triples) + """
            }
            """

            run_update(update_query)
            message = f"Recurso criado com sucesso: {resource_name}"

        except Exception as e:
            message = f"Erro: {e}"

    return render_template(
        "add_resource.html",
        message=message,
        classes=classes,
    )


@admin_bp.route("/add-knowledge", methods=["GET", "POST"])
def add_knowledge():
    message = None

    if request.method == "POST":
        try:
            knowledge_type = request.form.get("knowledge_type")
            primary = require_local_name(request.form.get("primary_value"), "Primeiro recurso")
            secondary_raw = request.form.get("secondary_value")
            boolean_raw = request.form.get("boolean_value")

            triples = []

            if knowledge_type == "mob_drop":
                secondary = require_local_name(secondary_raw, "Item")
                ensure_instance_of(primary, "Mob", "Mob")
                ensure_instance_of(secondary, "Item", "Item")

                triples = [
                    f"mc:{primary} mc:drops mc:{secondary} .",
                    f"mc:{secondary} mc:droppedBy mc:{primary} .",
                ]

            elif knowledge_type == "mob_spawn":
                secondary = require_local_name(secondary_raw, "Bioma")
                ensure_instance_of(primary, "Mob", "Mob")
                ensure_instance_of(secondary, "Biome", "Bioma")

                triples = [
                    f"mc:{primary} mc:spawnsIn mc:{secondary} .",
                    f"mc:{secondary} mc:hasSpawn mc:{primary} .",
                ]

            elif knowledge_type == "structure_biome":
                secondary = require_local_name(secondary_raw, "Bioma")
                ensure_instance_of(primary, "Structure", "Estrutura")
                ensure_instance_of(secondary, "Biome", "Bioma")

                triples = [
                    f"mc:{primary} mc:generatesIn mc:{secondary} .",
                    f"mc:{secondary} mc:hasStructure mc:{primary} .",
                ]

            elif knowledge_type == "dimension_access":
                secondary = require_local_name(secondary_raw, "Item")
                ensure_instance_of(primary, "Dimension", "Dimensão")
                ensure_instance_of(secondary, "Item", "Item")

                triples = [
                    f"mc:{primary} mc:requiredToEnter mc:{secondary} .",
                    f"mc:{secondary} mc:opensAccess mc:{primary} .",
                ]

            elif knowledge_type == "mining_tier":
                secondary = require_local_name(secondary_raw, "Tier")
                ensure_instance_of(primary, "Block", "Bloco")
                ensure_instance_of(secondary, "MaterialTier", "Tier")

                triples = [
                    f"mc:{primary} mc:requiresMinTier mc:{secondary} .",
                ]

            elif knowledge_type == "gravity_block":
                ensure_instance_of(primary, "Block", "Bloco")

                triples = [
                    f"mc:{primary} rdf:type mc:GravityBlock .",
                    f"mc:{primary} mc:affectedByGravity \"true\"^^xsd:boolean .",
                ]

            elif knowledge_type == "fire_immune":
                value = parse_boolean(boolean_raw, "Imune ao fogo")
                ensure_instance_of(primary, "Mob", "Mob")

                triples = [
                    f"mc:{primary} mc:isImmuneToFire \"{value}\"^^xsd:boolean .",
                ]

            elif knowledge_type == "sunlight_burn":
                value = parse_boolean(boolean_raw, "Arde à luz do sol")
                ensure_instance_of(primary, "Mob", "Mob")

                triples = [
                    f"mc:{primary} mc:isBurnableInSunlight \"{value}\"^^xsd:boolean .",
                ]

            else:
                raise ValueError("Tipo de conhecimento inválido.")

            update_query = PREFIXES + """
            INSERT DATA {
            """ + "\n".join(triples) + """
            }
            """

            run_update(update_query)
            message = "Conhecimento inserido com sucesso."

        except Exception as e:
            message = f"Erro: {e}"

    return render_template(
        "add_knowledge.html",
        message=message,
    )