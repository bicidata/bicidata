from datetime import datetime
import pandas as pd
from gbfs.client import GBFSClient
import xarray as xr
from tqdm import tqdm

client = GBFSClient("http://35.241.203.225/gbfs.json")
snapshots = client.request_feed("snapshots_information")

timestamps = sorted(int(t) for t in snapshots.get("data").get("timestamps"))

status_list = []

for t in tqdm(timestamps):
    data = client.request_feed("station_status_snapshots", timestamp=t).get("data").get("stations")

    status = pd.DataFrame.from_dict(data)

    bike_types = ["num_bikes_available_mechanical", "num_bikes_available_ebike"]
    status[bike_types] = status.num_bikes_available_types.apply(pd.Series)
    status = status.drop("num_bikes_available_types", axis=1)
    status = status.set_index("station_id")
    status = status.sort_index(axis=1)
    status.index = status.index.astype(int)
    status = status.sort_index()

    status_list.append(status)

dataset: xr.Dataset = xr.concat(
    [s.to_xarray() for s in status_list],
    dim=pd.DatetimeIndex(
        [datetime.utcfromtimestamp(t) for t in timestamps],
        name="times"
    )
)


data = client.request_feed("station_information").get("data").get("stations")
info = pd.DataFrame.from_dict(data)
info = info.set_index("station_id")
info = info.sort_index(axis=1)
info.index = info.index.astype(int)
info = info.sort_index()
info["groups"] = info.groups.apply(lambda x: x[0])
info = info.drop("rental_methods", axis=1)

dataset = xr.merge([dataset, info.to_xarray()])

comp = dict(zlib=True, complevel=5)
encoding = {var: comp for var in dataset.data_vars}

dataset.to_netcdf("data/gbfs_bcn_dump.dat", encoding=encoding, engine="h5netcdf")