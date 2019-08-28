API_KEY = "9cf735c3-a44a-404f-8b2f-c49d48b2b8b2"
sourceOntoAbbr = "CHEBI"

sourceTermListFile = "pickBackUp_termList.tsv"
# just a plain list of source terms
# the first line is assumed to be a header
#  and therefore not processed

# there's nothing in place to determine if the terms in the source term file are present in the source ontology
# or even that the source ontology abbreviation is legal, that the source terms are legal...
# having the input sorted makes it easier to pick back up after a network error

# example:

#?sStr
#http://purl.obolibrary.org/obo/CHEBI_1
#http://purl.obolibrary.org/obo/CHEBI_10
#http://purl.obolibrary.org/obo/CHEBI_100
#http://purl.obolibrary.org/obo/CHEBI_100000

# for the task of checking if there are existing CHEBI terms
# that could retire DrOn classes (like rosuvastatin)
# build the sourceTermListFile like this:
#
# load ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl.gz into a triplestore
#
# then
#
#PREFIX owl: <http://www.w3.org/2002/07/owl#>
#select distinct ?s where {
#       ?s a owl:Class .
#}
#order by ?s

constrainDestOnto = True

destOntoUriList = ["http://data.bioontology.org/ontologies/DRON"]

outputFile = "pickBackUp.out.tsv"
