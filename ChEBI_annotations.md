The full `chebi.owl` has includes the following annotations
- `rdfs:label` (one per class)
- `oboInOwl:hasExactSynonym` (possibly many)
- `oboInOwl:hasRelatedSynonym` (possibly many)
- `owl:deprecated`
- `obo:IAO_0000231`
    - 'has obsolescence reason'... always takes `obo:IAO_0000227` as it's object
- `obo:IAO_0100001`
     - 'term replaced by'.... possibly many

The synonyms always have a supporting axiom

oboInOwl:hasSynonymType
chebi2:IUPAC_NAME
chebi2:BRAND_NAME
chebi2:INN



## ChEBI Ontology Files

All use base address `ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/`

| Name                | Size      | Last Modified |             |
|---------------------|-----------|---------------|-------------|
| chebi.owl           | 487984 KB | 10/1/2019     | 10:17:00 PM |
| chebi_core.owl      | 223883 KB | 10/1/2019     | 10:17:00 PM |
| chebi_lite.owl      | 138622 KB | 10/1/2019     | 10:17:00 PM |
| chebi.obo           | 130865 KB | 10/1/2019     | 10:17:00 PM |
| chebi_core.obo      | 105534 KB | 10/1/2019     | 10:17:00 PM |
| chebi.owl.gz        | 31071 KB  | 10/1/2019     | 10:17:00 PM |
| chebi_lite.obo      | 28983 KB  | 10/1/2019     | 10:17:00 PM |
| chebi_core.owl.gz   | 19672 KB  | 10/1/2019     | 10:16:00 PM |
| chebi.obo.gz        | 18327 KB  | 10/1/2019     | 10:17:00 PM |
| chebi_core.obo.gz   | 13965 KB  | 10/1/2019     | 10:16:00 PM |
| chebi_lite.owl.gz   | 7229 KB   | 10/1/2019     | 10:16:00 PM |
| chebi_lite.obo.gz   | 3702 KB   | 10/1/2019     | 10:17:00 PM |
| fix.obo             | 182 KB    | 2/6/2014      | 12:00:00 AM |
| rex.obo             | 131 KB    | 2/6/2014      | 12:00:00 AM |
| chebi-proteins.owl  | 81 KB     | 10/8/2012     | 12:00:00 AM |
| chebi-disjoints.owl | 61 KB     | 2/16/2017     | 12:00:00 AM |
| chebi-in-bfo.owl    | 4 KB      | 10/1/2019     | 10:16:00 PM |
| nightly             |           | 9/29/2019     | 8:13:00 PM  |

## Search for synonym annotations lacking suporting axioms

```
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
ask 
where {
    values ?eVsR {
        oboInOwl:hasExactSynonym
        oboInOwl:hasRelatedSynonym
    }
    ?s ?eVsR ?o .
    minus {
        {
            ?a rdf:type owl:Axiom ;
               owl:annotatedSource ?s ;
               owl:annotatedProperty ?eVsR ;
               owl:annotatedTarget ?o ;
               oboInOwl:hasDbXref ?dbxr .
        } union {
            ?a rdf:type owl:Axiom ;
               owl:annotatedSource ?s ;
               owl:annotatedProperty ?eVsR ;
               owl:annotatedTarget ?o ;
               oboInOwl:hasSynonymType ?st .
        }
    } 
}
```
