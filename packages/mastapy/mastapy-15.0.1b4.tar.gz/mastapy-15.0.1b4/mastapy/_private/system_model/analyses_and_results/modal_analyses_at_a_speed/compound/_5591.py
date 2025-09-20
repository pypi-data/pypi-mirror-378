"""GearCompoundModalAnalysisAtASpeed"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
    _5612,
)

_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound",
    "GearCompoundModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5460,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
        _5537,
        _5544,
        _5547,
        _5548,
        _5549,
        _5558,
        _5562,
        _5565,
        _5580,
        _5583,
        _5586,
        _5595,
        _5599,
        _5602,
        _5605,
        _5614,
        _5634,
        _5640,
        _5643,
        _5646,
        _5647,
        _5658,
        _5661,
    )

    Self = TypeVar("Self", bound="GearCompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearCompoundModalAnalysisAtASpeed._Cast_GearCompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearCompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearCompoundModalAnalysisAtASpeed:
    """Special nested class for casting GearCompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "GearCompoundModalAnalysisAtASpeed"

    @property
    def mountable_component_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5612.MountableComponentCompoundModalAnalysisAtASpeed":
        return self.__parent__._cast(
            _5612.MountableComponentCompoundModalAnalysisAtASpeed
        )

    @property
    def component_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5558.ComponentCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5558,
        )

        return self.__parent__._cast(_5558.ComponentCompoundModalAnalysisAtASpeed)

    @property
    def part_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5614.PartCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5614,
        )

        return self.__parent__._cast(_5614.PartCompoundModalAnalysisAtASpeed)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7893.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7893,
        )

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
    def agma_gleason_conical_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5537.AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5537,
        )

        return self.__parent__._cast(
            _5537.AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5544.BevelDifferentialGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5544,
        )

        return self.__parent__._cast(
            _5544.BevelDifferentialGearCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_planet_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5547.BevelDifferentialPlanetGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5547,
        )

        return self.__parent__._cast(
            _5547.BevelDifferentialPlanetGearCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_sun_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5548.BevelDifferentialSunGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5548,
        )

        return self.__parent__._cast(
            _5548.BevelDifferentialSunGearCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5549.BevelGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5549,
        )

        return self.__parent__._cast(_5549.BevelGearCompoundModalAnalysisAtASpeed)

    @property
    def concept_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5562.ConceptGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5562,
        )

        return self.__parent__._cast(_5562.ConceptGearCompoundModalAnalysisAtASpeed)

    @property
    def conical_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5565.ConicalGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5565,
        )

        return self.__parent__._cast(_5565.ConicalGearCompoundModalAnalysisAtASpeed)

    @property
    def cylindrical_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5580.CylindricalGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5580,
        )

        return self.__parent__._cast(_5580.CylindricalGearCompoundModalAnalysisAtASpeed)

    @property
    def cylindrical_planet_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5583.CylindricalPlanetGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5583,
        )

        return self.__parent__._cast(
            _5583.CylindricalPlanetGearCompoundModalAnalysisAtASpeed
        )

    @property
    def face_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5586.FaceGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5586,
        )

        return self.__parent__._cast(_5586.FaceGearCompoundModalAnalysisAtASpeed)

    @property
    def hypoid_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5595.HypoidGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5595,
        )

        return self.__parent__._cast(_5595.HypoidGearCompoundModalAnalysisAtASpeed)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5599.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5599,
        )

        return self.__parent__._cast(
            _5599.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5602.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5602,
        )

        return self.__parent__._cast(
            _5602.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5605.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5605,
        )

        return self.__parent__._cast(
            _5605.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysisAtASpeed
        )

    @property
    def spiral_bevel_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5634.SpiralBevelGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5634,
        )

        return self.__parent__._cast(_5634.SpiralBevelGearCompoundModalAnalysisAtASpeed)

    @property
    def straight_bevel_diff_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5640.StraightBevelDiffGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5640,
        )

        return self.__parent__._cast(
            _5640.StraightBevelDiffGearCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5643.StraightBevelGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5643,
        )

        return self.__parent__._cast(
            _5643.StraightBevelGearCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_planet_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5646.StraightBevelPlanetGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5646,
        )

        return self.__parent__._cast(
            _5646.StraightBevelPlanetGearCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_sun_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5647.StraightBevelSunGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5647,
        )

        return self.__parent__._cast(
            _5647.StraightBevelSunGearCompoundModalAnalysisAtASpeed
        )

    @property
    def worm_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5658.WormGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5658,
        )

        return self.__parent__._cast(_5658.WormGearCompoundModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5661.ZerolBevelGearCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5661,
        )

        return self.__parent__._cast(_5661.ZerolBevelGearCompoundModalAnalysisAtASpeed)

    @property
    def gear_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "GearCompoundModalAnalysisAtASpeed":
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
class GearCompoundModalAnalysisAtASpeed(
    _5612.MountableComponentCompoundModalAnalysisAtASpeed
):
    """GearCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

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
    ) -> "List[_5460.GearModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.GearModalAnalysisAtASpeed]

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
    ) -> "List[_5460.GearModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.GearModalAnalysisAtASpeed]

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
    def cast_to(self: "Self") -> "_Cast_GearCompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_GearCompoundModalAnalysisAtASpeed
        """
        return _Cast_GearCompoundModalAnalysisAtASpeed(self)
