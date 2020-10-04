from typing import Optional, Union

from gbfs.client import GBFSClient
from gbfs.data.fetchers import RemoteJSONFetcher
from requests.exceptions import RequestException


class ResourceNotAvailable(BaseException):
    pass


# TODO explore asyncio fetcher!
class RemoteGBFS(RemoteJSONFetcher):
    def fetch(
            self,
            url: str,
    ):
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
