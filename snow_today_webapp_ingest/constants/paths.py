import os
from pathlib import Path

REPO_ROOT_DIR = Path(__file__).parent.parent.parent.absolute()

# Where static content is stored
REPO_DATA_DIR = REPO_ROOT_DIR / 'data'
REPO_SHAPES_DIR = REPO_DATA_DIR / 'shapes'
REPO_LEGENDS_DIR = REPO_DATA_DIR / 'legends'

# Index data
REGION_INDEX_FP = REPO_DATA_DIR / 'regions.json'
VARIABLES_INDEX_FP = REPO_DATA_DIR / 'variables.json'

STORAGE_DIR = Path(os.environ['STORAGE_DIR'])

# Where we write outputs:
STORAGE_COGS_DIR = STORAGE_DIR / 'cogs'
STORAGE_DYNAMIC_LEGENDS_DIR = STORAGE_DIR / 'dynamic_legends'
STORAGE_PLOTS_DIR = STORAGE_DIR / 'plots'
STORAGE_POINTS_DIR = STORAGE_DIR / 'points'

# Where inputs are plopped by upstream program:
INCOMING_DIR = STORAGE_DIR / 'incoming'
INCOMING_SWE_DIR = INCOMING_DIR / 'snow-water-equivalent'
INCOMING_SSP_DIR = INCOMING_DIR / 'snow-surface-properties'

INCOMING_TIF_DIR = INCOMING_SSP_DIR / 'tif'
INCOMING_PLOT_CSV_DIR = INCOMING_SSP_DIR / 'plot_csv'
