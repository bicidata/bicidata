from datetime import datetime
from gbfs.client import GBFSClient
import json
from pathlib import Path

GBFS_TARGET_API = "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json"
SNAPSHOT_TIME = 60

client = GBFSClient(GBFS_TARGET_API)

assert "station_status" in client.feeds, "GBFS must provide a 'station_status' endpoint."

status: dict = client.request_feed("station_status")

last_updated = int(datetime.timestamp(status.get("last_updated")))
now = int(datetime.now().timestamp())

with Path(f"gbfs/station_information/{last_updated}.json").open("w") as j:
    status.update(
        last_updated=last_updated,
        ttl=-1,
    )
    json.dump(status, j)


with Path("gbfs/snapshots.json").open("w") as j:
    snapshots = dict(
        last_updated=now,
        ttl=SNAPSHOT_TIME,
        data=dict(snapshots=[last_updated, ])
    )
    json.dump(snapshots, j)

with Path("gbfs/gbfs.json").open("w") as j:

    feeds = client.feeds.copy()
    feeds.update(
        station_status_snapshots="http://localhost:8000/gbfs/station_information/{timestamp}.json",
        snapshots_information="http://localhost:8000/gbfs/snapshots.json",
    )

    gbfs = dict(
        last_updated=now,
        ttl=SNAPSHOT_TIME,
        data={
            client.language: {"feeds": [dict(name=n, url=f) for n, f in feeds.items()]}
        }
    )

    json.dump(gbfs, j)


client_localhost = GBFSClient("http://localhost:8000/gbfs/gbfs.json")
snapshots_list = client_localhost.request_feed("snapshots_information").get("data").get("snapshots")
a = [client_localhost.request_feed("station_status_snapshots", timestamp=s) for s in snapshots_list]

if __name__ == '__main__':
    pass

