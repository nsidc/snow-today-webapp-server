---
title: "Webapp data interface"
---

The webapp data interface represents the **output** of the `snow_today_webapp_ingest`
Python code in this repository.

This output is written to a directory hosted by a web server so that the files can be
accessed by the browsers of users using the webapp.

This interface has been vastly simplified since the previous iteration of this
application, as the supercomputer now sends data largely ready-to-go. The major
differences between the supercomputer interface and this one are:

* We dynamically generate **legends** based on the data sent by the supercomputer.
* We convert GeoTIFFs sent by the super computer to **Cloud Optimized GeoTIFFs**.
* We copy over some **static** data from this repository (in the `static/` directory).
