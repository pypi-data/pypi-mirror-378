"""ConicalPinionManufacturingConfig"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_get_with_method,
    pythonnet_property_set_with_method,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.gears.manufacturing.bevel import _880

_DATABASE_WITH_SELECTED_ITEM = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Databases", "DatabaseWithSelectedItem"
)
_CONICAL_PINION_MANUFACTURING_CONFIG = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Bevel", "ConicalPinionManufacturingConfig"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335, _1338, _1341
    from mastapy._private.gears.manufacturing.bevel import _882, _885, _889, _910, _914
    from mastapy._private.gears.manufacturing.bevel.cutters import _917, _918

    Self = TypeVar("Self", bound="ConicalPinionManufacturingConfig")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalPinionManufacturingConfig._Cast_ConicalPinionManufacturingConfig",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalPinionManufacturingConfig",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalPinionManufacturingConfig:
    """Special nested class for casting ConicalPinionManufacturingConfig to subclasses."""

    __parent__: "ConicalPinionManufacturingConfig"

    @property
    def conical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_880.ConicalGearManufacturingConfig":
        return self.__parent__._cast(_880.ConicalGearManufacturingConfig)

    @property
    def conical_gear_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_882.ConicalGearMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _882

        return self.__parent__._cast(_882.ConicalGearMicroGeometryConfigBase)

    @property
    def gear_implementation_detail(
        self: "CastSelf",
    ) -> "_1341.GearImplementationDetail":
        from mastapy._private.gears.analysis import _1341

        return self.__parent__._cast(_1341.GearImplementationDetail)

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1338.GearDesignAnalysis":
        from mastapy._private.gears.analysis import _1338

        return self.__parent__._cast(_1338.GearDesignAnalysis)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1335.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1335

        return self.__parent__._cast(_1335.AbstractGearAnalysis)

    @property
    def conical_pinion_manufacturing_config(
        self: "CastSelf",
    ) -> "ConicalPinionManufacturingConfig":
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
class ConicalPinionManufacturingConfig(_880.ConicalGearManufacturingConfig):
    """ConicalPinionManufacturingConfig

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_PINION_MANUFACTURING_CONFIG

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def pinion_finish_manufacturing_machine(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped, "PinionFinishManufacturingMachine", "SelectedItemName"
        )

        if temp is None:
            return ""

        return temp

    @pinion_finish_manufacturing_machine.setter
    @exception_bridge
    @enforce_parameter_types
    def pinion_finish_manufacturing_machine(self: "Self", value: "str") -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "PinionFinishManufacturingMachine",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def pinion_rough_manufacturing_machine(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped, "PinionRoughManufacturingMachine", "SelectedItemName"
        )

        if temp is None:
            return ""

        return temp

    @pinion_rough_manufacturing_machine.setter
    @exception_bridge
    @enforce_parameter_types
    def pinion_rough_manufacturing_machine(self: "Self", value: "str") -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "PinionRoughManufacturingMachine",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def mesh_config(self: "Self") -> "_889.ConicalMeshManufacturingConfig":
        """mastapy.gears.manufacturing.bevel.ConicalMeshManufacturingConfig

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshConfig")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_concave_ob_configuration(
        self: "Self",
    ) -> "_885.ConicalMeshFlankManufacturingConfig":
        """mastapy.gears.manufacturing.bevel.ConicalMeshFlankManufacturingConfig

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionConcaveOBConfiguration")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_convex_ib_configuration(
        self: "Self",
    ) -> "_885.ConicalMeshFlankManufacturingConfig":
        """mastapy.gears.manufacturing.bevel.ConicalMeshFlankManufacturingConfig

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionConvexIBConfiguration")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_cutter_parameters_concave(
        self: "Self",
    ) -> "_910.PinionFinishMachineSettings":
        """mastapy.gears.manufacturing.bevel.PinionFinishMachineSettings

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionCutterParametersConcave")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_cutter_parameters_convex(
        self: "Self",
    ) -> "_910.PinionFinishMachineSettings":
        """mastapy.gears.manufacturing.bevel.PinionFinishMachineSettings

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionCutterParametersConvex")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_finish_cutter(self: "Self") -> "_917.PinionFinishCutter":
        """mastapy.gears.manufacturing.bevel.cutters.PinionFinishCutter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionFinishCutter")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_rough_cutter(self: "Self") -> "_918.PinionRoughCutter":
        """mastapy.gears.manufacturing.bevel.cutters.PinionRoughCutter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionRoughCutter")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pinion_rough_machine_setting(self: "Self") -> "_914.PinionRoughMachineSetting":
        """mastapy.gears.manufacturing.bevel.PinionRoughMachineSetting

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionRoughMachineSetting")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalPinionManufacturingConfig":
        """Cast to another type.

        Returns:
            _Cast_ConicalPinionManufacturingConfig
        """
        return _Cast_ConicalPinionManufacturingConfig(self)
