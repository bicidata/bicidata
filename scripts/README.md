To run the compilation of the dataset you must emulate a GBFS API, first unzip the 
`data/gbfs_bcn_dump_20200925.zip` into the data folder. The run from the root of the project: 

```
cd data/
python -m http.server
```

This will mock an API with the json files placed there. Now, in another terminal emulator, run:

```
python scripts/create_dataset.py
```

This will produce a xarray dataset that's supposed to be exactly like the one commited. 
To use the dataset you can play with `scripts/script.py` and run it:

```
python scripts/script.py
``` 
