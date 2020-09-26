import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

dataset = xr.open_dataset("data/gbfs_bcn_dump_20200925.dat")

capacity = int(dataset.capacity.sum())
print(f"'Bicing' total capacity:t status {capacity}")

max_bikes_available = int(dataset.num_bikes_available.sum("station_id").max())
print(f"'Bicing' max bikes available: {max_bikes_available}")

when_max_bikes_available = pd.to_datetime(
    dataset.times[dataset.num_bikes_available.sum("station_id").argmax()].values
)
print(f"When max bikes are available in UTC+0: {when_max_bikes_available}")


