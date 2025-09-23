from typing import Any, List, Tuple
from rdflib import RDF, URIRef
from edmlib.edm.value_types import Ref
from pydantic import BaseModel

from .enums import EDM_Namespace


class EDM_BaseClass(BaseModel):
    """
    Common base-class for all Pydantic models that represent edm-classes (context and core classes).
    Contains the abstracted logic for serializing the class itself to rdf; i.e. building a Ref for the instance of
    the class (Instances are skoped to the record). Also the logic for adding the triple denoting
    the instance with its class is included here.
    """

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Ref

    @classmethod
    def get_class_ref(cls):
        if cls.__name__ == "EDM_BaseClass":
            raise Exception("EDM_BaseClass is an abstract parent class that can't be converted to a URIRef.")

        cls_uri = EDM_Namespace.get_from_name(cls.__name__, return_full_uri=True)
        if cls_uri:
            return URIRef(cls_uri)
        else:
            raise Exception(f"Could not convert {cls.__name__} to URIRef.")

    @property
    def label(self):
        label = self.__class__.__name__
        return label

    def get_triples(self) -> List[Tuple[Any, Any, Any]]:
        triples: List[Tuple[Any, Any, Any]] = []
        try:
            subject = URIRef(self.id.value)
        except Exception as e:
            print("here: ", e)
            raise e
        try:
            triples.append(
                (  # type: ignore
                    subject,
                    RDF.type,
                    URIRef(f"{EDM_Namespace.get_from_name(self.label)}{self.label.split('_')[1]}"),
                )
            )
            for field_name, _ in self.model_fields.items():
                field_val = getattr(self, field_name)

                if field_name != "id" and field_val:
                    # TODO: make the prop_uri an instance of URIRef here, not below
                    prop_uri = EDM_Namespace.get_from_name(field_name, return_full_uri=True)

                    if isinstance(field_val, list):
                        val: Any
                        for val in field_val:
                            triples.append((subject, URIRef(f"{prop_uri}"), val.to_rdflib()))
                    else:
                        triples.append((subject, URIRef(f"{prop_uri}"), field_val.to_rdflib()))

            return triples
        except Exception as e:
            print("Third place in here: ", e)
            raise e
