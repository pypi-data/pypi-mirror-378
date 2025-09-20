"""InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
    _3666,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound",
    "InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3564,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
        _3636,
        _3640,
        _3643,
        _3648,
        _3653,
        _3658,
        _3661,
        _3664,
        _3669,
        _3671,
        _3679,
        _3685,
        _3690,
        _3694,
        _3698,
        _3701,
        _3704,
        _3714,
        _3723,
        _3726,
        _3733,
        _3736,
        _3739,
        _3742,
        _3751,
        _3757,
        _3760,
    )

    Self = TypeVar(
        "Self",
        bound="InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft._Cast_InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = (
    "InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft",
)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft"

    @property
    def connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3666.ConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3666.ConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

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
    def agma_gleason_conical_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3636.AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3636,
        )

        return self.__parent__._cast(
            _3636.AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def belt_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3640.BeltConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3640,
        )

        return self.__parent__._cast(
            _3640.BeltConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3643.BevelDifferentialGearMeshCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3643,
        )

        return self.__parent__._cast(
            _3643.BevelDifferentialGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3648.BevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3648,
        )

        return self.__parent__._cast(
            _3648.BevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def clutch_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3653.ClutchConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3653,
        )

        return self.__parent__._cast(
            _3653.ClutchConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3658.ConceptCouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3658,
        )

        return self.__parent__._cast(
            _3658.ConceptCouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3661.ConceptGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3661,
        )

        return self.__parent__._cast(
            _3661.ConceptGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3664.ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3664,
        )

        return self.__parent__._cast(
            _3664.ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3669.CouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3669,
        )

        return self.__parent__._cast(
            _3669.CouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_belt_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3671.CVTBeltConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3671,
        )

        return self.__parent__._cast(
            _3671.CVTBeltConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3679.CylindricalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3679,
        )

        return self.__parent__._cast(
            _3679.CylindricalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3685.FaceGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3685,
        )

        return self.__parent__._cast(
            _3685.FaceGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3690.GearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3690,
        )

        return self.__parent__._cast(
            _3690.GearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3694.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3694,
        )

        return self.__parent__._cast(
            _3694.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3698.KlingelnbergCycloPalloidConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3698,
        )

        return self.__parent__._cast(
            _3698.KlingelnbergCycloPalloidConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3701.KlingelnbergCycloPalloidHypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3701,
        )

        return self.__parent__._cast(
            _3701.KlingelnbergCycloPalloidHypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3704.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3704,
        )

        return self.__parent__._cast(
            _3704.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_to_part_shear_coupling_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3714.PartToPartShearCouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3714,
        )

        return self.__parent__._cast(
            _3714.PartToPartShearCouplingConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def ring_pins_to_disc_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3723.RingPinsToDiscConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3723,
        )

        return self.__parent__._cast(
            _3723.RingPinsToDiscConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3726.RollingRingConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3726,
        )

        return self.__parent__._cast(
            _3726.RollingRingConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3733.SpiralBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3733,
        )

        return self.__parent__._cast(
            _3733.SpiralBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3736.SpringDamperConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3736,
        )

        return self.__parent__._cast(
            _3736.SpringDamperConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3739.StraightBevelDiffGearMeshCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3739,
        )

        return self.__parent__._cast(
            _3739.StraightBevelDiffGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3742.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3742,
        )

        return self.__parent__._cast(
            _3742.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3751.TorqueConverterConnectionCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3751,
        )

        return self.__parent__._cast(
            _3751.TorqueConverterConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3757.WormGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3757,
        )

        return self.__parent__._cast(
            _3757.WormGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_mesh_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3760.ZerolBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3760,
        )

        return self.__parent__._cast(
            _3760.ZerolBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def inter_mountable_component_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
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
class InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft(
    _3666.ConnectionCompoundSteadyStateSynchronousResponseOnAShaft
):
    """InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
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
    ) -> "List[_3564.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft]

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
    ) -> "List[_3564.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft]

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
    ) -> "_Cast_InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_InterMountableComponentConnectionCompoundSteadyStateSynchronousResponseOnAShaft(
            self
        )
