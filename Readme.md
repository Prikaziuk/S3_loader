# Sentinel-3 images download

This script automates the per-point search and download of ESA Sentinel-3 images.

## Sources of data: 
- Copernicus Open Access Data Hub Service (DHUS) https://scihub.copernicus.eu/dhus (European Space Agency, ESA)
- Level-1 and Atmosphere Archive & Distribution System Distributed Active Archive Center (LAADS DAAC) https://ladsweb.modaps.eosdis.nasa.gov (National Aeronautics and Space Administration, NASA)

## Input:
- product type
- dates of acquisition
- coordinates of a point


## Credentials
DHUS and DAAC require authorization  that should be provided in ``S3_loader/S3_loader/config.py`` next to the rest of the code:
```
AUTH = ('username', 'password')
DAAC_API_KEY = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
```
``DAAC_API_KEY`` can be generated on https://ladsweb.modaps.eosdis.nasa.gov/profile/#app-keys.
ESA Sentinel-3 End User License Agreement should be accepted by ticking "Yes, I Agree to ESA Sentinel-3 End User License Agreement." at the end of the page https://urs.earthdata.nasa.gov/profile/edit

## Use cases:
1. Query for product names and unique identifiers (uuid)
2. Download of products:
	- online products - direct parallel download from Copernicus Open Access Hub
	- offline products (Long term archive, LTA) - from LAADS DAAC (if available)

## Output:
- SQLite database file with tables:
	1. site: coordinates
		- to keep track of "single coordinates - single database"
	2. products: name, uuid, size:
		- individual table for each product type
- Downloaded products


## Recommendations
- To open an SQLite database with GUI and export tables as csv you may use https://sqlitebrowser.org
- To download other Sentinel-1 and Sentinel-2 images you may use https://github.com/sentinelsat/sentinelsat
- Images from LTA are also (partially) available through Data and Information Access Services (DIAS) https://www.copernicus.eu/en/access-data/dias





