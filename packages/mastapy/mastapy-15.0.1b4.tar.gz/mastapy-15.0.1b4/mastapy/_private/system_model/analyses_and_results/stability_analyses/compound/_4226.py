"""InterMountableComponentConnectionCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4196,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "InterMountableComponentConnectionCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4092,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4166,
        _4170,
        _4173,
        _4178,
        _4183,
        _4188,
        _4191,
        _4194,
        _4199,
        _4201,
        _4209,
        _4215,
        _4220,
        _4224,
        _4228,
        _4231,
        _4234,
        _4244,
        _4253,
        _4256,
        _4263,
        _4266,
        _4269,
        _4272,
        _4281,
        _4287,
        _4290,
    )

    Self = TypeVar(
        "Self", bound="InterMountableComponentConnectionCompoundStabilityAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundStabilityAnalysis._Cast_InterMountableComponentConnectionCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis:
    """Special nested class for casting InterMountableComponentConnectionCompoundStabilityAnalysis to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundStabilityAnalysis"

    @property
    def connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4196.ConnectionCompoundStabilityAnalysis":
        return self.__parent__._cast(_4196.ConnectionCompoundStabilityAnalysis)

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
    def agma_gleason_conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4166.AGMAGleasonConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4166,
        )

        return self.__parent__._cast(
            _4166.AGMAGleasonConicalGearMeshCompoundStabilityAnalysis
        )

    @property
    def belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4170.BeltConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4170,
        )

        return self.__parent__._cast(_4170.BeltConnectionCompoundStabilityAnalysis)

    @property
    def bevel_differential_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4173.BevelDifferentialGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4173,
        )

        return self.__parent__._cast(
            _4173.BevelDifferentialGearMeshCompoundStabilityAnalysis
        )

    @property
    def bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4178.BevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4178,
        )

        return self.__parent__._cast(_4178.BevelGearMeshCompoundStabilityAnalysis)

    @property
    def clutch_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4183.ClutchConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4183,
        )

        return self.__parent__._cast(_4183.ClutchConnectionCompoundStabilityAnalysis)

    @property
    def concept_coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4188.ConceptCouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4188,
        )

        return self.__parent__._cast(
            _4188.ConceptCouplingConnectionCompoundStabilityAnalysis
        )

    @property
    def concept_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4191.ConceptGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4191,
        )

        return self.__parent__._cast(_4191.ConceptGearMeshCompoundStabilityAnalysis)

    @property
    def conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4194.ConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4194,
        )

        return self.__parent__._cast(_4194.ConicalGearMeshCompoundStabilityAnalysis)

    @property
    def coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4199.CouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4199,
        )

        return self.__parent__._cast(_4199.CouplingConnectionCompoundStabilityAnalysis)

    @property
    def cvt_belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4201.CVTBeltConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4201,
        )

        return self.__parent__._cast(_4201.CVTBeltConnectionCompoundStabilityAnalysis)

    @property
    def cylindrical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4209.CylindricalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4209,
        )

        return self.__parent__._cast(_4209.CylindricalGearMeshCompoundStabilityAnalysis)

    @property
    def face_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4215.FaceGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4215,
        )

        return self.__parent__._cast(_4215.FaceGearMeshCompoundStabilityAnalysis)

    @property
    def gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4220.GearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4220,
        )

        return self.__parent__._cast(_4220.GearMeshCompoundStabilityAnalysis)

    @property
    def hypoid_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4224.HypoidGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4224,
        )

        return self.__parent__._cast(_4224.HypoidGearMeshCompoundStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4228.KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4228,
        )

        return self.__parent__._cast(
            _4228.KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4231.KlingelnbergCycloPalloidHypoidGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4231,
        )

        return self.__parent__._cast(
            _4231.KlingelnbergCycloPalloidHypoidGearMeshCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4234.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4234,
        )

        return self.__parent__._cast(
            _4234.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundStabilityAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4244.PartToPartShearCouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4244,
        )

        return self.__parent__._cast(
            _4244.PartToPartShearCouplingConnectionCompoundStabilityAnalysis
        )

    @property
    def ring_pins_to_disc_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4253.RingPinsToDiscConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4253,
        )

        return self.__parent__._cast(
            _4253.RingPinsToDiscConnectionCompoundStabilityAnalysis
        )

    @property
    def rolling_ring_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4256.RollingRingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4256,
        )

        return self.__parent__._cast(
            _4256.RollingRingConnectionCompoundStabilityAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4263.SpiralBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4263,
        )

        return self.__parent__._cast(_4263.SpiralBevelGearMeshCompoundStabilityAnalysis)

    @property
    def spring_damper_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4266.SpringDamperConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4266,
        )

        return self.__parent__._cast(
            _4266.SpringDamperConnectionCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4269.StraightBevelDiffGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4269,
        )

        return self.__parent__._cast(
            _4269.StraightBevelDiffGearMeshCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4272.StraightBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4272,
        )

        return self.__parent__._cast(
            _4272.StraightBevelGearMeshCompoundStabilityAnalysis
        )

    @property
    def torque_converter_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4281.TorqueConverterConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4281,
        )

        return self.__parent__._cast(
            _4281.TorqueConverterConnectionCompoundStabilityAnalysis
        )

    @property
    def worm_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4287.WormGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4287,
        )

        return self.__parent__._cast(_4287.WormGearMeshCompoundStabilityAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4290.ZerolBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4290,
        )

        return self.__parent__._cast(_4290.ZerolBevelGearMeshCompoundStabilityAnalysis)

    @property
    def inter_mountable_component_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundStabilityAnalysis":
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
class InterMountableComponentConnectionCompoundStabilityAnalysis(
    _4196.ConnectionCompoundStabilityAnalysis
):
    """InterMountableComponentConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS
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
    ) -> "List[_4092.InterMountableComponentConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.InterMountableComponentConnectionStabilityAnalysis]

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
    ) -> "List[_4092.InterMountableComponentConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.InterMountableComponentConnectionStabilityAnalysis]

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
    ) -> "_Cast_InterMountableComponentConnectionCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis
        """
        return _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis(self)
