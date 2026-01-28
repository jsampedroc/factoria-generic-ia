import json
from pathlib import Path
from jsonschema import validate, ValidationError


class SchemaValidationError(Exception):
    pass


def validate_json(data: dict, schema_path: Path):
    schema = json.loads(schema_path.read_text())
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise SchemaValidationError(
            f"❌ JSON inválido según schema {schema_path.name}\n{e.message}"
        )