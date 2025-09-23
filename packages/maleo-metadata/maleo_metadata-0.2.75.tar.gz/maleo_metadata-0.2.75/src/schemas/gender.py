from maleo.mixins.identity import (
    Ids,
    UUIDs,
    Keys,
    Names,
)
from maleo.schemas.request import (
    ReadSingleQuery as BaseReadSingleQuery,
    ReadPaginatedMultipleQuery,
)
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.string import OptionalListOfStrings
from maleo.types.uuid import OptionalListOfUUIDs
from ..mixins.gender import Granularity


class CommonQuery(Granularity):
    pass


class ReadSingleQuery(CommonQuery, BaseReadSingleQuery):
    pass


class ReadMultipleQuery(
    CommonQuery,
    ReadPaginatedMultipleQuery,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass
