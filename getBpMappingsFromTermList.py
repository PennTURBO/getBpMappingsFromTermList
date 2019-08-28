from __future__ import print_function
import os
import urllib.request, urllib.error, urllib.parse
import json
import sys

# see performance notes at end of source code

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
	try:
      temp1 = opener.open(headerlessUrl)
	except KeyboardInterrupt:
      temp2 = temp1.read()
      temp3 = temp2.decode('utf-8')
      temp4 = json.loads(temp3)
      #print(temp4)
      return temp4
	except:
      return
    # return json.loads(opener.open(headerlessUrl).read().decode('utf-8'))

f = open(cfg.outputFile, "w", buffering = 1)

with open(cfg.sourceTermListFile) as fileHandle:
   next(fileHandle)
   inputLine = fileHandle.readline()
   while inputLine:
       strippedLine = inputLine.rstrip('\n')
       print(strippedLine, file=sys.stderr)
       encodedLine = urllib.parse.quote_plus(strippedLine)
       builtUrl = REST_URL+"/ontologies/" + cfg.sourceOntoAbbr + "/classes/"+ encodedLine + "/mappings?pagesize=" + str(PAGE_SIZE )
       returnedPage = getJson(builtUrl)
	   if returnedPage is None:
	     print("no result")
       else:
         for something in returnedPage:
             mapMeth = something['source']
             if mapMeth != 'SAME_URI':
                 sourceStruct = something['classes'][0]
                 mapStruct = something['classes'][1]
                 sourceOnt = sourceStruct['links']['ontology']
                 mappedOnt = mapStruct['links']['ontology']
                 sourceId = sourceStruct['@id']
                 mappedId = mapStruct['@id']
#               f.write(sourceId)
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

# ran from roughly Aug 27 16:00 UTC to Aug 27 21:33 UTC
# got from CHEBI_1 to CHEBI_4074
# so set last visited to previously successful http://purl.obolibrary.org/obo/CHEBI_40585

# add error handling... https://stackoverflow.com/questions/9446387/how-to-retry-urllib2-request-when-fails ?

# this went faster overall when, instead of /ontologies/:ontology/classes/:cls/mappings,
#  I used the /ontologies/:ontology/mappings method 
#  which takes a source ontology as input but doesn't require a list of terms
# but I found that harder to parse and harder for recovering from interrupted runs

# http://purl.obolibrary.org/obo/CHEBI_4074
# Traceback (most recent call last):
  # File "getBpMappingsFromTermList.py", line 44, in <module>
    # returnedPage = getJson(builtUrl)
  # File "getBpMappingsFromTermList.py", line 32, in getJson
    # return json.loads(opener.open(headerlessUrl).read().decode('utf-8'))
  # File "/usr/lib/python3.6/urllib/request.py", line 532, in open
    # response = meth(req, response)
  # File "/usr/lib/python3.6/urllib/request.py", line 642, in http_response
    # 'http', request, response, code, msg, hdrs)
  # File "/usr/lib/python3.6/urllib/request.py", line 570, in error
    # return self._call_chain(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 504, in _call_chain
    # result = func(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 650, in http_error_default
    # raise HTTPError(req.full_url, code, msg, hdrs, fp)
# urllib.error.HTTPError: HTTP Error 504: Gateway Time-out

# Also

# http://purl.obolibrary.org/obo/CHEBI_41597
# Traceback (most recent call last):
  # File "getBpMappingsFromTermList.py", line 44, in <module>
    # returnedPage = getJson(builtUrl)
  # File "getBpMappingsFromTermList.py", line 32, in getJson
    # return json.loads(opener.open(headerlessUrl).read().decode('utf-8'))
  # File "/usr/lib/python3.6/urllib/request.py", line 532, in open
    # response = meth(req, response)
  # File "/usr/lib/python3.6/urllib/request.py", line 642, in http_response
    # 'http', request, response, code, msg, hdrs)
  # File "/usr/lib/python3.6/urllib/request.py", line 570, in error
    # return self._call_chain(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 504, in _call_chain
    # result = func(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 650, in http_error_default
    # raise HTTPError(req.full_url, code, msg, hdrs, fp)
# urllib.error.HTTPError: HTTP Error 404: Not Found

# now:
# http://purl.obolibrary.org/obo/CHEBI_41597
# Traceback (most recent call last):
  # File "getBpMappingsFromTermList.py", line 52, in <module>
    # returnedPage = getJson(builtUrl)
  # File "getBpMappingsFromTermList.py", line 34, in getJson
    # temp1 = opener.open(headerlessUrl)
  # File "/usr/lib/python3.6/urllib/request.py", line 532, in open
    # response = meth(req, response)
  # File "/usr/lib/python3.6/urllib/request.py", line 642, in http_response
    # 'http', request, response, code, msg, hdrs)
  # File "/usr/lib/python3.6/urllib/request.py", line 570, in error
    # return self._call_chain(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 504, in _call_chain
    # result = func(*args)
  # File "/usr/lib/python3.6/urllib/request.py", line 650, in http_error_default
    # raise HTTPError(req.full_url, code, msg, hdrs, fp)
# urllib.error.HTTPError: HTTP Error 404: Not Found

