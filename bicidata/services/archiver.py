import os
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, Any, Union, List, Optional
from functools import partial

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


def station_information_to_dataframe(data):
    info = pd.DataFrame.from_dict(data)
    info = info.set_index("station_id")
    info = info.sort_index(axis=1)
    info.index = info.index.astype(int)
    info = info.sort_index()
    info["groups"] = info.groups.apply(lambda x: x[0])
    info = info.drop("rental_methods", axis=1)
    return info


def timestamp_is_date(
        dt: Union[float, int, datetime],
        day: Union[datetime, date]
) -> bool:
    if isinstance(dt, (float, int)):
        dt = datetime.utcfromtimestamp(dt)
    if isinstance(day, datetime):
        day = day.date()

    next_day = day + timedelta(1)

    day_dt = datetime(*day.timetuple()[:6])
    next_day_dt = datetime(*next_day.timetuple()[:6])

    return day_dt < dt < next_day_dt


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

    def _get_station_information(self) -> pd.DataFrame:
        station_data = self.api.request_feed("station_information").get("data").get("stations")
        return station_information_to_dataframe(station_data)

    def _get_station_status_snapshot(self, timestamp: int) -> pd.DataFrame:
        station_data = self.api.request_feed("station_status_snapshots", timestamp=timestamp).get("data").get("stations")
        return station_status_to_dataframe(station_data)

    def _get_snapshots_information(self) -> List[int]:
        timestamps_data = self.api.request_feed("snapshots_information").get("data").get("timestamps")
        return sorted(int(t) for t in timestamps_data)

    def _make_dataset(self) -> xr.Dataset:
        timestamps = self._get_snapshots_information()

        status_list = list(self._get_station_status_snapshot(t) for t in tqdm(timestamps))
        info = self._get_station_information()

        dataset_status: xr.Dataset = xr.concat(
            [s.to_xarray() for s in status_list],
            dim=pd.DatetimeIndex(
                [datetime.utcfromtimestamp(t) for t in timestamps],
                name="times"
            )
        )

        dataset_info = info.to_xarray()

        return xr.merge([dataset_status, dataset_info])

    def run(self):
        self.saver.save(self._make_dataset())


class ArchiverDate(Archiver):
    def __init__(
            self,
            api_resource: GBFSResourceSnapshots,
            saver: DatasetSaver,
            date: Optional[Union[datetime, date]] = None,
    ):
        self._date = None
        if date is not None:
            self.date = date
        super(ArchiverDate, self).__init__(api_resource, saver)

    @property
    def date(self):
        if self._date is not None:
            return self._date
        else:
            return datetime.utcnow().date() - timedelta(1)

    @date.setter
    def date(self, date):
        if isinstance(date, datetime):
            date = date.date()
        self._date = date

    # TODO move this hook inside the interface GBFSResourceSnapshots
    def _get_snapshots_information(self) -> List[int]:
        timestamps = super(ArchiverDate, self)._get_snapshots_information()
        is_date = partial(timestamp_is_date, day=self.date)
        timestamps = sorted(filter(is_date, timestamps))
        return timestamps


if __name__ == '__main__':

    dotenv.load_dotenv()

    archiver = ArchiverDate(
        GBFSResourceSnapshots("http://35.241.203.225/gbfs.json"),
        DatasetSaver(
            folder=Path(os.environ.get("SNAPSHOT_GBFS_FOLDER", "data")),
        ),
        date=datetime.utcnow().date() - timedelta(1)
    )
    archiver.run()
