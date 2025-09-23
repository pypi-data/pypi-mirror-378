from enum import StrEnum


# NOTE: shared
class MANDATE(StrEnum):
    """
    Encapsulates value options for a propertie`s or classe`s mandate, i.e.
    if a record MUST, SHOULD or CAN hold the designated class or property.
    """

    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


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
