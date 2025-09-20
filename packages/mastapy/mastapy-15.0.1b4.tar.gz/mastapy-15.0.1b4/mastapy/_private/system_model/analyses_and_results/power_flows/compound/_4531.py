"""RootAssemblyCompoundPowerFlow"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
    _4442,
)

_ROOT_ASSEMBLY_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "RootAssemblyCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups import (
        _5955,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4399
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4435,
        _4516,
    )

    Self = TypeVar("Self", bound="RootAssemblyCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="RootAssemblyCompoundPowerFlow._Cast_RootAssemblyCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("RootAssemblyCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RootAssemblyCompoundPowerFlow:
    """Special nested class for casting RootAssemblyCompoundPowerFlow to subclasses."""

    __parent__: "RootAssemblyCompoundPowerFlow"

    @property
    def assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4442.AssemblyCompoundPowerFlow":
        return self.__parent__._cast(_4442.AssemblyCompoundPowerFlow)

    @property
    def abstract_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4435.AbstractAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4435,
        )

        return self.__parent__._cast(_4435.AbstractAssemblyCompoundPowerFlow)

    @property
    def part_compound_power_flow(self: "CastSelf") -> "_4516.PartCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4516,
        )

        return self.__parent__._cast(_4516.PartCompoundPowerFlow)

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
    def root_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "RootAssemblyCompoundPowerFlow":
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
class RootAssemblyCompoundPowerFlow(_4442.AssemblyCompoundPowerFlow):
    """RootAssemblyCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ROOT_ASSEMBLY_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def compound_static_load(self: "Self") -> "_5955.AbstractStaticLoadCaseGroup":
        """mastapy.system_model.analyses_and_results.load_case_groups.AbstractStaticLoadCaseGroup

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CompoundStaticLoad")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4399.RootAssemblyPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.RootAssemblyPowerFlow]

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
    def assembly_analysis_cases(self: "Self") -> "List[_4399.RootAssemblyPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.RootAssemblyPowerFlow]

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

    @exception_bridge
    def set_face_widths_for_specified_safety_factors(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "SetFaceWidthsForSpecifiedSafetyFactors")

    @property
    def cast_to(self: "Self") -> "_Cast_RootAssemblyCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_RootAssemblyCompoundPowerFlow
        """
        return _Cast_RootAssemblyCompoundPowerFlow(self)
