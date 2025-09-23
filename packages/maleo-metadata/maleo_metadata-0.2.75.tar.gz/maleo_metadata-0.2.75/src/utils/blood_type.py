from typing import Literal, Type, Union, overload
from ..dtos.blood_type import (
    BasicBloodTypeData,
    StandardBloodTypeData,
    FullBloodTypeData,
)
from ..enums.blood_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicBloodTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardBloodTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullBloodTypeData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[
    Type[BasicBloodTypeData], Type[StandardBloodTypeData], Type[FullBloodTypeData]
]:
    if granularity is Granularity.BASIC:
        return BasicBloodTypeData
    elif granularity is Granularity.STANDARD:
        return StandardBloodTypeData
    elif granularity is Granularity.FULL:
        return FullBloodTypeData
