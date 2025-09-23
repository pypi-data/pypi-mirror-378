from typing import List, Optional

from ..base import EDM_BaseClass
from ..value_types import Ref


class SVCS_Service(EDM_BaseClass):
    """
    (Manually copied)

    Optional-Properties:
        dcterms_conformsTo, doap_implements

    Mandatory-Properties: None
    Recommended-Proeprties: None

    Definition:
        An established standard to which the web resource or service conforms.
        W3C WCAG 2.0 (web content accessibility guidelines).
        If the Service describes a IIIF resource, dcterms:conformsTo must be used
        to describe the IIIF protocol the resource is conforming to.

    Example:
        `<dcterms:conformsTo rdf:resource="http://iiif.io/api/image"/>`
    """

    dcterms_conformsTo: Optional[List[Ref]]
    """
    Mandate: 
        Optional

    Definition: 
        An established standard to which the web resource or service conforms. 
        W3C WCAG 2.0 (web content accessibility guidelines). If the Service describes 
        a IIIF resource, dcterms:conformsTo must be used to describe the IIIF protocol 
        the resource is conforming to.

    Example: 
        `<dcterms:conformsTo rdf:resource="http://iiif.io/api/image"/>`
    """

    doap_implements: Optional[Ref]
    """
    Mandate: 
        Optional
        
    Definition: 
    	A specification that a project implements. Could be a standard, API or legally defined level of conformance. 
        In IIIF doap:implements refers to the the protocol implemented in IIIF.

    Example: 
        `<doap:implements rdf:resource="http://iiif.io/api/image/2/level1.json"/>`
    """
