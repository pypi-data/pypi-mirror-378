"""PartCompoundSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7893

_PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "PartCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3315,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3368,
        _3369,
        _3370,
        _3372,
        _3374,
        _3375,
        _3376,
        _3378,
        _3379,
        _3381,
        _3382,
        _3383,
        _3384,
        _3386,
        _3387,
        _3388,
        _3389,
        _3391,
        _3393,
        _3394,
        _3396,
        _3397,
        _3399,
        _3400,
        _3402,
        _3404,
        _3405,
        _3407,
        _3409,
        _3410,
        _3411,
        _3413,
        _3415,
        _3417,
        _3418,
        _3419,
        _3420,
        _3421,
        _3423,
        _3424,
        _3425,
        _3426,
        _3428,
        _3429,
        _3430,
        _3432,
        _3434,
        _3436,
        _3437,
        _3439,
        _3440,
        _3442,
        _3443,
        _3444,
        _3445,
        _3446,
        _3447,
        _3448,
        _3450,
        _3452,
        _3454,
        _3455,
        _3456,
        _3457,
        _3458,
        _3459,
        _3461,
        _3462,
        _3464,
        _3465,
        _3466,
        _3468,
        _3469,
        _3471,
        _3472,
        _3474,
        _3475,
        _3477,
        _3478,
        _3480,
        _3481,
        _3482,
        _3483,
        _3484,
        _3485,
        _3486,
        _3487,
        _3489,
        _3490,
        _3491,
        _3492,
        _3493,
        _3495,
        _3496,
        _3498,
    )

    Self = TypeVar("Self", bound="PartCompoundSteadyStateSynchronousResponse")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundSteadyStateSynchronousResponse._Cast_PartCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting PartCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: "PartCompoundSteadyStateSynchronousResponse"

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7893.PartCompoundAnalysis":
        return self.__parent__._cast(_7893.PartCompoundAnalysis)

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
    def abstract_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3368.AbstractAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3368,
        )

        return self.__parent__._cast(
            _3368.AbstractAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def abstract_shaft_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3369.AbstractShaftCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3369,
        )

        return self.__parent__._cast(
            _3369.AbstractShaftCompoundSteadyStateSynchronousResponse
        )

    @property
    def abstract_shaft_or_housing_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3370.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3370,
        )

        return self.__parent__._cast(
            _3370.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse
        )

    @property
    def agma_gleason_conical_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3372.AGMAGleasonConicalGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3372,
        )

        return self.__parent__._cast(
            _3372.AGMAGleasonConicalGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def agma_gleason_conical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3374.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3374,
        )

        return self.__parent__._cast(
            _3374.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3375.AssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3375,
        )

        return self.__parent__._cast(
            _3375.AssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def bearing_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3376.BearingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3376,
        )

        return self.__parent__._cast(
            _3376.BearingCompoundSteadyStateSynchronousResponse
        )

    @property
    def belt_drive_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3378.BeltDriveCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3378,
        )

        return self.__parent__._cast(
            _3378.BeltDriveCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3379.BevelDifferentialGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3379,
        )

        return self.__parent__._cast(
            _3379.BevelDifferentialGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3381.BevelDifferentialGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3381,
        )

        return self.__parent__._cast(
            _3381.BevelDifferentialGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_planet_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3382.BevelDifferentialPlanetGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3382,
        )

        return self.__parent__._cast(
            _3382.BevelDifferentialPlanetGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_sun_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3383.BevelDifferentialSunGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3383,
        )

        return self.__parent__._cast(
            _3383.BevelDifferentialSunGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3384.BevelGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3384,
        )

        return self.__parent__._cast(
            _3384.BevelGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3386.BevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3386,
        )

        return self.__parent__._cast(
            _3386.BevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def bolt_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3387.BoltCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3387,
        )

        return self.__parent__._cast(_3387.BoltCompoundSteadyStateSynchronousResponse)

    @property
    def bolted_joint_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3388.BoltedJointCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3388,
        )

        return self.__parent__._cast(
            _3388.BoltedJointCompoundSteadyStateSynchronousResponse
        )

    @property
    def clutch_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3389.ClutchCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3389,
        )

        return self.__parent__._cast(_3389.ClutchCompoundSteadyStateSynchronousResponse)

    @property
    def clutch_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3391.ClutchHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3391,
        )

        return self.__parent__._cast(
            _3391.ClutchHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3393.ComponentCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3393,
        )

        return self.__parent__._cast(
            _3393.ComponentCompoundSteadyStateSynchronousResponse
        )

    @property
    def concept_coupling_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3394.ConceptCouplingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3394,
        )

        return self.__parent__._cast(
            _3394.ConceptCouplingCompoundSteadyStateSynchronousResponse
        )

    @property
    def concept_coupling_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3396.ConceptCouplingHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3396,
        )

        return self.__parent__._cast(
            _3396.ConceptCouplingHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def concept_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3397.ConceptGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3397,
        )

        return self.__parent__._cast(
            _3397.ConceptGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def concept_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3399.ConceptGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3399,
        )

        return self.__parent__._cast(
            _3399.ConceptGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def conical_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3400.ConicalGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3400,
        )

        return self.__parent__._cast(
            _3400.ConicalGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def conical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3402.ConicalGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3402,
        )

        return self.__parent__._cast(
            _3402.ConicalGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def connector_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3404.ConnectorCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3404,
        )

        return self.__parent__._cast(
            _3404.ConnectorCompoundSteadyStateSynchronousResponse
        )

    @property
    def coupling_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3405.CouplingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3405,
        )

        return self.__parent__._cast(
            _3405.CouplingCompoundSteadyStateSynchronousResponse
        )

    @property
    def coupling_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3407.CouplingHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3407,
        )

        return self.__parent__._cast(
            _3407.CouplingHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def cvt_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3409.CVTCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3409,
        )

        return self.__parent__._cast(_3409.CVTCompoundSteadyStateSynchronousResponse)

    @property
    def cvt_pulley_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3410.CVTPulleyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3410,
        )

        return self.__parent__._cast(
            _3410.CVTPulleyCompoundSteadyStateSynchronousResponse
        )

    @property
    def cycloidal_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3411.CycloidalAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3411,
        )

        return self.__parent__._cast(
            _3411.CycloidalAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def cycloidal_disc_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3413.CycloidalDiscCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3413,
        )

        return self.__parent__._cast(
            _3413.CycloidalDiscCompoundSteadyStateSynchronousResponse
        )

    @property
    def cylindrical_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3415.CylindricalGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3415,
        )

        return self.__parent__._cast(
            _3415.CylindricalGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def cylindrical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3417.CylindricalGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3417,
        )

        return self.__parent__._cast(
            _3417.CylindricalGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def cylindrical_planet_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3418.CylindricalPlanetGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3418,
        )

        return self.__parent__._cast(
            _3418.CylindricalPlanetGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def datum_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3419.DatumCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3419,
        )

        return self.__parent__._cast(_3419.DatumCompoundSteadyStateSynchronousResponse)

    @property
    def external_cad_model_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3420.ExternalCADModelCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3420,
        )

        return self.__parent__._cast(
            _3420.ExternalCADModelCompoundSteadyStateSynchronousResponse
        )

    @property
    def face_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3421.FaceGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3421,
        )

        return self.__parent__._cast(
            _3421.FaceGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def face_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3423.FaceGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3423,
        )

        return self.__parent__._cast(
            _3423.FaceGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def fe_part_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3424.FEPartCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3424,
        )

        return self.__parent__._cast(_3424.FEPartCompoundSteadyStateSynchronousResponse)

    @property
    def flexible_pin_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3425.FlexiblePinAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3425,
        )

        return self.__parent__._cast(
            _3425.FlexiblePinAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3426.GearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3426,
        )

        return self.__parent__._cast(_3426.GearCompoundSteadyStateSynchronousResponse)

    @property
    def gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3428.GearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3428,
        )

        return self.__parent__._cast(
            _3428.GearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def guide_dxf_model_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3429.GuideDxfModelCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3429,
        )

        return self.__parent__._cast(
            _3429.GuideDxfModelCompoundSteadyStateSynchronousResponse
        )

    @property
    def hypoid_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3430.HypoidGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3430,
        )

        return self.__parent__._cast(
            _3430.HypoidGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def hypoid_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3432.HypoidGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3432,
        )

        return self.__parent__._cast(
            _3432.HypoidGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3434.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3434,
        )

        return self.__parent__._cast(
            _3434.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3436.KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3436,
        )

        return self.__parent__._cast(
            _3436.KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> (
        "_3437.KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponse"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3437,
        )

        return self.__parent__._cast(
            _3437.KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3439.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3439,
        )

        return self.__parent__._cast(
            _3439.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3440.KlingelnbergCycloPalloidSpiralBevelGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3440,
        )

        return self.__parent__._cast(
            _3440.KlingelnbergCycloPalloidSpiralBevelGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3442.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3442,
        )

        return self.__parent__._cast(
            _3442.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def mass_disc_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3443.MassDiscCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3443,
        )

        return self.__parent__._cast(
            _3443.MassDiscCompoundSteadyStateSynchronousResponse
        )

    @property
    def measurement_component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3444.MeasurementComponentCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3444,
        )

        return self.__parent__._cast(
            _3444.MeasurementComponentCompoundSteadyStateSynchronousResponse
        )

    @property
    def microphone_array_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3445.MicrophoneArrayCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3445,
        )

        return self.__parent__._cast(
            _3445.MicrophoneArrayCompoundSteadyStateSynchronousResponse
        )

    @property
    def microphone_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3446.MicrophoneCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3446,
        )

        return self.__parent__._cast(
            _3446.MicrophoneCompoundSteadyStateSynchronousResponse
        )

    @property
    def mountable_component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3447.MountableComponentCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3447,
        )

        return self.__parent__._cast(
            _3447.MountableComponentCompoundSteadyStateSynchronousResponse
        )

    @property
    def oil_seal_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3448.OilSealCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3448,
        )

        return self.__parent__._cast(
            _3448.OilSealCompoundSteadyStateSynchronousResponse
        )

    @property
    def part_to_part_shear_coupling_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3450.PartToPartShearCouplingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3450,
        )

        return self.__parent__._cast(
            _3450.PartToPartShearCouplingCompoundSteadyStateSynchronousResponse
        )

    @property
    def part_to_part_shear_coupling_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3452.PartToPartShearCouplingHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3452,
        )

        return self.__parent__._cast(
            _3452.PartToPartShearCouplingHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def planetary_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3454.PlanetaryGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3454,
        )

        return self.__parent__._cast(
            _3454.PlanetaryGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def planet_carrier_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3455.PlanetCarrierCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3455,
        )

        return self.__parent__._cast(
            _3455.PlanetCarrierCompoundSteadyStateSynchronousResponse
        )

    @property
    def point_load_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3456.PointLoadCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3456,
        )

        return self.__parent__._cast(
            _3456.PointLoadCompoundSteadyStateSynchronousResponse
        )

    @property
    def power_load_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3457.PowerLoadCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3457,
        )

        return self.__parent__._cast(
            _3457.PowerLoadCompoundSteadyStateSynchronousResponse
        )

    @property
    def pulley_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3458.PulleyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3458,
        )

        return self.__parent__._cast(_3458.PulleyCompoundSteadyStateSynchronousResponse)

    @property
    def ring_pins_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3459.RingPinsCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3459,
        )

        return self.__parent__._cast(
            _3459.RingPinsCompoundSteadyStateSynchronousResponse
        )

    @property
    def rolling_ring_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3461.RollingRingAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3461,
        )

        return self.__parent__._cast(
            _3461.RollingRingAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def rolling_ring_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3462.RollingRingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3462,
        )

        return self.__parent__._cast(
            _3462.RollingRingCompoundSteadyStateSynchronousResponse
        )

    @property
    def root_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3464.RootAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3464,
        )

        return self.__parent__._cast(
            _3464.RootAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def shaft_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3465.ShaftCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3465,
        )

        return self.__parent__._cast(_3465.ShaftCompoundSteadyStateSynchronousResponse)

    @property
    def shaft_hub_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3466.ShaftHubConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3466,
        )

        return self.__parent__._cast(
            _3466.ShaftHubConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def specialised_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3468.SpecialisedAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3468,
        )

        return self.__parent__._cast(
            _3468.SpecialisedAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def spiral_bevel_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3469.SpiralBevelGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3469,
        )

        return self.__parent__._cast(
            _3469.SpiralBevelGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def spiral_bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3471.SpiralBevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3471,
        )

        return self.__parent__._cast(
            _3471.SpiralBevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3472.SpringDamperCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3472,
        )

        return self.__parent__._cast(
            _3472.SpringDamperCompoundSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3474.SpringDamperHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3474,
        )

        return self.__parent__._cast(
            _3474.SpringDamperHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_diff_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3475.StraightBevelDiffGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3475,
        )

        return self.__parent__._cast(
            _3475.StraightBevelDiffGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_diff_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3477.StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3477,
        )

        return self.__parent__._cast(
            _3477.StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3478.StraightBevelGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3478,
        )

        return self.__parent__._cast(
            _3478.StraightBevelGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3480.StraightBevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3480,
        )

        return self.__parent__._cast(
            _3480.StraightBevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_planet_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3481.StraightBevelPlanetGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3481,
        )

        return self.__parent__._cast(
            _3481.StraightBevelPlanetGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_sun_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3482.StraightBevelSunGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3482,
        )

        return self.__parent__._cast(
            _3482.StraightBevelSunGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3483.SynchroniserCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3483,
        )

        return self.__parent__._cast(
            _3483.SynchroniserCompoundSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_half_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3484.SynchroniserHalfCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3484,
        )

        return self.__parent__._cast(
            _3484.SynchroniserHalfCompoundSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_part_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3485.SynchroniserPartCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3485,
        )

        return self.__parent__._cast(
            _3485.SynchroniserPartCompoundSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_sleeve_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3486.SynchroniserSleeveCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3486,
        )

        return self.__parent__._cast(
            _3486.SynchroniserSleeveCompoundSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3487.TorqueConverterCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3487,
        )

        return self.__parent__._cast(
            _3487.TorqueConverterCompoundSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_pump_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3489.TorqueConverterPumpCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3489,
        )

        return self.__parent__._cast(
            _3489.TorqueConverterPumpCompoundSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_turbine_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3490.TorqueConverterTurbineCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3490,
        )

        return self.__parent__._cast(
            _3490.TorqueConverterTurbineCompoundSteadyStateSynchronousResponse
        )

    @property
    def unbalanced_mass_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3491.UnbalancedMassCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3491,
        )

        return self.__parent__._cast(
            _3491.UnbalancedMassCompoundSteadyStateSynchronousResponse
        )

    @property
    def virtual_component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3492.VirtualComponentCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3492,
        )

        return self.__parent__._cast(
            _3492.VirtualComponentCompoundSteadyStateSynchronousResponse
        )

    @property
    def worm_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3493.WormGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3493,
        )

        return self.__parent__._cast(
            _3493.WormGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def worm_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3495.WormGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3495,
        )

        return self.__parent__._cast(
            _3495.WormGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def zerol_bevel_gear_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3496.ZerolBevelGearCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3496,
        )

        return self.__parent__._cast(
            _3496.ZerolBevelGearCompoundSteadyStateSynchronousResponse
        )

    @property
    def zerol_bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3498.ZerolBevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3498,
        )

        return self.__parent__._cast(
            _3498.ZerolBevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def part_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "PartCompoundSteadyStateSynchronousResponse":
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
class PartCompoundSteadyStateSynchronousResponse(_7893.PartCompoundAnalysis):
    """PartCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3315.PartSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.PartSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3315.PartSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.PartSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_PartCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundSteadyStateSynchronousResponse
        """
        return _Cast_PartCompoundSteadyStateSynchronousResponse(self)
