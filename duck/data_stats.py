import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import yaml


def get_stats(data):
    return {"min": np.nanmin(data), "max": np.nanmax(data), "mean": np.nanmean(data), "std": np.nanstd(data)}

def gen_data_stats(filename, var, nbins=100):
    ds = xr.open_dataset(filename)

    vstats = get_stats(ds[var].values)
    bins = np.linspace(vstats["min"], vstats["max"], num=nbins + 1)

    ntime, nlon, nlat = ds[var].shape
    mratio = np.zeros(ntime)
    hist = np.zeros((ntime, nbins))
    for i in range(ntime):
        a = ds[var].values[i]
        idx = ~np.isnan(a)
        mratio[i] = idx.sum()
        a = np.histogram(a[idx], bins=bins)[0]
        hist[i] = a / max(a)

    mratio = 1 - mratio / (nlon * nlat)

    # TODO: It would be great to store the distribution graph in a database
    if False:
        plt.imshow(hist, aspect="auto", origin='lower', extent=[vstats["min"], vstats["max"], 0, ntime], cmap="gist_ncar")
        ax = plt.gca()
        ax.grid(color='gray', linestyle='-.', linewidth=1)
        plt.xlabel(var)
        plt.ylabel("Timesteps")
        plt.savefig("histime.png", dpi=50)

    # The following information should be stored in a database
    info = {}
    info["Attrs"] = str(ds.attrs)
    info["Dims"] = str(ds.dims)
    info["Vars"] = str(ds.variables)
    info["Vstats"] = str(vstats)
    info["Mstats"] = str(get_stats(mratio))
    with open("info.txt", "w") as f:
        yaml.safe_dump(info, f)

    return {"hist": "histime.png", "info": "info.txt"}
