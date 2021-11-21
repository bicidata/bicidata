import json
import multiprocessing as mp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from tqdm import tqdm


data_folder = Path("data/snapshots_firebase").resolve()

dataset = xr.load_dataset(data_folder / "dataset.dat")

bikes_per_post_code = dataset.groupby("post_code").sum().num_bikes_available.to_pandas()
bikes_barcelona = bikes_per_post_code.iloc[:, 700]


barcelona = gpd.read_file(data_folder / "barcelona_postcodes.geojson")
barcelona = barcelona.sort_values("COD_POSTAL")

barcelona["bikes"] = [
    bikes_barcelona[postcode] if postcode in bikes_barcelona else np.nan
    for postcode in barcelona["COD_POSTAL"]
]
barcelona = barcelona.dropna()
ax = barcelona.plot("bikes", legend=True)
ax.axis("off")
