from typing import Annotated, List, TypeAlias, Union
from pydantic import BaseModel, Field, StringConstraints, model_validator, field_validator
from typing import Optional
from typing_extensions import Self
from edmlib.edm.validation.uri import is_valid_uri, sanitize_url_quotation
from rdflib import URIRef, Literal


class Ref(BaseModel):
    """
    About IRIs (from the rdflib.URIRef docstring):

    RDF 1.1's IRI Section https://www.w3.org/TR/rdf11-concepts/#section-IRIs
    An IRI (Internationalized Resource Identifier) within an RDF graph is a Unicode string that conforms to the syntax defined in RFC 3987.
    IRIs in the RDF abstract syntax MUST be absolute, and MAY contain a fragment identifier.
    IRIs are a generalization of URIs [RFC3986] that permits a wider range of Unicode characters.
    """

    value: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    is_ref: bool = True

    @field_validator("value")
    @classmethod
    def validate_value_as_uri(cls, value: str):
        value = value.strip()
        value = sanitize_url_quotation(value)
        assert is_valid_uri(value)
        return value

    def to_rdflib(self):
        """
        Helper to convert this custom type to the rdflib equivalent
        Used in the graph serialization of the EDM_Base-Class
        """
        return URIRef(self.value)


class Lit(BaseModel):
    """
    Overrides the RDFLib Literal with a custom class, so that it is serializable in pydantic model.
    For the same reason, it uses the same attribute names.
    Ignore the normalize attribute, it is just added for completeness.
    """

    value: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    lang: Optional[str] = None
    datatype: Optional[str] = None
    normalize: Optional[bool] = False

    @model_validator(mode="after")
    def validate_consistency(self) -> Self:
        """
        Checks that literal either has a lang_tag or a datatype, not both.
        """
        if self.lang == "":
            self.lang = None
        if self.datatype == "":
            self.datatype = None
        assert not (
            self.lang and self.datatype
        ), f"A literal can either have a datatype or lang_tag, not both: {self.lang=}, {self.datatype=}."
        self.value = self.value.strip()

        return self

    def to_rdflib(self):
        """
        Helper to convert this custom type to the rdflib equivalent
        Used in the graph serialization of the EDM_Base-Class
        """
        return Literal(
            lexical_or_value=self.value,
            lang=self.lang,
            datatype=self.datatype,
            normalize=self.normalize,
        )


MixedValuesList: TypeAlias = List[Union[Lit, Ref]] | List[Ref] | List[Lit]
