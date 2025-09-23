from typing import Literal, Type, Union, overload
from ..dtos.gender import BasicGenderData, StandardGenderData, FullGenderData
from ..enums.gender import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicGenderData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardGenderData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullGenderData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[Type[BasicGenderData], Type[StandardGenderData], Type[FullGenderData]]:
    if granularity is Granularity.BASIC:
        return BasicGenderData
    elif granularity is Granularity.STANDARD:
        return StandardGenderData
    elif granularity is Granularity.FULL:
        return FullGenderData
