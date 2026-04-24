# Demonstrator for GeoTools

![CI](https://github.com/anaegel/app_geotools/workflows/CI/badge.svg)

a) Read grid from TIFF.
b) Write to VTK.
c) Read ESRI-ascii raster data.
d) Perform simulation.


## Installation

### Option 1: mit pip
Install UG4 (via Python)
```
pip install ug4py-base
```

Install geotools app:
```
git clone https://github.com/anaegel/app_geotools
cd app_geotools
python example-python.py
```

### Option 2: mit Conda
Falls du Conda verwendest, kannst du die Umgebung über `environment.yml` erstellen:
```
conda env create -f environment.yml
conda activate ug4py-geotools-test
```

Danach die Beispiele ausführen:
```
python example-python.py
python example-tiff.py
```

## Run application
Run application as follows:
```
cd app_geotools
python example.py
```

## TODO:
Known issues:
* Read ASCII data.
