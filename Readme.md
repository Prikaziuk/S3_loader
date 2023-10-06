# Sentinel-3 images download

This script automates the per-point search and download of ESA Sentinel-3 images.

An interactive documentation can be found on https://s3-loader.readthedocs.io/

## Sources of data: 
- Copernicus Open Access Data Hub Service (DHUS) https://scihub.copernicus.eu/dhus (European Space Agency, ESA)
- Level-1 and Atmosphere Archive & Distribution System Distributed Active Archive Center (LAADS DAAC) https://ladsweb.modaps.eosdis.nasa.gov (National Aeronautics and Space Administration, NASA)

## Requirements

```python -m pip install requests``` requests library https://requests.readthedocs.io/en/master/user/install/

## Credentials
DHUS and DAAC require authorization  that should be provided in ``S3_loader/config.py`` next to the rest of the code:
```
AUTH = ('username', 'password')
DAAC_API_KEY = 'very-long-chain-of-characters'  # since some time called API_TOKEN by DAAC
```
### DAAC registration

``update: since some time DAAC uses tokens, it is just a different name for API KEY``

``DAAC_API_KEY`` can be generated on https://ladsweb.modaps.eosdis.nasa.gov/profiles/#generate-token-modal

Two agreements have to be accepted to activate the ``DAAC_API_KEY``:

1. ESA Sentinel-3 End User License Agreement:
	- navigate to https://urs.earthdata.nasa.gov/profile/edit
	- scroll to the bottom
	- tick "Yes, I Agree to ESA Sentinel-3 End User License Agreement."
2. NASA agreement:
	- navigate to https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/
	- click on "S3A_OL_1_EFR"
	- the page will be redirected to log-in


## Input:
- product type
- dates of acquisition
- coordinates of a point

```See example.py for details```


## User steps:
1. Query for product names and unique identifiers (uuid)
2. Download of products:
	- online products - direct parallel download from Copernicus Open Access Hub
	- offline products (Long term archive, LTA) - from LAADS DAAC (if available)
3. Extract pixels from loaded images:
	- ESA SNAP with Sentinel-3 toolbox is required for this operation: http://step.esa.int/main/download/snap-download/
	- shapely package (for Windows from wheel is recommended) https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
4. Database extras:
	- mark offline (LTA) products
	- mark products available at DAAC
	- set "loaded" to avoid double download

## Output:
- SQLite database file with tables:
	1. site: coordinates
		- to keep track of "single coordinates - single database"
	2. products: name, uuid, size:
		- individual table for each product type
- Downloaded products
- Text files with extracted pixels

## OLCI level-1: Google Earth Engine alternative

Google Earth Engine can do everything that this package does [pixel extraction], but there is only OLCI level-1 collection available 
https://code.earthengine.google.com/61fe01512385e06b5bc3f65f78bef692?noload=true

## Recommendations
- To open an SQLite database with GUI and export tables as csv you may use https://sqlitebrowser.org
- To download other Sentinel-1 and Sentinel-2 images you may use https://github.com/sentinelsat/sentinelsat
- Images from LTA are also (partially) available through Data and Information Access Services (DIAS) https://www.copernicus.eu/en/access-data/dias

The code was used in (Prikaziuk, Yang en Van der Tol, 2021) https://doi.org/10.3390/rs13061098



