#!/usr/bin/env python2

import sys
import urllib
from routeParser import getElevations, saveElevation, parseKML
import string
import markdown

def main():
    """Read the file whose name is specified as a command-line argument. Parse
    it, substitute text which has a '%%%' flag at the beginning of a line.
    Also, it will apply markdown to the rest of the input document as well as
    adding a header for jekyll to read.  Write the preprocessed file to the 
    _posts directory with the filename taken from the title and date keys of 
    the parsed dictionary."""

    if len(sys.argv) != 2 or len(sys.argv) != 3:
        print("Usage: preProcessor filename [-v]")
        sys.exit(1)

    verbose = False
    if sys.argv[2] == '-v':
        verbose = True
    
    filename = sys.argv[1]
    try:
        infile = open(filename, 'r')
        lines = infile.readlines()
        infile.close()
    except:
        print("Could not open file: %s" % filename)
        sys.exit(1)
    
    parselines = [line for line in lines if line[:3] == '%%%']
    assert len(parselines) == 1
    line = parselines[0]

    if verbose:
        print("Parsing line.")
    argsDict = parseLine(line)

    elefilename = "images/eleprof/"+ argsDict['date'] + ".png"
    argsDict.update({'elefilename': elefilename})

    paths = argsDict['paths']
    size  = argsDict['size']

    if verbose:
        print("Generating elevation profile.")
    elevations = getElevations(paths, samples=250)

    if verbose:
        print("Saving elevation profile.")
    saveElevation(elefilename, elevations, size)

    if verbose:
        print("Generating HTML")
    html = makeHTML(**argsDict)
    index = lines.index(line)

    # Get the text other than the preprocessed line
    beforePPD = string.join(lines[:index], '')
    afterPPD = string.join(lines[index:], '')

    if verbose:
        print("Applying Markdown.")
    beforePPD = markdown.markdown(beforePPD)
    afterPPD = markdown.markdown(afterPPD)

    if verbose:
        print("Generating header for jekyll.")
    header = makeHeader(**argsDict)
    
    outString = header + \
                beforePPD + \
                html + \
                afterPPD
        
    outFileName = "_posts/%s-%s.html" % \
                   (argsDict['date'],argsDict['title'])
    outFileName = outFileName.replace(' ','')

    if verbose:
        print("Writing output file.")
    outfile = open(outFileName, 
                   'w')
    outfile.write(outString)
    outfile.close()

def makeHeader(**kwargs):
    """Make the header which jekyll will read to generate the page."""
    return '---\n' +\
           'layout: log\n' +\
           'title: %s\n' % kwargs['title'] +\
           'category: daily\n' +\
           '---\n'

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

    # There are a few things which need to be specified.
    if not argsDict.has_key('size'):
        print("size specification is manditiory")
        sys.exit(1)
    if not argsDict.has_key('date'):
        print("date specification is manditiory")
        sys.exit(1)
    if not argsDict.has_key('title'):
        print("title specification is manditiory")
        sys.exit(1)
    if not argsDict.has_key('mapLoc'):
        print("mapLoc specification is manditiory")
        sys.exit(1)

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

