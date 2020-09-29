import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

dataset = xr.open_dataset("data/gbfs_bcn_dump_20200925.dat")

capacity = int(dataset.capacity.sum())
print(f"'Bicing' total capacity: {capacity}")

max_bikes_available = int(dataset.num_bikes_available.sum("station_id").max())
print(f"'Bicing' max bikes available: {max_bikes_available}")

when_max_bikes_available = pd.to_datetime(
    dataset.times[dataset.num_bikes_available.sum("station_id").argmax()].values
)
print(f"When max bikes are available in UTC+0: {when_max_bikes_available}")


fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(111)

ds = dataset.sum("station_id")
ds.num_bikes_available.to_dataframe().plot.line(ax=ax, color="green")
ds.num_bikes_disabled.to_dataframe().plot.line(ax=ax, color="red")
ds.num_docks_available.to_dataframe().plot.line(ax=ax, color="blue")

ax.set_ylim(0, 10000)
ax.grid()
ax.set_ylabel("#")
ax.set_xlabel("Temps: Mes-dia hora")
ax.legend(["Bicis disponibles", "Bicis no funcionen", "Ancorartges disponibles"])

fig.savefig("data/fig0.png")


def values_pct(pct, bikes_totals):
    return f"{round(pct)}%, {int(pct/100 * bikes_totals)} bicis"


fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(111)

df = dataset.isel(times=dataset.num_bikes_available.sum("station_id").argmax()).to_dataframe()
df[["num_bikes_available", "num_bikes_disabled"]].sum().plot.pie(
    ax=ax,
    labels=["Disponibles", "No funcionen"],
    autopct=lambda x: values_pct(x, df[["num_bikes_available", "num_bikes_disabled"]].sum().sum())
)
ax.set_ylabel("")


fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(111)

df = dataset.isel(times=dataset.num_bikes_available.sum("station_id").argmax()).to_dataframe()
df[["num_bikes_available_mechanical", "num_bikes_available_ebike"]].sum().plot.pie(
    ax=ax,
    labels=["Mecàniques", "Elèctriques"],
    autopct=lambda x: values_pct(x, df[["num_bikes_available_mechanical", "num_bikes_available_ebike"]].sum().sum())
)
ax.set_ylabel("")


fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(111)

altitude_desc = dataset.altitude.to_dataframe().describe()

df: pd.DataFrame = (
    dataset
    .where(dataset.altitude < altitude_desc.loc["25%"].values)
    .num_bikes_available.dropna("station_id", how="all")
    .sum("station_id")
    .to_dataframe(name="Bicis disponibles 2-9 m")
)
df.plot.line(ax=ax)

df: pd.DataFrame = (
    dataset
    .where((dataset.altitude >= altitude_desc.loc["25%"].values) & (dataset.altitude < altitude_desc.loc["50%"].values))
    .num_bikes_available.dropna("station_id", how="all")
    .sum("station_id")
    .to_dataframe(name="Bicis disponibles 9-25 m")
)
df.plot.line(ax=ax)

df: pd.DataFrame = (
    dataset
    .where((dataset.altitude >= altitude_desc.loc["50%"].values) & (dataset.altitude < altitude_desc.loc["75%"].values))
    .num_bikes_available.dropna("station_id", how="all")
    .sum("station_id")
    .to_dataframe(name="Bicis disponibles 25-52 m")
)
df.plot.line(ax=ax)

df: pd.DataFrame = (
    dataset
    .where(dataset.altitude >= altitude_desc.loc["75%"].values)
    .num_bikes_available.dropna("station_id", how="all")
    .sum("station_id")
    .to_dataframe(name="Bicis disponibles 52-166 m")
)
df.plot.line(ax=ax)

ax.set_ylabel("#")
ax.set_xlabel("Temps: Mes-dia hora")
ax.set_ylim(0, 1800)
