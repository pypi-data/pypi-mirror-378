from typing import Literal, Type, Union, overload
from ..dtos.system_role import (
    BasicSystemRoleData,
    StandardSystemRoleData,
    FullSystemRoleData,
)
from ..enums.system_role import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicSystemRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardSystemRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullSystemRoleData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[
    Type[BasicSystemRoleData], Type[StandardSystemRoleData], Type[FullSystemRoleData]
]:
    if granularity is Granularity.BASIC:
        return BasicSystemRoleData
    elif granularity is Granularity.STANDARD:
        return StandardSystemRoleData
    elif granularity is Granularity.FULL:
        return FullSystemRoleData
