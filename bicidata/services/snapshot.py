import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

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
    def __init__(
            self,
            folder: Path = Path("gbfs"),
            gbfs_url: str = "http://localhost:8000"
    ):
        self.folder = folder
        self.gbfs_url = gbfs_url

    def save(
            self,
            timestamp: int,
            now: int,
            status: Dict,
            snapshots: Dict,
            feeds: Dict
    ):
        (self.folder / "station_status").mkdir(parents=True, exist_ok=True)

        with (self.folder / f"station_status/{timestamp}.json").open("w") as j:
            json.dump(status, j)

        snapshots_p = (self.folder / "snapshots.json")

        if snapshots_p.exists():
            with snapshots_p.open("r") as j:
                curr_snapshots = json.load(j)

            prev_snapshots = curr_snapshots.get("data").get("timestamps")
            prev_snapshots += snapshots.get("data").get("timestamps")

            snapshots["data"]["timestamps"] = prev_snapshots

        with snapshots_p.open("w") as j:
            json.dump(snapshots, j)

        feeds.update(
            station_status_snapshots=f"{self.gbfs_url}/station_status" + "/{timestamp}.json",
            snapshots_information=f"{self.gbfs_url}/snapshots.json",
        )

        gbfs = dict(
            last_updated=now,
            ttl=-1,
            data={
                "en": {"feeds": [dict(name=n, url=f) for n, f in feeds.items()]}
            }
        )

        with (self.folder / "gbfs.json").open("w") as j:
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
            # TODO this shoud be a model object
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
            data=dict(timestamps=[last_updated, ])
        )

        self.saver.save(last_updated, now, status, snapshots, feeds)


if __name__ == '__main__':

    dotenv.load_dotenv()

    snapshot = Snapshot(
        GBFSOnlineResource(
            api_url=os.environ.get("GBFS_SRC_API", "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json")
        ),
        FileStorageSaver(
            folder=Path(os.environ.get("SNAPSHOT_GBFS_FOLDER", "gbfs")),
            gbfs_url=os.environ.get("GBFS_DST_API", "http://localhost:8000/gbfs"),
        )
    )

    snapshot.run()



