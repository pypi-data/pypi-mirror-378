"""ShaftLoadCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.analyses_and_results.static_loads import _7681

_SHAFT_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "ShaftLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7682,
        _7711,
        _7804,
    )
    from mastapy._private.system_model.part_model.shaft_model import _2719

    Self = TypeVar("Self", bound="ShaftLoadCase")
    CastSelf = TypeVar("CastSelf", bound="ShaftLoadCase._Cast_ShaftLoadCase")


__docformat__ = "restructuredtext en"
__all__ = ("ShaftLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftLoadCase:
    """Special nested class for casting ShaftLoadCase to subclasses."""

    __parent__: "ShaftLoadCase"

    @property
    def abstract_shaft_load_case(self: "CastSelf") -> "_7681.AbstractShaftLoadCase":
        return self.__parent__._cast(_7681.AbstractShaftLoadCase)

    @property
    def abstract_shaft_or_housing_load_case(
        self: "CastSelf",
    ) -> "_7682.AbstractShaftOrHousingLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7682,
        )

        return self.__parent__._cast(_7682.AbstractShaftOrHousingLoadCase)

    @property
    def component_load_case(self: "CastSelf") -> "_7711.ComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7711,
        )

        return self.__parent__._cast(_7711.ComponentLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7804.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7804,
        )

        return self.__parent__._cast(_7804.PartLoadCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2903.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2903

        return self.__parent__._cast(_2903.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2899.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2899

        return self.__parent__._cast(_2899.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def shaft_load_case(self: "CastSelf") -> "ShaftLoadCase":
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
class ShaftLoadCase(_7681.AbstractShaftLoadCase):
    """ShaftLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def diameter_scaling_factor(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "DiameterScalingFactor")

        if temp is None:
            return 0.0

        return temp

    @diameter_scaling_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def diameter_scaling_factor(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "DiameterScalingFactor",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2719.Shaft":
        """mastapy.system_model.part_model.shaft_model.Shaft

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[ShaftLoadCase]":
        """List[mastapy.system_model.analyses_and_results.static_loads.ShaftLoadCase]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ShaftLoadCase":
        """Cast to another type.

        Returns:
            _Cast_ShaftLoadCase
        """
        return _Cast_ShaftLoadCase(self)
