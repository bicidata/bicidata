# bicidata

`bicidata` from `bici` the equivalent of `bike` in Spanish, Catalan, Portuguese or Galician.  

`bici` is pronounced in two syllables `bi-ci`, which can be pronounced as something similar to
`be-cy` or `be-thy` for a English speaker. The first one approximates better to Catalan, 
Portuguese and Latin Spanish, the second one to Spanish and Galician.  

`bicidata` is a framework to work with the [General Bikeshare Feed Specification](https://github.com/NABSA/gbfs/blob/master/gbfs.md#gbfsjson) 
(GBFS) data and aims to develop several services to collect, process and publish data from GBFS 
feeds different front-ends, such as, social media bots, etc. 

It is based upon Python 3, with a very unstable package API until v1.0.0 is reached. You may
use the code here, but I must warn you we are in the early stage of development. 

## Installation

You can use a deployed PyPI version of `bicidata`: 

```
pip install bicidata
```

However, that version may be outdated, so I recommend to install directly from GitHub:

```
pip install git+https://github.com/bicidata/bicidata.git
```

Or, if you want to have access to the code to develop new features (PRs are welcome!):

```
git clone https://github.com/bicidata/bicidata.git & cd bicidata
pip install -e .
```

##  Services

`bicidata` it is thought as a framework to provide services to work with GBFS data. These 
services could run together as a Python app or be launched alone (i.e. dockerized). 
Thus, scalability will be one of the main goals of `bicidata`. Some services have already profiled:

- **Snapshots:** as GBFS data is updated in "real-time" and it is not stored we need to do it 
for ourselves. 
- **Archivers:** assuming GBFS data is stored in raw JSON format, and a snapshot is taken 
every minute, the amount of data per day reaches around ~200MB for the city of Barcelona. So,
some kind of data preprocessing is needed, it could be something as zipper, or something more 
powerful, as data bases. 
- **Reporters:** we want data with swag, so we will create _reports_  with the available data.
- **Publishers:** and finally we want the data to become available to the public. 

### Snapshots

This is the first service that is being implemented, it creates snapshots of a given GBFS API
at the current timestamp. 

Run

```
python -m bicidata.services.snapshot
``` 

and it will create a snapshot of a live GBFS API in you filesystem to acquire its data. If
you want to loop it, you perfectly can do something like this from inside Python:

```python
import time
from bicidata.services.snapshot import Snapshot, GBFSOnlineResource, FileStorageSaver

num_snapshots = 60
snapshot_sample_time = 60  # time in seconds

snapshot = Snapshot(
    GBFSOnlineResource("https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json"),
    FileStorageSaver(),
)

for _ in range(60):
    snapshot.run()   
    time.sleep(snapshot_sample_time)
``` 

To consume the acquired data, you will find some examples at the `scripts/` folder. To
check for an advanced snap-shooter, consider run the `server` app.   

### Archivers

For the moment, there are any services to compress the data to more advanced structures 
than JSON, but I'm playing with pandas and xarray at `scripts/create_dataset.py`, 
so take a look if you want! 

### Reporters

Same here, there is a compiled dataset in the repo, so, if you want to play with it, feel
free, at `scripts/scripts.py` you will find this to start playing with: 

```python
import pandas as pd
import xarray as xr

dataset = xr.open_dataset("data/gbfs_bcn_dump_20200925.dat")

capacity = int(dataset.capacity.sum())
print(f"'Bicing' total capacity: {capacity}")

max_bikes_available = int(dataset.num_bikes_available.sum("station_id").max())
print(f"'Bicing' max bikes available: {max_bikes_available}")

when_max_bikes_available = pd.to_datetime(
    dataset.times[dataset.num_bikes_available.sum("station_id").argmax()].values
)
print(f"When max bikes are available in UTC+0: {when_max_bikes_available}")
```

With should produce something like: 

```
'Bicing' total capacity: 13328
'Bicing' max bikes available: 4116
When max bikes are available in UTC+0: 2020-09-25 01:35:09
```

## Server

All services are planed to run in a server instance, this server first will be implemented 
in python, but the idea is to run it using docker-compose or kubernetes, at some point... 

Now, it is implemented as a 24h snap-shooter,this will change soon with 
a more elegant way to run it. For the moment: 

```
python -m bicidata.apps.server
``` 

You can configure the server changing the `.env.template` to `.env` and placing there your
desired configuration. 




