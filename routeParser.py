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
import string
from matplotlib import pyplot as pyplt

ELEVATION_BASE_URL = 'http://maps.googleapis.com/maps/api/elevation/json'
STATICMAP_BASE_URL = 'http://maps.google.com/maps/api/staticmap'

# Program main: Parse a simple Point Placemark and print the coordinates.
def main():
  
    size = (650,400)
    kmlfile = open('kml/test.kml')
    kml = kmlfile.read()

    paths = parseKML(kml)

    elevations = []
    for path in paths:
        elevations += getElevation(path, samples=250)
    saveElevation('test.png',elevations, size)

def parseKML(kml):
    """Here kml is a filestream prehaps generated by .read(). This function
    Assumes that The KML contains a Document which contains only Points and
    LineStrings. If there is at least one LineString, the points contained in
    these LineStrings will be parsed and returned as one long string which is 
    readable by the Google Maps and Elevation APIs.
    
    If Parsing fails, an attribute error should be thrown."""

    # Use the convenience function to return the root feature of the parsed KML.
    root_feature = kmlengine.GetRootFeature(kmldom.ParseKml(kml))
  
    # We know the root feature is a Document which contains only Placemarks.
    document = kmldom.AsDocument(root_feature)
    numPlacemarks =  document.get_feature_array_size()
    coordinates = [[]]
    coordCounter = 0
    for i in range(numPlacemarks):
        placemark = kmldom.AsPlacemark(document.get_feature_array_at(i))
        geometry  = placemark.get_geometry()
        
        # Assume that the document contains only Points and LineStrings
        try:
            coordsDom = kmldom.AsLineString(geometry).get_coordinates()
            numCoords = coordsDom.get_coordinates_array_size()
        except AttributeError: 
            coordsDom = kmldom.AsPoint(geometry).get_coordinates()
            numCoords = coordsDom.get_coordinates_array_size()

        # Put all the coordinates in a list
        for j in range(numCoords):
            coordDom = coordsDom.get_coordinates_array_at(j)
            coordinates[-1].append((coordDom.get_latitude(),
                                coordDom.get_longitude()
                                ))
            coordCounter += 1
            # URLs can only be 2048 characters which works out to ~100
            # coordinates
            if coordCounter % 50 == 0:
                coordinates.append([])

    if coordCounter >= 25000:
        raise Exception('Too many coordinates for Elevation API.')

    paths = []
    for coords in coordinates:
    # Get the coordinates in the format that the Google APIs want
        coordinatesString = [coordToString(coord) for coord in coords]
        coordinatesString = string.join(coordinatesString, '|')
        paths.append(coordinatesString)

    return paths

def getElevation(path,
                 samples="100",
                 sensor="false",
                 **elvtn_args):
    """Uses the Google Elevation API to return an array of elevations. This 
    array will be as long as specified in samples."""

    elvtn_args.update({'path': path,
                       'samples': samples,
                       'sensor': sensor
                       })
    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
    response = simplejson.load(urllib.urlopen(url))

    elevations = [resultdict['elevation'] for resultdict in
        response['results']]
    return elevations

def saveElevation(filename,
                  elevations,
                  size):
    """Uses matplotlib to generate an elevation profile of the given 
    elevations array with image size size which is saved in the file 
    filename.
    
    Note: size should be in the format (X,Y)."""

    # Convert to feet since we're North Americans
    elevations = [elevation * 3.2808399 for elevation in elevations]
    pyplt.plot(elevations)
    pyplt.xticks([])
    pyplt.ylabel('Elevation in Feet')
    size = (size[0]/100., size[1]/100.)
    fig = pyplt.gcf()
    fig.set_size_inches(size[0],size[1])
    pyplt.savefig(filename, dpi=100)

def saveStaticMap(filename,
                 path,
                 size,
                 sensor="false",
                 maptype='terrain',
                 **maps_args):
    """A map is generated via the Google Static Map API. It will then be saved
    in the specified filename.
    
    Note: size should be in the format (X,Y)."""
    size = "%dx%d" % size

    maps_args.update({'path': path,
                      'size': size,
                      'sensor': sensor,
                      'maptype': maptype
                      })
    url = STATICMAP_BASE_URL + '?' + urllib.urlencode(maps_args)
    urllib.urlretrieve(url,filename)
  
def coordToString(coord):
    return '%0.5f,%0.5f' % coord

if __name__ == '__main__':
  main()
