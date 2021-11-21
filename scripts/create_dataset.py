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


StationDict = Dict[str, Any]
bike_types = ["num_bikes_available_mechanical", "num_bikes_available_ebike"]


def station_status_to_dataframe(
        status: StationDict  # TODO implement better model types or dataclasses
) -> pd.DataFrame:
    status = pd.DataFrame.from_dict(status)
    status[bike_types] = status.num_bikes_available_types.apply(pd.Series)
    status = status.drop("num_bikes_available_types", axis=1)
    status = status.set_index("station_id")
    status = status.sort_index(axis=1)
    status.index = status.index.astype(int)
    status = status.sort_index()

    return status


def station_information_to_dataframe(data: StationDict) -> pd.DataFrame:
    info = pd.DataFrame.from_dict(data)
    info = info.set_index("station_id")
    info = info.sort_index(axis=1)
    info.index = info.index.astype(int)
    info = info.sort_index()
    info["groups"] = info.groups.apply(lambda x: x[0])
    info = info.drop("rental_methods", axis=1)
    return info


station_information = station_information_to_dataframe(
    json.loads(Path("../data/snapshots_firebase/station_information.json").read_text())
    .get("data")
    .get("stations")
)

data_folder = Path("../data/snapshots_firebase").resolve()

all_paths = sorted(
    f
    for p in sorted(p for p in data_folder.iterdir() if p.is_dir())[1:15]
    for f in p.iterdir() if f.suffix == ".json"
)
all_data = (json.loads(p.read_text()).get("data").get("stations") for p in all_paths)
# all_df = list(station_status_to_dataframe(d.get("data").get("stations")) for d in all_data)

def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text())

with mp.Pool(4) as pool:
    all_df = []
    for df in tqdm(pool.imap(station_status_to_dataframe, all_data, chunksize=144), total=len(all_paths)):
        all_df.append(df)

timestamps = [datetime.utcfromtimestamp(int(p.stem)) for p in all_paths]

dataset_status: xr.Dataset = xr.concat(
    [s.to_xarray() for s in all_df],
    dim=pd.DatetimeIndex(
        timestamps,
        name="times"
    )
)

dataset = xr.merge([dataset_status, station_information.to_xarray()])




