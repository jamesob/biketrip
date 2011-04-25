#!/usr/bin/env python2

"""load up post via file.open

readlines it

iterate through the readlines until a line is found which starts with %%% or
something

eval the line after removing the %%% while making a note of the index we are
at in the readlines, call this index i

pray that the line contains a dictionary of useful stuff like
    date
    mapUrl(kml)
    CSSTags like sizes?

download the kml and do a .read() on it

parse the kml

generate elevation profile & map (save based on date)

generate the html to present these two images

replace the readlines[i] with this generated html code

write the preprocessed file

EXTRA write a script which will call the preprocessor, figureout from the
preprocessor which files need to be staged, stage them, commit them and push
them.
"""

import sys
import urllib
from routeParser import getElevations, saveElevation, parseKML

def main():
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
    return '<div id="regularMap"/>\n' +\
           '<script type="text/javascript">\n' +\
           '   initializeMap("regularEle");\n' +\
           '   loadKML("%s");\n' % kwargs['mapLoc'] +\
           '</script>' +\
           '<img id="regularEle" class="elevation" src="/%s"/>\n' %\
               kwargs['elefilename']

def parseLine(line):
    line = line[3:]
    argsDict = eval(line)
    kml = getKML(argsDict['mapLoc'])
    paths = parseKML(kml)
    argsDict.update({'paths': paths})
    return argsDict

def getKML(url):
    kmlfile = urllib.urlopen(url)
    kml = kmlfile.read()
    return kml

if __name__ == '__main__':
    main()

