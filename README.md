# bicidata

`bicidata` from `bici` the equivalent of `bike` in Spanish, Catalan, Portuguese or Galician.  

`bici` is pronounced in two syllables `bi-ci`, which can be pronounced as something similar to
`be-cy` or `be-thy` for a English speaker. The first one approximates better to Catalan, 
Portuguese and Latin Spanish, the second one to Spanish and Galician.  

`bicidate` is a framework to work with the [General Bikeshare Feed Specification](https://github.com/NABSA/gbfs/blob/master/gbfs.md#gbfsjson) 
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
at the current timestamp. Now, it is implemented as a 24h snapshoter,this will change soon with 
a more elegant way to run it. For the moment: 

```
python -m bicidata.services.snapshot
```  



 


