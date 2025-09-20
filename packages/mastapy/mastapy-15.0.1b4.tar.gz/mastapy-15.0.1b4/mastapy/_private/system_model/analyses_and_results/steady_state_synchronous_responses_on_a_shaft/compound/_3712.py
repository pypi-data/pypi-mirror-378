"""PartCompoundSteadyStateSynchronousResponseOnAShaft"""

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

_PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound",
    "PartCompoundSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3580,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
        _3631,
        _3632,
        _3633,
        _3635,
        _3637,
        _3638,
        _3639,
        _3641,
        _3642,
        _3644,
        _3645,
        _3646,
        _3647,
        _3649,
        _3650,
        _3651,
        _3652,
        _3654,
        _3656,
        _3657,
        _3659,
        _3660,
        _3662,
        _3663,
        _3665,
        _3667,
        _3668,
        _3670,
        _3672,
        _3673,
        _3674,
        _3676,
        _3678,
        _3680,
        _3681,
        _3682,
        _3683,
        _3684,
        _3686,
        _3687,
        _3688,
        _3689,
        _3691,
        _3692,
        _3693,
        _3695,
        _3697,
        _3699,
        _3700,
        _3702,
        _3703,
        _3705,
        _3706,
        _3707,
        _3708,
        _3709,
        _3710,
        _3711,
        _3713,
        _3715,
        _3717,
        _3718,
        _3719,
        _3720,
        _3721,
        _3722,
        _3724,
        _3725,
        _3727,
        _3728,
        _3729,
        _3731,
        _3732,
        _3734,
        _3735,
        _3737,
        _3738,
        _3740,
        _3741,
        _3743,
        _3744,
        _3745,
        _3746,
        _3747,
        _3748,
        _3749,
        _3750,
        _3752,
        _3753,
        _3754,
        _3755,
        _3756,
        _3758,
        _3759,
        _3761,
    )

    Self = TypeVar("Self", bound="PartCompoundSteadyStateSynchronousResponseOnAShaft")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundSteadyStateSynchronousResponseOnAShaft._Cast_PartCompoundSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundSteadyStateSynchronousResponseOnAShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting PartCompoundSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "PartCompoundSteadyStateSynchronousResponseOnAShaft"

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
    def abstract_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3631.AbstractAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3631,
        )

        return self.__parent__._cast(
            _3631.AbstractAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_shaft_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3632.AbstractShaftCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3632,
        )

        return self.__parent__._cast(
            _3632.AbstractShaftCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_shaft_or_housing_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3633.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3633,
        )

        return self.__parent__._cast(
            _3633.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3635.AGMAGleasonConicalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3635,
        )

        return self.__parent__._cast(
            _3635.AGMAGleasonConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3637.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3637,
        )

        return self.__parent__._cast(
            _3637.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3638.AssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3638,
        )

        return self.__parent__._cast(
            _3638.AssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bearing_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3639.BearingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3639,
        )

        return self.__parent__._cast(
            _3639.BearingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def belt_drive_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3641.BeltDriveCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3641,
        )

        return self.__parent__._cast(
            _3641.BeltDriveCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3642.BevelDifferentialGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3642,
        )

        return self.__parent__._cast(
            _3642.BevelDifferentialGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3644.BevelDifferentialGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3644,
        )

        return self.__parent__._cast(
            _3644.BevelDifferentialGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_planet_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3645.BevelDifferentialPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3645,
        )

        return self.__parent__._cast(
            _3645.BevelDifferentialPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_sun_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3646.BevelDifferentialSunGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3646,
        )

        return self.__parent__._cast(
            _3646.BevelDifferentialSunGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3647.BevelGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3647,
        )

        return self.__parent__._cast(
            _3647.BevelGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3649.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3649,
        )

        return self.__parent__._cast(
            _3649.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bolt_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3650.BoltCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3650,
        )

        return self.__parent__._cast(
            _3650.BoltCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bolted_joint_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3651.BoltedJointCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3651,
        )

        return self.__parent__._cast(
            _3651.BoltedJointCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def clutch_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3652.ClutchCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3652,
        )

        return self.__parent__._cast(
            _3652.ClutchCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def clutch_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3654.ClutchHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3654,
        )

        return self.__parent__._cast(
            _3654.ClutchHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3656.ComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3656,
        )

        return self.__parent__._cast(
            _3656.ComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3657.ConceptCouplingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3657,
        )

        return self.__parent__._cast(
            _3657.ConceptCouplingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3659.ConceptCouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3659,
        )

        return self.__parent__._cast(
            _3659.ConceptCouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3660.ConceptGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3660,
        )

        return self.__parent__._cast(
            _3660.ConceptGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3662.ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3662,
        )

        return self.__parent__._cast(
            _3662.ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3663.ConicalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3663,
        )

        return self.__parent__._cast(
            _3663.ConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3665.ConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3665,
        )

        return self.__parent__._cast(
            _3665.ConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def connector_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3667.ConnectorCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3667,
        )

        return self.__parent__._cast(
            _3667.ConnectorCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3668.CouplingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3668,
        )

        return self.__parent__._cast(
            _3668.CouplingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3670.CouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3670,
        )

        return self.__parent__._cast(
            _3670.CouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3672.CVTCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3672,
        )

        return self.__parent__._cast(
            _3672.CVTCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_pulley_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3673.CVTPulleyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3673,
        )

        return self.__parent__._cast(
            _3673.CVTPulleyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cycloidal_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3674.CycloidalAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3674,
        )

        return self.__parent__._cast(
            _3674.CycloidalAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cycloidal_disc_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3676.CycloidalDiscCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3676,
        )

        return self.__parent__._cast(
            _3676.CycloidalDiscCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3678.CylindricalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3678,
        )

        return self.__parent__._cast(
            _3678.CylindricalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3680.CylindricalGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3680,
        )

        return self.__parent__._cast(
            _3680.CylindricalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_planet_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3681.CylindricalPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3681,
        )

        return self.__parent__._cast(
            _3681.CylindricalPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def datum_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3682.DatumCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3682,
        )

        return self.__parent__._cast(
            _3682.DatumCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def external_cad_model_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3683.ExternalCADModelCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3683,
        )

        return self.__parent__._cast(
            _3683.ExternalCADModelCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3684.FaceGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3684,
        )

        return self.__parent__._cast(
            _3684.FaceGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3686.FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3686,
        )

        return self.__parent__._cast(
            _3686.FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def fe_part_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3687.FEPartCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3687,
        )

        return self.__parent__._cast(
            _3687.FEPartCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def flexible_pin_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3688.FlexiblePinAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3688,
        )

        return self.__parent__._cast(
            _3688.FlexiblePinAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3689.GearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3689,
        )

        return self.__parent__._cast(
            _3689.GearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3691.GearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3691,
        )

        return self.__parent__._cast(
            _3691.GearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def guide_dxf_model_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3692.GuideDxfModelCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3692,
        )

        return self.__parent__._cast(
            _3692.GuideDxfModelCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3693.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3693,
        )

        return self.__parent__._cast(
            _3693.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3695.HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3695,
        )

        return self.__parent__._cast(
            _3695.HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3697.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3697,
        )

        return self.__parent__._cast(
            _3697.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3699.KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3699,
        )

        return self.__parent__._cast(
            _3699.KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3700.KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3700,
        )

        return self.__parent__._cast(
            _3700.KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3702.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3702,
        )

        return self.__parent__._cast(
            _3702.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3703.KlingelnbergCycloPalloidSpiralBevelGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3703,
        )

        return self.__parent__._cast(
            _3703.KlingelnbergCycloPalloidSpiralBevelGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3705.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3705,
        )

        return self.__parent__._cast(
            _3705.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mass_disc_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3706.MassDiscCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3706,
        )

        return self.__parent__._cast(
            _3706.MassDiscCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def measurement_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3707.MeasurementComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3707,
        )

        return self.__parent__._cast(
            _3707.MeasurementComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def microphone_array_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3708.MicrophoneArrayCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3708,
        )

        return self.__parent__._cast(
            _3708.MicrophoneArrayCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def microphone_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3709.MicrophoneCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3709,
        )

        return self.__parent__._cast(
            _3709.MicrophoneCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mountable_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3710.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3710,
        )

        return self.__parent__._cast(
            _3710.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def oil_seal_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3711.OilSealCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3711,
        )

        return self.__parent__._cast(
            _3711.OilSealCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_to_part_shear_coupling_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3713.PartToPartShearCouplingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3713,
        )

        return self.__parent__._cast(
            _3713.PartToPartShearCouplingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_to_part_shear_coupling_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3715.PartToPartShearCouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3715,
        )

        return self.__parent__._cast(
            _3715.PartToPartShearCouplingHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def planetary_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3717.PlanetaryGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3717,
        )

        return self.__parent__._cast(
            _3717.PlanetaryGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def planet_carrier_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3718.PlanetCarrierCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3718,
        )

        return self.__parent__._cast(
            _3718.PlanetCarrierCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def point_load_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3719.PointLoadCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3719,
        )

        return self.__parent__._cast(
            _3719.PointLoadCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def power_load_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3720.PowerLoadCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3720,
        )

        return self.__parent__._cast(
            _3720.PowerLoadCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def pulley_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3721.PulleyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3721,
        )

        return self.__parent__._cast(
            _3721.PulleyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def ring_pins_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3722.RingPinsCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3722,
        )

        return self.__parent__._cast(
            _3722.RingPinsCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3724.RollingRingAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3724,
        )

        return self.__parent__._cast(
            _3724.RollingRingAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3725.RollingRingCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3725,
        )

        return self.__parent__._cast(
            _3725.RollingRingCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def root_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3727.RootAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3727,
        )

        return self.__parent__._cast(
            _3727.RootAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def shaft_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3728.ShaftCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3728,
        )

        return self.__parent__._cast(
            _3728.ShaftCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def shaft_hub_connection_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3729.ShaftHubConnectionCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3729,
        )

        return self.__parent__._cast(
            _3729.ShaftHubConnectionCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def specialised_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3731.SpecialisedAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3731,
        )

        return self.__parent__._cast(
            _3731.SpecialisedAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3732.SpiralBevelGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3732,
        )

        return self.__parent__._cast(
            _3732.SpiralBevelGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3734.SpiralBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3734,
        )

        return self.__parent__._cast(
            _3734.SpiralBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3735.SpringDamperCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3735,
        )

        return self.__parent__._cast(
            _3735.SpringDamperCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3737.SpringDamperHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3737,
        )

        return self.__parent__._cast(
            _3737.SpringDamperHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3738.StraightBevelDiffGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3738,
        )

        return self.__parent__._cast(
            _3738.StraightBevelDiffGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3740.StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3740,
        )

        return self.__parent__._cast(
            _3740.StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3741.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3741,
        )

        return self.__parent__._cast(
            _3741.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3743.StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3743,
        )

        return self.__parent__._cast(
            _3743.StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_planet_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3744.StraightBevelPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3744,
        )

        return self.__parent__._cast(
            _3744.StraightBevelPlanetGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_sun_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3745.StraightBevelSunGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3745,
        )

        return self.__parent__._cast(
            _3745.StraightBevelSunGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3746.SynchroniserCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3746,
        )

        return self.__parent__._cast(
            _3746.SynchroniserCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_half_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3747.SynchroniserHalfCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3747,
        )

        return self.__parent__._cast(
            _3747.SynchroniserHalfCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_part_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3748.SynchroniserPartCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3748,
        )

        return self.__parent__._cast(
            _3748.SynchroniserPartCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_sleeve_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3749.SynchroniserSleeveCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3749,
        )

        return self.__parent__._cast(
            _3749.SynchroniserSleeveCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3750.TorqueConverterCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3750,
        )

        return self.__parent__._cast(
            _3750.TorqueConverterCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_pump_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3752.TorqueConverterPumpCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3752,
        )

        return self.__parent__._cast(
            _3752.TorqueConverterPumpCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_turbine_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3753.TorqueConverterTurbineCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3753,
        )

        return self.__parent__._cast(
            _3753.TorqueConverterTurbineCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def unbalanced_mass_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3754.UnbalancedMassCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3754,
        )

        return self.__parent__._cast(
            _3754.UnbalancedMassCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def virtual_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3755.VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3755,
        )

        return self.__parent__._cast(
            _3755.VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3756.WormGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3756,
        )

        return self.__parent__._cast(
            _3756.WormGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3758.WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3758,
        )

        return self.__parent__._cast(
            _3758.WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3759.ZerolBevelGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3759,
        )

        return self.__parent__._cast(
            _3759.ZerolBevelGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3761.ZerolBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3761,
        )

        return self.__parent__._cast(
            _3761.ZerolBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "PartCompoundSteadyStateSynchronousResponseOnAShaft":
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
class PartCompoundSteadyStateSynchronousResponseOnAShaft(_7893.PartCompoundAnalysis):
    """PartCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

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
    ) -> "List[_3580.PartSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.PartSteadyStateSynchronousResponseOnAShaft]

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
    ) -> "List[_3580.PartSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.PartSteadyStateSynchronousResponseOnAShaft]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_PartCompoundSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_PartCompoundSteadyStateSynchronousResponseOnAShaft(self)
