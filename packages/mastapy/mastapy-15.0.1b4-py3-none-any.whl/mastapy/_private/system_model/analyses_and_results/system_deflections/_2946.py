"""BeltDriveSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.system_deflections import _3054

_BELT_DRIVE_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "BeltDriveSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7894,
        _7895,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4308
    from mastapy._private.system_model.analyses_and_results.static_loads import _7695
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2931,
        _2945,
        _2980,
        _3033,
    )
    from mastapy._private.system_model.part_model.couplings import _2820

    Self = TypeVar("Self", bound="BeltDriveSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="BeltDriveSystemDeflection._Cast_BeltDriveSystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BeltDriveSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BeltDriveSystemDeflection:
    """Special nested class for casting BeltDriveSystemDeflection to subclasses."""

    __parent__: "BeltDriveSystemDeflection"

    @property
    def specialised_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3054.SpecialisedAssemblySystemDeflection":
        return self.__parent__._cast(_3054.SpecialisedAssemblySystemDeflection)

    @property
    def abstract_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2931.AbstractAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2931,
        )

        return self.__parent__._cast(_2931.AbstractAssemblySystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3033.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3033,
        )

        return self.__parent__._cast(_3033.PartSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7894.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7894,
        )

        return self.__parent__._cast(_7894.PartFEAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7895.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7895,
        )

        return self.__parent__._cast(_7895.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7892.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7892,
        )

        return self.__parent__._cast(_7892.PartAnalysisCase)

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
    def cvt_system_deflection(self: "CastSelf") -> "_2980.CVTSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2980,
        )

        return self.__parent__._cast(_2980.CVTSystemDeflection)

    @property
    def belt_drive_system_deflection(self: "CastSelf") -> "BeltDriveSystemDeflection":
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
class BeltDriveSystemDeflection(_3054.SpecialisedAssemblySystemDeflection):
    """BeltDriveSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BELT_DRIVE_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2820.BeltDrive":
        """mastapy.system_model.part_model.couplings.BeltDrive

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
    def assembly_load_case(self: "Self") -> "_7695.BeltDriveLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.BeltDriveLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4308.BeltDrivePowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.BeltDrivePowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def belts(self: "Self") -> "List[_2945.BeltConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BeltConnectionSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Belts")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BeltDriveSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_BeltDriveSystemDeflection
        """
        return _Cast_BeltDriveSystemDeflection(self)
