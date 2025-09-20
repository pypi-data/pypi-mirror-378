"""InterMountableComponentConnectionCompoundDynamicAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6762,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "InterMountableComponentConnectionCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6661,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6732,
        _6736,
        _6739,
        _6744,
        _6749,
        _6754,
        _6757,
        _6760,
        _6765,
        _6767,
        _6775,
        _6781,
        _6786,
        _6790,
        _6794,
        _6797,
        _6800,
        _6810,
        _6819,
        _6822,
        _6829,
        _6832,
        _6835,
        _6838,
        _6847,
        _6853,
        _6856,
    )

    Self = TypeVar(
        "Self", bound="InterMountableComponentConnectionCompoundDynamicAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundDynamicAnalysis._Cast_InterMountableComponentConnectionCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundDynamicAnalysis:
    """Special nested class for casting InterMountableComponentConnectionCompoundDynamicAnalysis to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundDynamicAnalysis"

    @property
    def connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6762.ConnectionCompoundDynamicAnalysis":
        return self.__parent__._cast(_6762.ConnectionCompoundDynamicAnalysis)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7886,
        )

        return self.__parent__._cast(_7886.ConnectionCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7890.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7890,
        )

        return self.__parent__._cast(_7890.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6732.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6732,
        )

        return self.__parent__._cast(
            _6732.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def belt_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6736.BeltConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6736,
        )

        return self.__parent__._cast(_6736.BeltConnectionCompoundDynamicAnalysis)

    @property
    def bevel_differential_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6739.BevelDifferentialGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6739,
        )

        return self.__parent__._cast(
            _6739.BevelDifferentialGearMeshCompoundDynamicAnalysis
        )

    @property
    def bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6744.BevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6744,
        )

        return self.__parent__._cast(_6744.BevelGearMeshCompoundDynamicAnalysis)

    @property
    def clutch_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6749.ClutchConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6749,
        )

        return self.__parent__._cast(_6749.ClutchConnectionCompoundDynamicAnalysis)

    @property
    def concept_coupling_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6754.ConceptCouplingConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6754,
        )

        return self.__parent__._cast(
            _6754.ConceptCouplingConnectionCompoundDynamicAnalysis
        )

    @property
    def concept_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6757.ConceptGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6757,
        )

        return self.__parent__._cast(_6757.ConceptGearMeshCompoundDynamicAnalysis)

    @property
    def conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6760.ConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6760,
        )

        return self.__parent__._cast(_6760.ConicalGearMeshCompoundDynamicAnalysis)

    @property
    def coupling_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6765.CouplingConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6765,
        )

        return self.__parent__._cast(_6765.CouplingConnectionCompoundDynamicAnalysis)

    @property
    def cvt_belt_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6767.CVTBeltConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6767,
        )

        return self.__parent__._cast(_6767.CVTBeltConnectionCompoundDynamicAnalysis)

    @property
    def cylindrical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6775.CylindricalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6775,
        )

        return self.__parent__._cast(_6775.CylindricalGearMeshCompoundDynamicAnalysis)

    @property
    def face_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6781.FaceGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6781,
        )

        return self.__parent__._cast(_6781.FaceGearMeshCompoundDynamicAnalysis)

    @property
    def gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6786.GearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6786,
        )

        return self.__parent__._cast(_6786.GearMeshCompoundDynamicAnalysis)

    @property
    def hypoid_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6790.HypoidGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6790,
        )

        return self.__parent__._cast(_6790.HypoidGearMeshCompoundDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6794.KlingelnbergCycloPalloidConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6794,
        )

        return self.__parent__._cast(
            _6794.KlingelnbergCycloPalloidConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6797.KlingelnbergCycloPalloidHypoidGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6797,
        )

        return self.__parent__._cast(
            _6797.KlingelnbergCycloPalloidHypoidGearMeshCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6800.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6800,
        )

        return self.__parent__._cast(
            _6800.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundDynamicAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6810.PartToPartShearCouplingConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6810,
        )

        return self.__parent__._cast(
            _6810.PartToPartShearCouplingConnectionCompoundDynamicAnalysis
        )

    @property
    def ring_pins_to_disc_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6819.RingPinsToDiscConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6819,
        )

        return self.__parent__._cast(
            _6819.RingPinsToDiscConnectionCompoundDynamicAnalysis
        )

    @property
    def rolling_ring_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6822.RollingRingConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6822,
        )

        return self.__parent__._cast(_6822.RollingRingConnectionCompoundDynamicAnalysis)

    @property
    def spiral_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6829.SpiralBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6829,
        )

        return self.__parent__._cast(_6829.SpiralBevelGearMeshCompoundDynamicAnalysis)

    @property
    def spring_damper_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6832.SpringDamperConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6832,
        )

        return self.__parent__._cast(
            _6832.SpringDamperConnectionCompoundDynamicAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6835.StraightBevelDiffGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6835,
        )

        return self.__parent__._cast(
            _6835.StraightBevelDiffGearMeshCompoundDynamicAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6838.StraightBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6838,
        )

        return self.__parent__._cast(_6838.StraightBevelGearMeshCompoundDynamicAnalysis)

    @property
    def torque_converter_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6847.TorqueConverterConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6847,
        )

        return self.__parent__._cast(
            _6847.TorqueConverterConnectionCompoundDynamicAnalysis
        )

    @property
    def worm_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6853.WormGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6853,
        )

        return self.__parent__._cast(_6853.WormGearMeshCompoundDynamicAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6856.ZerolBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6856,
        )

        return self.__parent__._cast(_6856.ZerolBevelGearMeshCompoundDynamicAnalysis)

    @property
    def inter_mountable_component_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundDynamicAnalysis":
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
class InterMountableComponentConnectionCompoundDynamicAnalysis(
    _6762.ConnectionCompoundDynamicAnalysis
):
    """InterMountableComponentConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6661.InterMountableComponentConnectionDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.InterMountableComponentConnectionDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6661.InterMountableComponentConnectionDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.InterMountableComponentConnectionDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_InterMountableComponentConnectionCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundDynamicAnalysis
        """
        return _Cast_InterMountableComponentConnectionCompoundDynamicAnalysis(self)
