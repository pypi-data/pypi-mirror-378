from typing import Literal, Type, Union, overload
from ..dtos.service import BasicServiceData, StandardServiceData, FullServiceData
from ..enums.service import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicServiceData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardServiceData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullServiceData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[Type[BasicServiceData], Type[StandardServiceData], Type[FullServiceData]]:
    if granularity is Granularity.BASIC:
        return BasicServiceData
    elif granularity is Granularity.STANDARD:
        return StandardServiceData
    elif granularity is Granularity.FULL:
        return FullServiceData
