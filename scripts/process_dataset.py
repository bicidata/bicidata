import io
import json
import multiprocessing as mp
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
import skvideo.io
from tqdm import tqdm


def fig_to_im(fig: plt.Figure) -> np.ndarray:
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))

    return im


# Folder where data is located:
data_folder = Path("data/snapshots_firebase").resolve()

# Load the dataset:
dataset = xr.load_dataset(data_folder / "dataset.dat")
dataset["post_code"] = xr.apply_ufunc(lambda x: [a.zfill(5) for a in x], dataset.post_code)

# Load geojson data from Barcelona province post codes and limit it to Barcelona city:
barcelona = gpd.read_file(data_folder / "barcelona_postcodes.geojson")
barcelona = barcelona.loc[barcelona["COD_POSTAL"].isin(dataset.post_code.to_pandas().unique())]
barcelona = barcelona.sort_values("COD_POSTAL")

dataset_post_code = dataset.groupby("post_code").sum()

# Compare occupation
bikes_available = dataset_post_code["num_bikes_available"] / dataset_post_code["capacity"]

fig = plt.figure()
ax = fig.add_subplot(111)
bikes_available.to_pandas().transpose()[["08016", "08001"]].rolling(60).mean().plot.line(ax=ax)
ax.set_xticks(np.arange(18883, 18898))
ax.grid()
ax.minorticks_on()
ax.set_title("Bike occupation (available/capacity)")
ax.set_ylim(0, 1)
ax.set_ylabel("Occupation")
# fig.savefig("reports/occupation_comparisson.png")


# Plot Barcelona
bikes_total = dataset_post_code["num_bikes_available"] + dataset_post_code["num_bikes_disabled"]
bikes_total = bikes_total.to_pandas()

# plt.ioff()


writer = skvideo.io.FFmpegWriter("reports/bikes_barcelona.mp4")

bikes_day = bikes_total.iloc[:, :1440*3:6]

for d in tqdm(bikes_day, total=len(bikes_day.columns)):
    fig: plt.Figure = plt.figure()
    ax = fig.add_subplot(111)
    bikes_barcelona = bikes_total[d]
    barcelona["bikes"] = [bikes_barcelona[postcode] for postcode in barcelona["COD_POSTAL"]]
    ax = barcelona.plot("bikes", ax=ax, vmax=500, vmin=0)
    ax.axis("off")
    ax.set_title(d)

    im = fig_to_im(fig)
    writer.writeFrame(im)

    plt.close(fig)


writer.close()
