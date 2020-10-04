import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import dotenv

from bicidata.common import ResourceNotAvailable, GBFSResource


class FileStorageSaver(object):
    def __init__(
            self,
            folder: Path = Path("gbfs"),
            gbfs_url: str = "http://localhost:8000"
    ):
        self.folder = folder
        self.gbfs_url = gbfs_url

        (self.folder / "station_status").mkdir(parents=True, exist_ok=True)

        self._feeds_mirror_map = dict(
            station_status_snapshots=f"{self.gbfs_url}/station_status" + "/{timestamp}.json",
            snapshots_information=f"{self.gbfs_url}/snapshots.json",
        )

    def _make_gbfs(self, timestamp, feeds):
        return dict(
            last_updated=timestamp,
            ttl=-1,
            data={
                "en": {"feeds": [dict(name=n, url=f) for n, f in feeds.items()]}
            }
        )

    def _make_snapshots(self, snapshots_folder: Path, timestamp):
        if snapshots_folder.exists():
            with snapshots_folder.open("r") as j:
                snapshots = json.load(j)

            snapshots["data"]["timestamps"].append(timestamp)
            snapshots["last_updated"] = timestamp
            snapshots["ttl"] = -1

        else:
            snapshots = dict(
                last_updated=timestamp,
                ttl=-1,
                data=dict(timestamps=[timestamp, ])
            )

        return snapshots

    def save(
            self,
            timestamp: int,
            now: int,
            status: Dict,
            feeds: Dict
    ):

        with (self.folder / f"station_status/{timestamp}.json").open("w") as j:
            json.dump(status, j)

        snapshots_p = (self.folder / "snapshots.json")

        snapshots = self._make_snapshots(snapshots_p, timestamp)

        with snapshots_p.open("w") as j:
            json.dump(snapshots, j)

        feeds.update(self._feeds_mirror_map)

        gbfs = self._make_gbfs(now, feeds)

        with (self.folder / "gbfs.json").open("w") as j:
            json.dump(gbfs, j)


class FIFOFileStorageSaver(FileStorageSaver):

    def __init__(self, *args, **kwargs):
        self._fifo_size = kwargs.pop("size", 3)
        super(FIFOFileStorageSaver, self).__init__(*args, **kwargs)

    def _make_snapshots(self, snapshots_folder: Path, timestamp):
        # Hook a FIFO before returning the snapshots object:
        snapshots = super(FIFOFileStorageSaver, self)._make_snapshots(snapshots_folder, timestamp)

        if len(snapshots.get("data").get("timestamps")) >= self._fifo_size:
            pop_timestamp, *snapshots["data"]["timestamps"] = snapshots["data"]["timestamps"]
            os.remove(self.folder / f"station_status/{pop_timestamp}.json")

        return snapshots


class Snapshot(object):
    def __init__(
            self,
            api_resource: GBFSResource,
            saver: FileStorageSaver,

    ):
        self.api = api_resource
        self.saver = saver

    def run(self):
        try:
            # TODO this shoud be a model object
            status = self.api.request_feed("station_status")
        except ResourceNotAvailable:
            return

        feeds = self.api.feeds.copy()
        last_updated = int(datetime.timestamp(status.get("last_updated")))
        now = int(datetime.utcnow().timestamp())

        status.update(
            last_updated=last_updated,
            ttl=-1,
        )

        self.saver.save(last_updated, now, status, feeds)


if __name__ == '__main__':

    dotenv.load_dotenv()

    snapshot = Snapshot(
        GBFSResource(
            url=os.environ.get("GBFS_SRC_API", "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json")
        ),
        FileStorageSaver(
            folder=Path(os.environ.get("SNAPSHOT_GBFS_FOLDER", "gbfs")),
            gbfs_url=os.environ.get("GBFS_DST_API", "http://localhost:8000/gbfs"),
        )
    )

    snapshot.run()



