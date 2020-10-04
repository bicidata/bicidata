import os
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, Any, Union

import dotenv
import pandas as pd
import xarray as xr
from tqdm import tqdm

from bicidata.common import GBFSResourceSnapshots

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


# TODO Generalize for any day and create a partial for yesterday
def is_yesterday(
        dt: Union[float, int, datetime]
) -> bool:
    if isinstance(dt, (float, int)):
        dt = datetime.utcfromtimestamp(dt)

    today = datetime.utcnow().date()
    yesterday = today - timedelta(1)

    today_dt = datetime(*today.timetuple()[:6])
    yesterday_dt = datetime(*yesterday.timetuple()[:6])

    return yesterday_dt < dt < today_dt


class DatasetSaver(object):
    def __init__(
            self,
            folder: Path = Path("data"),

    ):
        self.folder = folder

    def save(
            self,
            dataset: xr.Dataset,
            name: Union[str, Path] = "gbfs_dump.dat",
    ):
        comp = dict(zlib=True, complevel=5)
        encoding = {var: comp for var in dataset.data_vars}

        dataset.to_netcdf(
            self.folder / name,
            encoding=encoding,
            engine="h5netcdf"
        )


class Archiver(object):
    def __init__(
            self,
            api_resource: GBFSResourceSnapshots,
            saver: DatasetSaver,
    ):
        self.api = api_resource
        self.saver = saver

    def _make_dataset(self) -> xr.Dataset:
        snapshots = self.api.request_feed("snapshots_information")
        timestamps = (int(t) for t in snapshots.get("data").get("timestamps"))
        timestamps = sorted(filter(is_yesterday, timestamps))

        status_list = []

        for t in tqdm(timestamps):
            data = self.api.request_feed("station_status_snapshots", timestamp=t).get("data").get("stations")
            status = station_status_to_dataframe(data)
            status_list.append(status)

        dataset: xr.Dataset = xr.concat(
            [s.to_xarray() for s in status_list],
            dim=pd.DatetimeIndex(
                [datetime.utcfromtimestamp(t) for t in timestamps],
                name="times"
            )
        )

        data = self.api.request_feed("station_information").get("data").get("stations")
        info = pd.DataFrame.from_dict(data)
        info = info.set_index("station_id")
        info = info.sort_index(axis=1)
        info.index = info.index.astype(int)
        info = info.sort_index()
        info["groups"] = info.groups.apply(lambda x: x[0])
        info = info.drop("rental_methods", axis=1)

        return xr.merge([dataset, info.to_xarray()])

    def run(self):
        self.saver.save(self._make_dataset())


if __name__ == '__main__':

    dotenv.load_dotenv()

    archiver = Archiver(
        GBFSResourceSnapshots("http://35.241.203.225/gbfs.json"),
        DatasetSaver(
            folder=Path(os.environ.get("SNAPSHOT_GBFS_FOLDER", "data")),
        ),
    )
    archiver.run()
