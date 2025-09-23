import json
import os
import re
from typing import List

from pydantic import BaseModel, model_validator
from pyld import jsonld
from rdflib import Graph
from typing_extensions import Self

from edmlib.edm.jsonld_cached_documentloader import cached_requests_document_loader
from .classes import (
    CC_License,
    EDM_Agent,
    EDM_Place,
    EDM_ProvidedCHO,
    EDM_TimeSpan,
    EDM_WebResource,
    ORE_Aggregation,
    SKOS_Concept,
    SVCS_Service,
)
from .enums import EDM_Namespace
import requests

__all__ = ["EDM_Record"]


jsonld.set_document_loader(cached_requests_document_loader())

edm_jsonld_frame_path = os.path.join(
    os.path.dirname(__file__), "edm_jsonld_frame.jsonld"
)
with open(edm_jsonld_frame_path) as frame_file:
    edm_jsonld_frame = json.load(frame_file)


class EDM_Record(BaseModel):
    """
    Pydantic model representing an edm record, as a fully typed structure.
    All contained non-standard types are themselves BaseModels, and the fields are always also either BaseModels or
    standard-types. This ensures that without further conversion, an instance of this class can be
    dumped as a dict (or json) and restored from such a dict (or json).

    Validation:
    This model is responsible for validating the overall structure, order and completeness
    of the record.
    The individual models for each of its properties are responsible for validating their own attributes –
    their completeness, cardinality and structure.
    Finally, the special type models - Ref and Lit - within those container types are responsible for validating
    the indiviudal values.
    """

    # model_config = ConfigDict(strict=False)
    provided_cho: EDM_ProvidedCHO
    aggregation: ORE_Aggregation
    web_resource: List[EDM_WebResource] | None = None
    skos_concept: List[SKOS_Concept] | None = None
    edm_agent: List[EDM_Agent] | None = None
    edm_time_span: List[EDM_TimeSpan] | None = None
    edm_place: List[EDM_Place] | None = None
    cc_license: List[CC_License] | None = None
    svcs_service: List[SVCS_Service] | None = None

    def get_rdf_graph(self):
        """
        Return whole record as as an RDF - rdflib.Graph object.
        """
        graph = Graph()
        namespaces = EDM_Namespace.get_namespace_tuples()
        for tup in namespaces:
            graph.bind(tup[0].lower(), tup[1])
        # TODO: abstract the instance list into a callable hook
        for instance in [
            "provided_cho",
            "web_resource",
            "aggregation",
            "skos_concept",
            "edm_agent",
            "edm_time_span",
            "edm_place",
            "cc_license",
            "svcs_service",
        ]:
            attval = getattr(self, instance)
            if attval:
                if isinstance(attval, list):
                    for val in attval:  # type: ignore
                        # print("val was list for", val, attval) # type: ignore
                        triples = val.get_triples()  # type: ignore
                        [graph.add(triple) for triple in triples]  # type: ignore
                else:
                    # print("val was not a list for", attval)
                    triples = attval.get_triples()
                    [graph.add(triple) for triple in triples]
        return graph

    def serialize(self, format: str = "pretty-xml", max_depth: int = 1) -> str:
        """
        Serialize graph to rdf/xml with pretty-formatting.
        """
        graph = self.get_rdf_graph()
        return graph.serialize(format=format, max_depth=max_depth)

    def get_framed_json_ld(self):
        graph = self.get_rdf_graph()
        json_str = graph.serialize(format="json-ld", auto_compact=True)
        # TODO: this needs fixing, as there a relative uri replacements that can be broken by this
        json_str = re.sub('file:///.+?(?P<uri>[^#/]+)"', r'#\g<uri>"', json_str)
        json_data = json.loads(json_str)
        return jsonld.frame(
            json_data,
            edm_jsonld_frame,
            options={"embed": "@always"},
        )

    @model_validator(mode="after")
    def validate_provided_cho_identity(self) -> Self:
        assert (
            self.provided_cho.id.value == self.aggregation.edm_aggregatedCHO.value
        ), f"URIs of providedCHO and aggregation.edm_aggregatedCHO do not match: {self.provided_cho.id.value=} != {self.aggregation.edm_aggregatedCHO.value=}."
        return self

    # === media checks ===

    def fetch_edm_isShownBy_head(self, **kwargs) -> requests.Response:
        shown_by = self.aggregation.edm_isShownBy
        if not shown_by:
            raise Exception(">edm_isShownBy< is >None<. Cannot fetch head.")
        return requests.head(shown_by.value, **kwargs)

    def has_edm_object(self) -> bool:
        return bool(self.aggregation.edm_object)

    def fetch_edm_object_head(self, **kwargs) -> requests.Response:
        _object = self.aggregation.edm_object
        if not _object:
            raise Exception(">edm_object< is >None<. Cannot fetch head.")
        return requests.head(_object.value, **kwargs)

    def has_edm_hasView(self) -> bool:
        return bool(self.aggregation.edm_hasView)

    def fetch_edm_hasView_heads(self, **kwargs) -> list[requests.Response]:
        has_view = self.aggregation.edm_hasView
        if not has_view:
            raise Exception(">edm_hasView< is >None<. Cannot fetch heads.")
        return [requests.head(view.value, **kwargs) for view in has_view]

    def fetch_edm_isShownAt_head(self, **kwargs) -> requests.Response:
        shown_at = self.aggregation.edm_isShownAt
        if not shown_at:
            raise Exception(">edm_isShownAt< is >None<. Cannot fetch head.")
        return requests.head(shown_at.value, **kwargs)
