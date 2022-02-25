# Quick Guide to get your Duck


## Install duck with conda

We need `mamba` to install the requirements.
Use your existing `mamba` or install it from here:
https://github.com/conda-forge/miniforge

Get the source:
```console
git clone https://github.com/FREVA-CLINT/duck.git
cd duck
```

Create the conda environment for duck:
```console
mamba env create
```

Activate the duck environment:
```console
conda activate duck
```

Install duck in this environment:
```console
pip install -e .
```

Start your duck as a web service:
```console
duck start -d
```

See it is responding by sending a WPS `GetCapabilities` request:

http://localhost:5000?service=WPS&request=GetCapabilities

You can stop the service with:
```console
duck stop
```

## Start the service with access from outside

You need to start your service with the hostname and IP address to be accessible from outside.

Example:
```console
duck start --hostname smartduck.lake.earth -b 194.100.0.10
```

Check if it is running:
```console
duck status
```

Check access:

http://smartduck.lake.earth:5000?service=WPS&request=GetCapabilities

Stop it:
```console
duck stop
```
