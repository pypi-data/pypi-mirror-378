from typing import List, Optional, Union  # type: ignore

# from rdflib import Literal, URIRef
from typing_extensions import Self
from pydantic import model_validator
from edmlib.edm.value_types import MixedValuesList, Ref, Lit
from edmlib.edm.base import EDM_BaseClass
from edmlib.edm.validation.edm_rights import assert_valid_statement, normalize_statement


class ORE_Aggregation(EDM_BaseClass):
    """ORE Aggregation

    mandatory-properties: EDM_aggregatedCHO, EDM_dataProvider, EDM_isShownAt, EDM_isShownBy, EDM_provider, EDM_rights

    optional-properties: EDM_hasView, DC_rights, EDM_ugc

    recommended-properties: EDM_object, EDM_intermediateProvider

    """

    edm_aggregatedCHO: Ref
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Ref
    
    Description: 

    The identifier of the source object e.g. the Mona Lisa itself. This could be a full li
	nked open data URI or an internal identifier. `<edm:aggregatedCHO rdf:resource=“#UEDIN:
	214”/>`
    """

    edm_dataProvider: Union[Lit, Ref]
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Union[Lit, Ref]
    
    Description: 

    The name or identifier of the data provider of the object (i.e. the organisation provi
	ding data to an aggregator). Identifiers will not be available until Europeana has imp
	lemented its Organization profile.  In the case of the data provider Zuidwestbrabants 
	Museum, which delivers data through Erfgoedplus.be to LoCloud, the properties would lo
	ok like this: `<edm:dataProvider>Zuidwestbrabants  Museum</edm:dataProvider> <edm:inter
	mediateProvider>Erfgoedplus.be</edm:intermediateProvider> <edm:provider>LoCloud</edm:p
	rovider>`
    """

    edm_provider: Union[Lit, Ref]
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Union[Lit, Ref]
    
    Description: 

    The name or identifier of the provider of the object (i.e. the organisation providing 
	data directly to Europeana). Identifiers will not be available until Europeana has imp
	lemented its Organization profile.  In the case of the provider LoCloud, which collect
	s data from the data provider Zuidwestbrabants Museum through Erfgoedplus.be, the prop
	erties would look like this: `<edm:dataProvider>Zuidwestbrabants Museum</edm:dataProvid
	er> <edm:intermediateProvider>Erfgoedplus.be</edm:intermediateProvider><edm:provider>L
	oCloud</edm:provider>`
    """

    edm_rights: Ref
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Ref
    
    Description: 

    This is a mandatory property and the value given here should be the rights statement t
	hat applies to the digital representation as given (for example) in edm:object or edm:
	isShownAt/By, when these resources are not provided with their own edm:rights (see edm
	:rights documentation). The value for the rights statement in this element must be a U
	RI from the list of available values. Note: rights statements must be exactly as speci
	fied there, which means they must start with http and not https. (For assesing rights 
	imformation check https://pro.europeana.eu/page/available-rights-statements ) The righ
	ts statement given in this property will also by default apply to the previews used in
	 the portal and will support portal search and display functionality.  Where there are
	 several web resources attached to one edm:ProvidedCHO the rights statement given here
	 will be regarded as the “reference” value for all the web resources. Therefore a suit
	able value should be chosen with care if the rights statements vary between different 
	resources. In fact in such cases Europeana encourages the provision of separate rights
	 statements for each individual web resource. Please note that the object page on http
	://europeana.eu   displays the rights of the digital representation selected in the vi
	ewer, which is found in the edm:rights of the WebResource that corresponds to the sele
	cted edm:isShownBy or edm:hasView. If there is no such edm:isShownBy or edm:hasView re
	presentation available, or if there is one but there is no specific edm:rights attache
	d to it, then by default the page displays the edm:rights attached to the ore:Aggregat
	ion.For example, a low­‐resolution of a JPEG file could be CC‐BY, while the high resol
	ution version or a video showing the object would be CC-­BY-­NC. In such cases the rig
	hts statements given for the individual web resources would ‘override’ the one specifi
	ed at the ore:Aggregation level. Any other associated web resources would still be gov
	erned by the edm:rights of the ore:Aggregation.   `<edm:rights rdf:resource=“http://cre
	ativecommons.org/publicdomain/mark/1.0/”/> <edm:rights rdf:resource=“http://rightsstat
	ements.org/vocab/InC/1.0/”/>`  Or create a reference to an instance of the cc:License c
	lass where additional details of the rights can be provided (such as an expiry date fo
	r the restrictions): http://rightsstatements.org/vocab/NoC-­NC/1.0/ or `<edm:rights rdf
	:resource="#statement_3000095353971"/>`
    """

    edm_hasView: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The URL of a web resource which is a digital representation of the CHO. This may be th
	e source object itself in the case of a born digital cultural heritage object. edm:has
	View should only be used where there are several views of the CHO and one (or both) of
	 the mandatory edm:isShownAt or edm:isShownBy properties have already been used. It is
	 for cases where one CHO has several views of the same object. (e.g. a shoe and a deta
	il of the label of the shoe)  `<edm:hasView rdf:resource="http://www.mimo‐db.eu/media/U
	EDIN/VIDEO/0032195v.mpg"/> <edm:hasView rdf:resource="http://www.mimo-­db.eu/media/UED
	IN/AUDIO/0032195s.mp3"/>`
    """

    edm_isShownAt: Optional[Ref] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Ref]
    
    Description: 

    The URL of a web view of the object in full information context. An edm:isShownAt must
	 be provided. If there is no edm:isShownAt for an object, there must be a edm:isShownB
	y. If both are available, provide both. The use of edm:isShownBy is preferred. Providi
	ng an edm:isShownAt is strongly recommended in all cases.`<edm:isShownAt rdf:resource="
	http://www.mimo-­‐db.eu/UEDIN/214"/>`
    """

    edm_isShownBy: Optional[Ref] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Ref]
    
    Description: 

    The URL of a web view of the object. An edm:isShownBy must be provided. If there is no
	 edm:isShownBy for an object, there must be a edm:isShownAt. The use of edm:isShownBy 
	is preferred. Europeana generates previews for any direct link to an image file. See E
	uropeana Media Policy or information regarding the specifications of previews. `<edm:is
	ShownBy rdf:resource="http://www.mimo‐db.eu/media/UEDIN/IMAGE/0032195c.jpg"/>`
    """

    edm_object: Optional[Ref] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Ref]
    
    Description: 

    The URL of a representation of the CHO which will be used for generating previews for 
	use in the Europeana portal. This may be the same URL as edm:isShownBy.See Europeana M
	edia Policy for information regarding the specifications of previews. This must be an 
	image, even if it is for a sound object. `<edm:object rdf:resource="http://www.mimo-‐db
	.eu/media/UEDIN/IMAGE/0032195c.jpg"/>`In accordance with Europeana's 2023 data publicat
	ion approach, objects with edm:type=IMAGE that have no edm:isShownBy nor edm:object wi
	ll not be published in Europeana. (See also ContentTier 1: Image type )
    """

    dc_rights: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Ideally this should be applied to the edm:WebResource or the edm:ProvidedCHO. It is in
	cluded here for the conversion of data from ESE where it is not known which object the
	 rights apply to.
    """

    edm_ugc: Optional[Lit] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Lit]
    
    Description: 

    This is a mandatory property for objects that are user generated or user created that 
	have been collected by crowdsourcing or project activity. The property is used to iden
	tify such content and can only take the value “true” (lower case). `<edm:ugc>true</edm:
	ugc>`
    """

    edm_intermediateProvider: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The name or identifier of the intermediate organization that selects, collates, or cur
	ates data from a Data Provider that is then aggregated by a Provider from which Europe
	ana harvests. The Intermediate Provider must be distinct from both the Data Provider a
	nd the Provider in the data supply chain. Identifiers will not be available until Euro
	peana has implemented its Organization profile. In the case of the Erfgoedplus.be, whi
	ch collects data from Zuidwestbrabants Museum and provides it to LoCloud, the properti
	es would look like this: `<edm:dataProvider>Zuidwestbrabants Museum</edm:dataProvider> 
	<edm:provider>LoCloud</edm:provider> <edm:intermediateProvider>Erfgoedplus.be</edm:int
	ermediateProvider>`
    """

    @model_validator(mode="after")
    def validate_conditional_attributes(self) -> Self:
        assert (
            self.edm_isShownAt
        ), f"Aggregation must have edm_isShownAt, got: {self.edm_isShownAt}."
        assert (
            self.edm_isShownBy
        ), f"Aggregation must have edm_isShownBy, got: {self.edm_isShownBy}."

        assert self.edm_rights, "Missing edm-rights"

        assert self.edm_rights.value, "Missing value for edm-rights"

        self.edm_rights.value = normalize_statement(self.edm_rights.value)
        assert_valid_statement(self.edm_rights.value)

        return self


class EDM_ProvidedCHO(EDM_BaseClass):
    """

    mandatory-properties: DC_description, DC_language, DC_subject, DC_title, DC_type, DCTERMS_spatial, DCTERMS_temporal, EDM_type

    optional-properties: DC_coverage, DC_format, DC_relation, DC_rights, DCTERMS_conformsTo, DCTERMS_extent, DCTERMS_hasFormat, DCTERMS_hasPart, DCTERMS_hasVersion, DCTERMS_isFormatOf, DCTERMS_isReferencedBy, DCTERMS_isReplacedBy, DCTERMS_isRequiredBy, DCTERMS_isVersionOf, DCTERMS_medium, DCTERMS_provenance, DCTERMS_references, DCTERMS_replaces, DCTERMS_requires, DCTERMS_tableOfContents , EDM_currentLocation, EDM_hasMet, EDM_hasType, EDM_incorporates, EDM_isDerivativeOf, EDM_isRelatedTo, EDM_isRepresentationOf, EDM_isSimilarTo, EDM_isSuccessorOf, EDM_realizes, OWL_sameAs

    recommended-properties: DC_contributor, DC_creator, DC_date, DC_identifier, DC_publisher, DC_source, DCTERMS_alternative, DCTERMS_created, DCTERMS_isPartOf, DCTERMS_issued, EDM_IsNextInSequence

    """

    edm_type: Lit
    """
    Mandate: 
    mandatory

    Cardinality: 
    exactly_one

    Value-Type:
    Lit
    
    Description: 

    The value must be one of the types accepted by Europeana as it will support portal fun
	ctionality: TEXT, VIDEO, SOUND, IMAGE, 3D. (For 3D, when applicable, use the value “3D
	‐PDF” in dc:format ) `<edm:type>IMAGE</edm:type>` (upper-­case & case sensitive) `<edm:ty
	pe>3D</edm:type>` (upper-­case & case sensitive)
    """

    dc_contributor: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for contributors to the CHO. If possible supply the identifier of the contributor 
	from an authority source. Providers with richer role terms can elect to map a subset t
	o dc:contributor and others to dc:creator. Repeat for multiple contributors. `<dc:contr
	ibutor>Maria Callas</dc:contributor>` or create a reference to an instance of the Agent
	 class `<dc:contributor rdf:resource=“http://www.example.com/MariaCallas”>`For recommend
	ations on medata quality see Tier A-C requirements , 
    """

    dc_coverage: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The spatial or temporal topic of the CHO. Use the more precise dcterms:spatial or dcte
	rms:temporal properties if the data will support it. `<dc:coverage>1995-­1996</dc:cover
	age>` or `<dc:coverage>Berlin</dc:coverage>` or create a reference to an instance of a co
	ntextual class, for example, a Place class `<dc:coverage rdf:resource=“https://sws.geon
	ames.org/2950159/ ”/>`
    """

    dc_creator: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    For the creator of the CHO. If possible supply the identifier of the creator from an a
	uthority source. Repeat for multiple creators.  `<dc:creator>Shakespeare, William</dc:c
	reator>` or create a reference to an instance of the Agent class `<dc:creator rdf:resour
	ce=“http://viaf.org/viaf/96994048”/>`For recommendations on medata quality see Tier A-C
	 requirements . 
    """

    dc_date: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for a significant date in the life of the CHO.  Europeana recommends date conformi
	ng to ISO 8601 starting with the year and with hyphens (YYYY-­MM-DD). NB: other EDM el
	ements are relevant for expressing dates of different events in the life of the CHO: d
	cterms:temporal, dcterms:created and dcterms:issued. Be careful and choose the most ap
	propriate one! `<dc:date>Early 20th century</dc:date>` or `<dc:date>1919</dc:date>` or cre
	ate a reference to an instance of the TimeSpan class `<dc:date rdf:resource=“http://sem
	ium.org/time/19xx_1_third”/>`
    """

    dc_description: Optional[MixedValuesList] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A description of the CHO. If there is no dc:description for an object, there must be a
	 dc:title. If both are  available, provide both. `<dc:description>Illustrated guide to 
	airport markings and lighting signals, with particular reference to SMGCS  (Surface Mo
	vement Guidance and Control System) for airports with low visibility conditions.</dc:d
	escription>`
    """

    dc_format: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for the terms generally applied to indicate the format of the cultural heritage ob
	ject or the file format of a born digital object. Use the value “3D-­PDF” if appropria
	te. `<dc:format>paper</dc:format>`For recommendations on medata quality see Tier A-C req
	uirements . 
    """

    dc_identifier: List[Lit]
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    An identifier of the original CHO. `<dc:identifier>RP-­T-­1952-­380</dc:identifier>`
    """

    dc_language: Optional[List[Lit]] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    The language of text CHOs and also for other types of CHO if there is a language aspec
	t. Mandatory for TEXT objects, strongly recommended for other object types with a lang
	uage element. Best practice is to use ISO 639 two- or three-letter primary language ta
	gs.Repeat for multiple languages. We also recommend the use of the ISO 639-­2 code for
	 no linguistic content (ZXX).
    """

    dc_publisher: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The name of the publisher of the CHO. If possible supply the identifier of the publish
	er from an authority source. `<dc:publisher>Oxford University Press</dc:publisher>` or c
	reate a reference to an instance of the Agent class `<dc:publisher rdf:resource=“http:/
	/www.oup.com/”/>`For recommendations on medata quality see Tier A-C requirements . 
    """

    dc_relation: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The name or identifier of a related resource, generally used for other related CHOs. C
	f edm:isRelatedTo. `<dc:relation>maps.crace.1/33</dc:relation>` (Shelf mark) Or to provi
	de a link to another object: `<dc:relation rdf:resource=“http://www.identifier/relatedO
	bject”/>`
    """

    dc_rights: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use to give the name of the rights holder of the CHO if possible or for more general r
	ights information. (Note that the controlled edm:rights property relates to the digita
	l objects and applies to the edm:WebResource and/or edm:Aggregation). `<dc:rights>Copyr
	ight © British Library Board</dc:rights>`
    """

    dc_source: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A related resource from which the described resource is derived in whole or in part i.
	e. the source of the original CHO.  (Not the name of the content holder: for this see 
	edm:dataProvider.) `<dc:source>Security Magazine pp 3-12</dc:source>`
    """

    dc_subject: Optional[MixedValuesList] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The subject of the CHO.One of dc:subject or dc:type or dcterms:spatial or dcterms:temp
	oral must be  provided; if more than one of these properties is available, please prov
	ide them all. High-­level dc:subject  values like 'archaeology' are allowed, especiall
	y when there is no other subject that can be easily filled in. `<dc:subject>archeology<
	/dc:subject>`or create a reference to an instance of the Concept class `<skos:Concept rd
	f:about="http://semantics.gr/authorities/ekt-unesco/560215094">   <skos:prefLabel xml:
	lang="el">Αρχαιολογία</skos:prefLabel>   <skos:prefLabel xml:lang="en">Archaeology</sk
	os:prefLabel></skos:Concept>`For recommendations on medata quality see Tier A-C require
	ments . 
    """

    dc_title: Optional[List[Lit]] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    A name given to the CHO. dc:title should be present; but if there is no dc:title avail
	able, it is acceptable to have dc:description instead. dc:title and dc:description sho
	uld be distinct. Exact translations of the title can be  provided using appropriate xm
	l language attributes. `<dc:title xml:lang=“en”>Eight Weeks</dc:title> <dc:title xml:la
	ng=“it”>Ocho semanas</ dc:title>`
    """

    dc_type: Optional[MixedValuesList] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The nature or genre of the CHO. Ideally the term(s) will be taken from a controlled vo
	cabulary. One of dc:type or dc:subject or dcterms:spatial or dcterms:temporal must be 
	provided; if more than one of these properties is available, please provide them all. 
	dc:type should not be (strictly) identical to edm:type. `<dc:type>Book</dc:type>` or `<dc
	:type>trombone</dc:type>` or create a reference to an instance of the Concept class `<dc
	:type rdf:resource=“http://www.mimo-­db.eu/HornbostelAndSachs/356/”>`For recommendation
	s on medata quality see Tier A-C requirements . 
    """

    dcterms_alternative: Optional[List[Lit]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    Any alternative title of the CHO including abbreviations or translations that may not 
	be exact. `<dcterms:alternativexml:lang=“en”>Eight weeks: a novel</dcterms:alternative>`
    """

    dcterms_conformsTo: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    An established standard to which the CHO conforms. `<dcterms:conformsTo>W3C WCAG 2.0</d
	cterms:conformsTo>` (conforms to web content accessibility guidelines). Or link to the 
	resource `<dcterms:conformsTo rdf:resource=“http://www.w3.org/TR/WCAG/”/>`
    """

    dcterms_created: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The date of creation of the CHO. Europeana recommends date conforming to ISO 8601 star
	ting with the year and with hyphens (YYYY-­MM-DD). NB: other EDM elements are relevant
	 for expressing dates of different events in the life of the CHO: dc:date, dcterms:tem
	poral and dcterms:issued. Be careful and choose the most appropriate one! `<dcterms:cre
	ated>Mid 16th century</dcterms:created>` or `<dcterms:created>1584</dcterms:created>` or 
	create a reference to an instance of the TimeSpan class`<dcterms:created rdf:resource=“
	http://semium.org/time/15xx_3_third”/>`For recommendations on medata quality see Tier A
	-C requirements . 
    """

    dcterms_extent: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The size or duration of the CHO. `<dcterms:extent>13 cm</dcterms:extent>` (the width of 
	an original object). `<dcterms:extent>34 minutes</dcterms:extent>` (the duration of an a
	udio file)
    """

    dcterms_hasFormat: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A resource related to the CHO that is substantially the same as the CHO but in another
	 format. `<dcterms:hasFormat>http://upload.wikimedia.org/wikipedia/en/f/f3/Europeana_lo
	go.png</dcterms:hasFormat>` for a png image file of the described tiff resource Or as a
	 link to a resource `<dcterms:hasFormat rdf:resource=“http://upload.wikimedia.org/wikip
	edia/en/f/f3/Europeana_logo.png’’/>`
    """

    dcterms_hasPart: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A resource that is included either physically or logically in the CHO. It is possible 
	to use either dcterms:isPartOf or dcterms:hasPart to express relation between objects 
	in a hierarchy. However in many cases (especially when a parent object has many childr
	en) it is preferable to use dcterms:isPartOf. `<dcterms:hasPart>Vol.2. Issue 1</dcterms
	:hasPart>`
    """

    dcterms_hasVersion: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another, later resource that is a version, edition or adaptation of the CHO demonstrat
	ing substantive changes in content rather than format. `<dcterms:hasVersion>The Sorcere
	r’s Apprentice (translation by Edwin Zeydel, 1955)</dcterms:hasVersion>` In this exampl
	e the 1955 translation is a version of the described resource.
    """

    dcterms_isFormatOf: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another resource that is substantially the same as the CHO but in another format. `<dct
	erms:isFormatOf>Europeana_logo.tiff</dcterms:isFormatOf>` where the resource being desc
	ribed is a png image file
    """

    dcterms_isPartOf: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A resource in which the CHO is physically or logically included. This property can be 
	used for objects that are part of a hierarchy and will be used to support an appropria
	te display in the portal. For that purpose it will be necessary to supply a reference 
	as the value. See the Task Force report on representing hierarchical entities.  It is 
	possible to use either dcterms:isPartOf or dcterms:hasPart to express relation between
	 objects in a hierarchy. However in many cases (especially when a parent object has ma
	ny children) it is preferable to use dcterms:isPartOf. `<dcterms:isPartOf>Crace Collect
	ion of Maps of London</dcterms:isPartOf>`
    """

    dcterms_isReferencedBy: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another resource that references, cites or otherwise points to the CHO. `<dcterms:isRef
	erencedBy>Till, Nicholas (1994) Mozart and the Enlightenment: Truth, Virtue and Beauty
	 in Mozart’s Operas, W. W. Norton & Company</dcterms:isReferencedBy>`
    """

    dcterms_isReplacedBy: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another resource that supplants , displaces, or supersedes the CHO. `<dcterms:isReplace
	dBy>http://dublincore.org/about/2009/01/05/bylaws/</dcterms:isReplacedBy>` where the re
	source described is an older version (http://dublincore.org/about/2006/01/01/bylaws/) 
	or link `<dcterms:isReplacedBy rdf:resource=“http://dublincore.org/about/2009/01/05/byl
	aws/”/>`
    """

    dcterms_isRequiredBy: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another related resource that requires the CHO to support its function, delivery or co
	herence `<isRequiredBy>http://www.myslides.com/myslideshow.ppt</isRequiredBy>` where the
	 image being described is required for an online slideshow.
    """

    dcterms_issued: Optional[MixedValuesList] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Date of formal issuance or publication of the CHO. Europeana recommends date conformin
	g to ISO 8601  starting with the year and with hyphens (YYYY-­MM-DD). NB: other EDM el
	ements are relevant for expressing dates of different events in the life of the CHO: d
	c:date, dcterms:temporal and dcterms:created. Be careful and choose the most appropria
	te one! `<dcterms:issued>1993</dcterms:issued>` or create a reference to an instance of 
	the TimeSpan class `<dcterms:issued rdf:resource=“http://semium.org/time/17xx_3_third”/
	>` (late 18th century)For recommendations on medata quality see Tier A-C requirements .
	 
    """

    dcterms_isVersionOf: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another, earlier resource of which the CHO is a version, edition or adaptation, demons
	trating substantive changes in content rather than format. `<dcterms:isVersionOf>The So
	rcerer’s Apprentice<dcterms:isVersionOf>`In this example The Sorcerer’s Apprentice (tra
	nslation by Edwin Zeydel, 1955) is the resource being described.
    """

    dcterms_medium: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The material or physical carrier of the CHO.  `<dcterms:medium>metal</dcterms:medium>`Fo
	r recommendations on medata quality see Tier A-C requirements . 
    """

    dcterms_provenance: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A statement of changes in ownership and custody of the CHO since its creation. Signifi
	cant for authenticity, integrity and interpretation. `<dcterms:provenance>Donated to Th
	e National Library in 1965</dcterms:provenance>`
    """

    dcterms_references: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Other resources referenced, cited or otherwise pointed to by the CHO. `<dcterms:referen
	ces>Honderd jaar Noorse schilderkunst </dcterms:references>`
    """

    dcterms_replaces: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A related resource that is supplanted, displaced, or superseded by the CHO. `<dcterms:r
	eplaces>http://dublincore.org/about/2006/01/01/bylaws/</dcterms:replaces>` where the re
	source described is a newer version (http://dublincore.org/about/2009/01/05/bylaws/) o
	r link to resource `<dcterms:replaces rdf:resource=“http://dublincore.org/about/2006/01
	/01/bylaws/”/>`
    """

    dcterms_requires: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another resource that is required by the described resource to support its function, d
	elivery or coherence. `<dcterms:requires>http://ads.ahds.ac.uk/project/userinfo/css/old
	browsers.css </dcterms:requires>` where the resource described is an HTML file at http:
	//ads.ahds.ac.uk/project/userinfo/digitalTextArchiving.html 
    """

    dcterms_spatial: Optional[MixedValuesList] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Spatial characteristics of the CHO. i.e. what the CHO represents or depicts in terms o
	f space (e.g. a location, coordinate or place). Either dcterms:spatial or dc:type or d
	c:subject or dcterms:temporal must be provided; if more than one of these properties i
	s available, please provide them all. dcterms:spatial is used to record the place depi
	cted in the CHO and other locations associated with it as opposed to edm:currentLocati
	on which is used only to record the place where the CHO is currently held (e.g. a muse
	um or gallery). Be careful to choose the most appropriate one! `<dcterms:spatial>Portug
	al</dcterms:spatial>` or create a reference to an instance of the Place class `<dcterms:
	spatial rdf:resource=“https://sws.geonames.org/2264397/ ”/>`For recommendations on meda
	ta quality see Tier A-C requirements . 
    """

    dcterms_tableOfContents: Optional[List[Lit]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Lit]]
    
    Description: 

    A list of sub‐units of the CHO.`<dcterms:tableOfContents>Chapter 1. Introduction, Chapt
	er 2. History </dcterms:tableOfContents>`
    """

    dcterms_temporal: Optional[MixedValuesList] = None
    """
    Mandate: 
    mandatory

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Temporal characteristics of the CHO. i.e. what the CHO is about or depicts in terms of
	 time (e.g. a period, date or date range.) Either dcterms:temporal or dc:type or dc:su
	bject or dcterms:spatial must be provided; if more than one of these properties is ava
	ilable, please provide them all. Europeana recommends date conforming to ISO 8601 star
	ting with the year and with hyphens (YYYY-MM-DD). NB: other EDM elements are relevant 
	for expressing dates of different events in the life of the CHO: dc:date, dcterms:crea
	ted and dcterms:issued. Be careful and choose the most appropriate one! `<dcterms:tempo
	ral>Roman Empire</dcterms:temporal>` or create a reference to an instance of the TimeSp
	an class `<dcterms:temporal rdf:resource=“http://semium.org/time/roman_empire”/>`For rec
	ommendations on medata quality see Tier A-C requirements . 
    """

    edm_currentLocation: Optional[Union[Lit, Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Union[Lit, Ref]]
    
    Description: 

    The geographic location whose boundaries presently include the CHO. This location must
	 have a position within an established positioning system: a location with coordinates
	 or address or inside another location that has a position, such as a room within a (m
	useum) building. Ideally this position should be provided with the value of the proper
	ty, either by using a reference (to a Place entity) that has coordinates or an address
	 attribute, or as a simple Lit. edm:currentLocation is used only to record the pla
	ce where the CHO is currently held (e.g. a museum or gallery)dcterms:spatial is used t
	o record the place depicted in the CHO and other locations associated with itBe carefu
	l to choose the most appropriate one!`<edm:currentLocation rdf:resource=“https://sws.ge
	onames.org/2950159/”>` (Identifier for Berlin)For recommendations on medata quality see
	 Tier A-C requirements . 
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

    The identifier of an agent, a place, a time period or any other identifiable entity th
	at the CHO may have “met” in its life. `<edm:hasMet rdf:resource=“http://viaf.org/viaf/
	96994048/”> (Identifier for William Shakespeare) <edm:hasMet rdf:resource=“https://sws
	.geonames.org/6620265/ ”>` (location identifier for Shakespeare’s Globe theatre.)For re
	commendations on medata quality see Tier A-C requirements . 
    """

    edm_hasType: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The identifier of a concept, or a word or phrase from a controlled vocabulary (thesaur
	us etc) giving the type of the CHO. E.g. Painting from the AAT thesaurus. This propert
	y can be seen as a super-­property of e.g. dc:format or dc:type to support “What” ques
	tions. `<edm:hasType>Painting</edm:hasType>`
    """

    edm_incorporates: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of another resource that is incorporated in the described CHO. E.g. the
	 movie “A Clockwork Orange” incorporates Rossini’s La Gazza Ladra” in its soundtrack. 
	`<edm:incorporates rdf:resource=“http://www.identifier/IncorporatedResource/“>`
    """

    edm_isDerivativeOf: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of another resource from which the described CHO has been derived. E.g.
	 the identifier of Moby Dick when the Italian translation is the described CHO. `<edm:i
	sDerivativeOf rdf:resource=“http://www.identifier/SourceResource/”>`
    """

    edm_isNextInSequence: Optional[List[Ref]] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of the preceding object where both objects are part of the same overall
	 resource. Use this for objects that are part of a hierarchy or sequence to ensure cor
	rect display in the portal. `<edm:isNextInSequence rdf:resource=“http://www.identifier/
	PrecedingResource”/>`
    """

    edm_isRelatedTo: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The identifier or name of a concept or other resource to which the described CHO is re
	lated. E.g. Moby Dick is related to XIX Century literature. Cf dc:relation. `<edm:isRel
	atedTo>Literature</edm:isRelatedTo>` Or link to resource `<edm:isRelatedTo rdf:resource=
	“http://www.eionet.europa.eu/gemet/concept?cp=4850/”>`
    """

    edm_isRepresentationOf: Optional[Ref] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Ref]
    
    Description: 

    The identifier of another object of which the described CHO is a representation. E.g. 
	the identifier of the statue when the CHO being described is a painting of that statue
	. `<edm:isRepresentativeOf rdf:resource=“http://www.identifier/RepresentedResource/”>`
    """

    edm_isSimilarTo: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of another resource to which the described CHO is similar. `<edm:isSimil
	arTo rdf:resource=“http://www.identifier/SimilarResource”/>`
    """

    edm_isSuccessorOf: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

     The identifier of a resource to which the described CHO is a successor. E.g. “The Two
	 Towers” is a successor of “Fellowship of the Ring”. `<edm:isSuccessorOf rdf:resource=“
	http://dbpedia.org/resource/The_Fellowship_of_the_Ring/”>`
    """

    edm_realizes: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    If the CHO described is of type edm:PhysicalThing it may realize an information object
	. E.g. a copy of the Gutenberg publication realizes the Bible.
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

    Use to point to your own (linked data) representation of the object, if you have already minted a URI identifier for it. It is also possible to provide URIs minted by third-parties for the object. `<owl:sameAs rdf:resource=“http://www.identifier/SameResourceElsewhere/”>`
    """

    @model_validator(mode="after")
    def validate_dependent_edm(self) -> Self:
        assert (
            self.dc_type
            or self.dc_subject
            or self.dcterms_temporal
            or self.dcterms_spatial
        ), f"ProvidedCHO must have one of [dc_type, dc_subject, dcterms_termporal, dctermrs_spatial], got {self.dc_type=}, {self.dc_subject=}, {self.dcterms_spatial=}, {self.dcterms_temporal=}."
        assert (
            self.dc_title or self.dc_description
        ), f"ProvidedCHO must have either a dc_title or dc_description, got {self.dc_title=}, {self.dc_description=}."
        if self.edm_type.value == "TEXT":
            assert (
                self.dc_language
            ), f"ProvidedCHO must have dc_language if it is of edm_type 'TEXT', got {self.edm_type=}, {self.dc_language}."
        assert (
            not self.edm_type.lang
        ), f"Property edm_type is not allowed to have a lang-tag"

        return self


class EDM_WebResource(EDM_BaseClass):
    """

    optional-properties: DC_creator, DC_description, DC_format, DC_rights, DC_source, DC_type, DCTERMS_conformsTo, DCTERMS_created, DCTERMS_extent, DCTERMS_hasPart, DCTERMS_isFormatOf, DCTERMS_isPartOf, DCTERMS_isReferencedBy, DCTERMS_issued, EDM_isNextInSequence, OWL_sameAs, SVCS_has_service, DCTERMS_IsReferencedBy

    recommended-properties: EDM_rights

    """

    dc_creator: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    For the creator of the web resource. If possible supply the identifier of the creator 
	from an authority source. Repeat for multiple creators. `<dc:creator xml:lang=“es”>Bibl
	icoteca Nacional de España</dc:creator>` or create a reference to an instance of the Ag
	ent class `<dc:creator rdf:resource=“http://viaf.org/viaf/147143794/”/>`
    """

    dc_description: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for an account or description of this digital representation `<dc:description>Perfo
	rmance with Buccin trombone</dc:description>`
    """

    dc_format: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for the format of this digital representation. (Use the value “3D‐PDF” if appropri
	ate.)`<dc:format>image/jpeg</dc:format>`
    """

    dc_rights: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Use for the name of the rights holder of this digital representation if possible or fo
	r more general rights information. Note the difference between this property and the m
	andatory, controlled edm:rights property below. `<dc:rights> Copyright © British Librar
	y Board</dc:rights>`
    """

    dc_source: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A related resource from which the Web resource is derived in whole or in part. `<dc:sou
	rce>The name of the source video tape <dc:source>`
    """

    dc_type: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The nature or genre of the digital representation. Ideally the term(s) will be taken f
	rom a controlled vocabulary.dc:type should not be (strictly) identical to edm:type. `<d
	c:type>video</dc:type>` or create a reference to an instance of the Concept class `<dc:t
	ype rdf:about= “http://schema.org/VideoObject” >`
    """

    dcterms_conformsTo: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    An established standard to which the web resource conforms. `<dcterms:conformsTo>W3C WC
	AG 2.0</dcterms:conformsTo>` (web content accessibility guidelines).
    """

    dcterms_created: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Date of creation of the Web resource. Europeana recommends date conforming to ISO 8601
	 starting with the year and with hyphens (YYYY-MM-DD). `<dcterms:created>2010</dcterms:
	created>` or create a reference to an instance of the TimeSpan class `<dc:date rdf:resou
	rce=“http://semium.org/time/2010”/>`
    """

    dcterms_extent: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    The size or duration of the digital resource. `<dcterms:extent>1h 26 min 41 sec</dcterm
	s:extent>`
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

    A resource that is included either physically or logically in the web resource. `<dcter
	ms:hasPart rdf:resource=“http://www.identifier/Part”/>`
    """

    dcterms_isFormatOf: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Another resource that is substantially the same as the web resource but in another for
	mat.  `<dcterms:isFormatOf>http://upload.wikimedia.org/wikipedia/en/f/f3/Europeana_logo
	.png</dcterms:isFormatOf>` for a png image file of the described tiff web resource. Or 
	as a link to a resource `<dcterms:isFormatOf rdf:resource=“http://upload.wikimedia.org/
	wikipedia/en/f/f3/Europeana_logo.png”/>`
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

    A resource in which the WebResource is physically or logically included. This property
	 can be used for web resources that are part of a hierarchy. Hierarchies can be repres
	ented as hierarchies of ProvidedCHOs or hierarchies of web resources but not both at t
	he same time. See the Task Force report on representing hierarchical entities. `<dcterm
	s:isPartOf rdf:resource=“http://data.europeana.eu/item/08701/1B0BACAA44D5A807E43D9B411
	C9781AAD2F96E65”/>`
    """

    dcterms_isReferencedBy: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    A related resource that references, cites, or otherwise points to the described resour
	ce. In a IIIF implementation, dcterms:isReferencedBy can be used to connect a edm:WebR
	esource to a IIIF manifest URI. `<dcterms:isReferencedBy rdf:resource="https://gallica.
	bnf.fr/iiif/ark:/12148/btv1b55001425m/manifest.json"/>`
    """

    dcterms_issued: Optional[MixedValuesList] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[MixedValuesList]
    
    Description: 

    Date of formal issuance or publication of the web resource. Europeana recommends date 
	conforming to ISO 8601 starting with the year and with hyphens (YYYY‐MM-DD). `<dcterms:
	issued>1999</dcterms:issued>` or create a reference to an instance of the TimeSpan clas
	s`<dcterms:issued rdf:resource=“http://semium.org/time/2010”/>`
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

    Where one CHO has several web resources, shown by multiple instances of the edm:hasVie
	w property on the ore:Aggregation this property can be used to show the sequence of th
	e objects. Each web resource (apart from the first in the sequence) should use this pr
	operty to give the URI of the preceding resource in the sequence.
    """

    edm_rights: Optional[Ref] = None
    """
    Mandate: 
    recommended

    Cardinality: 
    zero_to_one

    Value-Type:
    Optional[Ref]
    
    Description: 

    The value in this element will indicate the copyright, usage and access rights that ap
	ply to this digital representation. It is strongly recommended that a value is supplie
	d for this property for each instance of a web resource.The value for the rights state
	ment in this element must be a URI from the list of available values. Note: rights sta
	tements must be exactly as specified there, which means they must start with http and 
	not https. The rights statement specified at the level of the web resource will ‘overr
	ide’ the statement specified at the level of the aggregation. `<edm:rights rdf:resource
	=“http://creativecommons.org/publicdomain/mark/1.0/”/> <edm:rights rdf:resource=“http:
	//rightsstatements.org/vocab/InC/1.0/”/>`  Or create a reference to an instance of the 
	cc:License class where additional details of the rights can be provided (such as an ex
	piry date for the restrictions): http://rightsstatements.org/vocab/NoC-NC/1.0/or `<edm:
	rights rdf:resource="#statement_3000095353971"/>`This is a recommended property.
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

    Provide the URI of another web representation of the same resource. `<owl:sameAs rdf:re
	source=”urn:soundcloud:150424305>`
    """

    svcs_has_service: Optional[List[Ref]] = None
    """
    Mandate: 
    optional

    Cardinality: 
    zero_to_many

    Value-Type:
    Optional[List[Ref]]
    
    Description: 

    The identifier of the svcs:Service required to consume the edm:WebResource. Example: 	
	
`<svcs:has_service rdf:resource="http://www.example.org/Service/IIIF">`
    """

    @model_validator(mode="after")
    def validate_web_resource(self) -> Self:
        if (
            hasattr(self, "edm_rights")
            and self.edm_rights is not None
            and self.edm_rights.value is not None
        ):
            assert self.edm_rights
            assert self.edm_rights.value, "Missing value for edm-rights"

            self.edm_rights.value = normalize_statement(self.edm_rights.value)
            assert_valid_statement(self.edm_rights.value)

        return self
