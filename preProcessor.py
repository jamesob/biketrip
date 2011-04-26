#!/usr/bin/env python2

import sys
import urllib
from routeParser import getElevations, saveElevation, parseKML

def main():
    """Read the file whose name is specified as a command-line argument. Parse
    it, substitute text which has a '%%%' flag at the beginning of a line.
    Write the preprocessed file to a hardcoded position."""

    filename = sys.argv[1]
    try:
        infile = open(filename, 'r')
        lines = infile.readlines()
    except:
        print("Could not open file: %s" % filename)

    parselines = [line for line in lines if line[:3] == '%%%']
    for line in parselines:
        argsDict = parseLine(line)
        if not argsDict.has_key('size'):
            print("size specification is manditiory")
            sys.exit(1)
        if not argsDict.has_key('date'):
            print("date specification is manditiory")
            sys.exit(1)
        if not argsDict.has_key('title'):
            print("title specification is manditiory")
            sys.exit(1)

        elefilename = "images/eleprof/"+ argsDict['date'] + ".png"
        argsDict.update({'elefilename': elefilename})

        paths = argsDict['paths']
        size  = argsDict['size']

        elevations = getElevations(paths, samples=250)
        saveElevation(elefilename, elevations, size)

        html = makeHTML(**argsDict)
        index = lines.index(line)
        lines[index] = html

    outfile = open("_posts/%s-%s.html" % \
                   (argsDict['date'],argsDict['title']), 
                   'w')
    outfile.writelines(lines)


def makeHTML(**kwargs):
    """Make the html which corresponds to the dictionary. This is hardcoded to
    use our pre decided divs."""

    return '<div id="regularMap"/>\n' +\
           '<script type="text/javascript">\n' +\
           '   initializeMap("regularMap");\n' +\
           '   loadKML("%s");\n' % kwargs['mapLoc'] +\
           '</script>' +\
           '<img id="regularEle" class="elevation" src="/%s"/>\n' %\
               kwargs['elefilename']

def parseLine(line):
    """Parse the line by removing the first three characters, evaling the line,
    which hopefully will eval to a dictionary, getting the kml from the from
    the url, parsing that into paths and loading that into the returned
    dictionary."""

    line = line[3:]
    argsDict = eval(line)
    kml = getKML(argsDict['mapLoc'])
    paths = parseKML(kml)
    argsDict.update({'paths': paths})
    return argsDict

def getKML(url):
    """Open the url and get return a string which hopefully contains some
    KML."""
    
    kmlfile = urllib.urlopen(url)
    kml = kmlfile.read()
    return kml

if __name__ == '__main__':
    main()
