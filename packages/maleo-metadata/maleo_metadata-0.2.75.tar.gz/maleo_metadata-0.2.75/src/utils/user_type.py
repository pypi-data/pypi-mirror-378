from typing import Literal, Type, Union, overload
from ..dtos.user_type import BasicUserTypeData, StandardUserTypeData, FullUserTypeData
from ..enums.user_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicUserTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardUserTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullUserTypeData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[Type[BasicUserTypeData], Type[StandardUserTypeData], Type[FullUserTypeData]]:
    if granularity is Granularity.BASIC:
        return BasicUserTypeData
    elif granularity is Granularity.STANDARD:
        return StandardUserTypeData
    elif granularity is Granularity.FULL:
        return FullUserTypeData
