"""ConnectionCompoundMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7886

_CONNECTION_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "ConnectionCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5703
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5825,
        _5827,
        _5831,
        _5834,
        _5839,
        _5844,
        _5846,
        _5849,
        _5852,
        _5855,
        _5860,
        _5862,
        _5866,
        _5868,
        _5870,
        _5876,
        _5881,
        _5885,
        _5887,
        _5889,
        _5892,
        _5895,
        _5905,
        _5907,
        _5914,
        _5917,
        _5921,
        _5924,
        _5927,
        _5930,
        _5933,
        _5942,
        _5948,
        _5951,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundMultibodyDynamicsAnalysis._Cast_ConnectionCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting ConnectionCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "ConnectionCompoundMultibodyDynamicsAnalysis"

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
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
    def abstract_shaft_to_mountable_component_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5825.AbstractShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5825,
        )

        return self.__parent__._cast(
            _5825.AbstractShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5827.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5827,
        )

        return self.__parent__._cast(
            _5827.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def belt_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5831.BeltConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5831,
        )

        return self.__parent__._cast(
            _5831.BeltConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5834.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5834,
        )

        return self.__parent__._cast(
            _5834.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5839.BevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5839,
        )

        return self.__parent__._cast(
            _5839.BevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def clutch_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5844.ClutchConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5844,
        )

        return self.__parent__._cast(
            _5844.ClutchConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def coaxial_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5846.CoaxialConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5846,
        )

        return self.__parent__._cast(
            _5846.CoaxialConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5849.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5849,
        )

        return self.__parent__._cast(
            _5849.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5852.ConceptGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5852,
        )

        return self.__parent__._cast(
            _5852.ConceptGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5855.ConicalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5855,
        )

        return self.__parent__._cast(
            _5855.ConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5860.CouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5860,
        )

        return self.__parent__._cast(
            _5860.CouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cvt_belt_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5862.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5862,
        )

        return self.__parent__._cast(
            _5862.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5866.CycloidalDiscCentralBearingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5866,
        )

        return self.__parent__._cast(
            _5866.CycloidalDiscCentralBearingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5868.CycloidalDiscPlanetaryBearingConnectionCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5868,
        )

        return self.__parent__._cast(
            _5868.CycloidalDiscPlanetaryBearingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cylindrical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5870.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5870,
        )

        return self.__parent__._cast(
            _5870.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def face_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5876.FaceGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5876,
        )

        return self.__parent__._cast(
            _5876.FaceGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5881.GearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5881,
        )

        return self.__parent__._cast(_5881.GearMeshCompoundMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5885.HypoidGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5885,
        )

        return self.__parent__._cast(
            _5885.HypoidGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def inter_mountable_component_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5887.InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5887,
        )

        return self.__parent__._cast(
            _5887.InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5889.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5889,
        )

        return self.__parent__._cast(
            _5889.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5892.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5892,
        )

        return self.__parent__._cast(
            _5892.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5895.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5895,
        )

        return self.__parent__._cast(
            _5895.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5905.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5905,
        )

        return self.__parent__._cast(
            _5905.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def planetary_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5907.PlanetaryConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5907,
        )

        return self.__parent__._cast(
            _5907.PlanetaryConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def ring_pins_to_disc_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5914.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5914,
        )

        return self.__parent__._cast(
            _5914.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def rolling_ring_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5917.RollingRingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5917,
        )

        return self.__parent__._cast(
            _5917.RollingRingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def shaft_to_mountable_component_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5921.ShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5921,
        )

        return self.__parent__._cast(
            _5921.ShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5924.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5924,
        )

        return self.__parent__._cast(
            _5924.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spring_damper_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5927.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5927,
        )

        return self.__parent__._cast(
            _5927.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5930.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5930,
        )

        return self.__parent__._cast(
            _5930.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5933.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5933,
        )

        return self.__parent__._cast(
            _5933.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5942.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5942,
        )

        return self.__parent__._cast(
            _5942.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def worm_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5948.WormGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5948,
        )

        return self.__parent__._cast(
            _5948.WormGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def zerol_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5951.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5951,
        )

        return self.__parent__._cast(
            _5951.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "ConnectionCompoundMultibodyDynamicsAnalysis":
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
class ConnectionCompoundMultibodyDynamicsAnalysis(_7886.ConnectionCompoundAnalysis):
    """ConnectionCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

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
    ) -> "List[_5703.ConnectionMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.ConnectionMultibodyDynamicsAnalysis]

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
    ) -> "List[_5703.ConnectionMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.ConnectionMultibodyDynamicsAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_ConnectionCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_ConnectionCompoundMultibodyDynamicsAnalysis(self)
