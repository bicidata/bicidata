import json
import os
from datetime import datetime
from pathlib import Path

import dotenv
from gbfs.client import GBFSClient
from requests.exceptions import RequestException


class ResourceNotAvailable(BaseException):
    pass


class GBFSOnlineResource(object):
    def __init__(
            self,
            api_url: str,
    ):
        self.client = GBFSClient(api_url)
        assert "station_status" in self.client.feeds, "GBFS must provide a 'station_status' endpoint."

    def snap(self):
        feeds = self.client.feeds.copy()
        try:
            data = self.client.request_feed("station_status")
        except RequestException:
            raise ResourceNotAvailable
        return feeds, data


class FileStorageSaver(object):
    def __init__(self):
        pass

    def save(
            self,
            timestamp: int,
            status: dict,
            snapshots: dict,
            gbfs: dict,
    ):

        with Path(f"gbfs/station_status/{timestamp}.json").open("w") as j:
            json.dump(status, j)

        with Path("gbfs/snapshots.json").open("w") as j:
            json.dump(snapshots, j)

        with Path("gbfs/gbfs.json").open("w") as j:
            json.dump(gbfs, j)


class Snapshot(object):
    def __init__(
            self,
            api_resource: GBFSOnlineResource,
            saver: FileStorageSaver,
    ):
        self.api = api_resource
        self.saver = saver

    def run(self):
        try:
            feeds, status = self.api.snap()
        except ResourceNotAvailable:
            return

        last_updated = int(datetime.timestamp(status.get("last_updated")))
        now = int(datetime.now().timestamp())

        status.update(
            last_updated=last_updated,
            ttl=-1,
        )

        snapshots = dict(
            last_updated=now,
            ttl=-1,
            data=dict(snapshots=[last_updated, ])
        )

        feeds.update(
            station_status_snapshots="http://localhost:8000/gbfs/station_status/{timestamp}.json",
            snapshots_information="http://localhost:8000/gbfs/snapshots.json",
        )

        gbfs = dict(
            last_updated=now,
            ttl=-1,
            data={
                "en": {"feeds": [dict(name=n, url=f) for n, f in feeds.items()]}
            }
        )

        self.saver.save(last_updated, status, snapshots, gbfs)


if __name__ == '__main__':

    dotenv.load_dotenv()

    snapshot = Snapshot(
        GBFSOnlineResource(os.environ.get(
            "GBFS_TARGET_API", "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json"
        )),
        FileStorageSaver()
    )

    snapshot.run()



