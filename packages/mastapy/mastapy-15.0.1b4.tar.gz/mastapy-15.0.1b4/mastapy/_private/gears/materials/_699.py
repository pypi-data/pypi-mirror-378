"""ISOTR1417912001CoefficientOfFrictionConstants"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import overridable
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.utility.databases import _2033

_ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "ISOTR1417912001CoefficientOfFrictionConstants"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    Self = TypeVar("Self", bound="ISOTR1417912001CoefficientOfFrictionConstants")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ISOTR1417912001CoefficientOfFrictionConstants._Cast_ISOTR1417912001CoefficientOfFrictionConstants",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISOTR1417912001CoefficientOfFrictionConstants",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISOTR1417912001CoefficientOfFrictionConstants:
    """Special nested class for casting ISOTR1417912001CoefficientOfFrictionConstants to subclasses."""

    __parent__: "ISOTR1417912001CoefficientOfFrictionConstants"

    @property
    def named_database_item(self: "CastSelf") -> "_2033.NamedDatabaseItem":
        return self.__parent__._cast(_2033.NamedDatabaseItem)

    @property
    def isotr1417912001_coefficient_of_friction_constants(
        self: "CastSelf",
    ) -> "ISOTR1417912001CoefficientOfFrictionConstants":
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
class ISOTR1417912001CoefficientOfFrictionConstants(_2033.NamedDatabaseItem):
    """ISOTR1417912001CoefficientOfFrictionConstants

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def constant_c1(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "ConstantC1")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @constant_c1.setter
    @exception_bridge
    @enforce_parameter_types
    def constant_c1(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "ConstantC1", value)

    @property
    @exception_bridge
    def load_intensity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "LoadIntensityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @load_intensity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def load_intensity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "LoadIntensityExponent", value)

    @property
    @exception_bridge
    def oil_viscosity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "OilViscosityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @oil_viscosity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_viscosity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilViscosityExponent", value)

    @property
    @exception_bridge
    def pitch_line_velocity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PitchLineVelocityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @pitch_line_velocity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def pitch_line_velocity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PitchLineVelocityExponent", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ISOTR1417912001CoefficientOfFrictionConstants":
        """Cast to another type.

        Returns:
            _Cast_ISOTR1417912001CoefficientOfFrictionConstants
        """
        return _Cast_ISOTR1417912001CoefficientOfFrictionConstants(self)
