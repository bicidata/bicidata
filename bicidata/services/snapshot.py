from datetime import datetime
from gbfs.client import GBFSClient
import json
from pathlib import Path


class GBFSOnlineResource(object):
    def __init__(
            self,
            api_url: str,
    ):
        self.client = GBFSClient(api_url)
        assert "station_status" in self.client.feeds, "GBFS must provide a 'station_status' endpoint."

    def snap(self):
        return (
            self.client.feeds.copy(),
            self.client.request_feed("station_status"),
        )


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

        with Path(f"gbfs/station_information/{timestamp}.json").open("w") as j:
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
        feeds, status = self.api.snap()

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
            station_status_snapshots="http://localhost:8000/gbfs/station_information/{timestamp}.json",
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

    GBFS_TARGET_API = "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json"
    SNAPSHOT_TIME = 60
    NUMBER_OF_SNAPSHOTS = 60 * 24

    snapshot = Snapshot(
        GBFSOnlineResource(GBFS_TARGET_API),
        FileStorageSaver()
    )

    snapshot.run()

    import asyncio


    async def periodic():
        while True:
            snapshot.run()
            await asyncio.sleep(SNAPSHOT_TIME)


    def stop():
        task.cancel()


    loop = asyncio.get_event_loop()
    loop.call_later(SNAPSHOT_TIME * NUMBER_OF_SNAPSHOTS, stop)
    task = loop.create_task(periodic())

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Cntrl+C pressed.")


