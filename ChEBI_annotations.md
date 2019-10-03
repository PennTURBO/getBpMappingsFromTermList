Previously, the BioPortal API was used to retrieve mappings between ChEBI terms and DrOn terms. The mapping file only contained the term IDs/URIs. This current document addresses adding the labels, from both sources, to the mapping to aid in quality control. Adding this capability to script XXX was considered, but the current implementation uses raw SPARQL queries ti clarify some filtering opportunities.

FOr example, rosuvastatin is modelled with differnt terms in the two ontologies: CHEBI:38545 and obo:DRON_00018679. When DrOn asserts that Crestor tablets obo:DRON_00018679 as an active ingredient, it breaks the potential link to ChEBI's 'anticholesteremic drug'.

For ChEBI, let's only consider terms that are rdfs:subClassOf* obo:CHEBI_24431 (chemical entity). That is, don't examine the labels of roles, etc. for the purpose of aligning with DrOn.

Could we possibly constrain even more? Molecular entity and chemical substance?

- CHEBI:24431 chemical entity
    - CHEBI:59999 chemical substance
    - CHEBI:23367 molecular entity
    - CHEBI:24433 group
    - CHEBI:33250 atom

For DrOn, let's only consider terms that are the granular part of an active ingredient.

Both of those rules may be mostly irrelevant, if the label matrices are going to be merged with the BioPortal mappings, and if BioPortal only maps ingredients. (DrOn doesn't model roles? and ChEBI doesn't model products?)

    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix ibo: <http://purl.obolibrary.org/obo/BFO_0000053>
    prefix hgp: <http://purl.obolibrary.org/obo/BFO_0000071>
    prefix actIng: <http://purl.obolibrary.org/obo/DRON_00000028>
    select 
    distinct 
    ?ingredient ?ingLab
    where {
        ?s_4 rdf:first ?s_4_b ;
             rdf:rest ?s_5 .
        ?s_4_b rdf:type owl:Restriction ;
               owl:onProperty ibo: ;
               owl:someValuesFrom actIng: .
        ?s_5 rdf:first ?s_6 ;
             rdf:rest ?s_7 .
        ?s_7 rdf:rest rdf:nil;
             rdf:first ?s_8 .
        ?s_8 rdf:type owl:Restriction ;
             owl:onProperty hgp: ;
             owl:someValuesFrom ?ingredient .
        graph <http://purl.obolibrary.org/obo/dron/dron-ingredient.owl> {
            ?ingredient rdfs:label ?ingLab   
        }
        minus {
            graph <http://purl.obolibrary.org/obo/dron/dron-chebi.owl> {
                ?ingredient rdfs:label ?chebiLab   
            }  
        }
    }
    
The following query retrieves all ChEBI labels, exact synonyms, related synonyms, as well as the deprecation flag. We could further condense by lowercasing. I don't think it can be filtered by language, but the non-English labels might be enriched for one of the synonym authorities. The distinct group_concat query wouldn't run for me on a 16 GB server, but it did run in < 1 minute on a 128 GB server.

```
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
select ?s ?l ?deprecated
(group_concat( ?es;
        separator="|") as ?eses) 
(group_concat( ?rs;
        separator="|") as ?rses) 
where {
    ?s rdfs:subClassOf* obo:CHEBI_24431 ;
                      rdfs:label ?l .
    optional {
        ?s oboInOwl:hasExactSynonym ?es .
    }
    optional {
        ?s oboInOwl:hasRelatedSynonym ?rs .
    }
    optional {
        ?s owl:deprecated  ?deprecated .
    }
}
group by ?s ?l ?deprecated
```

The full `chebi.owl` has includes the following annotations
- `rdfs:label` (one per class)
- `oboInOwl:hasExactSynonym` (possibly many)
- `oboInOwl:hasRelatedSynonym` (possibly many, even as many as 50)
- `owl:deprecated`
- `obo:IAO_0000231`
    - 'has obsolescence reason'... always takes `obo:IAO_0000227` as it's object
- `obo:IAO_0100001`
     - 'term replaced by' (possibly many)

For every synonym assertion, there will be a supporting axiom. The axioms can assert a synonym type or a database cross reference. The data base cross references are sources or authorities (like "KEGG"), not the identifying values used by those third party authorities (like "D00217").

There are 46,351 IUPAC `ExactSynonym`s, which presumably would never match a DrOn `rdfs:label`. 

It would probably be best to leave out the `chebi:BRAND_NAME` synonyms, too. While DrOn doesn't have terms for brands in the absence of a dose form (like "Tylenol"), ChEBI does assert that "Tylenol" is a `KEGG DRUG` synonym for `CHEBI:46195` ("paracetamol"). `KEGG COMPOUND` is the source of the "Acetaminophen" synonym that is asserted as the rdfs:label of `obo:CHEBI_46195` in `dron-ingredient.owl`. ("paracetamol" is asserted as the label in `dron-chebi.owl`)


Because ChEBI classes can have many related synonyms, and because some of the sources may not be very useful for mapping to DrOn, some triage might be beneficial.


| ?eVsR                                                            | ?st                                               | ?dbxr                  | ?count |
|------------------------------------------------------------------|---------------------------------------------------|------------------------|--------|
| oboInOwl:hasRelatedSynonym |                                                   | ChEBI                  | 67720  |
| oboInOwl:hasExactSynonym   | chebi:IUPAC_NAME |                        | 46351  |
| oboInOwl:hasExactSynonym   |                                                   | IUPAC                  | 44880  |
| oboInOwl:hasRelatedSynonym |                                                   | ChemIDplus             | 29163  |
| oboInOwl:hasRelatedSynonym |                                                   | HMDB                   | 23174  |
| oboInOwl:hasRelatedSynonym |                                                   | KEGG_COMPOUND          | 11494  |
| oboInOwl:hasRelatedSynonym |                                                   | SUBMITTER              | 11442  |
| oboInOwl:hasRelatedSynonym |                                                   | UniProt                | 9248   |
| oboInOwl:hasExactSynonym   |                                                   | KEGG_COMPOUND          | 8515   |
| oboInOwl:hasRelatedSynonym |                                                   | IUPAC                  | 7498   |
| oboInOwl:hasRelatedSynonym |                                                   | DrugCentral            | 6359   |
| oboInOwl:hasRelatedSynonym |                                                   | NIST_Chemistry_WebBook | 5677   |
| oboInOwl:hasRelatedSynonym | chebi:INN        |                        | 4943   |
| oboInOwl:hasExactSynonym   |                                                   | UniProt                | 3332   |
| oboInOwl:hasRelatedSynonym |                                                   | LIPID_MAPS             | 2678   |
| oboInOwl:hasRelatedSynonym | chebi:BRAND_NAME |                        | 2500   |
| oboInOwl:hasExactSynonym   |                                                   | HMDB                   | 1727   |
| oboInOwl:hasRelatedSynonym |                                                   | DrugBank               | 1448   |
| oboInOwl:hasExactSynonym   |                                                   | ChEBI                  | 1435   |
| oboInOwl:hasRelatedSynonym |                                                   | WHO_MedNet             | 1279   |
| oboInOwl:hasRelatedSynonym |                                                   | PDBeChem               | 1225   |
| oboInOwl:hasRelatedSynonym |                                                   | KEGG_DRUG              | 1205   |
| oboInOwl:hasRelatedSynonym |                                                   | JCBN                   | 1013   |
| oboInOwl:hasRelatedSynonym |                                                   | MetaCyc                | 890    |
| oboInOwl:hasExactSynonym   |                                                   | ChemIDplus             | 666    |
| oboInOwl:hasRelatedSynonym |                                                   | Alan_Wood's_Pesticides | 519    |
| oboInOwl:hasRelatedSynonym |                                                   | KEGG_GLYCAN            | 420    |
| oboInOwl:hasExactSynonym   |                                                   | PDBeChem               | 420    |
| oboInOwl:hasRelatedSynonym |                                                   | ChEMBL                 | 360    |
| oboInOwl:hasRelatedSynonym |                                                   | MolBase                | 261    |
| oboInOwl:hasRelatedSynonym |                                                   | UM-BBD                 | 251    |
| oboInOwl:hasExactSynonym   |                                                   | JCBN                   | 214    |
| oboInOwl:hasRelatedSynonym |                                                   | CBN                    | 213    |
| oboInOwl:hasRelatedSynonym |                                                   | KNApSAcK               | 187    |
| oboInOwl:hasExactSynonym   |                                                   | SUBMITTER              | 166    |
| oboInOwl:hasRelatedSynonym |                                                   | SMID                   | 157    |
| oboInOwl:hasRelatedSynonym |                                                   | IUBMB                  | 143    |
| oboInOwl:hasRelatedSynonym |                                                   | Patent                 | 120    |
| oboInOwl:hasExactSynonym   |                                                   | NIST_Chemistry_WebBook | 111    |
| oboInOwl:hasExactSynonym   |                                                   | ChEMBL                 | 96     |
| oboInOwl:hasExactSynonym   |                                                   | KEGG_DRUG              | 65     |
| oboInOwl:hasRelatedSynonym |                                                   | IUPHAR                 | 61     |
| oboInOwl:hasRelatedSynonym |                                                   | RESID                  | 61     |
| oboInOwl:hasExactSynonym   |                                                   | DrugCentral            | 55     |
| oboInOwl:hasExactSynonym   |                                                   | CBN                    | 39     |
| oboInOwl:hasRelatedSynonym |                                                   | COMe                   | 33     |
| oboInOwl:hasRelatedSynonym |                                                   | LINCS                  | 32     |
| oboInOwl:hasRelatedSynonym |                                                   | PDB                    | 28     |
| oboInOwl:hasExactSynonym   |                                                   | LIPID_MAPS             | 26     |
| oboInOwl:hasRelatedSynonym |                                                   | EMBL                   | 23     |
| oboInOwl:hasExactSynonym   |                                                   | IUBMB                  | 20     |
| oboInOwl:hasExactSynonym   |                                                   | UM-BBD                 | 19     |
| oboInOwl:hasExactSynonym   |                                                   | COMe                   | 10     |
| oboInOwl:hasExactSynonym   |                                                   | KNApSAcK               | 10     |
| oboInOwl:hasRelatedSynonym |                                                   | PPDB                   | 10     |
| oboInOwl:hasExactSynonym   |                                                   | IUPHAR                 | 9      |
| oboInOwl:hasRelatedSynonym |                                                   | EuroFIR                | 4      |
| oboInOwl:hasExactSynonym   |                                                   | MetaCyc                | 4      |
| oboInOwl:hasExactSynonym   |                                                   | WHO_MedNet             | 4      |
| oboInOwl:hasExactSynonym   |                                                   | DrugBank               | 3      |
| oboInOwl:hasExactSynonym   |                                                   | KEGG_GLYCAN            | 3      |
| oboInOwl:hasExactSynonym   |                                                   | Alan_Wood's_Pesticides | 2      |
| oboInOwl:hasRelatedSynonym |                                                   | FooDB                  | 2      |
| oboInOwl:hasRelatedSynonym |                                                   | GlyTouCan              | 2      |
| oboInOwl:hasExactSynonym   |                                                   | LINCS                  | 2      |
| oboInOwl:hasExactSynonym   |                                                   | PDB                    | 2      |
| oboInOwl:hasExactSynonym   |                                                   | Beilstein              | 1      |
| oboInOwl:hasRelatedSynonym |                                                   | Beilstein              | 1      |
| oboInOwl:hasRelatedSynonym |                                                   | EBI_Industry_Programme | 1      |
| oboInOwl:hasExactSynonym   |                                                   | MolBase                | 1      |
| oboInOwl:hasExactSynonym   |                                                   | Patent                 | 1      |
| oboInOwl:hasRelatedSynonym |                                                   | PubChem                | 1      |
| oboInOwl:hasRelatedSynonym |                                                   | VSDB                   | 1      |


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

## Search for synonym annotations lacking supporting axioms

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

## Creating complete tabulation of axiom sources

```
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX chebi2: <http://purl.obolibrary.org/obo/chebi#>
PREFIX : <http://purl.obolibrary.org/obo/chebi.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
select 
#?s ?eVsR ?o ?dbxr ?st
?eVsR ?st ?dbxr (count(?a) as ?count)
where {
    values ?eVsR {
        oboInOwl:hasExactSynonym
        oboInOwl:hasRelatedSynonym
    }
    ?s rdfs:subClassOf* obo:CHEBI_24431 ;
                      ?eVsR ?o .
    {
        {
            ?a rdf:type owl:Axiom ;
               owl:annotatedSource ?s ;
               owl:annotatedProperty ?eVsR ;
               owl:annotatedTarget ?o ;
               oboInOwl:hasDbXref ?dbxr .
            #            filter (?dbxr != "IUPAC")
        } 
        union  {
            ?a rdf:type owl:Axiom ;
               owl:annotatedSource ?s ;
               owl:annotatedProperty ?eVsR ;
               owl:annotatedTarget ?o ;
               oboInOwl:hasSynonymType ?st .
            #            filter (?st != 	chebi2:IUPAC_NAME)
        }
    }
}
group by ?eVsR ?st ?dbxr
order by desc (count(?a))
```


## Finding examples of synonyms from a specified authority

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX chebi: <http://purl.obolibrary.org/obo/chebi/>
PREFIX chebi2: <http://purl.obolibrary.org/obo/chebi#>
select ?authPred ?s ?eVsR ?o where {
    values ?authPred {
        oboInOwl:hasDbXref
        oboInOwl:hasSynonymType
    }
    ?a rdf:type owl:Axiom ;
       owl:annotatedSource ?s ;
       owl:annotatedProperty ?eVsR ;
       owl:annotatedTarget ?o ;
       ?authPred "UniProt" .
} limit 100
```

## Complete DrOn active ingredient + dose query

    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX hsv: <http://purl.obolibrary.org/obo/OBI_0001937>
    PREFIX hmul: <http://purl.obolibrary.org/obo/IAO_0000039>
    PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix sma: <http://purl.obolibrary.org/obo/OBI_0000576>
    prefix ibo: <http://purl.obolibrary.org/obo/BFO_0000053>
    prefix hgp: <http://purl.obolibrary.org/obo/BFO_0000071>
    prefix actIng: <http://purl.obolibrary.org/obo/DRON_00000028>
    select ?drug ?drugLab ?dosage 
    #?measurementUnitLabel  
    ?mmulLab 
    ?ingredient ?ingLab
    where {
        ?drug rdfs:subClassOf ?s_1 ;
              rdfs:label ?drugLab .
        ?s_1 rdf:type owl:Restriction ;
             owl:someValuesFrom ?s_2 ;
             owl:onProperty ro:has_proper_part .
        ?s_2 owl:intersectionOf ?s_3 .
        ?s_3 rdf:first sma: ;
             rdf:rest ?s_4 .
        ?s_4 rdf:first ?s_4_b ;
             rdf:rest ?s_5 .
        ?s_4_b rdf:type owl:Restriction ;
               owl:onProperty ibo: ;
               owl:someValuesFrom actIng: .
        ?s_5 rdf:first ?s_6 ;
             rdf:rest ?s_7 .
        ?s_7 rdf:rest rdf:nil;
             rdf:first ?s_8 .
        ?s_8 rdf:type owl:Restriction ;
             owl:onProperty hgp: ;
             owl:someValuesFrom ?ingredient .
        ?s_6 rdf:type owl:Restriction ;
             owl:someValuesFrom ?s_9 ;
             owl:onProperty ibo: .
        ?s_9 owl:intersectionOf ?s_10 ;
             rdf:type owl:Class .
        ?s_10 rdf:rest ?s_11 ;
              rdf:first ?doseQual .
        ?s_11 rdf:first ?s_12 ;
              rdf:rest ?s_13 .
        ?s_13 rdf:rest rdf:nil  ;
              rdf:first ?s_14 .
        ?s_14 rdf:type owl:Restriction ;
              owl:onProperty hsv: ;
              owl:hasValue ?dosage .
        ?s_12 owl:onProperty hmul: ;
              rdf:type owl:Restriction ;
              owl:hasValue ?measurementUnitLabel .
        optional {
            ?measurementUnitLabel rdfs:label ?mmulLab
        }
        optional {
            ?ingredient rdfs:label ?ingLab
        }
    } limit 100
    
    ## DrOn terms that don't apper in the new labeled __active ingredient__ mappings
    
        > setdiff(ChEBI_to_DrOn_BpMappingsFromTermList_out$dest.term, joined$dest.term)
      [1] "http://purl.obolibrary.org/obo/DRON_00730906" "http://purl.obolibrary.org/obo/DRON_00723774"
      [3] "http://purl.obolibrary.org/obo/DRON_00723195" "http://purl.obolibrary.org/obo/DRON_00014022"
      [5] "http://purl.obolibrary.org/obo/CHEBI_32150"   "http://purl.obolibrary.org/obo/DRON_00730849"
      [7] "http://purl.obolibrary.org/obo/DRON_00017601" "http://purl.obolibrary.org/obo/DRON_00750866"
      [9] "http://purl.obolibrary.org/obo/DRON_00750867" "http://purl.obolibrary.org/obo/DRON_00756591"
     [11] "http://purl.obolibrary.org/obo/DRON_00750868" "http://purl.obolibrary.org/obo/DRON_00750875"
     [13] "http://purl.obolibrary.org/obo/DRON_00750874" "http://purl.obolibrary.org/obo/DRON_00759069"
     [15] "http://purl.obolibrary.org/obo/DRON_00723182" "http://purl.obolibrary.org/obo/CHEBI_25524"  
     [17] "http://purl.obolibrary.org/obo/DRON_00750844" "http://purl.obolibrary.org/obo/DRON_00750845"
     [19] "http://purl.obolibrary.org/obo/DRON_00723865" "http://purl.obolibrary.org/obo/DRON_00750795"
     [21] "http://purl.obolibrary.org/obo/DRON_00723192" "http://purl.obolibrary.org/obo/DRON_00723199"
     [23] "http://purl.obolibrary.org/obo/DRON_00017995" "http://purl.obolibrary.org/obo/DRON_00018254"
     [25] "http://purl.obolibrary.org/obo/DRON_00013327" "http://purl.obolibrary.org/obo/DRON_00016721"
     [27] "http://purl.obolibrary.org/obo/DRON_00014200" "http://purl.obolibrary.org/obo/DRON_00011188"
     [29] "http://purl.obolibrary.org/obo/DRON_00014312" "http://purl.obolibrary.org/obo/DRON_00015095"
     [31] "http://purl.obolibrary.org/obo/DRON_00010852" "http://purl.obolibrary.org/obo/DRON_00012431"
     [33] "http://purl.obolibrary.org/obo/DRON_00015110" "http://purl.obolibrary.org/obo/DRON_00015893"
     [35] "http://purl.obolibrary.org/obo/DRON_00014407" "http://purl.obolibrary.org/obo/DRON_00014174"
     [37] "http://purl.obolibrary.org/obo/DRON_00010760" "http://purl.obolibrary.org/obo/DRON_00013058"
     [39] "http://purl.obolibrary.org/obo/DRON_00724154" "http://purl.obolibrary.org/obo/DRON_00013144"
     [41] "http://purl.obolibrary.org/obo/DRON_00015309" "http://purl.obolibrary.org/obo/DRON_00013021"
     [43] "http://purl.obolibrary.org/obo/DRON_00013522" "http://purl.obolibrary.org/obo/DRON_00013032"
     [45] "http://purl.obolibrary.org/obo/DRON_00017061" "http://purl.obolibrary.org/obo/DRON_00015482"
     [47] "http://purl.obolibrary.org/obo/DRON_00014947" "http://purl.obolibrary.org/obo/DRON_00016420"
     [49] "http://purl.obolibrary.org/obo/DRON_00016110" "http://purl.obolibrary.org/obo/DRON_00016040"
     [51] "http://purl.obolibrary.org/obo/DRON_00019168" "http://purl.obolibrary.org/obo/DRON_00013499"
     [53] "http://purl.obolibrary.org/obo/DRON_00017099" "http://purl.obolibrary.org/obo/DRON_00723552"
     [55] "http://purl.obolibrary.org/obo/DRON_00012979" "http://purl.obolibrary.org/obo/DRON_00018948"
     [57] "http://purl.obolibrary.org/obo/DRON_00018646" "http://purl.obolibrary.org/obo/DRON_00015470"
     [59] "http://purl.obolibrary.org/obo/DRON_00015833" "http://purl.obolibrary.org/obo/DRON_00015638"
     [61] "http://purl.obolibrary.org/obo/DRON_00014348" "http://purl.obolibrary.org/obo/DRON_00015589"
     [63] "http://purl.obolibrary.org/obo/DRON_00017082" "http://purl.obolibrary.org/obo/DRON_00018436"
     [65] "http://purl.obolibrary.org/obo/DRON_00017139" "http://purl.obolibrary.org/obo/DRON_00014070"
     [67] "http://purl.obolibrary.org/obo/DRON_00017210" "http://purl.obolibrary.org/obo/DRON_00014729"
     [69] "http://purl.obolibrary.org/obo/DRON_00014639" "http://purl.obolibrary.org/obo/DRON_00012176"
     [71] "http://purl.obolibrary.org/obo/DRON_00013877" "http://purl.obolibrary.org/obo/DRON_00014737"
     [73] "http://purl.obolibrary.org/obo/DRON_00019026" "http://purl.obolibrary.org/obo/DRON_00019231"
     [75] "http://purl.obolibrary.org/obo/DRON_00013256" "http://purl.obolibrary.org/obo/DRON_00014991"
     [77] "http://purl.obolibrary.org/obo/DRON_00012144" "http://purl.obolibrary.org/obo/DRON_00015068"
     [79] "http://purl.obolibrary.org/obo/DRON_00017480" "http://purl.obolibrary.org/obo/DRON_00015972"
     [81] "http://purl.obolibrary.org/obo/DRON_00016258" "http://purl.obolibrary.org/obo/DRON_00013341"
     [83] "http://purl.obolibrary.org/obo/DRON_00015658" "http://purl.obolibrary.org/obo/DRON_00012996"
     [85] "http://purl.obolibrary.org/obo/DRON_00018531" "http://purl.obolibrary.org/obo/DRON_00013014"
     [87] "http://purl.obolibrary.org/obo/DRON_00015928" "http://purl.obolibrary.org/obo/DRON_00013506"
     [89] "http://purl.obolibrary.org/obo/DRON_00012861" "http://purl.obolibrary.org/obo/DRON_00018790"
     [91] "http://purl.obolibrary.org/obo/DRON_00015152" "http://purl.obolibrary.org/obo/DRON_00015732"
     [93] "http://purl.obolibrary.org/obo/DRON_00014154" "http://purl.obolibrary.org/obo/DRON_00016990"
     [95] "http://purl.obolibrary.org/obo/DRON_00013022" "http://purl.obolibrary.org/obo/DRON_00013864"
     [97] "http://purl.obolibrary.org/obo/DRON_00016969" "http://purl.obolibrary.org/obo/DRON_00016740"
     [99] "http://purl.obolibrary.org/obo/DRON_00013997" "http://purl.obolibrary.org/obo/DRON_00017634"
    [101] "http://purl.obolibrary.org/obo/DRON_00017888" "http://purl.obolibrary.org/obo/DRON_00017587"
    [103] "http://purl.obolibrary.org/obo/DRON_00016909" "http://purl.obolibrary.org/obo/DRON_00014334"
    [105] "http://purl.obolibrary.org/obo/DRON_00012889" "http://purl.obolibrary.org/obo/DRON_00750789"
    [107] "http://purl.obolibrary.org/obo/DRON_00019170" "http://purl.obolibrary.org/obo/DRON_00016736"
    [109] "http://purl.obolibrary.org/obo/DRON_00723979" "http://purl.obolibrary.org/obo/DRON_00013884"
    [111] "http://purl.obolibrary.org/obo/DRON_00016919" "http://purl.obolibrary.org/obo/DRON_00014106"
    [113] "http://purl.obolibrary.org/obo/DRON_00015347" "http://purl.obolibrary.org/obo/DRON_00015150"
    [115] "http://purl.obolibrary.org/obo/DRON_00018132" "http://purl.obolibrary.org/obo/DRON_00723493"
    [117] "http://purl.obolibrary.org/obo/DRON_00723501" "http://purl.obolibrary.org/obo/DRON_00015362"
    [119] "http://purl.obolibrary.org/obo/DRON_00011228" "http://purl.obolibrary.org/obo/DRON_00017246"
    [121] "http://purl.obolibrary.org/obo/DRON_00730821" "http://purl.obolibrary.org/obo/DRON_00730832"
    [123] "http://purl.obolibrary.org/obo/DRON_00723583" "http://purl.obolibrary.org/obo/DRON_00015083"
    [125] "http://purl.obolibrary.org/obo/DRON_00014189" "http://purl.obolibrary.org/obo/DRON_00018532"
    [127] "http://purl.obolibrary.org/obo/DRON_00724026" "http://purl.obolibrary.org/obo/DRON_00017936"
    [129] "http://purl.obolibrary.org/obo/DRON_00012893" "http://purl.obolibrary.org/obo/DRON_00015593"
    [131] "http://purl.obolibrary.org/obo/DRON_00723769" "http://purl.obolibrary.org/obo/DRON_00723961"
    [133] "http://purl.obolibrary.org/obo/DRON_00018826" "http://purl.obolibrary.org/obo/DRON_00018128"
    [135] "http://purl.obolibrary.org/obo/DRON_00010072" "http://purl.obolibrary.org/obo/CHEBI_35969"  
    [137] "http://purl.obolibrary.org/obo/DRON_00723762" "http://purl.obolibrary.org/obo/DRON_00723737"
    [139] "http://purl.obolibrary.org/obo/DRON_00016064" "http://purl.obolibrary.org/obo/CHEBI_13389"  
    [141] "http://purl.obolibrary.org/obo/DRON_00014970" "http://purl.obolibrary.org/obo/DRON_00723185"
    [143] "http://purl.obolibrary.org/obo/DRON_00020250" "http://purl.obolibrary.org/obo/DRON_00750788"
    [145] "http://purl.obolibrary.org/obo/DRON_00723787" "http://purl.obolibrary.org/obo/DRON_00724007"
    [147] "http://purl.obolibrary.org/obo/DRON_00723665" "http://purl.obolibrary.org/obo/DRON_00723761"
    [149] "http://purl.obolibrary.org/obo/DRON_00723526" "http://purl.obolibrary.org/obo/DRON_00016163"
    [151] "http://purl.obolibrary.org/obo/DRON_00723992" "http://purl.obolibrary.org/obo/DRON_00724002"
    [153] "http://purl.obolibrary.org/obo/DRON_00723482" "http://purl.obolibrary.org/obo/DRON_00723990"
    [155] "http://purl.obolibrary.org/obo/CHEBI_37140"   "http://purl.obolibrary.org/obo/CHEBI_22470"  
    [157] "http://purl.obolibrary.org/obo/DRON_00723751" "http://purl.obolibrary.org/obo/DRON_00723966"
    [159] "http://purl.obolibrary.org/obo/DRON_00016555" "http://purl.obolibrary.org/obo/DRON_00723747"
    [161] "http://purl.obolibrary.org/obo/CHEBI_35813"   "http://purl.obolibrary.org/obo/CHEBI_18145"  
    [163] "http://purl.obolibrary.org/obo/DRON_00016378" "http://purl.obolibrary.org/obo/DRON_00724073"
    [165] "http://purl.obolibrary.org/obo/DRON_00018228" "http://purl.obolibrary.org/obo/DRON_00723752"
    [167] "http://purl.obolibrary.org/obo/DRON_00013124" "http://purl.obolibrary.org/obo/DRON_00020306"
    [169] "http://purl.obolibrary.org/obo/DRON_00016413" "http://purl.obolibrary.org/obo/CHEBI_50778"  
    [171] "http://purl.obolibrary.org/obo/DRON_00723784" "http://purl.obolibrary.org/obo/DRON_00012981"
    [173] "http://purl.obolibrary.org/obo/DRON_00014058" "http://purl.obolibrary.org/obo/DRON_00015712"
    [175] "http://purl.obolibrary.org/obo/CHEBI_60583"   "http://purl.obolibrary.org/obo/DRON_00017745"
    [177] "http://purl.obolibrary.org/obo/DRON_00018136" "http://purl.obolibrary.org/obo/DRON_00012993"
    [179] "http://purl.obolibrary.org/obo/DRON_00723967" "http://purl.obolibrary.org/obo/DRON_00723529"
    [181] "http://purl.obolibrary.org/obo/DRON_00012603" "http://purl.obolibrary.org/obo/DRON_00723673"
    [183] "http://purl.obolibrary.org/obo/DRON_00010027" "http://purl.obolibrary.org/obo/DRON_00723949"
    [185] "http://purl.obolibrary.org/obo/DRON_00723620" "http://purl.obolibrary.org/obo/DRON_00723765"
    [187] "http://purl.obolibrary.org/obo/DRON_00013856" "http://purl.obolibrary.org/obo/DRON_00016463"
    [189] "http://purl.obolibrary.org/obo/DRON_00017086" "http://purl.obolibrary.org/obo/DRON_00723760"
    [191] "http://purl.obolibrary.org/obo/DRON_00723948" "http://purl.obolibrary.org/obo/DRON_00016830"
    [193] "http://purl.obolibrary.org/obo/DRON_00723540" "http://purl.obolibrary.org/obo/DRON_00730806"
    [195] "http://purl.obolibrary.org/obo/DRON_00723623" "http://purl.obolibrary.org/obo/DRON_00015910"
    [197] "http://purl.obolibrary.org/obo/DRON_00016251" "http://purl.obolibrary.org/obo/DRON_00012998"
    [199] "http://purl.obolibrary.org/obo/DRON_00750796" "http://purl.obolibrary.org/obo/DRON_00014125"
    [201] "http://purl.obolibrary.org/obo/CHEBI_25555"   "http://purl.obolibrary.org/obo/DRON_00012850"
    [203] "http://purl.obolibrary.org/obo/DRON_00012974" "http://purl.obolibrary.org/obo/DRON_00013076"
    [205] "http://purl.obolibrary.org/obo/DRON_00012681" "http://purl.obolibrary.org/obo/DRON_00730813"
    [207] "http://purl.obolibrary.org/obo/DRON_00017400" "http://purl.obolibrary.org/obo/DRON_00014242"
    [209] "http://purl.obolibrary.org/obo/DRON_00014556" "http://purl.obolibrary.org/obo/DRON_00012896"
    [211] "http://purl.obolibrary.org/obo/DRON_00723982" "http://purl.obolibrary.org/obo/DRON_00723776"
    [213] "http://purl.obolibrary.org/obo/DRON_00723678" "http://purl.obolibrary.org/obo/DRON_00018159"
    [215] "http://purl.obolibrary.org/obo/DRON_00017593" "http://purl.obolibrary.org/obo/DRON_00723538"
    [217] "http://purl.obolibrary.org/obo/DRON_00013488" "http://purl.obolibrary.org/obo/DRON_00010282"
    [219] "http://purl.obolibrary.org/obo/DRON_00014517" "http://purl.obolibrary.org/obo/DRON_00020101"
    [221] "http://purl.obolibrary.org/obo/DRON_00014564" "http://purl.obolibrary.org/obo/DRON_00013062"
    [223] "http://purl.obolibrary.org/obo/DRON_00010392" "http://purl.obolibrary.org/obo/DRON_00724078"
    [225] "http://purl.obolibrary.org/obo/DRON_00019082" "http://purl.obolibrary.org/obo/DRON_00014961"
    [227] "http://purl.obolibrary.org/obo/DRON_00017481" "http://purl.obolibrary.org/obo/DRON_00016609"
    [229] "http://purl.obolibrary.org/obo/DRON_00750801" "http://purl.obolibrary.org/obo/DRON_00014908"
    [231] "http://purl.obolibrary.org/obo/DRON_00017130" "http://purl.obolibrary.org/obo/DRON_00018140"
    [233] "http://purl.obolibrary.org/obo/DRON_00018972" "http://purl.obolibrary.org/obo/DRON_00010827"
    [235] "http://purl.obolibrary.org/obo/DRON_00015394" "http://purl.obolibrary.org/obo/DRON_00723814"
    [237] "http://purl.obolibrary.org/obo/DRON_00013019" "http://purl.obolibrary.org/obo/DRON_00011812"
    [239] "http://purl.obolibrary.org/obo/DRON_00012860" "http://purl.obolibrary.org/obo/DRON_00016933"
    [241] "http://purl.obolibrary.org/obo/DRON_00012831" "http://purl.obolibrary.org/obo/DRON_00016927"
    [243] "http://purl.obolibrary.org/obo/DRON_00011760" "http://purl.obolibrary.org/obo/DRON_00010337"
    [245] "http://purl.obolibrary.org/obo/DRON_00018673" "http://purl.obolibrary.org/obo/DRON_00018235"
    [247] "http://purl.obolibrary.org/obo/DRON_00015227" "http://purl.obolibrary.org/obo/DRON_00016932"
    [249] "http://purl.obolibrary.org/obo/DRON_00012876" "http://purl.obolibrary.org/obo/DRON_00015499"
    [251] "http://purl.obolibrary.org/obo/DRON_00011390" "http://purl.obolibrary.org/obo/DRON_00750827"
    [253] "http://purl.obolibrary.org/obo/DRON_00724123" "http://purl.obolibrary.org/obo/DRON_00724198"
    [255] "http://purl.obolibrary.org/obo/DRON_00015664" "http://purl.obolibrary.org/obo/DRON_00012475"
    [257] "http://purl.obolibrary.org/obo/DRON_00011455" "http://purl.obolibrary.org/obo/DRON_00017357"
    [259] "http://purl.obolibrary.org/obo/DRON_00018047" "http://purl.obolibrary.org/obo/DRON_00015862"
    [261] "http://purl.obolibrary.org/obo/DRON_00018663" "http://purl.obolibrary.org/obo/DRON_00018186"
    [263] "http://purl.obolibrary.org/obo/DRON_00015959" "http://purl.obolibrary.org/obo/DRON_00016068"
    [265] "http://purl.obolibrary.org/obo/DRON_00012858" "http://purl.obolibrary.org/obo/DRON_00017837"
    [267] "http://purl.obolibrary.org/obo/DRON_00013313" "http://purl.obolibrary.org/obo/DRON_00017730"
    [269] "http://purl.obolibrary.org/obo/DRON_00723746" "http://purl.obolibrary.org/obo/CHEBI_24859"  
    [271] "http://purl.obolibrary.org/obo/DRON_00017200" "http://purl.obolibrary.org/obo/DRON_00012878"
    [273] "http://purl.obolibrary.org/obo/DRON_00013906" "http://purl.obolibrary.org/obo/DRON_00010413"
    [275] "http://purl.obolibrary.org/obo/DRON_00013638" "http://purl.obolibrary.org/obo/DRON_00723735"
    [277] "http://purl.obolibrary.org/obo/DRON_00723984" "http://purl.obolibrary.org/obo/DRON_00013306"
    [279] "http://purl.obolibrary.org/obo/DRON_00014321" "http://purl.obolibrary.org/obo/DRON_00014388"
    [281] "http://purl.obolibrary.org/obo/DRON_00723742" "http://purl.obolibrary.org/obo/DRON_00723768"
    [283] "http://purl.obolibrary.org/obo/DRON_00723820" "http://purl.obolibrary.org/obo/DRON_00015392"
    [285] "http://purl.obolibrary.org/obo/DRON_00015034" "http://purl.obolibrary.org/obo/DRON_00016780"
    [287] "http://purl.obolibrary.org/obo/DRON_00012875" "http://purl.obolibrary.org/obo/DRON_00750794"
    [289] "http://purl.obolibrary.org/obo/DRON_00015246" "http://purl.obolibrary.org/obo/DRON_00012453"
    [291] "http://purl.obolibrary.org/obo/DRON_00012735" "http://purl.obolibrary.org/obo/DRON_00012888"
    [293] "http://purl.obolibrary.org/obo/DRON_00012975" "http://purl.obolibrary.org/obo/DRON_00015544"
    [295] "http://purl.obolibrary.org/obo/DRON_00014292" "http://purl.obolibrary.org/obo/DRON_00012879"
    [297] "http://purl.obolibrary.org/obo/DRON_00011531" "http://purl.obolibrary.org/obo/DRON_00723692"
    [299] "http://purl.obolibrary.org/obo/DRON_00723296" "http://purl.obolibrary.org/obo/DRON_00012976"
    [301] "http://purl.obolibrary.org/obo/DRON_00017247" "http://purl.obolibrary.org/obo/DRON_00723738"
    [303] "http://purl.obolibrary.org/obo/DRON_00018731" "http://purl.obolibrary.org/obo/DRON_00723214"
    [305] "http://purl.obolibrary.org/obo/DRON_00011012" "http://purl.obolibrary.org/obo/PR_000000001" 
    [307] "http://purl.obolibrary.org/obo/DRON_00012892" "http://purl.obolibrary.org/obo/DRON_00016281"
    [309] "http://purl.obolibrary.org/obo/DRON_00724015" "http://purl.obolibrary.org/obo/DRON_00761788"
    [311] "http://purl.obolibrary.org/obo/DRON_00017835" "http://purl.obolibrary.org/obo/CHEBI_37406"  
    [313] "http://purl.obolibrary.org/obo/DRON_00018135" "http://purl.obolibrary.org/obo/DRON_00723474"
    [315] "http://purl.obolibrary.org/obo/DRON_00723550" "http://purl.obolibrary.org/obo/DRON_00010600"
    [317] "http://purl.obolibrary.org/obo/DRON_00015348" "http://purl.obolibrary.org/obo/DRON_00750822"
    [319] "http://purl.obolibrary.org/obo/DRON_00016665" "http://purl.obolibrary.org/obo/DRON_00014690"
    [321] "http://purl.obolibrary.org/obo/CHEBI_39462"   "http://purl.obolibrary.org/obo/DRON_00018560"
    [323] "http://purl.obolibrary.org/obo/DRON_00723514" "http://purl.obolibrary.org/obo/DRON_00723750"
    [325] "http://purl.obolibrary.org/obo/DRON_00018920" "http://purl.obolibrary.org/obo/DRON_00723193"
    [327] "http://purl.obolibrary.org/obo/DRON_00013258" "http://purl.obolibrary.org/obo/DRON_00012970"
    [329] "http://purl.obolibrary.org/obo/DRON_00724127" "http://purl.obolibrary.org/obo/DRON_00756590"
    [331] "http://purl.obolibrary.org/obo/DRON_00010567" "http://purl.obolibrary.org/obo/DRON_00016018"
    [333] "http://purl.obolibrary.org/obo/DRON_00013063" "http://purl.obolibrary.org/obo/DRON_00013026"
    [335] "http://purl.obolibrary.org/obo/DRON_00010596" "http://purl.obolibrary.org/obo/DRON_00724169"
    [337] "http://purl.obolibrary.org/obo/DRON_00016254" "http://purl.obolibrary.org/obo/DRON_00010604"
    [339] "http://purl.obolibrary.org/obo/DRON_00020210" "http://purl.obolibrary.org/obo/DRON_00013428"
    [341] "http://purl.obolibrary.org/obo/DRON_00723778" "http://purl.obolibrary.org/obo/DRON_00013640"
    [343] "http://purl.obolibrary.org/obo/DRON_00723679" "http://purl.obolibrary.org/obo/DRON_00019834"
    [345] "http://purl.obolibrary.org/obo/DRON_00723965" "http://purl.obolibrary.org/obo/DRON_00016701"
    [347] "http://purl.obolibrary.org/obo/DRON_00723796" "http://purl.obolibrary.org/obo/DRON_00011804"
    [349] "http://purl.obolibrary.org/obo/DRON_00017836" "http://purl.obolibrary.org/obo/DRON_00012972"
    [351] "http://purl.obolibrary.org/obo/DRON_00723745" "http://purl.obolibrary.org/obo/CHEBI_48339"  
    [353] "http://purl.obolibrary.org/obo/DRON_00013135" "http://purl.obolibrary.org/obo/DRON_00017078"
    [355] "http://purl.obolibrary.org/obo/DRON_00724074" "http://purl.obolibrary.org/obo/DRON_00723530"
    [357] "http://purl.obolibrary.org/obo/DRON_00723974" "http://purl.obolibrary.org/obo/DRON_00015291"
    [359] "http://purl.obolibrary.org/obo/DRON_00724125" "http://purl.obolibrary.org/obo/DRON_00723779"
    [361] "http://purl.obolibrary.org/obo/DRON_00013741" "http://purl.obolibrary.org/obo/DRON_00723554"
    [363] "http://purl.obolibrary.org/obo/DRON_00723672" "http://purl.obolibrary.org/obo/DRON_00016738"
    [365] "http://purl.obolibrary.org/obo/DRON_00016879" "http://purl.obolibrary.org/obo/DRON_00018835"
    [367] "http://purl.obolibrary.org/obo/DRON_00011829" "http://purl.obolibrary.org/obo/DRON_00018148"
    [369] "http://purl.obolibrary.org/obo/DRON_00730809" "http://purl.obolibrary.org/obo/CHEBI_50122"  
    [371] "http://purl.obolibrary.org/obo/DRON_00012124" "http://purl.obolibrary.org/obo/DRON_00012880"
    [373] "http://purl.obolibrary.org/obo/DRON_00017776" "http://purl.obolibrary.org/obo/DRON_00016921"
    [375] "http://purl.obolibrary.org/obo/DRON_00017199" "http://purl.obolibrary.org/obo/DRON_00017637"
    [377] "http://purl.obolibrary.org/obo/DRON_00723485" "http://purl.obolibrary.org/obo/DRON_00723781"
    [379] "http://purl.obolibrary.org/obo/DRON_00730916" "http://purl.obolibrary.org/obo/DRON_00019437"
    [381] "http://purl.obolibrary.org/obo/DRON_00723867" "http://purl.obolibrary.org/obo/BFO_0000023"  
    [383] "http://purl.obolibrary.org/obo/DRON_00013137" "http://purl.obolibrary.org/obo/DRON_00015393"
    [385] "http://purl.obolibrary.org/obo/DRON_00020010" "http://purl.obolibrary.org/obo/DRON_00017253"
    [387] "http://purl.obolibrary.org/obo/DRON_00018173" "http://purl.obolibrary.org/obo/DRON_00017832"
    [389] "http://purl.obolibrary.org/obo/CHEBI_21653"   "http://purl.obolibrary.org/obo/DRON_00016225"
    [391] "http://purl.obolibrary.org/obo/DRON_00750869" "http://purl.obolibrary.org/obo/DRON_00723996"
    [393] "http://purl.obolibrary.org/obo/DRON_00018520" "http://purl.obolibrary.org/obo/DRON_00013121"
    [395] "http://purl.obolibrary.org/obo/DRON_00723771" "http://purl.obolibrary.org/obo/DRON_00018153"
    [397] "http://purl.obolibrary.org/obo/DRON_00015641" "http://purl.obolibrary.org/obo/DRON_00018683"
    [399] "http://purl.obolibrary.org/obo/DRON_00724087" "http://purl.obolibrary.org/obo/DRON_00723945"
    [401] "http://purl.obolibrary.org/obo/DRON_00017774" "http://purl.obolibrary.org/obo/DRON_00723988"
    [403] "http://purl.obolibrary.org/obo/DRON_00723836" "http://purl.obolibrary.org/obo/DRON_00723221"
    [405] "http://purl.obolibrary.org/obo/DRON_00723962" "http://purl.obolibrary.org/obo/DRON_00017215"
    [407] "http://purl.obolibrary.org/obo/DRON_00014998" "http://purl.obolibrary.org/obo/DRON_00013847"
    [409] "http://purl.obolibrary.org/obo/DRON_00010158" "http://purl.obolibrary.org/obo/DRON_00018854"
    [411] "http://purl.obolibrary.org/obo/DRON_00013481" "http://purl.obolibrary.org/obo/DRON_00723579"
    [413] "http://purl.obolibrary.org/obo/DRON_00017757" "http://purl.obolibrary.org/obo/DRON_00013338"
    [415] "http://purl.obolibrary.org/obo/DRON_00014863" "http://purl.obolibrary.org/obo/DRON_00016418"
    [417] "http://purl.obolibrary.org/obo/DRON_00015069" "http://purl.obolibrary.org/obo/DRON_00724016"
    [419] "http://purl.obolibrary.org/obo/DRON_00010901" "http://purl.obolibrary.org/obo/DRON_00020208"
    [421] "http://purl.obolibrary.org/obo/DRON_00015609" "http://purl.obolibrary.org/obo/DRON_00018582"
    [423] "http://purl.obolibrary.org/obo/DRON_00014188" "http://purl.obolibrary.org/obo/DRON_00012971"
    [425] "http://purl.obolibrary.org/obo/DRON_00016915" "http://purl.obolibrary.org/obo/DRON_00013825"
    [427] "http://purl.obolibrary.org/obo/DRON_00012488" "http://purl.obolibrary.org/obo/DRON_00013318"
    [429] "http://purl.obolibrary.org/obo/DRON_00014691" "http://purl.obolibrary.org/obo/DRON_00723207"
    [431] "http://purl.obolibrary.org/obo/DRON_00014191" "http://purl.obolibrary.org/obo/DRON_00014039"
    [433] "http://purl.obolibrary.org/obo/DRON_00014250" "http://purl.obolibrary.org/obo/DRON_00018791"
    [435] "http://purl.obolibrary.org/obo/DRON_00014917" "http://purl.obolibrary.org/obo/DRON_00723841"
    [437] "http://purl.obolibrary.org/obo/DRON_00014193" "http://purl.obolibrary.org/obo/DRON_00750814"
    [439] "http://purl.obolibrary.org/obo/DRON_00019502" "http://purl.obolibrary.org/obo/DRON_00750786"
    [441] "http://purl.obolibrary.org/obo/DRON_00011892" "http://purl.obolibrary.org/obo/DRON_00723539"
    [443] "http://purl.obolibrary.org/obo/DRON_00723736" "http://purl.obolibrary.org/obo/DRON_00019090"
    [445] "http://purl.obolibrary.org/obo/DRON_00014263" "http://purl.obolibrary.org/obo/DRON_00723557"
    [447] "http://purl.obolibrary.org/obo/DRON_00723525" "http://purl.obolibrary.org/obo/DRON_00016719"
    [449] "http://purl.obolibrary.org/obo/DRON_00019892" "http://purl.obolibrary.org/obo/DRON_00019228"
    [451] "http://purl.obolibrary.org/obo/DRON_00020018" "http://purl.obolibrary.org/obo/DRON_00018981"
    [453] "http://purl.obolibrary.org/obo/DRON_00018842" "http://purl.obolibrary.org/obo/DRON_00016952"
    [455] "http://purl.obolibrary.org/obo/DRON_00014262" "http://purl.obolibrary.org/obo/DRON_00020017"
    [457] "http://purl.obolibrary.org/obo/DRON_00017214" "http://purl.obolibrary.org/obo/DRON_00016196"
    [459] "http://purl.obolibrary.org/obo/DRON_00010623" "http://purl.obolibrary.org/obo/DRON_00012537"
    [461] "http://purl.obolibrary.org/obo/DRON_00014302" "http://purl.obolibrary.org/obo/DRON_00019003"
    [463] "http://purl.obolibrary.org/obo/CHEBI_4562"    "http://purl.obolibrary.org/obo/DRON_00730866"
    [465] "http://purl.obolibrary.org/obo/DRON_00018916" "http://purl.obolibrary.org/obo/DRON_00013042"
    [467] "http://purl.obolibrary.org/obo/DRON_00019607" "http://purl.obolibrary.org/obo/DRON_00019862"
    [469] "http://purl.obolibrary.org/obo/DRON_00724048" "http://purl.obolibrary.org/obo/DRON_00723741"
    [471] "http://purl.obolibrary.org/obo/DRON_00723901" "http://purl.obolibrary.org/obo/DRON_00012885"
    [473] "http://purl.obolibrary.org/obo/DRON_00020262" "http://purl.obolibrary.org/obo/DRON_00020261"
    [475] "http://purl.obolibrary.org/obo/DRON_00013938" "http://purl.obolibrary.org/obo/DRON_00013271"
    [477] "http://purl.obolibrary.org/obo/DRON_00020193" "http://purl.obolibrary.org/obo/DRON_00020183"
    [479] "http://purl.obolibrary.org/obo/CHEBI_26907"   "http://purl.obolibrary.org/obo/DRON_00011062"
    [481] "http://purl.obolibrary.org/obo/DRON_00013127" "http://purl.obolibrary.org/obo/DRON_00016186"
    [483] "http://purl.obolibrary.org/obo/DRON_00019216" "http://purl.obolibrary.org/obo/DRON_00012153"
    [485] "http://purl.obolibrary.org/obo/DRON_00723783" "http://purl.obolibrary.org/obo/DRON_00013061"
    [487] "http://purl.obolibrary.org/obo/DRON_00020137" "http://purl.obolibrary.org/obo/DRON_00017294"
    [489] "http://purl.obolibrary.org/obo/DRON_00020100" "http://purl.obolibrary.org/obo/DRON_00723648"
    [491] "http://purl.obolibrary.org/obo/DRON_00011816" "http://purl.obolibrary.org/obo/DRON_00019908"
    [493] "http://purl.obolibrary.org/obo/DRON_00723805" "http://purl.obolibrary.org/obo/DRON_00011109"
    [495] "http://purl.obolibrary.org/obo/DRON_00012325" "http://purl.obolibrary.org/obo/DRON_00013280"
    [497] "http://purl.obolibrary.org/obo/DRON_00723650" "http://purl.obolibrary.org/obo/DRON_00750851"
    [499] "http://purl.obolibrary.org/obo/DRON_00020008" "http://purl.obolibrary.org/obo/DRON_00018264"
    [501] "http://purl.obolibrary.org/obo/DRON_00019903" "http://purl.obolibrary.org/obo/DRON_00019799"
    [503] "http://purl.obolibrary.org/obo/DRON_00019617" "http://purl.obolibrary.org/obo/DRON_00019456"
    [505] "http://purl.obolibrary.org/obo/DRON_00019466" "http://purl.obolibrary.org/obo/DRON_00019459"
    [507] "http://purl.obolibrary.org/obo/CHEBI_7591"    "http://purl.obolibrary.org/obo/CHEBI_23238"  
    [509] "http://purl.obolibrary.org/obo/DRON_00750770" "http://purl.obolibrary.org/obo/DRON_00723857"
    [511] "http://purl.obolibrary.org/obo/DRON_00730812" "http://purl.obolibrary.org/obo/DRON_00730811"
    [513] "http://purl.obolibrary.org/obo/DRON_00020322" "http://purl.obolibrary.org/obo/DRON_00730816"
    [515] "http://purl.obolibrary.org/obo/DRON_00018684" "http://purl.obolibrary.org/obo/DRON_00019906"
    [517] "http://purl.obolibrary.org/obo/DRON_00750775" "http://purl.obolibrary.org/obo/CHEBI_57589"  
    [519] "http://purl.obolibrary.org/obo/DRON_00018670" "http://purl.obolibrary.org/obo/DRON_00015118"
    [521] "http://purl.obolibrary.org/obo/DRON_00013342" "http://purl.obolibrary.org/obo/DRON_00750778"
    [523] "http://purl.obolibrary.org/obo/DRON_00750776" "http://purl.obolibrary.org/obo/DRON_00013272"
    [525] "http://purl.obolibrary.org/obo/DRON_00017672" "http://purl.obolibrary.org/obo/DRON_00723203"
    [527] "http://purl.obolibrary.org/obo/DRON_00016198" "http://purl.obolibrary.org/obo/DRON_00013807"
    [529] "http://purl.obolibrary.org/obo/DRON_00724063" "http://purl.obolibrary.org/obo/DRON_00018349"
    [531] "http://purl.obolibrary.org/obo/DRON_00018007" "http://purl.obolibrary.org/obo/DRON_00016976"
    [533] "http://purl.obolibrary.org/obo/DRON_00750783" "http://purl.obolibrary.org/obo/DRON_00730819"
    [535] "http://purl.obolibrary.org/obo/DRON_00010811" "http://purl.obolibrary.org/obo/DRON_00016020"
    [537] "http://purl.obolibrary.org/obo/DRON_00018196" "http://purl.obolibrary.org/obo/DRON_00011913"
    [539] "http://purl.obolibrary.org/obo/DRON_00730831" "http://purl.obolibrary.org/obo/DRON_00000029"
    [541] "http://purl.obolibrary.org/obo/DRON_00724122" "http://purl.obolibrary.org/obo/DRON_00018797"
    [543] "http://purl.obolibrary.org/obo/DRON_00012990" "http://purl.obolibrary.org/obo/DRON_00750784"
    [545] "http://purl.obolibrary.org/obo/DRON_00750779" "http://purl.obolibrary.org/obo/DRON_00750787"
    [547] "http://purl.obolibrary.org/obo/DRON_00750792" "http://purl.obolibrary.org/obo/DRON_00723860"
    [549] "http://purl.obolibrary.org/obo/DRON_00018103" "http://purl.obolibrary.org/obo/DRON_00010161"
    [551] "http://purl.obolibrary.org/obo/DRON_00723758" "http://purl.obolibrary.org/obo/DRON_00730826"
    [553] "http://purl.obolibrary.org/obo/DRON_00730827" "http://purl.obolibrary.org/obo/DRON_00017815"
    [555] "http://purl.obolibrary.org/obo/DRON_00723963" "http://purl.obolibrary.org/obo/DRON_00017809"
    [557] "http://purl.obolibrary.org/obo/DRON_00016117" "http://purl.obolibrary.org/obo/DRON_00730834"
    [559] "http://purl.obolibrary.org/obo/DRON_00723545" "http://purl.obolibrary.org/obo/DRON_00730835"
    [561] "http://purl.obolibrary.org/obo/DRON_00750803" "http://purl.obolibrary.org/obo/DRON_00750768"
    [563] "http://purl.obolibrary.org/obo/DRON_00016223" "http://purl.obolibrary.org/obo/DRON_00019860"
    [565] "http://purl.obolibrary.org/obo/DRON_00019519" "http://purl.obolibrary.org/obo/DRON_00724109"
    [567] "http://purl.obolibrary.org/obo/DRON_00723879" "http://purl.obolibrary.org/obo/DRON_00750799"
    [569] "http://purl.obolibrary.org/obo/DRON_00730830" "http://purl.obolibrary.org/obo/DRON_00013349"
    [571] "http://purl.obolibrary.org/obo/DRON_00018949" "http://purl.obolibrary.org/obo/DRON_00019976"
    [573] "http://purl.obolibrary.org/obo/DRON_00730879" "http://purl.obolibrary.org/obo/DRON_00012992"
    [575] "http://purl.obolibrary.org/obo/DRON_00730912" "http://purl.obolibrary.org/obo/DRON_00013143"
    [577] "http://purl.obolibrary.org/obo/DRON_00012434" "http://purl.obolibrary.org/obo/DRON_00012435"
    [579] "http://purl.obolibrary.org/obo/DRON_00016912" "http://purl.obolibrary.org/obo/DRON_00011870"
    [581] "http://purl.obolibrary.org/obo/DRON_00016896" "http://purl.obolibrary.org/obo/DRON_00723184"
    [583] "http://purl.obolibrary.org/obo/DRON_00012332" "http://purl.obolibrary.org/obo/DRON_00011384"
    [585] "http://purl.obolibrary.org/obo/DRON_00018187" "http://purl.obolibrary.org/obo/DRON_00724178"
    [587] "http://purl.obolibrary.org/obo/DRON_00014036" "http://purl.obolibrary.org/obo/DRON_00010919"
    [589] "http://purl.obolibrary.org/obo/DRON_00723934" "http://purl.obolibrary.org/obo/DRON_00020280"
    [591] "http://purl.obolibrary.org/obo/DRON_00723743" "http://purl.obolibrary.org/obo/DRON_00730838"
    [593] "http://purl.obolibrary.org/obo/DRON_00750820" "http://purl.obolibrary.org/obo/DRON_00730837"
    [595] "http://purl.obolibrary.org/obo/DRON_00750815" "http://purl.obolibrary.org/obo/DRON_00723862"
    [597] "http://purl.obolibrary.org/obo/DRON_00750813" "http://purl.obolibrary.org/obo/DRON_00750812"
    [599] "http://purl.obolibrary.org/obo/DRON_00730836" "http://purl.obolibrary.org/obo/DRON_00750811"
    [601] "http://purl.obolibrary.org/obo/DRON_00750818" "http://purl.obolibrary.org/obo/DRON_00010761"
    [603] "http://purl.obolibrary.org/obo/DRON_00014990" "http://purl.obolibrary.org/obo/DRON_00013355"
    [605] "http://purl.obolibrary.org/obo/DRON_00730839" "http://purl.obolibrary.org/obo/DRON_00750819"
    [607] "http://purl.obolibrary.org/obo/DRON_00730848" "http://purl.obolibrary.org/obo/DRON_00750823"
    [609] "http://purl.obolibrary.org/obo/DRON_00015608" "http://purl.obolibrary.org/obo/DRON_00723472"
    [611] "http://purl.obolibrary.org/obo/DRON_00723904" "http://purl.obolibrary.org/obo/DRON_00018237"
    [613] "http://purl.obolibrary.org/obo/DRON_00730843" "http://purl.obolibrary.org/obo/DRON_00750857"
    [615] "http://purl.obolibrary.org/obo/DRON_00723524" "http://purl.obolibrary.org/obo/DRON_00018141"
    [617] "http://purl.obolibrary.org/obo/DRON_00011447" "http://purl.obolibrary.org/obo/DRON_00017463"
    [619] "http://purl.obolibrary.org/obo/DRON_00750800" "http://purl.obolibrary.org/obo/DRON_00723861"
    [621] "http://purl.obolibrary.org/obo/DRON_00750826" "http://purl.obolibrary.org/obo/DRON_00750824"
    [623] "http://purl.obolibrary.org/obo/DRON_00730840" "http://purl.obolibrary.org/obo/DRON_00750834"
    [625] "http://purl.obolibrary.org/obo/DRON_00750832" "http://purl.obolibrary.org/obo/DRON_00750830"
    [627] "http://purl.obolibrary.org/obo/DRON_00750831" "http://purl.obolibrary.org/obo/DRON_00019499"
    [629] "http://purl.obolibrary.org/obo/DRON_00013120" "http://purl.obolibrary.org/obo/DRON_00019939"
    [631] "http://purl.obolibrary.org/obo/DRON_00730824" "http://purl.obolibrary.org/obo/DRON_00750790"
    [633] "http://purl.obolibrary.org/obo/DRON_00750840" "http://purl.obolibrary.org/obo/DRON_00750835"
    [635] "http://purl.obolibrary.org/obo/DRON_00730850" "http://purl.obolibrary.org/obo/DRON_00750842"
    [637] "http://purl.obolibrary.org/obo/DRON_00750838" "http://purl.obolibrary.org/obo/DRON_00730847"
    [639] "http://purl.obolibrary.org/obo/DRON_00750837" "http://purl.obolibrary.org/obo/DRON_00730846"
    [641] "http://purl.obolibrary.org/obo/DRON_00016235" "http://purl.obolibrary.org/obo/DRON_00012575"
    [643] "http://purl.obolibrary.org/obo/DRON_00015053" "http://purl.obolibrary.org/obo/DRON_00017728"
    [645] "http://purl.obolibrary.org/obo/DRON_00012969" "http://purl.obolibrary.org/obo/DRON_00013939"
    [647] "http://purl.obolibrary.org/obo/DRON_00730900" "http://purl.obolibrary.org/obo/DRON_00014021"
    [649] "http://purl.obolibrary.org/obo/DRON_00724197" "http://purl.obolibrary.org/obo/DRON_00013969"
    [651] "http://purl.obolibrary.org/obo/DRON_00017258" "http://purl.obolibrary.org/obo/DRON_00015061"
    [653] "http://purl.obolibrary.org/obo/DRON_00014906" "http://purl.obolibrary.org/obo/DRON_00017698"
    [655] "http://purl.obolibrary.org/obo/DRON_00750843" "http://purl.obolibrary.org/obo/DRON_00730864"
    [657] "http://purl.obolibrary.org/obo/DRON_00730860" "http://purl.obolibrary.org/obo/CHEBI_50217"  
    [659] "http://purl.obolibrary.org/obo/DRON_00750849" "http://purl.obolibrary.org/obo/DRON_00750853"
    [661] "http://purl.obolibrary.org/obo/DRON_00750848" "http://purl.obolibrary.org/obo/DRON_00750847"
    [663] "http://purl.obolibrary.org/obo/DRON_00730858" "http://purl.obolibrary.org/obo/DRON_00730865"
    [665] "http://purl.obolibrary.org/obo/DRON_00750855" "http://purl.obolibrary.org/obo/DRON_00750852"
    [667] "http://purl.obolibrary.org/obo/DRON_00730862" "http://purl.obolibrary.org/obo/DRON_00750862"
    [669] "http://purl.obolibrary.org/obo/DRON_00750860" "http://purl.obolibrary.org/obo/DRON_00730851"
    [671] "http://purl.obolibrary.org/obo/DRON_00750865" "http://purl.obolibrary.org/obo/DRON_00014175"
    [673] "http://purl.obolibrary.org/obo/DRON_00011543" "http://purl.obolibrary.org/obo/DRON_00019403"
    [675] "http://purl.obolibrary.org/obo/DRON_00017899" "http://purl.obolibrary.org/obo/DRON_00010065"
    [677] "http://purl.obolibrary.org/obo/DRON_00013356" "http://purl.obolibrary.org/obo/DRON_00723224"
    [679] "http://purl.obolibrary.org/obo/DRON_00012881" "http://purl.obolibrary.org/obo/DRON_00014187"
    [681] "http://purl.obolibrary.org/obo/DRON_00013976" "http://purl.obolibrary.org/obo/DRON_00015949"
    [683] "http://purl.obolibrary.org/obo/DRON_00012219" "http://purl.obolibrary.org/obo/DRON_00018130"
    [685] "http://purl.obolibrary.org/obo/DRON_00016878" "http://purl.obolibrary.org/obo/DRON_00012886"
    [687] "http://purl.obolibrary.org/obo/DRON_00018287" "http://purl.obolibrary.org/obo/DRON_00013302"
    [689] "http://purl.obolibrary.org/obo/DRON_00011712" "http://purl.obolibrary.org/obo/DRON_00012989"
    [691] "http://purl.obolibrary.org/obo/DRON_00012882" "http://purl.obolibrary.org/obo/DRON_00013746"
    [693] "http://purl.obolibrary.org/obo/DRON_00016063"
