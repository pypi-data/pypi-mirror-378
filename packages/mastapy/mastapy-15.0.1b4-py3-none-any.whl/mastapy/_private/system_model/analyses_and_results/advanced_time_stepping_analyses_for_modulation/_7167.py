"""ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation"""

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
from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
    _7193,
)

_CONICAL_GEAR_MESH_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation",
    "ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
        _7138,
        _7146,
        _7151,
        _7169,
        _7198,
        _7200,
        _7202,
        _7205,
        _7208,
        _7237,
        _7243,
        _7246,
        _7264,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7885,
        _7888,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2970,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2533

    Self = TypeVar(
        "Self", bound="ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation._Cast_ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation:
    """Special nested class for casting ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation to subclasses."""

    __parent__: "ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation"

    @property
    def gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7193.GearMeshAdvancedTimeSteppingAnalysisForModulation":
        return self.__parent__._cast(
            _7193.GearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def inter_mountable_component_connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7200.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7200,
        )

        return self.__parent__._cast(
            _7200.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7169.ConnectionAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7169,
        )

        return self.__parent__._cast(
            _7169.ConnectionAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7888.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7888,
        )

        return self.__parent__._cast(_7888.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7885.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7885,
        )

        return self.__parent__._cast(_7885.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2895.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2895

        return self.__parent__._cast(_2895.ConnectionAnalysis)

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
    def agma_gleason_conical_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7138.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7138,
        )

        return self.__parent__._cast(
            _7138.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7146.BevelDifferentialGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7146,
        )

        return self.__parent__._cast(
            _7146.BevelDifferentialGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7151.BevelGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7151,
        )

        return self.__parent__._cast(
            _7151.BevelGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def hypoid_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7198.HypoidGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7198,
        )

        return self.__parent__._cast(
            _7198.HypoidGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7202.KlingelnbergCycloPalloidConicalGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7202,
        )

        return self.__parent__._cast(
            _7202.KlingelnbergCycloPalloidConicalGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7205.KlingelnbergCycloPalloidHypoidGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7205,
        )

        return self.__parent__._cast(
            _7205.KlingelnbergCycloPalloidHypoidGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7208.KlingelnbergCycloPalloidSpiralBevelGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7208,
        )

        return self.__parent__._cast(
            _7208.KlingelnbergCycloPalloidSpiralBevelGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spiral_bevel_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7237.SpiralBevelGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7237,
        )

        return self.__parent__._cast(
            _7237.SpiralBevelGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_diff_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7243.StraightBevelDiffGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7243,
        )

        return self.__parent__._cast(
            _7243.StraightBevelDiffGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7246.StraightBevelGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7246,
        )

        return self.__parent__._cast(
            _7246.StraightBevelGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def zerol_bevel_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7264.ZerolBevelGearMeshAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7264,
        )

        return self.__parent__._cast(
            _7264.ZerolBevelGearMeshAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def conical_gear_mesh_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation":
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
class ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation(
    _7193.GearMeshAdvancedTimeSteppingAnalysisForModulation
):
    """ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _CONICAL_GEAR_MESH_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2533.ConicalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.ConicalGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(
        self: "Self",
    ) -> "List[ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]":
        """List[mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]

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
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_2970.ConicalGearMeshSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.ConicalGearMeshSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation
        """
        return _Cast_ConicalGearMeshAdvancedTimeSteppingAnalysisForModulation(self)
