The script `getBpMappingsFromTermList.py` was written to retrieve mappings from ChEBI terms to DrOn terms from the BioPortal API. The output, like `ChEBI_to_DrOn_BpMappingsFromTermList.out.tsv`, only contains the term IDs/URIs. 

This document addresses adding labels and synonyms, from both sources, in order help with quality control. Adding this capability to `getBpMappingsFromTermList.py` was considered, but in order to clarify some filtering opportunities, manually issued SPARQL queries and a short R merging script were used instead. The resulting labeled mappings can be found in https://github.com/PennTURBO/getBpMappingsFromTermList/blob/master/ChEBI_to_DrOn_BpMappingsFromTermList.out.withLabels.tsv

For example, rosuvastatin is modeled with different terms in the two ontologies: `obo:CHEBI_38545` and `obo:DRON_00018679`. When DrOn asserts that Crestor tablets have `obo:DRON_00018679` as an active ingredient, it breaks the potential link to ChEBI's 'anticholesteremic drug'. So `obo:DRON_00018679` could be retired from the DrugOntology and replaced with `obo:CHEBI_38545`. 

For ChEBI, let's only consider terms that are `rdfs:subClassOf*` `obo:CHEBI_24431` ('chemical entity'). That is, don't bother examining the labels of roles, etc. for the purpose of aligning with DrOn.

_Could we possibly constrain this even more? Just examining the labels of Molecular entities and chemical substances?_

    CHEBI:24431 chemical entity
        CHEBI:59999 chemical substance
        CHEBI:23367 molecular entity
        CHEBI:24433 group
        CHEBI:33250 atom

The following query retrieves all ChEBI labels, exact synonyms, related synonyms. It was run on a server with 128 GB RAM.

An open question is whether some of the sources of ChEBI synonyms aren't useful for confirming equivalence with DrOn terms, and should therefore be omitted.

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

The full version of `chebi.owl` includes annotations like these on chemical entities
- `rdfs:label` (one per class)
- `oboInOwl:hasExactSynonym` (possibly many)
- `oboInOwl:hasRelatedSynonym` (possibly many, even as many as 50)

For every synonym assertion, there will be a supporting axiom. The axioms can assert a synonym type or a database cross reference. The data base cross references are sources or authorities (like "KEGG"), not the identifying values used by those third party authorities (like "D00217").

Regarding unhelpful synonym sources: there are 46,351 IUPAC `ExactSynonym`s, which presumably would never match a DrOn `rdfs:label`. Omitting the `chebi:BRAND_NAME` synonyms might be justified, too. While DrOn doesn't have terms for brands in the absence of a dose form (like "Tylenol"), ChEBI does assert that "Tylenol" is a `KEGG DRUG` synonym for `obo:CHEBI_46195` ("paracetamol").

### Table of all ChEBI synonym sources

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

### Finding examples of synonyms from a specified authority

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

## DrOn label query

    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select ?ingredient ?ingLab
        where {
            graph <http://purl.obolibrary.org/obo/dron/dron-ingredient.owl> {
                ?ingredient rdfs:label ?ingLab   
            }
            minus {
                graph <http://purl.obolibrary.org/obo/dron/dron-chebi.owl> {
                    ?ingredient rdfs:label ?chebiLab   
                }  
            }
        }

## Merging the BioPortal mappings with the ChEBI and DrOn labels

    ChEBI_to_DrOn_BpMappingsFromTermList_out <-
      read_delim(
        "C:/Users/Mark Miller/getBpMappingsFromTermList/ChEBI_to_DrOn_BpMappingsFromTermList.out.tsv",
        "\t",
        escape_double = FALSE,
        trim_ws = TRUE,
        col_names = c(
          "source.ont",
          "source.term",
          "map.meth",
          "dest.ont",
          "dest.term"
        )
      )

    # dron.labs <-
    #   read_delim(
    #     "dronActIngLabs.tsv",
    #     "\t",
    #     escape_double = FALSE,
    #     trim_ws = TRUE
    #   )


    dron.labs <-
      read_delim(
        "dron_all_labels.tsv",
        "\t",
        escape_double = FALSE,
        trim_ws = TRUE
      )

    names(dron.labs) <-
      gsub(pattern = "^\\?",
           replacement = "",
           x = names(dron.labs))

    chebi_labels_synonyms_depr_distinct <-
      read_delim(
        "chebi_labels_synonyms_depr_distinct.tsv",
        "\t",
        escape_double = FALSE,
        trim_ws = TRUE
      )


    names(chebi_labels_synonyms_depr_distinct) <-
      gsub(
        pattern = "^\\?",
        replacement = "",
        x = names(chebi_labels_synonyms_depr_distinct)
      )

    chebi_labels_synonyms_depr_distinct$s <-
      gsub(pattern = "<|>",
           replacement = "",
           x = chebi_labels_synonyms_depr_distinct$s)


    dron.labs$ingredient <-
      gsub(pattern = "<|>",
           replacement = "",
           x = dron.labs$ingredient)


    joined <-
      dplyr::inner_join(x = ChEBI_to_DrOn_BpMappingsFromTermList_out,
                        y = chebi_labels_synonyms_depr_distinct,
                        by = c("source.term" = "s"))

    joined <-
      dplyr::inner_join(x = joined,
                        y = dron.labs,
                        by = c("dest.term" = "ingredient"))

    # dput(names(joined))
    names(joined) <-
      c(
        "source.ont",
        "source.term",
        "map.meth",
        "dest.ont",
        "dest.term",
        "source.label",
        "deprecated",
        "source.exact.syns",
        "source.related.syns",
        "dest.label"
      )

    joined <- joined[,  c(
      "source.ont",
      "source.term",
      "map.meth",
      "dest.ont",
      "dest.term",
      "source.label",
      "source.exact.syns",
      "source.related.syns",
      "dest.label"
    )]

    setdiff(ChEBI_to_DrOn_BpMappingsFromTermList_out$dest.term,
            joined$dest.term)
    
## DrOn terms that don't appear in the new labeled _active ingredient_ mappings

~ 700 DrOn terms from `ChEBI_to_DrOn_BpMappingsFromTermList.out.tsv` are lost when inner-joined to the results from the attempted active-ingredient-only query

Removing the active ingredient constraint brings it down to 32
    
    > setdiff(ChEBI_to_DrOn_BpMappingsFromTermList_out$dest.term, joined$dest.term)
     [1] "http://purl.obolibrary.org/obo/CHEBI_32150"   "http://purl.obolibrary.org/obo/CHEBI_25524"  
     [3] "http://purl.obolibrary.org/obo/CHEBI_35969"   "http://purl.obolibrary.org/obo/CHEBI_13389"  
     [5] "http://purl.obolibrary.org/obo/CHEBI_37140"   "http://purl.obolibrary.org/obo/CHEBI_22470"  
     [7] "http://purl.obolibrary.org/obo/CHEBI_35813"   "http://purl.obolibrary.org/obo/CHEBI_18145"  
     [9] "http://purl.obolibrary.org/obo/CHEBI_50778"   "http://purl.obolibrary.org/obo/CHEBI_60583"  
    [11] "http://purl.obolibrary.org/obo/CHEBI_25555"   "http://purl.obolibrary.org/obo/CHEBI_24859"  
    [13] "http://purl.obolibrary.org/obo/PR_000000001"  "http://purl.obolibrary.org/obo/CHEBI_37406"  
    [15] "http://purl.obolibrary.org/obo/CHEBI_39462"   "http://purl.obolibrary.org/obo/CHEBI_48339"  
    [17] "http://purl.obolibrary.org/obo/CHEBI_50122"   "http://purl.obolibrary.org/obo/BFO_0000023"  
    [19] "http://purl.obolibrary.org/obo/CHEBI_21653"   "http://purl.obolibrary.org/obo/DRON_00019228"
    [21] "http://purl.obolibrary.org/obo/DRON_00016952" "http://purl.obolibrary.org/obo/CHEBI_4562"   
    [23] "http://purl.obolibrary.org/obo/DRON_00013042" "http://purl.obolibrary.org/obo/DRON_00019607"
    [25] "http://purl.obolibrary.org/obo/CHEBI_26907"   "http://purl.obolibrary.org/obo/CHEBI_7591"   
    [27] "http://purl.obolibrary.org/obo/CHEBI_23238"   "http://purl.obolibrary.org/obo/CHEBI_57589"  
    [29] "http://purl.obolibrary.org/obo/DRON_00000029" "http://purl.obolibrary.org/obo/DRON_00750819"
    [31] "http://purl.obolibrary.org/obo/DRON_00750823" "http://purl.obolibrary.org/obo/CHEBI_50217"  
    

    
## List of ChEBI Ontology Files

All use base address `ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/`

`chebi_core.owl` and `chebi_lite.owl` include smaller subsets of synomyms, compared to `chebi.owl`


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

## Checking if any synonym annotations lack a supporting source axiom

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

## Creating the complete tabulation of ChEBI synonym sources

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
    }


## Abandoned attempt to limit DrOn label search to active ingredients, disregarding dosage

This constrained query (and even the ChEBI chemical entity filter) may be somewhat irrelevant, if the label matrices are going to be merged with the BioPortal mappings, and if BioPortal only maps ingredients. (DrOn doesn't model roles? and ChEBI doesn't model products?)

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

### to be removed

I looked for labeled chemical entities in ChEBI with the deprecation flag but didn't find any.

- `owl:deprecated`
- `obo:IAO_0000231`
    - 'has obsolescence reason'... always takes `obo:IAO_0000227` as it's object
- `obo:IAO_0100001`
     - 'term replaced by' (possibly many)
     
----
     
We could further condense the ChEBI synonyms by lowercasing. I don't think they can be filtered by language, but the non-English labels might be enriched for one of the synonym authorities. The distinct group_concat query wouldn't run for me on a 16 GB server, but it did run in < 1 minute on a 128 GB server.

ChEBI attributes `obo:CHEBI_46195`'s synonym 'Acetaminphen' to `KEGG COMPOUND`. "paracetamol" is asserted as the `rdfs:label` in `dron-chebi.owl`, but "Acetaminophen" is asserted as the label in `dron-ingredient.owl`. 

Because ChEBI classes can have many related synonyms, and because some of the sources may not be very useful for mapping to DrOn, some triage might be beneficial.
