import json
from pathlib import Path

from IPython.display import Markdown, display
from jsonschema import ValidationError, validate
from loguru import logger

from snow_today_webapp_ingest.types_.base import BaseModel, RootModel


def display_jsonschema_and_example_markdown(
    *,
    example_fp: str,
    model: type[BaseModel] | type[RootModel],
    base_dir: str,
) -> None:
    include_fp = Path(base_dir, example_fp)
    include_json_dct = json.loads(include_fp.read_text())
    jsonschema_dct = model.model_json_schema()

    # Validate
    # NOTE: For whatever reason, the normal method of validating with Pydantic doesn't
    # work for the recursive hierarchy schema. JSONSchema validation does work.
    #     model.model_validate_json(include_str)
    try:
        validate(
            schema=jsonschema_dct,
            instance=include_json_dct,
        )
    except ValidationError as e:
        logger.error(f"'{include_fp.name}' failed validation ({e})")
        raise

    # Print schema from model and example
    display_jsonschema_markdown(jsonschema_dct)

    display(
        Markdown(
            f"""
<details>
<summary>Example</summary>
```{{.json filename="{example_fp}"}}
{json.dumps(include_json_dct, indent=2)}
```
</details>
"""
        )
    )


def display_jsonschema_markdown(
    jsonschema_dct: dict,
) -> None:
    json_str = json.dumps(jsonschema_dct, indent=2)
    display(
        Markdown(
            f"""
<details>
<summary>Schema</summary>
```json
{json_str}
```
</details>
"""
        )
    )
