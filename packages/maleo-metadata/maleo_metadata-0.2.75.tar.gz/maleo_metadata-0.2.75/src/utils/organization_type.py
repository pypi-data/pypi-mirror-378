from typing import Literal, Type, Union, overload
from ..dtos.organization_type import (
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
)
from ..enums.organization_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicOrganizationTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardOrganizationTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullOrganizationTypeData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[
    Type[BasicOrganizationTypeData],
    Type[StandardOrganizationTypeData],
    Type[FullOrganizationTypeData],
]:
    if granularity is Granularity.BASIC:
        return BasicOrganizationTypeData
    elif granularity is Granularity.STANDARD:
        return StandardOrganizationTypeData
    elif granularity is Granularity.FULL:
        return FullOrganizationTypeData
