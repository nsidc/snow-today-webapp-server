#!/bin/bash
# Validate JSON against schemas.

jsonschema -i data/variables.json schema/variablesIndex.json
jsonschema -i data/shapes/states/index.json schema/shapesIndex.json

echo "Validation successful."
