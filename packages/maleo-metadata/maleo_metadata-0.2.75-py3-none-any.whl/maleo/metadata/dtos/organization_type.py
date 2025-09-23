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
from maleo.mixins.general import Order
from maleo.mixins.identity import (
    IdentifierTypeValue,
    Ids,
    UUIDs,
    Keys,
    Names,
)
from maleo.types.integer import OptionalInteger, OptionalListOfIntegers
from maleo.types.string import OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.organization_type import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as OrganizationTypeKey,
)
from ..mixins.organization_type import Granularity, Key, Name
from ..types.organization_type import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(Name[str], Key, Order[OptionalInteger]):
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


class ReadMultipleParameter(
    CommonParameter,
    ReadPaginatedMultipleParameter,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass


class FullUpdateData(Name[str], Order[OptionalInteger]):
    pass


class PartialUpdateData(Name[OptionalString], Order[OptionalInteger]):
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


class BaseOrganizationTypeData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


OrganizationTypeDataT = TypeVar(
    "OrganizationTypeDataT",
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
)


OrganizationTypeT = TypeVar(
    "OrganizationTypeT",
    OrganizationTypeKey,
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
)


class OrganizationTypeMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_type: OrganizationTypeT = Field(..., description="Organization type")


class OptionalOrganizationTypeMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_type: Optional[OrganizationTypeT] = Field(
        ..., description="Organization type"
    )


class OrganizationTypesMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_types: List[OrganizationTypeT] = Field(
        ..., description="Organization types"
    )


class OptionalOrganizationTypesMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_types: Optional[List[OrganizationTypeT]] = Field(
        ..., description="Organization types"
    )
