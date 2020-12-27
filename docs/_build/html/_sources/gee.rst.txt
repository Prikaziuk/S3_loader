Google Earth Engine
======================

An alternative way of getting per pixel time series.

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
