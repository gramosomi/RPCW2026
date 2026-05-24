import re

from config import PREFIXES

LOCAL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def safe_local_name(value: str) -> str:
    value = (value or "").strip()

    if not LOCAL_NAME_RE.match(value):
        raise ValueError("Nome local inválido.")

    return value


def get_classes_query():
    return PREFIXES + """
    SELECT DISTINCT ?class
    WHERE {
      ?class a owl:Class .
      FILTER(STRSTARTS(STR(?class), STR(mc:)))
    }
    ORDER BY ?class
    """


def get_instances_of_class_query(class_name: str):
    class_name = safe_local_name(class_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?instance
    WHERE {{
      ?instance rdf:type ?type .
      ?type rdfs:subClassOf* mc:{class_name} .
      FILTER(STRSTARTS(STR(?instance), STR(mc:)))
      FILTER(?instance != mc:{class_name})
    }}
    ORDER BY ?instance
    """


def get_resource_details_query(resource_name: str):
    resource_name = safe_local_name(resource_name)

    return PREFIXES + f"""
    SELECT ?p ?o
    WHERE {{
      mc:{resource_name} ?p ?o .
    }}
    ORDER BY ?p ?o
    """


def get_resource_inverse_query(resource_name: str):
    resource_name = safe_local_name(resource_name)

    return PREFIXES + f"""
    SELECT ?s ?p
    WHERE {{
      ?s ?p mc:{resource_name} .
    }}
    ORDER BY ?p ?s
    """


def get_recipe_ingredients_query(item_name: str):
    item_name = safe_local_name(item_name)

    return PREFIXES + f"""
    SELECT ?recipe ?ingredient (COUNT(?slot) AS ?quantity) ?outputQuantity
    WHERE {{
      ?recipe mc:produces mc:{item_name} ;
              mc:outputQuantity ?outputQuantity ;
              mc:hasSlot ?slot .

      ?slot mc:slotItem ?ingredient .
    }}
    GROUP BY ?recipe ?ingredient ?outputQuantity
    ORDER BY ?recipe ?ingredient
    """


def get_mobs_that_drop_item_query(item_name: str):
    item_name = safe_local_name(item_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?mob
    WHERE {{
      {{
        mc:{item_name} mc:droppedBy ?mob .
      }}
      UNION
      {{
        ?mob mc:drops mc:{item_name} .
      }}
    }}
    ORDER BY ?mob
    """


def get_biomes_for_mob_query(mob_name: str):
    mob_name = safe_local_name(mob_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?biome
    WHERE {{
      {{
        mc:{mob_name} mc:spawnsIn ?biome .
      }}
      UNION
      {{
        ?biome mc:hasSpawn mc:{mob_name} .
      }}
    }}
    ORDER BY ?biome
    """


def get_tool_for_block_query(block_name: str):
    block_name = safe_local_name(block_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?tool ?tier
    WHERE {{
      OPTIONAL {{
        mc:{block_name} mc:minedWith ?tool .
      }}
      OPTIONAL {{
        mc:{block_name} mc:requiresMinTier ?tier .
      }}
    }}
    ORDER BY ?tier ?tool
    """


def get_items_for_enchantment_query(enchantment_name: str):
    enchantment_name = safe_local_name(enchantment_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?item
    WHERE {{
      {{
        ?item mc:canBeEnchantedWith mc:{enchantment_name} .
      }}
      UNION
      {{
        mc:{enchantment_name} mc:applicableTo ?item .
      }}
    }}
    ORDER BY ?item
    """


def get_structures_for_biome_query(biome_name: str):
    biome_name = safe_local_name(biome_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?structure
    WHERE {{
      {{
        ?structure mc:generatesIn mc:{biome_name} .
      }}
      UNION
      {{
        mc:{biome_name} mc:hasStructure ?structure .
      }}
    }}
    ORDER BY ?structure
    """


def get_material_progression_query(_unused: str = ""):
    return PREFIXES + """
    SELECT ?tier ?order
    WHERE {
      ?tier a mc:MaterialTier ;
            mc:tierOrder ?order .
    }
    ORDER BY ?order ?tier
    """


def get_fire_immune_mobs_query(_unused: str = ""):
    return PREFIXES + """
    SELECT DISTINCT ?mob
    WHERE {
      ?mob mc:isImmuneToFire true .
    }
    ORDER BY ?mob
    """


def get_sunlight_burn_mobs_query(_unused: str = ""):
    return PREFIXES + """
    SELECT DISTINCT ?mob
    WHERE {
      ?mob mc:isBurnableInSunlight true .
    }
    ORDER BY ?mob
    """


def get_required_items_for_dimension_query(dimension_name: str):
    dimension_name = safe_local_name(dimension_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?item
    WHERE {{
      {{
        mc:{dimension_name} mc:requiredToEnter ?item .
      }}
      UNION
      {{
        ?item mc:opensAccess mc:{dimension_name} .
      }}
    }}
    ORDER BY ?item
    """


def get_gravity_blocks_query(_unused: str = ""):
    return PREFIXES + """
    SELECT DISTINCT ?block
    WHERE {
      {
        ?block a mc:GravityBlock .
      }
      UNION
      {
        ?block mc:affectedByGravity true .
      }
    }
    ORDER BY ?block
    """


def get_top_foods_by_saturation_query(_unused: str = ""):
    return PREFIXES + """
    SELECT ?food ?saturation ?foodPoints
    WHERE {
      ?food a mc:Food ;
            mc:saturation ?saturation ;
            mc:foodPoints ?foodPoints .
    }
    ORDER BY DESC(?saturation)
    LIMIT 20
    """


def get_incompatible_enchantments_query(enchantment_name: str):
    enchantment_name = safe_local_name(enchantment_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?other
    WHERE {{
      {{
        mc:{enchantment_name} mc:incompatibleWith ?other .
      }}
      UNION
      {{
        ?other mc:incompatibleWith mc:{enchantment_name} .
      }}
    }}
    ORDER BY ?other
    """


def ask_resource_exists_query(resource_name: str):
    resource_name = safe_local_name(resource_name)

    return PREFIXES + f"""
    ASK {{
      {{
        mc:{resource_name} ?p ?o .
      }}
      UNION
      {{
        ?s ?p mc:{resource_name} .
      }}
    }}
    """


def ask_class_exists_query(class_name: str):
    class_name = safe_local_name(class_name)

    return PREFIXES + f"""
    ASK {{
      mc:{class_name} a owl:Class .
    }}
    """


def ask_property_exists_query(property_name: str):
    property_name = safe_local_name(property_name)

    return PREFIXES + f"""
    ASK {{
      mc:{property_name} a ?type .
      FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
    }}
    """


def ask_instance_of_query(resource_name: str, class_name: str):
    resource_name = safe_local_name(resource_name)
    class_name = safe_local_name(class_name)

    return PREFIXES + f"""
    ASK {{
      mc:{resource_name} rdf:type ?type .
      ?type rdfs:subClassOf* mc:{class_name} .
    }}
    """


def get_property_metadata_query(property_name: str):
    property_name = safe_local_name(property_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?type ?domain ?range
    WHERE {{
      mc:{property_name} a ?type .
      FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))

      OPTIONAL {{
        mc:{property_name} rdfs:domain ?domain .
      }}

      OPTIONAL {{
        mc:{property_name} rdfs:range ?range .
      }}
    }}
    ORDER BY ?type ?domain ?range
    """


def get_insertable_properties_query():
    return PREFIXES + """
    SELECT DISTINCT ?property ?type
    WHERE {
      ?property a ?type .
      FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
      FILTER(STRSTARTS(STR(?property), STR(mc:)))
    }
    ORDER BY ?property
    """

def get_recipes_using_item_query(item_name: str):
    item_name = safe_local_name(item_name)

    return PREFIXES + f"""
    SELECT DISTINCT ?recipe ?outputItem
    WHERE {{
      {{
        ?recipe mc:hasIngredient mc:{item_name} .
      }}
      UNION
      {{
        ?recipe mc:hasSlot ?slot .
        ?slot mc:slotItem mc:{item_name} .
      }}

      OPTIONAL {{
        ?recipe mc:produces ?outputItem .
      }}
    }}
    ORDER BY ?recipe
    """

def get_recipe_output_query(recipe_name: str) -> str:
    recipe_name = safe_local_name(recipe_name)

    return PREFIXES + f"""
    SELECT ?outputItem
    WHERE {{
      mc:{recipe_name} mc:produces ?outputItem .
    }}
    """
