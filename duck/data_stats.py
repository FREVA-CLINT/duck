import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import yaml
import pathlib

def get_stats(data):
    return {
        "min": float(np.nanmin(data)), 
        "max": float(np.nanmax(data)), 
        "mean": float(np.nanmean(data)), 
        "std": float(np.nanstd(data))
    }


class DataStats(object):
    def __init__(self, output_dir):
        if isinstance(output_dir, pathlib.Path):
            self.output_dir = output_dir
        else:
            self.output_dir = pathlib.Path(output_dir)
        self.info = None

   
    def gen_data_stats(self, filename, var, nbins=100):
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
        plt.imshow(hist, aspect="auto", origin='lower', extent=[vstats["min"], vstats["max"], 0, ntime], cmap="gist_ncar")
        ax = plt.gca()
        ax.grid(color='gray', linestyle='-.', linewidth=1)
        plt.xlabel(var)
        plt.ylabel("Timesteps")
        outfile = self.output_dir / "histime.png"
        plt.savefig(outfile.as_posix(), dpi=50)

        # The following information should be stored in a database
        attrs = {}
        orig_attrs = dict(ds.attrs)
        for key in orig_attrs:
            value = isinstance(orig_attrs[key], str):
            attrs[key] = value

        self.info = {}
        self.info["Attrs"] = attrs
        self.info["Dims"] = dict(ds.dims)
        self.info["Vars"] = list(dict(ds.variables).keys())
        # print(vstats)
        self.info["Vstats"] = vstats
        self.info["Mstats"] = get_stats(mratio)
    
    def write_json(self):
        outfile = self.output_dir / "info.txt"
        with open(outfile.as_posix(), "w") as f:
            yaml.dump(self.info, f)
        return outfile
    
    def write_png(self):
        outfile = self.output_dir / "histime.png"
        return outfile



