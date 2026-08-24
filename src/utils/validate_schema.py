import json
import sys

import jsonschema
from jsonschema import ValidationError


def main():
    schema_path = "schema/output_schema.json"
    output_path = "data/testing-input-output/output.json"

    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
        with open(output_path, "r") as f:
            data = json.load(f)

        jsonschema.validate(instance=data, schema=schema)
        print("✅ Schema Compliance Audit PASSED: Output payload strictly adheres to schema contracts.")
    except ValidationError as e:
        print(f"❌ CONSTITUTION VIOLATION: Output payload failed schema validation: {e.message}", file=sys.stderr)
        sys.exit(1)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"❌ CRITICAL ERROR during schema verification: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
