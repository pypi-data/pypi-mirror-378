"""InstantaneousCoefficientOfFrictionCalculator"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.gears.materials import _682

_INSTANTANEOUS_COEFFICIENT_OF_FRICTION_CALCULATOR = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "InstantaneousCoefficientOfFrictionCalculator"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.materials import _676, _688, _698, _704, _705, _711
    from mastapy._private.gears.rating.cylindrical import _550

    Self = TypeVar("Self", bound="InstantaneousCoefficientOfFrictionCalculator")
    CastSelf = TypeVar(
        "CastSelf",
        bound="InstantaneousCoefficientOfFrictionCalculator._Cast_InstantaneousCoefficientOfFrictionCalculator",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InstantaneousCoefficientOfFrictionCalculator",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InstantaneousCoefficientOfFrictionCalculator:
    """Special nested class for casting InstantaneousCoefficientOfFrictionCalculator to subclasses."""

    __parent__: "InstantaneousCoefficientOfFrictionCalculator"

    @property
    def coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_682.CoefficientOfFrictionCalculator":
        return self.__parent__._cast(_682.CoefficientOfFrictionCalculator)

    @property
    def benedict_and_kelley_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_676.BenedictAndKelleyCoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _676

        return self.__parent__._cast(
            _676.BenedictAndKelleyCoefficientOfFrictionCalculator
        )

    @property
    def drozdov_and_gavrikov_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_688.DrozdovAndGavrikovCoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _688

        return self.__parent__._cast(
            _688.DrozdovAndGavrikovCoefficientOfFrictionCalculator
        )

    @property
    def isotc60_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_698.ISOTC60CoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _698

        return self.__parent__._cast(_698.ISOTC60CoefficientOfFrictionCalculator)

    @property
    def misharin_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_704.MisharinCoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _704

        return self.__parent__._cast(_704.MisharinCoefficientOfFrictionCalculator)

    @property
    def o_donoghue_and_cameron_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_705.ODonoghueAndCameronCoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _705

        return self.__parent__._cast(
            _705.ODonoghueAndCameronCoefficientOfFrictionCalculator
        )

    @property
    def script_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_711.ScriptCoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _711

        return self.__parent__._cast(_711.ScriptCoefficientOfFrictionCalculator)

    @property
    def instantaneous_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "InstantaneousCoefficientOfFrictionCalculator":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class InstantaneousCoefficientOfFrictionCalculator(
    _682.CoefficientOfFrictionCalculator
):
    """InstantaneousCoefficientOfFrictionCalculator

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INSTANTANEOUS_COEFFICIENT_OF_FRICTION_CALCULATOR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def cylindrical_gear_mesh_rating(self: "Self") -> "_550.CylindricalGearMeshRating":
        """mastapy.gears.rating.cylindrical.CylindricalGearMeshRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGearMeshRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_InstantaneousCoefficientOfFrictionCalculator":
        """Cast to another type.

        Returns:
            _Cast_InstantaneousCoefficientOfFrictionCalculator
        """
        return _Cast_InstantaneousCoefficientOfFrictionCalculator(self)
