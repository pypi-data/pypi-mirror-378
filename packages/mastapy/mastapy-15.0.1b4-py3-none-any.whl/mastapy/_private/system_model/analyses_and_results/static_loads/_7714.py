"""ConceptCouplingLoadCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import list_with_selected_item, overridable
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.analyses_and_results.static_loads import _7727
from mastapy._private.system_model.part_model import _2708

_CONCEPT_COUPLING_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "ConceptCouplingLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.math_utility import _1723
    from mastapy._private.math_utility.control import _1766
    from mastapy._private.system_model import _2418
    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7680,
        _7804,
        _7828,
    )
    from mastapy._private.system_model.part_model.couplings import _2825

    Self = TypeVar("Self", bound="ConceptCouplingLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="ConceptCouplingLoadCase._Cast_ConceptCouplingLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConceptCouplingLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConceptCouplingLoadCase:
    """Special nested class for casting ConceptCouplingLoadCase to subclasses."""

    __parent__: "ConceptCouplingLoadCase"

    @property
    def coupling_load_case(self: "CastSelf") -> "_7727.CouplingLoadCase":
        return self.__parent__._cast(_7727.CouplingLoadCase)

    @property
    def specialised_assembly_load_case(
        self: "CastSelf",
    ) -> "_7828.SpecialisedAssemblyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7828,
        )

        return self.__parent__._cast(_7828.SpecialisedAssemblyLoadCase)

    @property
    def abstract_assembly_load_case(
        self: "CastSelf",
    ) -> "_7680.AbstractAssemblyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7680,
        )

        return self.__parent__._cast(_7680.AbstractAssemblyLoadCase)

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
    def concept_coupling_load_case(self: "CastSelf") -> "ConceptCouplingLoadCase":
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
class ConceptCouplingLoadCase(_7727.CouplingLoadCase):
    """ConceptCouplingLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONCEPT_COUPLING_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def efficiency(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Efficiency")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @efficiency.setter
    @exception_bridge
    @enforce_parameter_types
    def efficiency(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Efficiency", value)

    @property
    @exception_bridge
    def power_load_for_reference_speed(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_PowerLoad":
        """ListWithSelectedItem[mastapy.system_model.part_model.PowerLoad]"""
        temp = pythonnet_property_get(self.wrapped, "PowerLoadForReferenceSpeed")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_PowerLoad",
        )(temp)

    @power_load_for_reference_speed.setter
    @exception_bridge
    @enforce_parameter_types
    def power_load_for_reference_speed(self: "Self", value: "_2708.PowerLoad") -> None:
        generic_type = (
            list_with_selected_item.ListWithSelectedItem_PowerLoad.implicit_type()
        )
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "PowerLoadForReferenceSpeed", value)

    @property
    @exception_bridge
    def speed_ratio(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "SpeedRatio")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @speed_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def speed_ratio(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "SpeedRatio", value)

    @property
    @exception_bridge
    def speed_ratio_specification_method(
        self: "Self",
    ) -> "_2418.ConceptCouplingSpeedRatioSpecificationMethod":
        """mastapy.system_model.ConceptCouplingSpeedRatioSpecificationMethod"""
        temp = pythonnet_property_get(self.wrapped, "SpeedRatioSpecificationMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.SystemModel.ConceptCouplingSpeedRatioSpecificationMethod",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model._2418",
            "ConceptCouplingSpeedRatioSpecificationMethod",
        )(value)

    @speed_ratio_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def speed_ratio_specification_method(
        self: "Self", value: "_2418.ConceptCouplingSpeedRatioSpecificationMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.SystemModel.ConceptCouplingSpeedRatioSpecificationMethod",
        )
        pythonnet_property_set(self.wrapped, "SpeedRatioSpecificationMethod", value)

    @property
    @exception_bridge
    def speed_ratio_vs_time(self: "Self") -> "_1723.Vector2DListAccessor":
        """mastapy.math_utility.Vector2DListAccessor

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpeedRatioVsTime")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2825.ConceptCoupling":
        """mastapy.system_model.part_model.couplings.ConceptCoupling

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def speed_ratio_pid_control(self: "Self") -> "_1766.PIDControlSettings":
        """mastapy.math_utility.control.PIDControlSettings

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpeedRatioPIDControl")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConceptCouplingLoadCase":
        """Cast to another type.

        Returns:
            _Cast_ConceptCouplingLoadCase
        """
        return _Cast_ConceptCouplingLoadCase(self)
