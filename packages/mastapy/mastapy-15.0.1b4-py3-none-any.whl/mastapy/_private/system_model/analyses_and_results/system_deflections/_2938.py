"""AssemblySystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections import _2931

_ASSEMBLY_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "AssemblySystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1347
    from mastapy._private.nodal_analysis import _53
    from mastapy._private.shafts import _43
    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7894,
        _7895,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4305
    from mastapy._private.system_model.analyses_and_results.static_loads import _7692
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2932,
        _2944,
        _2946,
        _2948,
        _2955,
        _2956,
        _2959,
        _2961,
        _2965,
        _2967,
        _2973,
        _2980,
        _2981,
        _2984,
        _2988,
        _3001,
        _3003,
        _3004,
        _3005,
        _3010,
        _3018,
        _3021,
        _3025,
        _3026,
        _3029,
        _3030,
        _3032,
        _3033,
        _3036,
        _3038,
        _3039,
        _3040,
        _3042,
        _3045,
        _3048,
        _3049,
        _3052,
        _3056,
        _3060,
        _3062,
        _3065,
        _3072,
        _3078,
        _3082,
        _3085,
        _3088,
    )
    from mastapy._private.system_model.part_model import _2663

    Self = TypeVar("Self", bound="AssemblySystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="AssemblySystemDeflection._Cast_AssemblySystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AssemblySystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AssemblySystemDeflection:
    """Special nested class for casting AssemblySystemDeflection to subclasses."""

    __parent__: "AssemblySystemDeflection"

    @property
    def abstract_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2931.AbstractAssemblySystemDeflection":
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
    def root_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3048.RootAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3048,
        )

        return self.__parent__._cast(_3048.RootAssemblySystemDeflection)

    @property
    def assembly_system_deflection(self: "CastSelf") -> "AssemblySystemDeflection":
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
class AssemblySystemDeflection(_2931.AbstractAssemblySystemDeflection):
    """AssemblySystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ASSEMBLY_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def overall_bearing_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OverallBearingReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def overall_gear_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OverallGearReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def overall_oil_seal_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OverallOilSealReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def overall_shaft_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OverallShaftReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def overall_system_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OverallSystemReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def analysis_settings(self: "Self") -> "_53.AnalysisSettingsItem":
        """mastapy.nodal_analysis.AnalysisSettingsItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AnalysisSettings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2663.Assembly":
        """mastapy.system_model.part_model.Assembly

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
    def assembly_load_case(self: "Self") -> "_7692.AssemblyLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.AssemblyLoadCase

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
    def power_flow_results(self: "Self") -> "_4305.AssemblyPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.AssemblyPowerFlow

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
    def rating_for_all_gear_sets(self: "Self") -> "_1347.GearSetGroupDutyCycle":
        """mastapy.gears.analysis.GearSetGroupDutyCycle

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RatingForAllGearSets")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def shaft_settings(self: "Self") -> "_43.ShaftSettingsItem":
        """mastapy.shafts.ShaftSettingsItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftSettings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bearings(self: "Self") -> "List[_2944.BearingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BearingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Bearings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def belt_drives(self: "Self") -> "List[_2946.BeltDriveSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BeltDriveSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BeltDrives")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bevel_differential_gear_sets(
        self: "Self",
    ) -> "List[_2948.BevelDifferentialGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BevelDifferentialGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelDifferentialGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bolted_joints(self: "Self") -> "List[_2955.BoltedJointSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BoltedJointSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BoltedJoints")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bolts(self: "Self") -> "List[_2956.BoltSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BoltSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Bolts")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def cv_ts(self: "Self") -> "List[_2980.CVTSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.CVTSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CVTs")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def clutches(self: "Self") -> "List[_2959.ClutchSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ClutchSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Clutches")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_details(self: "Self") -> "List[_2961.ComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def concept_couplings(
        self: "Self",
    ) -> "List[_2965.ConceptCouplingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConceptCouplingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConceptCouplings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def concept_gear_sets(self: "Self") -> "List[_2967.ConceptGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConceptGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConceptGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_details(self: "Self") -> "List[_2973.ConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConnectionSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def cycloidal_assemblies(
        self: "Self",
    ) -> "List[_2981.CycloidalAssemblySystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.CycloidalAssemblySystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CycloidalAssemblies")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def cycloidal_discs(self: "Self") -> "List[_2984.CycloidalDiscSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.CycloidalDiscSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CycloidalDiscs")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def cylindrical_gear_sets(
        self: "Self",
    ) -> "List[_2988.CylindricalGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.CylindricalGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def fe_parts(self: "Self") -> "List[_3003.FEPartSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.FEPartSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FEParts")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def face_gear_sets(self: "Self") -> "List[_3001.FaceGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.FaceGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FaceGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def flexible_pin_assemblies(
        self: "Self",
    ) -> "List[_3004.FlexiblePinAssemblySystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.FlexiblePinAssemblySystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FlexiblePinAssemblies")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def hypoid_gear_sets(self: "Self") -> "List[_3010.HypoidGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.HypoidGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HypoidGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(
        self: "Self",
    ) -> "List[_3018.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidHypoidGearSets"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(
        self: "Self",
    ) -> "List[_3021.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidSpiralBevelGearSets"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def mass_discs(self: "Self") -> "List[_3025.MassDiscSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.MassDiscSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MassDiscs")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def measurement_components(
        self: "Self",
    ) -> "List[_3026.MeasurementComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.MeasurementComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeasurementComponents")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def microphones(self: "Self") -> "List[_3029.MicrophoneSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.MicrophoneSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Microphones")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def mountable_component_details(
        self: "Self",
    ) -> "List[_3030.MountableComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.MountableComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MountableComponentDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def oil_seals(self: "Self") -> "List[_3032.OilSealSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.OilSealSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OilSeals")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def part_to_part_shear_couplings(
        self: "Self",
    ) -> "List[_3036.PartToPartShearCouplingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.PartToPartShearCouplingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PartToPartShearCouplings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def planet_carriers(self: "Self") -> "List[_3038.PlanetCarrierSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.PlanetCarrierSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PlanetCarriers")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def point_loads(self: "Self") -> "List[_3039.PointLoadSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.PointLoadSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PointLoads")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def power_loads(self: "Self") -> "List[_3040.PowerLoadSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.PowerLoadSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerLoads")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def ring_pins(self: "Self") -> "List[_3042.RingPinsSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.RingPinsSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RingPins")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def rolling_bearings(self: "Self") -> "List[_2944.BearingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BearingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RollingBearings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def rolling_ring_assemblies(
        self: "Self",
    ) -> "List[_3045.RollingRingAssemblySystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.RollingRingAssemblySystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RollingRingAssemblies")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def shaft_hub_connections(
        self: "Self",
    ) -> "List[_3049.ShaftHubConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ShaftHubConnectionSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftHubConnections")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def shafts(self: "Self") -> "List[_3052.ShaftSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ShaftSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Shafts")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def shafts_and_housings(
        self: "Self",
    ) -> "List[_2932.AbstractShaftOrHousingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.AbstractShaftOrHousingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftsAndHousings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def sorted_converged_component_details(
        self: "Self",
    ) -> "List[_2961.ComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SortedConvergedComponentDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def sorted_converged_connection_details(
        self: "Self",
    ) -> "List[_2973.ConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConnectionSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SortedConvergedConnectionDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def sorted_unconverged_component_details(
        self: "Self",
    ) -> "List[_2961.ComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SortedUnconvergedComponentDetails")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def sorted_unconverged_connection_details(
        self: "Self",
    ) -> "List[_2973.ConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConnectionSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SortedUnconvergedConnectionDetails"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def spiral_bevel_gear_sets(
        self: "Self",
    ) -> "List[_3056.SpiralBevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.SpiralBevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpiralBevelGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def spring_dampers(self: "Self") -> "List[_3060.SpringDamperSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.SpringDamperSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpringDampers")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_gear_sets(
        self: "Self",
    ) -> "List[_3062.StraightBevelDiffGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.StraightBevelDiffGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelDiffGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_gear_sets(
        self: "Self",
    ) -> "List[_3065.StraightBevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.StraightBevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def supercharger_rotor_sets(
        self: "Self",
    ) -> "List[_2988.CylindricalGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.CylindricalGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SuperchargerRotorSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def synchronisers(self: "Self") -> "List[_3072.SynchroniserSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.SynchroniserSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Synchronisers")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def torque_converters(
        self: "Self",
    ) -> "List[_3078.TorqueConverterSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.TorqueConverterSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TorqueConverters")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def unbalanced_masses(self: "Self") -> "List[_3082.UnbalancedMassSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.UnbalancedMassSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UnbalancedMasses")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def unconverged_bearings_sorted_by_load(
        self: "Self",
    ) -> "List[_2944.BearingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BearingSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UnconvergedBearingsSortedByLoad")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def unconverged_gear_meshes_sorted_by_power(
        self: "Self",
    ) -> "List[_3005.GearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.GearMeshSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "UnconvergedGearMeshesSortedByPower"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def worm_gear_sets(self: "Self") -> "List[_3085.WormGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.WormGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WormGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def zerol_bevel_gear_sets(
        self: "Self",
    ) -> "List[_3088.ZerolBevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ZerolBevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ZerolBevelGearSets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_AssemblySystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_AssemblySystemDeflection
        """
        return _Cast_AssemblySystemDeflection(self)
