import asyncio
import os

import dotenv

from bicidata.services.snapshot import Snapshot, GBFSOnlineResource, FileStorageSaver

if __name__ == '__main__':

    dotenv.load_dotenv()

    snapshot = Snapshot(
        GBFSOnlineResource(os.environ.get(
            "GBFS_TARGET_API", "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json")
        ),
        FileStorageSaver()
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