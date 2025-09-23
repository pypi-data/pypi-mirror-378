from rdflib import Graph, URIRef, Literal, RDF

from edmlib.edm import (
    EDM_Record,
    EDM_Namespace,
    EDM_ProvidedCHO,
    EDM_WebResource,
    ORE_Aggregation,
    CC_License,
    SKOS_Concept,
    EDM_Agent,
    EDM_Place,
    EDM_TimeSpan,
    SVCS_Service,
    Lit,
    Ref,
)

from typing import get_type_hints, List, Any, Dict, Self
from rdflib.term import _castPythonToLiteral


def check_if_many(cls: object, attname: str) -> bool:
    """
    Checks against an objects type annotation if the attribute with 'attname' expects a list of values or a single value. I.e. checks the
    cardinality of a property in the context of a spefic class.
    """
    hints = get_type_hints(cls).get(attname)
    return bool(
        hints
        and (
            str(hints).startswith("typing.Optional[typing.List")
            or str(hints).startswith("typing.List")
            or str(hints).startswith("typing.Union[typing.List")
        ),
    )


def to_literal(literal: Literal) -> Lit:
    """
    Temporary helper function to convert rdflib.Literal to edm_python.edm.Lit
    """

    obj, dtype = _castPythonToLiteral(literal.value, literal.datatype)

    return Lit.model_construct(
        value=str(obj),
        lang=literal.language,
        datatype=dtype,
    )


def to_ref(ref: URIRef) -> Ref:
    """
    Temporary helper function to convert rdflib.URIRef to edm_python.edm.Ref
    """
    value = str(ref)
    return Ref.model_construct(value=value)


def cls_attribute_to_ref(attname: str) -> URIRef:
    """
    Helper that converts a edm_classes attribute name to the corresponding properties full IRI.
    """
    res = attname.split("_")
    ns = "WGS84_POS" if attname.startswith("WGS84_POS") else res[0]

    res = "_".join(res[1:]) if len(res) > 2 else res[1]

    return URIRef(f"{getattr(EDM_Namespace, ns.upper())}{res}")


def cls_attribute_to_ref_new(attname: str) -> URIRef:
    """
    Helper that converts a edm_classes attribute name to the corresponding properties full IRI.
    """
    res = attname.split("_")
    if attname.startswith("wgs84_pos"):
        ns = "WGS84_POS"
        res = attname.replace("wgs84_pos_", "")
    else:
        ns = res[0]

        res = "_".join(res[1:]) if len(res) > 2 else res[1]

    return URIRef(f"{getattr(EDM_Namespace, ns.upper())}{res}")


def get_attributes(cls: object) -> Dict[str, URIRef]:
    """
    For a given edm-class, get a list of all its properties as edm_python.edm.Ref objects.
    """
    attlist = list(cls.__dict__.get("__annotations__").keys())  # type: ignore
    return {el: cls_attribute_to_ref_new(el) for el in attlist}


def convert(lit_or_ref: URIRef | Literal) -> Ref | Lit:
    """
    Helper to convert a rdlib.URIRef or rdflib.Literal to the
    corresponding edm-python object (Lit or Ref).
    """
    if isinstance(lit_or_ref, URIRef):
        return to_ref(lit_or_ref)

    assert isinstance(
        lit_or_ref, Literal
    ), f"Argument 'lit_or_ref'  must be of tpye 'rdflib.URIRef' or 'rdflib.Literal' go {type(lit_or_ref)} instead."

    return to_literal(lit_or_ref)


class EDM_Parser:
    """
    Parser for edm-xml records. Returns an edm_python.edm.EDM_Record object.
    """

    @classmethod
    def from_file(cls, path: str, format: str = "xml") -> Self:
        # TODO: add logic to add the placholder here and to remove it in serialization again
        graph = Graph().parse(path, format=format, publicID="placeholder")
        return cls(graph=graph)

    @classmethod
    def from_string(cls, content: str, format: str = "xml") -> Self:
        # TODO: add logic to add the placholder here and to remove it in serialization again
        graph = Graph().parse(data=content, format=format, publicID="placeholder")
        return cls(graph=graph)

    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def get_single_ref(self, obj_cls: object) -> URIRef:
        """
        Loooks up instances of a given obj_cls (a edm_python edm-class) and returns
        a single IRI.
        This method expects that the cardinality of the obj_cls is one per record.
        """
        res = self.get_many_ref(obj_cls)
        assert len(res) == 1, f"Got: {len(res)}, {res=}"
        # print("in get single ref: ", res[0])
        return res[0]

    def get_many_ref(self, obj_cls: object) -> List[URIRef]:
        """
        Loooks up instances of a given obj_cls (a edm_python edm-class) and returns
        a list of instance-IRIs.
        This method expects that the cardinality of the obj_cls is one or more.
        """
        # TODO: check assertion that subjects are always uri-refs...
        return [
            el[0]  # type: ignore
            for el in self.graph.triples((None, RDF.type, obj_cls.get_class_ref()))  # type: ignore
        ]

    def get_triples(self, ref: URIRef):
        """
        Return all predicate-object triples for a given URIRef within the instance`s-graph.
        """
        return self.graph.predicate_objects(ref)

    def get_aggregation(self):
        agg = list(
            self.graph.triples(
                (
                    None,
                    RDF.type,
                    ORE_Aggregation.get_class_ref(),
                )
            )
        )
        assert len(agg) == 1, f"Expected one aggregation, got {len(agg)}. {agg=}"
        return agg[0][0]

    def get_webresources(self) -> list[Any]:
        webresources = list(
            self.graph.triples(
                (
                    None,
                    RDF.type,
                    EDM_WebResource.get_class_ref(),
                ),
            ),
        )
        return [el[0] for el in webresources]

    def get_instance_triples(self, instance: URIRef, cls_obj: object) -> Dict[str, Any]:
        attribs = get_attributes(cls_obj)
        temp: Dict[str, Any] = {}
        for att, ref in attribs.items():
            values = [
                convert(el[2])  # type: ignore
                for el in list(self.graph.triples((instance, ref, None)))
            ]
            values = [
                lit_or_ref for lit_or_ref in values if lit_or_ref.value.strip() != ""
            ]

            if cls_obj == ORE_Aggregation and att == "edm_aggregatedCHO":
                # ORE_Aggregation.edm_aggregatedCHO needs to have as its new
                # value the validation function's result. This is because, at a
                # later stage, it is validated against the EDM_ProvidedCHO.id in
                # EDM_Record.validate_provided_cho_identity(). ProvidedCHO has
                # its validation value assigned at instantiation and would
                # therefore not match ORE_Aggregation.edm_aggregatedCHO.
                #
                # The validation function returns a Ref that might differ from
                # the original value, because urls are sanitized via
                # sanitize_url_quotation() in Ref.validate_value_as_uri().
                values = [
                    value.__class__.model_validate(
                        value.__class__(**value.model_dump())
                    )
                    for value in values
                ]
            else:
                for value in values:
                    value.__class__.model_validate(
                        value.__class__(**value.model_dump())
                    )
            if values:
                many = check_if_many(cls_obj, att)
                if not many:
                    assert (
                        len(values) == 1
                    ), f"Expected 1 value but got {len(values)}; {cls_obj=}; {att=}"
                    values = values[0]
                temp.update({att: values})
        return temp

    def parse_single_class(self, cls_obj: object) -> Any:
        add = {}
        match cls_obj.__name__:  # type: ignore
            case "EDM_ProvidedCHO":
                inst = self.get_single_ref(cls_obj)
            case "ORE_Aggregation":
                inst = self.get_aggregation()
                add = {
                    "edm_provider": Lit(value="Kulturpool", lang="de"),
                }
            case _:  # type: ignore
                pass
        triples = self.get_instance_triples(inst, cls_obj)  # type: ignore

        triples.update(**add)
        return cls_obj(id=Ref(value=str(inst)), **triples)  # type: ignore

    def parse_many_class(self, cls_obj: Any) -> List[Any]:
        match cls_obj.__name__:
            case "EDM_WebResource":
                instances = self.get_webresources()
            case _:
                instances = self.get_many_ref(cls_obj)
        res: List[Any] = []
        for inst in instances:
            # print("instance", type(inst), inst)
            res.append(
                cls_obj(
                    id=Ref(value=str(inst)),
                    **self.get_instance_triples(inst, cls_obj),  # type: ignore
                )
            )

        return res

    def parse(self) -> EDM_Record:
        cho = self.parse_single_class(EDM_ProvidedCHO)
        aggre = self.parse_single_class(ORE_Aggregation)
        web_resources = self.parse_many_class(EDM_WebResource)
        skos_concepts = self.parse_many_class(SKOS_Concept)
        edm_time_spans = self.parse_many_class(EDM_TimeSpan)
        edm_agents = self.parse_many_class(EDM_Agent)
        edm_places = self.parse_many_class(EDM_Place)
        cc_licenses = self.parse_many_class(CC_License)
        svcs_services = self.parse_many_class(SVCS_Service)

        return EDM_Record(
            provided_cho=cho,
            aggregation=aggre,
            web_resource=web_resources,
            skos_concept=skos_concepts,
            edm_time_span=edm_time_spans,
            edm_agent=edm_agents,
            edm_place=edm_places,
            cc_license=cc_licenses,
            svcs_service=svcs_services,
        )
