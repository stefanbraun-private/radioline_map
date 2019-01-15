# radioline_map
*radioline_map* reads network topology from master RF-module *RAD-868-IFS* (c) by Phoenix Contact
 combines it with GeoJSON metadata and generates an interactive layer on OSM (Open Street Map).

Copyright (C) 2019 Stefan Braun


## about radioline_map
An INOFFICIAL OpenSource command line application written in Python 3.  

This tool needs a serial connection to master RF-module via *RAD-CABLE-USB* (c) or *IFS-RS232-DATACABLE* (c) by Phoenix Contact.   
It is optimized for usage in our company and works well with *RAD-868-IFS*, it's possible that it works for all industrial radio frequency modules in their "Trusted Wireless 2.0" (c) product line with IFS-dataport.       
There's no warranty that this tool works in every situation!   
   
   
### usage   
```
usage: generate_map.py [-h] [--zoom ZOOM] [--open_browser] [-v] --port COMPORT
                       --mapfile MAPFILE --htmlfile HTMLFILE

Show network topology of RF-modules *RAD-868-IFS* on OSM(Open Street Map).

optional arguments:
  -h, --help            show this help message and exit
  --zoom ZOOM, -z ZOOM  initial zoom factor on map (default: 15)
  --open_browser, -b    open generated map in webbrowser (default: False)
  -v, --verbosity       output verbosity, setting this flag more times means
                        more verbosity (default: loglevel WARNING)

required named arguments:
  --port COMPORT, -p COMPORT
                        serial COM-port connected to IFS-dataport (e.g.
                        "COM1")
  --mapfile MAPFILE, -m MAPFILE
                        path to GeoJSON mapfile (e.g. "map.geojson")
  --htmlfile HTMLFILE, -o HTMLFILE
                        path to HTML output file (e.g. "map.html")
```
=>editing of GeoJSON file (editing of locations, modules and text):   
it's simple with website   
http://geojson.io   
simply "Open"->"File", then after editing "Save"->"GeoJSON"   
   
## example   
```
radioline_map.exe --port COM3 --mapfile ..\test\map.geojson --htmlfile ..\test\map.html --zoom 9 --open_browser -v -v
```   
   **=>subdirectory "test" on GitHub contains files for the example above.**   
   [hint: locations in "map.geojson" are fictional, the modules-setup is currently under my desk... :-) ]   
   [hint2: hmm, it seems that a HTML tag is missing in the generated file... otherwise I could you the interactive map under https://htmlpreview.github.io/?https://github.com/stefanbraun-private/radioline_map/blob/master/test/map.html ]   
   
Non-interactive Screenshot showing master module, network topology, RSSI-values, link quality and module metadata as popup and tooltip:   
![screenshot_radioline_map.png](https://stefanbraun-private.github.io/img/screenshot_radioline_map.png)
   
   
   
   
Disclaimer: Use 'radioline_map' at your own risk!   
