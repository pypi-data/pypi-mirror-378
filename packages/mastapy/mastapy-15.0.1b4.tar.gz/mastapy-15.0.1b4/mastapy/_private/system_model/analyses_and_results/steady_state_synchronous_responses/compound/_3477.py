"""StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
    _3386,
)

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3345,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3368,
        _3374,
        _3402,
        _3428,
        _3449,
        _3468,
        _3475,
        _3476,
    )
    from mastapy._private.system_model.part_model.gears import _2789

    Self = TypeVar(
        "Self", bound="StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse._Cast_StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: "StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse"

    @property
    def bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3386.BevelGearSetCompoundSteadyStateSynchronousResponse":
        return self.__parent__._cast(
            _3386.BevelGearSetCompoundSteadyStateSynchronousResponse
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
    def part_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3449.PartCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3449,
        )

        return self.__parent__._cast(_3449.PartCompoundSteadyStateSynchronousResponse)

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
    def straight_bevel_diff_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse":
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
class StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse(
    _3386.BevelGearSetCompoundSteadyStateSynchronousResponse
):
    """StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2789.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2789.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

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
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3345.StraightBevelDiffGearSetSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.StraightBevelDiffGearSetSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_gears_compound_steady_state_synchronous_response(
        self: "Self",
    ) -> "List[_3475.StraightBevelDiffGearCompoundSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound.StraightBevelDiffGearCompoundSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "StraightBevelDiffGearsCompoundSteadyStateSynchronousResponse"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_meshes_compound_steady_state_synchronous_response(
        self: "Self",
    ) -> "List[_3476.StraightBevelDiffGearMeshCompoundSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound.StraightBevelDiffGearMeshCompoundSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped,
            "StraightBevelDiffMeshesCompoundSteadyStateSynchronousResponse",
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_3345.StraightBevelDiffGearSetSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.StraightBevelDiffGearSetSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse
        """
        return _Cast_StraightBevelDiffGearSetCompoundSteadyStateSynchronousResponse(
            self
        )
