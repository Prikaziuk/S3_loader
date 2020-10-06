# Sentinel-3 images download

This script automates the per-point search and download of ESA Sentinel-3 images.

## Sources of data: 
- Copernicus Open Access Data Hub Service (DHUS) https://scihub.copernicus.eu/dhus (European Space Agency, ESA)
- Level-1 and Atmosphere Archive & Distribution System Distributed Active Archive Center (LAADS DAAC) https://ladsweb.modaps.eosdis.nasa.gov (National Aeronautics and Space Administration, NASA)

## Input:
- coordinates of a point
- product type
- dates of acquisition
- credentials for DHUS

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





