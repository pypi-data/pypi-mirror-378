from maleo.mixins.general import Codes
from maleo.mixins.hierarchy import IsRoot, IsParent, IsChild, IsLeaf
from maleo.mixins.identity import (
    Ids,
    UUIDs,
    ParentIds,
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
from ..mixins.medical_role import Granularity


class CommonQuery(Granularity):
    pass


class ReadSingleQuery(CommonQuery, BaseReadSingleQuery):
    pass


class ReadMultipleSpecializationsQuery(
    CommonQuery,
    ReadPaginatedMultipleQuery,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    Codes[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass


class ReadMultipleQuery(
    CommonQuery,
    ReadPaginatedMultipleQuery,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    Codes[OptionalListOfStrings],
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    ParentIds[OptionalListOfIntegers],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass
