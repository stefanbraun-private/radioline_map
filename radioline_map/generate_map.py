#!/usr/bin/env python
# encoding: utf-8
"""
radioline_map/generate_map.py

*radioline_map* reads network topology from master RF-module *RAD-868-IFS* (c) by Phoenix Contact
 combines it with GeoJSON metadata and generates an interactive layer on OSM (Open Street Map).

Copyright (C) 2019 Stefan Braun


changelog:
v0.0.1, January 13th 2019 -- release v0.0.1
v0.0.0, January 06th 2019 -- preparing start of project.



This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import logging
import argparse
import json
import folium
from radioline_map.serialconn import Serialconn
import webbrowser
import os


# setup of logging
# (based on tutorial https://docs.python.org/2/howto/logging.html )
# create logger =>set level to DEBUG if you want to catch all log messages!
logger = logging.getLogger('radioline_map.generate_map')
logger.setLevel(logging.DEBUG)

# create console handler
# =>set level to DEBUG if you want to see everything on console!
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

VERSION = '0.0.1'




class RadModule(object):
    def __init__(self, rad_id, postal_address, in_operation, longitude, latitude, comment):
        self.rad_id = rad_id
        self.postal_address = postal_address
        self.in_operation = in_operation
        self.longitude = longitude
        self.latitude = latitude
        self.comment = comment

        self.rssi = -255
        self.parent = 0

    def __repr__(self):
        """ developer representation of this object """
        # idea from https://stackoverflow.com/questions/25278563/python-return-dictionary-in-separate-lines-in-repr-method
        return self.__class__.__name__ + '(' + ', '.join('%s=%s' % (k, repr(v)) for k, v in self.__dict__.items()) + ')'



def main(comport, mapfile, htmlfile, zoom, open_browser, verbosity):

    logger.info('main(): radioline_map / version ' + VERSION)
    logger.info('main(): *********************************')

    # set console logging verbosity
    global ch
    if verbosity >= 3:
        ch.setLevel(logging.DEBUG)
    elif verbosity >= 2:
        ch.setLevel(logging.INFO)
    elif verbosity >= 1:
        ch.setLevel(logging.WARNING)
    else:
        ch.setLevel(logging.ERROR)


    logger.info('main(): Reading mapfile "' + mapfile + '" as GeoJSON file...')
    try:
        with open(mapfile, mode='r') as f:
            metadata = json.load(f)
    except Exception as ex:
        logger.exception('main(): Could not read mapfile! Got exception: ' + repr(ex))
        raise ex

    logger.info('main(): Extracting metadata from mapfile...')
    modules = {}
    try:
        rad_id_set = set()
        for feature in metadata['features']:
            # check RAD-ID
            rad_id = int(feature['properties']['RAD_ID'])
            assert 1 <= rad_id <= 250, 'RAD-ID must be a number from 1 to 250, got "' + str(rad_id) + '"instead...'
            assert rad_id not in rad_id_set, 'RAD-ID must be unique, "' + str(rad_id) + '" was chosen more than once...'
            rad_id_set.add(rad_id)

            # create Radioline module instances
            module = RadModule(rad_id=rad_id,
                               postal_address=feature['properties']['postal_address'],
                               in_operation=feature['properties']['in_operation'],
                               longitude=feature['geometry']['coordinates'][0],
                               latitude=feature['geometry']['coordinates'][1],
                               comment=feature['properties']['comment'])
            logger.debug('main(): Loaded Radioline-module: ' + repr(module))
            modules[rad_id] = module

        assert 1 in modules, 'Radioline master module with RAD-ID 1 is missing in GeoJSON file!'
    except Exception as ex:
        logger.exception('main(): Mapfile contains invalid metadata! Got exception: ' + repr(ex))
        raise ex


    # edited example from https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html
    #plt.plot([9.369685649871826, 8.723959922790527], [47.42320225367014, 47.500401963349994], 'r*-', linewidth=4)

    # generate layer on OpenStreetMap
    # based on examples from https://deparkes.co.uk/2016/05/06/colchester-public-toilets/
    # and https://deparkes.co.uk/2016/06/03/plot-lines-in-folium/

    # position of radioline master module is center of map
    logger.debug('main(): OpenStreetMap/leaflet.js map is centered at location [' + str(modules[1].longitude) + ', ' + str(
        modules[1].latitude) + ']')
    center = (modules[1].latitude, modules[1].longitude)
    rad_map = folium.Map(location=center, zoom_start=zoom)


    # get current network topology
    logger.info('main(): Establishing serial connection to master RF-module for getting network topology...')
    serialconn = Serialconn(comport=comport)
    parents_list = serialconn.get_networkstatus_list('parents')
    logger.debug('main(): parents_list=' + repr(parents_list))
    rssi_list = serialconn.get_networkstatus_list('rssi')
    logger.debug('main(): rssi_list=' + repr(rssi_list))


    # fill live network status into every slave module instance
    # =>we assume that GeoJSON file contains all RF modules!
    for key, mod in modules.items():
        # simplicity (or fragility?) in our data structure:
        #   key of modules dictionary == index in lists == RAD-ID
        mod.parent = parents_list[key]
        # interpretation of RSSI values: raw value 100 means -100dBm
        mod.rssi = -rssi_list[key]


    # add locations and connections to map
    for _, mod in modules.items():
        # adding module locations as markers
        if mod.rad_id == 1:
            # master module gets a special color
            color = 'blue'
        else:
            if mod.in_operation:
                if mod.parent:
                    color = 'green'
                else:
                    # unreachable module
                    color = 'red'
            else:
                # inactive module
                color = 'black'

        tooltip_str = '<br>'.join(['RAD-ID: ' + str(mod.rad_id),
                                   'RSSI: ' + str(mod.rssi) + 'dBm'])
        popup_str = '<br>'.join(['RAD-ID: ' + str(mod.rad_id),
                                 'address: ' + mod.postal_address,
                                 'RSSI: ' + str(mod.rssi) + 'dBm',
                                 'in operation: ' + 'yes' if mod.in_operation else 'no',
                                 'comment: ' + mod.comment])
        folium.Marker(location=[mod.latitude, mod.longitude],
                      popup=popup_str,
                      tooltip=tooltip_str,
                      icon=folium.Icon(color=color)).add_to(rad_map)

        # adding radio links as lines
        if mod.in_operation:
            if mod.parent:
                try:
                    parent = modules[mod.parent]
                    points = [(mod.latitude, mod.longitude),
                              (parent.latitude, parent.longitude)]
                    if mod.rssi > -90:
                        color = 'green'
                    elif mod.rssi > -100:
                        color = 'orange'
                    else:
                        color = 'red'
                    folium.PolyLine(points, color=color, weight=2.5, opacity=1).add_to(rad_map)
                except KeyError as ex:
                    logger.exception('main(): invalid topology detected: RAD-ID "' + str(mod.rad_id) + '" has invalid parent module!')
                    raise ex

    logger.info('main(): Saving generated OpenStreetMap/leaflet.js map into file ' + htmlfile)
    rad_map.save(htmlfile)

    if open_browser:
        # open generated map in system defaults webbrowser
        # with help from https://stackoverflow.com/questions/22004498/webbrowser-open-in-python
        abs_path = os.path.realpath(htmlfile)
        url = 'file://' + abs_path
        logger.info('main(): Open generated file in default webbrowser (URL=' + url + ')')
        webbrowser.open(url)

    # FIXME: we should return correct status when something went wrong...
    return 0        # success



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show network topology of RF-modules *RAD-868-IFS* on OSM(Open Street Map).')

    parser.add_argument('--zoom', '-z', dest='zoom', type=int, help='initial zoom factor on map (default: 15)', default=15)
    parser.add_argument('--open_browser', '-b', action="store_true", help='open generated map in webbrowser (default: False)')

    # allow increase of loglevel with command line argument
    # (help from https://docs.python.org/3/howto/argparse.html )
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="output verbosity, setting this flag more times means more verbosity (default: loglevel WARNING)")

    # with help from https://stackoverflow.com/questions/24180527/argparse-required-arguments-listed-under-optional-arguments
    requiredNamed = parser.add_argument_group('required named arguments')

    requiredNamed.add_argument('--port', '-p', dest='comport', type=str, help='serial COM-port connected to IFS-dataport (e.g. "COM1")', required=True)
    requiredNamed.add_argument('--mapfile', '-m', dest='mapfile', type=str, help='path to GeoJSON mapfile (e.g. "map.geojson")', required=True)
    requiredNamed.add_argument('--htmlfile', '-o', dest='htmlfile', type=str, help='path to HTML output file (e.g. "map.html")', required=True)

    args = parser.parse_args()

    status = main(comport = args.comport,
                  mapfile = args.mapfile,
                  htmlfile = args.htmlfile,
                  zoom = args.zoom,
                  open_browser = args.open_browser,
                  verbosity = args.verbosity
                  )
    #sys.exit(status)
