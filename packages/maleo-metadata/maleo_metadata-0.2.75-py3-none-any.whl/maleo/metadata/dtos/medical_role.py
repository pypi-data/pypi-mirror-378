from pydantic import BaseModel, Field
from uuid import UUID
from typing import Generic, List, Literal, Optional, TypeVar, overload
from maleo.enums.status import ListOfDataStatuses, FULL_DATA_STATUSES
from maleo.mixins.identity import DataIdentifier
from maleo.mixins.status import DataStatus
from maleo.mixins.timestamp import LifecycleTimestamp, DataTimestamp
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
)
from maleo.mixins.general import Codes, Order
from maleo.mixins.hierarchy import IsRoot, IsParent, IsChild, IsLeaf
from maleo.mixins.identity import ParentId
from maleo.mixins.identity import (
    IdentifierTypeValue,
    Ids,
    UUIDs,
    ParentIds,
    Keys,
    Names,
)
from maleo.types.integer import OptionalInteger, OptionalListOfIntegers
from maleo.types.string import OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.medical_role import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as MedicalRoleKey,
)
from ..mixins.medical_role import Granularity, Code, Key, Name
from ..types.medical_role import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(
    Name[str],
    Key,
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CommonParameter,
    CreateDataMixin,
):
    pass


class ReadSingleParameter(
    CommonParameter, BaseReadSingleParameter[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            granularity=granularity,
        )


class ReadMultipleSpecializationsParameter(
    CommonParameter,
    ReadPaginatedMultipleParameter,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    Codes[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
    ParentId[int],
):
    pass


class ReadMultipleParameter(
    CommonParameter,
    ReadPaginatedMultipleParameter,
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


class FullUpdateData(
    Name[str],
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class PartialUpdateData(
    Name[OptionalString],
    Code[OptionalString],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    CommonParameter,
    UpdateDataMixin[UpdateDataT],
    IdentifierTypeValue[
        IdentifierType,
        IdentifierValueType,
    ],
    Generic[UpdateDataT],
):
    pass


class StatusUpdateParameter(
    CommonParameter,
    BaseStatusUpdateParameter,
):
    pass


class BaseMedicalRoleData(
    Name[str],
    Key,
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class BasicMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


MedicalRoleDataT = TypeVar(
    "MedicalRoleDataT",
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
)


MedicalRoleT = TypeVar(
    "MedicalRoleT",
    MedicalRoleKey,
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
)


class MedicalRoleMixin(BaseModel, Generic[MedicalRoleT]):
    medical_role: MedicalRoleT = Field(..., description="Medical role")


class OptionalMedicalRoleMixin(BaseModel, Generic[MedicalRoleT]):
    medical_role: Optional[MedicalRoleT] = Field(..., description="Medical role")


class MedicalRolesMixin(BaseModel, Generic[MedicalRoleT]):
    medical_roles: List[MedicalRoleT] = Field(..., description="Medical roles")


class OptionalMedicalRolesMixin(BaseModel, Generic[MedicalRoleT]):
    medical_roles: Optional[List[MedicalRoleT]] = Field(
        ..., description="Medical roles"
    )
