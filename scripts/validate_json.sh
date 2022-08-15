#!/bin/bash
# Validate JSON against schemas.
set -euo pipefail

jsonschema -i data/variables.json schema/variablesIndex.json
jsonschema -i data/regions.json schema/regionsIndex.json

echo "Validation successful."
