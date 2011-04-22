#!/usr/bin/env python2

# Copyright 2008, Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#  3. Neither the name of Google Inc. nor the names of its contributors may be
#     used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This program demonstrates use of the KML DOM Python SWIG bindings for
# creating and accessing simple elements and attributes such as
# Feature's <name> and <visibility> and Object's id= as in <Placemark>.

# Modified: 2011 by Mike Atkins
# Note: depends on libkml, matplotlib and simplejson

import kmldom
import kmlengine
import urllib
import simplejson
from matplotlib import pyplot as pyplt

ELEVATION_BASE_URL = 'http://maps.googleapis.com/maps/api/elevation/json'

# Program main: Parse a simple Point Placemark and print the coordinates.
def main():
  
    kmlfile = open('kml/route.kml')
    kml = kmlfile.read()
  
  
    # Use the convenience function to return the root feature of the parsed KML.
    root_feature = kmlengine.GetRootFeature(kmldom.ParseKml(kml))
  
    # We know the root feature is a Document which contains only Placemarks.
    document = kmldom.AsDocument(root_feature)
    numPlacemarks =  document.get_feature_array_size()
    coordinates = []
    for i in range(numPlacemarks):
        placemark = kmldom.AsPlacemark(document.get_feature_array_at(i))
        geometry  = placemark.get_geometry()
        
        # Assume that the first and last Placemarks are start/end and only
        # contain a single point.
        if i == 0 or i+1 == numPlacemarks:
            coordsDom = kmldom.AsPoint(geometry).get_coordinates()
        else:
            coordsDom = kmldom.AsLineString(geometry).get_coordinates()
        numCoords = coordsDom.get_coordinates_array_size()
       
        # Put all the coordinates in a list
        for j in range(numCoords):
            coordDom = coordsDom.get_coordinates_array_at(j)
            coordinates.append((coordDom.get_latitude(),
                                coordDom.get_longitude()
                                ))

    # Get the coordinates in the format that the Elevation API wants
    coordinatesString = [coordToString(coord) for coord in coordinates]
    coordinatesString = reduce(coordJoinFunc, coordinatesString)

    elevations = getElevation(coordinatesString, 250)
    # Convert to feet since we're North Americans
    elevations = [elevation * 3.2808399 for elevation in elevations]
    pyplt.plot(elevations)
    pyplt.xticks([])
    pyplt.ylabel('Elevation in Feet')
    pyplt.savefig('images/eleprof/usa.png')


def getElevation(path,
                 samples="100",
                 sensor="false",
                 **elvtn_args):

    elvtn_args.update({'path': path,
                       'samples': samples,
                       'sensor': sensor
                       })
    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
    response = simplejson.load(urllib.urlopen(url))

    elevations = [resultdict['elevation'] for resultdict in
        response['results']]
    return elevations

  
def coordToString(coord):
    return '%0.5f,%0.5f' % coord

def coordJoinFunc(coord1,
                  coord2):
    return coord1 + '|' + coord2

if __name__ == '__main__':
  main()
