import re

LOCAL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

XSD_TYPES = {
    "string": "xsd:string",
    "integer": "xsd:integer",
    "float": "xsd:float",
    "boolean": "xsd:boolean",
}

XSD_URI_TO_LITERAL_TYPE = {
    "http://www.w3.org/2001/XMLSchema#string": "string",
    "http://www.w3.org/2001/XMLSchema#integer": "integer",
    "http://www.w3.org/2001/XMLSchema#int": "integer",
    "http://www.w3.org/2001/XMLSchema#float": "float",
    "http://www.w3.org/2001/XMLSchema#double": "float",
    "http://www.w3.org/2001/XMLSchema#decimal": "float",
    "http://www.w3.org/2001/XMLSchema#boolean": "boolean",
}


def is_valid_local_name(value):
    return bool(value and LOCAL_NAME_RE.match(value))


def require_local_name(value, field_name):
    value = (value or "").strip()

    if not is_valid_local_name(value):
        print("teste")
        raise ValueError(f"{field_name} inválido.")

    return value


def sparql_literal(value, datatype):
    value = (value or "").strip()

    if datatype not in XSD_TYPES:
        raise ValueError("Tipo de literal inválido.")

    if datatype == "integer":
        int(value)
        return f'"{value}"^^xsd:integer'

    if datatype == "float":
        float(value)
        return f'"{value}"^^xsd:float'

    if datatype == "boolean":
        lowered = value.lower()
        if lowered not in {"true", "false"}:
            raise ValueError("Booleano deve ser true ou false.")
        return f'"{lowered}"^^xsd:boolean'

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"^^xsd:string'


def sparql_string_literal(value):
    return sparql_literal(value, "string")


def parse_boolean(value, field_name="Valor booleano"):
    value = (value or "").strip().lower()

    if value not in {"true", "false"}:
        raise ValueError(f"{field_name} deve ser true ou false.")

    return value


def literal_type_for_xsd_uri(uri):
    return XSD_URI_TO_LITERAL_TYPE.get(uri)