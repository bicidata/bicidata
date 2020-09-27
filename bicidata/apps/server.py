import asyncio
import os
from pathlib import Path

import dotenv

from bicidata.services.snapshot import Snapshot, GBFSOnlineResource, FileStorageSaver

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


    async def periodic():
        while True:
            try:
                snapshot.run()
                print("Snapshot!")
            except Exception as e:
                print(e)
            await asyncio.sleep(int(os.environ.get("SNAPSHOT_SAMPLE_TIME", 60)))


    def stop():
        task.cancel()


    loop = asyncio.get_event_loop()
    task = loop.create_task(periodic())

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Aborted.")