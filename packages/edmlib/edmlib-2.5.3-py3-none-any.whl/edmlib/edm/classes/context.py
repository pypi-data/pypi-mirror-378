from typing import Any, List, Optional, Union, Self  # type: ignore
from pydantic import model_validator
from ..value_types import MixedValuesList, Lit, Ref
from ..base import EDM_BaseClass


class SKOS_Concept(EDM_BaseClass):
    """

    optional-properties: SKOS_broader, SKOS_narrower, SKOS_related, SKOS_broadMatch, SKOS_narrowMatch, SKOS_relatedMatch, SKOS_exactMatch, SKOS_closeMatch, SKOS_note, SKOS_notation, SKOS_inScheme

    recommended-properties: SKOS_prefLabel, SKOS_altLabel

    """

    skos_prefLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The preferred form of the name of the concept. Although the maximum number of occurren
	ces is set at 1, it can be interpreted as 1 per language tag. At least one skos:prefLa
	bel SHOULD be provided. Several prefLabels with languages tags are strongly recommende
	d for language variants and translations.This is a recommended property for this class
	.`<skos:prefLabel xml:lang="fr">Buccin</skos:prefLabel><skos:prefLabel xml:lang="de">Bu
	ccin</skos:prefLabel><skos:prefLabel xml:lang="nl">Buccin</skos:prefLabel>`For recommen
	dations on medata quality see Tier A-C requirements , more specifically Metadata Tier 
	B and Metadata Tier C
    """

    skos_altLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Alternative forms of the name of the concept. Recommended unless several prefLabel are
	 already given with different language tags (altLabel is not suitable for translations
	 of prefLabel).`<skos:altLabel xml:lang="en">Buccin</skos:altLabel>`This is a recommende
	d property for this class.
    """

    skos_broader: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a broader concept in the same thesaurus or controlled vocabulary.`<sk
	os:broader rdf:resource=“http://www.mimo-db.eu/InstrumentsKeywords/4369_1 ”/>`For recom
	mendations on medata quality see Tier A-C requirements , more specifically Metadata Ti
	er B and Metadata Tier C
    """

    skos_narrower: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a narrower concept.`<skos:narrower rdf:resource=“http://narrower.term
	/”/>`For recommendations on medata quality see Tier A-C requirements , more specificall
	y Metadata Tier B and Metadata Tier C
    """

    skos_related: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a related concept`<skos:related rdf:resource=“http://related.term/”/>`
	For recommendations on medata quality see Tier A-C requirements , more specifically Me
	tadata Tier B and Metadata Tier C
    """

    skos_broadMatch: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a broader, narrower or related matching concepts from other concept 
	schemes.`<skos:broadMatch rdf:resource=“http://broadMatch.term/”/><skos:narrowMatch rdf
	:resource=“http://narrowMatch.term/”/><skos:relatedMatch rdf:resource=“http://relatedM
	atch.term/”/>`
    """

    skos_narrowMatch: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a broader, narrower or related matching concepts from other concept 
	schemes.`<skos:broadMatch rdf:resource=“http://broadMatch.term/”/><skos:narrowMatch rdf
	:resource=“http://narrowMatch.term/”/><skos:relatedMatch rdf:resource=“http://relatedM
	atch.term/”/>`
    """

    skos_relatedMatch: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of a broader, narrower or related matching concepts from other concept 
	schemes.`<skos:broadMatch rdf:resource=“http://broadMatch.term/”/><skos:narrowMatch rdf
	:resource=“http://narrowMatch.term/”/><skos:relatedMatch rdf:resource=“http://relatedM
	atch.term/”/>`
    """

    skos_exactMatch: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of close or exactly matching concepts from other concept schemes.`<skos:
	exactMatch rdf:resource=“http://exactMatch.term/”/><skos:closeMatch rdf:resource=“http
	://closeMatch.term/”/>`For recommendations on medata quality see Tier A-C requirements 
	, more specifically Metadata Tier B and Metadata Tier C
    """

    skos_closeMatch: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of close or exactly matching concepts from other concept schemes.`<skos:
	exactMatch rdf:resource=“http://exactMatch.term/”/><skos:closeMatch rdf:resource=“http
	://closeMatch.term/”/>`For recommendations on medata quality see Tier A-C requirements 
	, more specifically Metadata Tier B and Metadata Tier C
    """

    skos_note: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Information relating to the concept.`<skos:note>The buccin is a visually distinctive tr
	ombone popularized in military bands in France between 1810–1845 which subsequently fa
	ded into obscurity.</skos:note>`For recommendations on medata quality see Tier A-C requ
	irements, more specifically Metadata Tier B and Metadata Tier C.
    """

    skos_notation: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The notation in which the concept is represented. This may not be words in natural lan
	guage for someknowledge organisation systems e.g. algebra`<skos:notation rdf:datatype=“
	http://www.w3.org/2001/XMLSchema#int”>123</skos:notation>`
    """

    skos_inScheme: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The URI of a concept scheme
    """

    @model_validator(mode="after")
    def validate_skos_pref_label(self) -> Self:
        pref_label: Optional[list[Lit]] = getattr(self, "skos_prefLabel")
        if pref_label and isinstance(pref_label, list) and len(pref_label) > 1:
            tag_set = {label.lang for label in pref_label if label.lang}
            assert (
                len(tag_set) == len(pref_label)
            ), f"If multiple pref_labels are provided, each must have a lang tag and the lang tags must be distinct"
        return self


class EDM_Agent(EDM_BaseClass):
    """

    optional-properties: SKOS_note, DC_date, DC_identifier, DCTERMS_hasPart, DCTERMS_isPartOf, EDM_begin, EDM_end, EDM_hasMet, EDM_isRelatedTo, FOAF_name, RDAGR2_biographicalInformation, RDAGR2_dateOfEstablishment, RDAGR2_dateOfTermination, RDAGR2_gender, RDAGR2_placeOfBirth, RDAGR2_placeOfDeath, RDAGR2_professionOrOccupation, OWL_sameAs

    recommended-properties: SKOS_prefLabel, SKOS_altLabel, RDAGR2_dateOfBirth, RDAGR2_dateOfDeath

    """

    skos_prefLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The preferred form of the name of the agent. Although the maximum number of occurrence
	s is set at 1, it can be interpreted as 1 per language tag. At least one skos:prefLabe
	l SHOULD be provided. Several prefLabels with languages tags are strongly recommended 
	for language variants and translations. This is a recommended property for this class.
	`<skos:prefLabel xml:lang=''fr''>Courtois neveu aîné</skos:prefLabel><skos:prefLabel xm
	l:lang=''en''>Courtois’eldest nephew</skos:prefLabel>` For recommendations on medata qu
	ality see Tier A-C requirements , more specifically Metadata Tier B and Metadata Tier 
	C
    """

    skos_altLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Alternative forms of the name of the agent. This is a recommended property for this cl
	ass.`<skos:altLabel xml:lang="en">Courtois</skos:altLabel><skos:altLabel xml:lang="fr">
	Augte. Courtois aîné</skos:altLabel>`
    """

    skos_note: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    A note about the agent e.g. biographical notes.`<skos:note> Courtois neveu aîné started
	 a company of the same name manufacturing brass instruments in Paris in 1803</skos:not
	e>`
    """

    dc_date: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A significant date associated with the Agent. Europeana recommends date conforming to 
	ISO 8601 starting with the year and with hyphens (YYYY-MM-DD).`<dc:date>1803</dc:date/>`
    """

    dc_identifier: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    An identifier of the agent.`<dc:identifier>http://viaf.org/viaf/96994048  </dc:identifi
	er>`
    """

    dcterms_hasPart: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to an Agent that is part of the Agent being described (e.g. a part of a corp
	oration).`<dcterms:hasPart rdf:resource=“http://identifier/partOfCorporation/”>`
    """

    dcterms_isPartOf: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to an agent that the described agent is part of.`<dcterms:isPartOf rdf:resour
	ce=“http://identifier/parentCorporation/”>`
    """

    edm_begin: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date the agent was born/established. Europeana recommends date conforming to ISO 8
	601 starting with the year and with hyphens (YYYY-MM-DD).`<edm:begin>1795</edm:begin>`Ge
	neric "begin" and "end" properties are being used to indicate start date and end date 
	generically for edm:Agent and edm:TimeSpan. For edm:Agent this can be interpreted andb
	irth and death dates.For recommendations on medata quality see Tier A-C requirements ,
	 more specifically Metadata Tier B and Metadata Tier C
    """

    edm_end: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    Generic "begin" and "end" properties are being used to indicate start date and end dat
	e generically for edm:Agent and edm:TimeSpan. For edm:Agent this can be interpreted an
	dbirth and death dates.For recommendations on medata quality see Tier A-C requirements
	 , more specifically Metadata Tier B and Metadata Tier C
    """

    edm_hasMet: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to another entity which the agent has “met” in a broad sense. For example a 
	reference to a Place class`<edm:hasMet rdf:resource=“http://sws.geonames.org/6620265/”>`
    """

    edm_isRelatedTo: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to other entities, particularly other agents, with whom the agent is related
	 in a generic sense.`<edm:isRelatedTo rdf:resource=“http://identifier/relatedAgent/”>`
    """

    foaf_name: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The name of the agent as a simple textual string.`<foaf:name>Auguste Courtois</foaf:nam
	e>`
    """

    rdagr2_biographicalInformation: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Information pertaining to the life or history of the agent.`<rdaGr2:biographicalInforma
	tion>Courtois neveu aîné started a company of the same name manufacturing brass instru
	ments in Paris in 1803</rdaGr2:biographicalInformation>`
    """

    rdagr2_dateOfBirth: Optional[Lit] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date the agent (person) was born. Europeana recommends date conforming to ISO 8601
	 starting with the year and with hyphens (YYYY-MM-DD). This is a recommended property 
	for this class.`<rdaGr2:dateOfBirth>1795</rdaGr2:dateOfBirth>`dates.For recommendations 
	on medata quality see Tier A-C requirements , more specifically Metadata Tier B and Me
	tadata Tier C
    """

    rdagr2_dateOfDeath: Optional[Lit] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date the agent (person) died. Europeana recommends date conforming to ISO 8601 sta
	rting with the year and with hyphens (YYYY‐MM-DD). This is a recommended property for 
	this class.`<rdaGr2:dateOfDeath>1895</rdaGr2:dateOfDeath>`For recommendations on medata 
	quality see Tier A-C requirements , more specifically Metadata Tier B and Metadata Tie
	r C
    """

    rdagr2_dateOfEstablishment: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date on which the agent (corporate body) was established or founded.`<rdaGr2:dateOf
	Establishment>1795</rdaGr2:dateOfEstablishment>`
    """

    rdagr2_dateOfTermination: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date on which the agent (corporate body) was terminated or dissolved.`<rdaGr2:dateO
	fTermination>1895</rdaGr2:dateOfTermination>`
    """

    rdagr2_gender: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The gender with which the agent identifies.`< rdaGr2:gender>Female</rdaGr2:gender>`
    """

    rdagr2_placeOfBirth: Optional[Union[Lit, Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Union[Lit, Ref]]
    
    Description: 

    The town, city, province, state, and/or country in which a person was born.`<rdaGr2:pla
	ceOfBirth>Lusaka, Northern Rhodesia</rdaGr2:placeOfBirth><rdaGr2:placeOfBirth rdf:reso
	urce=”http://sws.geonames.org/909137/”/>`For recommendations on medata quality see Tier
	 A-C requirements , more specifically Metadata Tier B and Metadata Tier C
    """

    rdagr2_placeOfDeath: Optional[Union[Lit, Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Union[Lit, Ref]]
    
    Description: 

    The town, city, province, state, and/or country in which a person died.`<rdaGr2:placeOf
	Death>London, United Kingdom</rdaGr2:placeOfDeath><rdaGr2:placeOfDeath rdf:resource=“h
	ttp://sws.geonames.org/2635167/”/>`For recommendations on medata quality see Tier A-C r
	equirements , more specifically Metadata Tier B and Metadata Tier C
    """

    rdagr2_professionOrOccupation: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The profession or occupation in which the agent works or has worked.`<rdaGr2:profession
	OrOccupation>Instrument Maker</rdaGr2:professionOrOccupation>`
    """

    owl_sameAs: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Another URI of the same agent.`<owl:sameAs rdf:resource=“http://www.identifier/sameReso
	urceElsewhere”/>`
    """

    @model_validator(mode="after")
    def validate_skos_pref_label(self) -> Self:
        pref_label: Optional[list[Lit]] = getattr(self, "skos_prefLabel")
        if pref_label and isinstance(pref_label, list) and len(pref_label) > 1:
            tag_set = {label.lang for label in pref_label if label.lang}
            assert (
                len(tag_set) == len(pref_label)
            ), f"If multiple pref_labels are provided, each must have a lang tag and the lang tags must be distinct"
        return self


class EDM_TimeSpan(EDM_BaseClass):
    """

    optional-properties: SKOS_altLabel, SKOS_note, DCTERMS_hasPart, DCTERMS_isPartOf, EDM_isNextInSequence, OWL_sameAs

    recommended-properties: SKOS_prefLabel, EDM_begin, EDM_end

    """

    skos_prefLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The preferred form of the name of the timespan or period. Although the maximum number 
	of occurrences is set at 1, it can be interpreted as 1 per language tag. At least one 
	skos:prefLabel SHOULD be provided. Several prefLabels with languages tags are strongly
	 recommended for language variants andtranslations.`<skos:prefLabel xml:lang=“en”>Roman
	 Empire</skos:prefLabel>`This is a recommended property for this class.
    """

    skos_altLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Alternative forms of the name of the timespan or period. `<skos:altLabel xml:lang=''fr'
	'>Empire romain (27 avant J.-­‐C.-­‐476 après J.-­C.)</skos:altLabel >`
    """

    skos_note: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Information relating to the timespan or period.`<skos:note>The Roman Empire (Latin: Imp
	erium Romanum) was the post-­Republican period of the ancient Roman civilization, char
	acterised by an autocratic form of government and large territorial holdings around th
	e Mediterranean in Europe, Africa, and Asia.</skos:note>`
    """

    dcterms_hasPart: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to a timespan which is part of the described timespan.
    """

    dcterms_isPartOf: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to a timespan of which the described timespan is a part.
    """

    edm_begin: Optional[Lit] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date the timespan started. Europeana recommends date conforming to ISO 8601 starti
	ng with the year and with hyphens (YYYY-­MM-DD). Providing edm:begin in combination wi
	th edm:end is recommended for this class.Example 1: `<edm:begin>-0026</edm:begin>`Exampl
	e:2: <edm:begin>27 BC</edm:begin>Note: '27 BC', while allowed, does not follow the abo
	ve recommendation.For recommendations on medata quality see Tier A-C requirements , mo
	re specifically Metadata Tier B and Metadata Tier C
    """

    edm_end: Optional[Lit] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The date the timespan finished. Europeana recommends date conforming to ISO 8601 start
	ing with the year and with hyphens (YYYY‐MM-DD). Providing edm:end in combination with
	 edm:begin is recommended for this class.`<edm:end>1770</edm:end>`For recommendations on
	 medata quality see Tier A-C requirements , more specifically Metadata Tier B and Meta
	data Tier C
    """

    edm_isNextInSequence: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Can be used to represent a sequence of Time periods. Use this for objects that are par
	t of a hierarchy or sequence to ensure correct display in the portal.`<edm:isNextInSequ
	ence rdf:resource=“http://semium.org/time/roman_republic”/>` (The Roman Empire was prec
	eded by the Roman Republic)
    """

    owl_sameAs: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The URI of a timespan`<owl:sameAs rdf:resource=“http://semium.org/time/roman_empire”/>`
    """

    @model_validator(mode="after")
    def validate_skos_pref_label(self) -> Self:
        pref_label: Optional[list[Lit]] = getattr(self, "skos_prefLabel")
        if pref_label and isinstance(pref_label, list) and len(pref_label) > 1:
            tag_set = {label.lang for label in pref_label if label.lang}
            assert (
                len(tag_set) == len(pref_label)
            ), f"If multiple pref_labels are provided, each must have a lang tag and the lang tags must be distinct"
        return self


class CC_License(EDM_BaseClass):
    """

    mandatory-properties: ODRL_inheritFrom

    optional-properties: CC_deprecatedOn

    """

    odrl_inheritFrom: Ref
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Ref
    
    Description: 

    ID of a base rights statement from which the described License is derived. This value 
	must come for alist of statements controlled by Europeana.`<odrl:inheritFrom rdf:resour
	ce=“http://rightsstatements.org/vocab/NoC-­NC/1.0/”/>`
    """

    cc_deprecatedOn: Any = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Any
    
    Description: 

    The date that the license expires, as it has been described, which implies among other
	 things the expiration of the restrictions specified by the license.`<cc:deprecatedOn r
	df:datatype=”http://www.w3.org/2001/XMLSchema#date”>2029‐06-­01</cc:deprecatedOn>` Note
	 this datatype is mandatory for cc:deprecatedOn.
    """


class EDM_Place(EDM_BaseClass):
    """

    optional-properties: WGS84_POS_lat, WGS84_POS_long, WGS84_POS_alt, SKOS_prefLabel, SKOS_altLabel, SKOS_note, DCTERMS_hasPart, DCTERMS_isPartOf, EDM_isNextInSequence, OWL_sameAs

    """

    wgs84_pos_lat: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The latitude of a spatial thing (decimal degrees). This is a recommended property for 
	this class.`<wgs84_pos:lat>51.5075</wgs84_pos:lat>`For recommendations on medata quality
	 see Tier A-C requirements , more specifically Metadata Tier B and Metadata Tier C 
    """

    wgs84_pos_long: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The longitude of a spatial thing (decimal degrees). This is a recommended property for
	 this class.`<wgs84_pos:long>-­‐0.1231</wgs84_pos:long>`For recommendations on medata qu
	ality see Tier A-C requirements, more specifically Metadata Tier B and Metadata Tier C
	 
    """

    wgs84_pos_alt: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    The altitude of a spatial thing (decimal metres above the reference)`<wgs84_pos:alt>21<
	/wgs84_pos:alt>`
    """

    skos_prefLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The preferred form of the name of the place. Although the maximum number of occurrence
	s is set at 1, it can be interpreted as 1 per language tag. At least one skos:prefLabe
	l SHOULD be provided. Several prefLabels with languages tags are strongly recommended 
	for language variants and translations.`<skos:prefLabel xml:lang="en">London</skos:pref
	Label>`For recommendations on medata quality see Tier A-C requirements , more specifica
	lly Metadata Tier B and Metadata Tier C 
    """

    skos_altLabel: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Alternative forms of the name of the place.`<skos:altLabel xml:lang="en">Greater London
	</skos:altLabel>`
    """

    skos_note: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Information relating to the place.`<skos:note xml:lang="en">Pop. 21m</skos:note>`
    """

    dcterms_hasPart: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to a place that is part of the place being described.`<dcterms:hasPart rdf:re
	source=“http://sws.geonames.org/2643741/”/>` (City of London)
    """

    dcterms_isPartOf: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Reference to a place that the described place is part of.`<dcterms:isPartOf rdf:resourc
	e=“http://sws.geonames.org/2635167/”/>` (United Kingdom)
    """

    edm_isNextInSequence: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    Can be used to represent a sequence of Place entities over time e.g. the historical la
	yers of the city of Troy. Use this for objects that are part of a hierarchy or sequenc
	e to ensure correct display in the portal.
    """

    owl_sameAs: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    URI of a Place`<owl:sameAs rdf:resource=“http://sws.geonames.org/2635167/”/>`(London)
    """

    @model_validator(mode="after")
    def validate_skos_pref_label(self) -> Self:
        pref_label: Optional[list[Lit]] = getattr(self, "skos_prefLabel")
        if pref_label and isinstance(pref_label, list) and len(pref_label) > 1:
            tag_set = {label.lang for label in pref_label if label.lang}
            assert (
                len(tag_set) == len(pref_label)
            ), f"If multiple pref_labels are provided, each must have a lang tag and the lang tags must be distinct"
        return self
