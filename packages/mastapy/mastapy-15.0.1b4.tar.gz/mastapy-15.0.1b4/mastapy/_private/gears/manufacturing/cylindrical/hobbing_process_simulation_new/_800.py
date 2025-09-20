"""WormGrindingProcessMarkOnShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
    _798,
)

_WORM_GRINDING_PROCESS_MARK_ON_SHAFT = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew",
    "WormGrindingProcessMarkOnShaft",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
        _784,
    )
    from mastapy._private.utility_gui.charts import _2073

    Self = TypeVar("Self", bound="WormGrindingProcessMarkOnShaft")
    CastSelf = TypeVar(
        "CastSelf",
        bound="WormGrindingProcessMarkOnShaft._Cast_WormGrindingProcessMarkOnShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("WormGrindingProcessMarkOnShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_WormGrindingProcessMarkOnShaft:
    """Special nested class for casting WormGrindingProcessMarkOnShaft to subclasses."""

    __parent__: "WormGrindingProcessMarkOnShaft"

    @property
    def worm_grinding_process_calculation(
        self: "CastSelf",
    ) -> "_798.WormGrindingProcessCalculation":
        return self.__parent__._cast(_798.WormGrindingProcessCalculation)

    @property
    def process_calculation(self: "CastSelf") -> "_784.ProcessCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _784,
        )

        return self.__parent__._cast(_784.ProcessCalculation)

    @property
    def worm_grinding_process_mark_on_shaft(
        self: "CastSelf",
    ) -> "WormGrindingProcessMarkOnShaft":
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
class WormGrindingProcessMarkOnShaft(_798.WormGrindingProcessCalculation):
    """WormGrindingProcessMarkOnShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _WORM_GRINDING_PROCESS_MARK_ON_SHAFT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def number_of_profile_bands(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfProfileBands")

        if temp is None:
            return 0

        return temp

    @number_of_profile_bands.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_profile_bands(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfProfileBands", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def number_of_transverse_plane(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTransversePlane")

        if temp is None:
            return 0

        return temp

    @number_of_transverse_plane.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_transverse_plane(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfTransversePlane",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def shaft_diameter(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ShaftDiameter")

        if temp is None:
            return 0.0

        return temp

    @shaft_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def shaft_diameter(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "ShaftDiameter", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def shaft_mark_chart(self: "Self") -> "_2073.ThreeDChartDefinition":
        """mastapy.utility_gui.charts.ThreeDChartDefinition

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftMarkChart")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_WormGrindingProcessMarkOnShaft":
        """Cast to another type.

        Returns:
            _Cast_WormGrindingProcessMarkOnShaft
        """
        return _Cast_WormGrindingProcessMarkOnShaft(self)
