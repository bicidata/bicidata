from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, Union, List, Tuple
from functools import partial

from tqdm import tqdm
from gbfs.client import GBFSClient
from gbfs.data.fetchers import RemoteJSONFetcher
from requests.exceptions import RequestException

JSONDict = Dict[str, Any]


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


class ResourceNotAvailable(BaseException):
    pass


# TODO explore asyncio fetcher!
class RemoteGBFS(RemoteJSONFetcher):
    def fetch(
            self,
            url: str,
    ) -> JSONDict:
        try:
            return super(RemoteGBFS, self).fetch(url)
        except RequestException:
            raise ResourceNotAvailable


class GBFSResource(GBFSClient):
    def __init__(
            self,
            url: str,
            language: Optional[str] = None,
    ):
        super(GBFSResource, self).__init__(url, language, RemoteGBFS())
        assert "station_status" in self.feeds, "GBFS must provide a 'station_status' endpoint."


class GBFSResourceSnapshots(GBFSResource):
    def __init__(
            self,
            url: str,
            language: Optional[str] = None,
    ):
        super(GBFSResourceSnapshots, self).__init__(url, language)
        assert "snapshots_information" in self.feeds, "GBFS must provide a 'snapshots_information' endpoint."

    def _request_snapshots_timestamps(self) -> List[int]:
        timestamps_data = self.request_feed("snapshots_information").get("data").get("timestamps")
        return sorted(int(t) for t in timestamps_data)

    def request_snapshots(self) -> Tuple[List[int], List[JSONDict]]:
        ts = self._request_snapshots_timestamps()
        return (
            ts,
            [self.request_feed("station_status_snapshots", timestamp=t).get("data").get("stations") for t in tqdm(ts)]
        )


class GBFSResourceSnapshotsDate(GBFSResourceSnapshots):
    def __init__(
            self,
            url: str,
            language: Optional[str] = None,
            date: Optional[Union[datetime, date]] = None,
    ):
        super(GBFSResourceSnapshotsDate, self).__init__(url, language)
        self._date = None
        if date is not None:
            self.date = date

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

    def _request_snapshots_timestamps(self) -> List[int]:
        timestamps = super(GBFSResourceSnapshotsDate, self)._request_snapshots_timestamps()
        is_date = partial(timestamp_is_date, day=self.date)
        timestamps = sorted(filter(is_date, timestamps))
        return timestamps


