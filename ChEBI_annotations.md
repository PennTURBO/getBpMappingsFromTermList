For ChEBI, only consider terms that are rdfs:subClassOf* obo:CHEBI_24431 (chemcal entitiy). That is, don't examine the lables of roles, etc.

For DrOn, only consider terms that are the granular part of seomthing.

Both of those rules may be mostly irrelevant, if the label matrixes are going to be merged with the BioPortal mappings, and if BioPortal only maps ingredients. (DrOn doesn't model roles? and ChEBI doesn't model products?)

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

The following query retrieves all ChEBI labels, exact synonyms, related synonyms, as well as the deprecation flag. It would at the very least look better if `distinct` was applied to the group concationation of the synonyms. I haven't been able to get group  concationation + distinct to work yet. I think that's because the server I'm using only has 16 GB RAM.

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

There are 46,351 IUPAC `ExactSynonym`s, which presumably would never match a DrOn `rdfs:label`

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
