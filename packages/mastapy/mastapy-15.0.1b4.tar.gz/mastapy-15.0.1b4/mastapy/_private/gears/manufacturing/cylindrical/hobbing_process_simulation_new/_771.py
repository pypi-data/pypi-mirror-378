"""HobbingProcessGearShape"""

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
    _770,
)

_HOBBING_PROCESS_GEAR_SHAPE = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew",
    "HobbingProcessGearShape",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
        _784,
    )
    from mastapy._private.utility_gui.charts import _2075

    Self = TypeVar("Self", bound="HobbingProcessGearShape")
    CastSelf = TypeVar(
        "CastSelf", bound="HobbingProcessGearShape._Cast_HobbingProcessGearShape"
    )


__docformat__ = "restructuredtext en"
__all__ = ("HobbingProcessGearShape",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_HobbingProcessGearShape:
    """Special nested class for casting HobbingProcessGearShape to subclasses."""

    __parent__: "HobbingProcessGearShape"

    @property
    def hobbing_process_calculation(
        self: "CastSelf",
    ) -> "_770.HobbingProcessCalculation":
        return self.__parent__._cast(_770.HobbingProcessCalculation)

    @property
    def process_calculation(self: "CastSelf") -> "_784.ProcessCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _784,
        )

        return self.__parent__._cast(_784.ProcessCalculation)

    @property
    def hobbing_process_gear_shape(self: "CastSelf") -> "HobbingProcessGearShape":
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
class HobbingProcessGearShape(_770.HobbingProcessCalculation):
    """HobbingProcessGearShape

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _HOBBING_PROCESS_GEAR_SHAPE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_tooth_shape_chart(self: "Self") -> "_2075.TwoDChartDefinition":
        """mastapy.utility_gui.charts.TwoDChartDefinition

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearToothShapeChart")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def number_of_gear_shape_bands(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfGearShapeBands")

        if temp is None:
            return 0

        return temp

    @number_of_gear_shape_bands.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_gear_shape_bands(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfGearShapeBands",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def result_z_plane(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ResultZPlane")

        if temp is None:
            return 0.0

        return temp

    @result_z_plane.setter
    @exception_bridge
    @enforce_parameter_types
    def result_z_plane(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "ResultZPlane", float(value) if value is not None else 0.0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_HobbingProcessGearShape":
        """Cast to another type.

        Returns:
            _Cast_HobbingProcessGearShape
        """
        return _Cast_HobbingProcessGearShape(self)
