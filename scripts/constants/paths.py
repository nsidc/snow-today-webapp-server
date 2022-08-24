from pathlib import Path


REPO_ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
REPO_DATA_DIR = REPO_ROOT_DIR / 'data'
REPO_SHAPES_DIR = REPO_DATA_DIR / 'shapes'

REGION_INDEX_FP = REPO_DATA_DIR / 'regions.json'
VARIABLES_INDEX_FP = REPO_DATA_DIR / 'variables.json'
