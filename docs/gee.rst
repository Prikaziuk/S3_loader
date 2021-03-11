Google Earth Engine
======================

An alternative way of getting per pixel time series, available only for OLCI level-1 up to now
https://code.earthengine.google.com/61fe01512385e06b5bc3f65f78bef692?noload=true


However:

#. Data is modified (images are reprojected)
#. Tie-point coordinates are used (less accurate then per pixel geo-coordinates)

Missing data:

#. Observation geometry (solar and observation angles)
#. Meteorological data
#. Top of atmoshpere solar flux

Missing data can be restored in the following way.

Angles
--------

SZA, SAA - pysolar
OZA, OAA - download 10 best orbits

Meteodata
----------

CAMS

Solar flux
------------

Use table
