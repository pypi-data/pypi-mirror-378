"""ConnectionCompoundModalAnalysisAtASpeed"""

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

_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound",
    "ConnectionCompoundModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5436,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
        _5536,
        _5538,
        _5542,
        _5545,
        _5550,
        _5555,
        _5557,
        _5560,
        _5563,
        _5566,
        _5571,
        _5573,
        _5577,
        _5579,
        _5581,
        _5587,
        _5592,
        _5596,
        _5598,
        _5600,
        _5603,
        _5606,
        _5616,
        _5618,
        _5625,
        _5628,
        _5632,
        _5635,
        _5638,
        _5641,
        _5644,
        _5653,
        _5659,
        _5662,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundModalAnalysisAtASpeed._Cast_ConnectionCompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundModalAnalysisAtASpeed:
    """Special nested class for casting ConnectionCompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "ConnectionCompoundModalAnalysisAtASpeed"

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
    def abstract_shaft_to_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> (
        "_5536.AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed"
    ):
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5536,
        )

        return self.__parent__._cast(
            _5536.AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5538.AGMAGleasonConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5538,
        )

        return self.__parent__._cast(
            _5538.AGMAGleasonConicalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def belt_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5542.BeltConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5542,
        )

        return self.__parent__._cast(_5542.BeltConnectionCompoundModalAnalysisAtASpeed)

    @property
    def bevel_differential_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5545.BevelDifferentialGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5545,
        )

        return self.__parent__._cast(
            _5545.BevelDifferentialGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5550.BevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5550,
        )

        return self.__parent__._cast(_5550.BevelGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def clutch_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5555.ClutchConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5555,
        )

        return self.__parent__._cast(
            _5555.ClutchConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def coaxial_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5557.CoaxialConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5557,
        )

        return self.__parent__._cast(
            _5557.CoaxialConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def concept_coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5560.ConceptCouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5560,
        )

        return self.__parent__._cast(
            _5560.ConceptCouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def concept_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5563.ConceptGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5563,
        )

        return self.__parent__._cast(_5563.ConceptGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5566.ConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5566,
        )

        return self.__parent__._cast(_5566.ConicalGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5571.CouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5571,
        )

        return self.__parent__._cast(
            _5571.CouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cvt_belt_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5573.CVTBeltConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5573,
        )

        return self.__parent__._cast(
            _5573.CVTBeltConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5577.CycloidalDiscCentralBearingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5577,
        )

        return self.__parent__._cast(
            _5577.CycloidalDiscCentralBearingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5579.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5579,
        )

        return self.__parent__._cast(
            _5579.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cylindrical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5581.CylindricalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5581,
        )

        return self.__parent__._cast(
            _5581.CylindricalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def face_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5587.FaceGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5587,
        )

        return self.__parent__._cast(_5587.FaceGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5592.GearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5592,
        )

        return self.__parent__._cast(_5592.GearMeshCompoundModalAnalysisAtASpeed)

    @property
    def hypoid_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5596.HypoidGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5596,
        )

        return self.__parent__._cast(_5596.HypoidGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def inter_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5598.InterMountableComponentConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5598,
        )

        return self.__parent__._cast(
            _5598.InterMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5600.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5600,
        )

        return self.__parent__._cast(
            _5600.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5603.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5603,
        )

        return self.__parent__._cast(
            _5603.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> (
        "_5606.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysisAtASpeed"
    ):
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5606,
        )

        return self.__parent__._cast(
            _5606.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def part_to_part_shear_coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5616.PartToPartShearCouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5616,
        )

        return self.__parent__._cast(
            _5616.PartToPartShearCouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def planetary_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5618.PlanetaryConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5618,
        )

        return self.__parent__._cast(
            _5618.PlanetaryConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def ring_pins_to_disc_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5625.RingPinsToDiscConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5625,
        )

        return self.__parent__._cast(
            _5625.RingPinsToDiscConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def rolling_ring_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5628.RollingRingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5628,
        )

        return self.__parent__._cast(
            _5628.RollingRingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def shaft_to_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5632.ShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5632,
        )

        return self.__parent__._cast(
            _5632.ShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def spiral_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5635.SpiralBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5635,
        )

        return self.__parent__._cast(
            _5635.SpiralBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def spring_damper_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5638.SpringDamperConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5638,
        )

        return self.__parent__._cast(
            _5638.SpringDamperConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5641.StraightBevelDiffGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5641,
        )

        return self.__parent__._cast(
            _5641.StraightBevelDiffGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5644.StraightBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5644,
        )

        return self.__parent__._cast(
            _5644.StraightBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def torque_converter_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5653.TorqueConverterConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5653,
        )

        return self.__parent__._cast(
            _5653.TorqueConverterConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def worm_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5659.WormGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5659,
        )

        return self.__parent__._cast(_5659.WormGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5662.ZerolBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5662,
        )

        return self.__parent__._cast(
            _5662.ZerolBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "ConnectionCompoundModalAnalysisAtASpeed":
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
class ConnectionCompoundModalAnalysisAtASpeed(_7886.ConnectionCompoundAnalysis):
    """ConnectionCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

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
    ) -> "List[_5436.ConnectionModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.ConnectionModalAnalysisAtASpeed]

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
    ) -> "List[_5436.ConnectionModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.ConnectionModalAnalysisAtASpeed]

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
    def cast_to(self: "Self") -> "_Cast_ConnectionCompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundModalAnalysisAtASpeed
        """
        return _Cast_ConnectionCompoundModalAnalysisAtASpeed(self)
