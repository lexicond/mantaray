# %% [markdown]
#

# %%
## Imports
import logging
from pathlib import Path
logging.basicConfig(level=logging.DEBUG)

import plecos.plecos as plecos

PATH_DATA_ROOT = Path("~/DATA").expanduser()
path_data_dir = PATH_DATA_ROOT / 'British_birdsong'
path_metadata = path_data_dir / 'metadata.json'
if not plecos.is_valid(path_metadata):
    plecos.list_errors(path_metadata)


