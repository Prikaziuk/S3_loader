# Sentinel-3 images download

This script automates the per-point search and download of ESA Sentinel-3 images.

## Sources of data: 
- Copernicus Open Access Data Hub Service (DHUS) https://scihub.copernicus.eu/dhus (European Space Agency, ESA)
- Level-1 and Atmosphere Archive & Distribution System Distributed Active Archive Center (LAADS DAAC) https://ladsweb.modaps.eosdis.nasa.gov (National Aeronautics and Space Administration, NASA)

## Input:
- product type
- dates of acquisition
- coordinates of a point

```See example.py for details```

## Credentials
DHUS and DAAC require authorization  that should be provided in ``S3_loader/config.py`` next to the rest of the code:
```
AUTH = ('username', 'password')
DAAC_API_KEY = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
```
``DAAC_API_KEY`` can be generated on https://ladsweb.modaps.eosdis.nasa.gov/profile/#app-keys.
ESA Sentinel-3 End User License Agreement should be accepted by ticking "Yes, I Agree to ESA Sentinel-3 End User License Agreement." at the end of the page https://urs.earthdata.nasa.gov/profile/edit

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





