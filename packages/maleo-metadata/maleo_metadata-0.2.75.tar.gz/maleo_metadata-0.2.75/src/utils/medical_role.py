from typing import Literal, Type, Union, overload
from ..dtos.medical_role import (
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
)
from ..enums.medical_role import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicMedicalRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardMedicalRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullMedicalRoleData]: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> Union[
    Type[BasicMedicalRoleData], Type[StandardMedicalRoleData], Type[FullMedicalRoleData]
]:
    if granularity is Granularity.BASIC:
        return BasicMedicalRoleData
    elif granularity is Granularity.STANDARD:
        return StandardMedicalRoleData
    elif granularity is Granularity.FULL:
        return FullMedicalRoleData
