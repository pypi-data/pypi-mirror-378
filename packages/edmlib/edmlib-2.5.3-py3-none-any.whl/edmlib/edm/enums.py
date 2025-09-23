from enum import StrEnum
from typing import Union
from rdflib import Namespace

__all__ = [
    "EDM_Namespace",
    "XSD_Types",
]


class EDM_Namespace(StrEnum):
    """
    Represents the basic namespaces that are listed in the edm mapping guidelines.
    @nopdoc
    """

    ORE = "http://www.openarchives.org/ore/terms/"
    SKOS = "http://www.w3.org/2004/02/skos/core#"
    EDM = "http://www.europeana.eu/schemas/edm/"
    RDAGR2 = "http://rdvocab.info/ElementsGr2/"
    FOAF = "http://xmlns.com/foaf/0.1/"
    DC = "http://purl.org/dc/elements/1.1/"
    DCTERMS = "http://purl.org/dc/terms/"
    OWL = "http://www.w3.org/2002/07/owl#"
    CC = "http://creativecommons.org/ns#"
    WGS84_POS = "http://www.w3.org/2003/01/geo/wgs84_pos#"
    CRM = "http://www.cidoc-crm.org/cidoc-­crm/"
    ODRL = "http://www.w3.org/ns/odrl/2/"
    SVCS = "http://rdfs.org/sioc/services#"
    DOAP = "http://usefulinc.com/ns/doap#"

    # TODO: gp/refactor all uri methods
    @classmethod
    def get_namespace_tuples(cls):
        return [(k, Namespace(v)) for k, v in cls.__members__.items()]

    @classmethod
    def get_uri_from_prefix(cls, prefix: str) -> str:
        """
        Returns the namespace-uri for a given prefix as a string.
        Prefix will be converted to uppercase to match the ENUM attribute naming style.
        """
        namespace_uri = getattr(
            cls,
            prefix.upper(),
        ).value
        if not namespace_uri:
            raise Exception(
                f"Could not match prefix {prefix} with any known {cls.__name__}-Option."
            )
        return namespace_uri

    @classmethod
    def get_from_name(cls, name: str, return_full_uri: bool = False) -> str:
        """
        Expects a property in the form: "EDM_PropertyName" ( {PREFIX}_{PropertyName} ) and returns
        either only the namespace-uri as a string or the full uri of the given property
        or class – if return_full_uri is set to 'True'
        """
        if name.startswith("wgs84_pos"):
            ns = "WGS84_POS"
            label = name.replace("wgs84_pos_", "")
        else:
            (ns, label) = name.split("_", 1)

        ns_uri = getattr(cls, ns.upper()).value
        if return_full_uri:
            return ns_uri + label
        return ns_uri

    @classmethod
    def list(cls) -> list[str]:
        return [el.value for el in cls]


class XSD_Types(StrEnum):
    """
    Enum that represents all XSD-Datatypes as defined in the 2001 XML schema definition.
    Converted from the rdflib implementation of the XML schema.

    can by checked via the following import:

    from rdflib import XML
    @nopdoc
    """

    ASSERTIONS = "http://www.w3.org/2001/XMLSchema#Assertions"
    ENTITIES = "http://www.w3.org/2001/XMLSchema#ENTITIES"
    ENTITY = "http://www.w3.org/2001/XMLSchema#ENTITY"
    ID = "http://www.w3.org/2001/XMLSchema#ID"
    IDREF = "http://www.w3.org/2001/XMLSchema#IDREF"
    IDREFS = "http://www.w3.org/2001/XMLSchema#IDREFS"
    NCNAME = "http://www.w3.org/2001/XMLSchema#NCName"
    NMTOKEN = "http://www.w3.org/2001/XMLSchema#NMTOKEN"
    NMTOKENS = "http://www.w3.org/2001/XMLSchema#NMTOKENS"
    NOTATION = "http://www.w3.org/2001/XMLSchema#NOTATION"
    NAME = "http://www.w3.org/2001/XMLSchema#Name"
    QNAME = "http://www.w3.org/2001/XMLSchema#QName"
    ANYURI = "http://www.w3.org/2001/XMLSchema#anyURI"
    BASE64BINARY = "http://www.w3.org/2001/XMLSchema#base64Binary"
    BOOLEAN = "http://www.w3.org/2001/XMLSchema#boolean"
    BOUNDED = "http://www.w3.org/2001/XMLSchema#bounded"
    BYTE = "http://www.w3.org/2001/XMLSchema#byte"
    CARDINALITY = "http://www.w3.org/2001/XMLSchema#cardinality"
    DATE = "http://www.w3.org/2001/XMLSchema#date"
    DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
    DATETIMESTAMP = "http://www.w3.org/2001/XMLSchema#dateTimeStamp"
    DAY = "http://www.w3.org/2001/XMLSchema#day"
    DAYTIMEDURATION = "http://www.w3.org/2001/XMLSchema#dayTimeDuration"
    DECIMAL = "http://www.w3.org/2001/XMLSchema#decimal"
    DOUBLE = "http://www.w3.org/2001/XMLSchema#double"
    DURATION = "http://www.w3.org/2001/XMLSchema#duration"
    ENUMERATION = "http://www.w3.org/2001/XMLSchema#enumeration"
    EXPLICITTIMEZONE = "http://www.w3.org/2001/XMLSchema#explicitTimezone"
    FLOAT = "http://www.w3.org/2001/XMLSchema#float"
    FRACTIONDIGITS = "http://www.w3.org/2001/XMLSchema#fractionDigits"
    GDAY = "http://www.w3.org/2001/XMLSchema#gDay"
    GMONTH = "http://www.w3.org/2001/XMLSchema#gMonth"
    GMONTHDAY = "http://www.w3.org/2001/XMLSchema#gMonthDay"
    GYEAR = "http://www.w3.org/2001/XMLSchema#gYear"
    GYEARMONTH = "http://www.w3.org/2001/XMLSchema#gYearMonth"
    HEXBINARY = "http://www.w3.org/2001/XMLSchema#hexBinary"
    HOUR = "http://www.w3.org/2001/XMLSchema#hour"
    INT = "http://www.w3.org/2001/XMLSchema#int"
    INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
    LANGUAGE = "http://www.w3.org/2001/XMLSchema#language"
    LENGTH = "http://www.w3.org/2001/XMLSchema#length"
    LONG = "http://www.w3.org/2001/XMLSchema#long"
    MAXEXCLUSIVE = "http://www.w3.org/2001/XMLSchema#maxExclusive"
    MAXINCLUSIVE = "http://www.w3.org/2001/XMLSchema#maxInclusive"
    MAXLENGTH = "http://www.w3.org/2001/XMLSchema#maxLength"
    MINEXCLUSIVE = "http://www.w3.org/2001/XMLSchema#minExclusive"
    MININCLUSIVE = "http://www.w3.org/2001/XMLSchema#minInclusive"
    MINLENGTH = "http://www.w3.org/2001/XMLSchema#minLength"
    MINUTE = "http://www.w3.org/2001/XMLSchema#minute"
    MONTH = "http://www.w3.org/2001/XMLSchema#month"
    NEGATIVEINTEGER = "http://www.w3.org/2001/XMLSchema#negativeInteger"
    NONNEGATIVEINTEGER = "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    NONPOSITIVEINTEGER = "http://www.w3.org/2001/XMLSchema#nonPositiveInteger"
    NORMALIZEDSTRING = "http://www.w3.org/2001/XMLSchema#normalizedString"
    NUMERIC = "http://www.w3.org/2001/XMLSchema#numeric"
    ORDERED = "http://www.w3.org/2001/XMLSchema#ordered"
    PATTERN = "http://www.w3.org/2001/XMLSchema#pattern"
    POSITIVEINTEGER = "http://www.w3.org/2001/XMLSchema#positiveInteger"
    SECOND = "http://www.w3.org/2001/XMLSchema#second"
    SHORT = "http://www.w3.org/2001/XMLSchema#short"
    STRING = "http://www.w3.org/2001/XMLSchema#string"
    TIME = "http://www.w3.org/2001/XMLSchema#time"
    TIMEZONEOFFSET = "http://www.w3.org/2001/XMLSchema#timezoneOffset"
    TOKEN = "http://www.w3.org/2001/XMLSchema#token"
    TOTALDIGITS = "http://www.w3.org/2001/XMLSchema#totalDigits"
    UNSIGNEDBYTE = "http://www.w3.org/2001/XMLSchema#unsignedByte"
    UNSIGNEDINT = "http://www.w3.org/2001/XMLSchema#unsignedInt"
    UNSIGNEDLONG = "http://www.w3.org/2001/XMLSchema#unsignedLong"
    UNSIGNEDSHORT = "http://www.w3.org/2001/XMLSchema#unsignedShort"
    WHITESPACE = "http://www.w3.org/2001/XMLSchema#whiteSpace"
    YEAR = "http://www.w3.org/2001/XMLSchema#year"
    YEARMONTHDURATION = "http://www.w3.org/2001/XMLSchema#yearMonthDuration"

    @classmethod
    def get(cls, value: str) -> Union["XSD_Types", None]:
        # TODO: test this method and check existing output
        if not value:
            return None

        return getattr(cls, value.upper()) or None

    @classmethod
    def list(cls) -> list[str]:
        return [el.value for el in cls]


# NOTE: shared
class MANDATE(StrEnum):
    """
    Encapsulates value options for a propertie`s or classe`s mandate, i.e.
    if a record MUST, SHOULD or CAN hold the designated class or property.
    """

    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"

    @classmethod
    def list(cls) -> list[str]:
        return [el.value for el in cls]


# NOTE: shared
class CARDINALITY(StrEnum):
    """
    Encapsulates the cardinality options of a Property. I.e. how often it
    must or can appear within a class.
    """

    ZERO_TO_ONE = "zero_to_one"
    ZERO_TO_MANY = "zero_to_many"
    EXACTLY_ONE = "exactly_one"

    @property
    def is_optional(self):
        return self.value.startswith("zero")

    @classmethod
    def list(cls) -> list[str]:
        return [el.value for el in cls]
