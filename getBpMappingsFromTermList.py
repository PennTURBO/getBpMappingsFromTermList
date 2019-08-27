from __future__ import print_function
import os
import urllib.request, urllib.error, urllib.parse
import json
import sys

# usage:
# python3 getBpMappingsFromTermList.py ChEBI_to_DrOn_BpMappingsFromTermList_config

# somewhat recklessly allows the user to specify a configuration file as a package
# modify ChEBI_to_DrOn_BpMappingsFromTermList_config.py.template as needed
# save with the .py extension
# but omit the .py extension when invoking

cfgArg = sys.argv[1]
cfg = __import__(cfgArg)

# see http://data.bioontology.org/documentation#Mapping
# presumably, all of the mappings will be the results of LOOM mapping
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2815474/

# there's nothing in place here to determine if the terms in the source term file are present in the source ontology
# or even that the source ontology abbreviation is legal, that the source terms are legal...
# having the input sorted makes it easier to pick back up after a network error

REST_URL = "http://data.bioontology.org"
PAGE_SIZE = 500

def getJson(headerlessUrl):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + cfg.API_KEY)]
    return json.loads(opener.open(headerlessUrl).read().decode('utf-8'))

f = open(cfg.outputFile, "w")

with open(cfg.sourceTermListFile) as fileHandle:
   next(fileHandle)
   inputLine = fileHandle.readline()
   while inputLine:
       strippedLine = inputLine.rstrip('\n')
       print(strippedLine, file=sys.stderr)
       encodedLine = urllib.parse.quote_plus(strippedLine)
       builtUrl = REST_URL+"/ontologies/" + cfg.sourceOntoAbbr + "/classes/"+ encodedLine + "/mappings?pagesize=" + str(PAGE_SIZE )
       returnedPage = getJson(builtUrl)
       for something in returnedPage:
           mapMeth = something['source']
           if mapMeth != 'SAME_URI':
               sourceStruct = something['classes'][0]
               mapStruct = something['classes'][1]
               sourceOnt = sourceStruct['links']['ontology']
               mappedOnt = mapStruct['links']['ontology']
               sourceId = sourceStruct['@id']
               mappedId = mapStruct['@id']
               # bioportal's loom method can also result in what appears to be a same-uri match
               #   we just plain don't want to save same-uri mappings!
               if sourceId != mappedId:
                   if ((mappedOnt in cfg.destOntoUriList) or (not cfg.constrainDestOnto)):
                       mapRes = "\t".join([sourceOnt, sourceId, mapMeth, mappedOnt, mappedId])
                       print(mapRes, file=sys.stderr)
                       f.write(mapRes)
                       f.write("\n")
       inputLine = fileHandle.readline()
f.close()
