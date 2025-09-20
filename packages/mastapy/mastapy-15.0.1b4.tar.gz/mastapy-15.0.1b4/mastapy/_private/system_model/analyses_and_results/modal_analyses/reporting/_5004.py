"""SingleExcitationResultsModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
    _4997,
)

_SINGLE_EXCITATION_RESULTS_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting",
    "SingleExcitationResultsModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
        _5000,
    )

    Self = TypeVar("Self", bound="SingleExcitationResultsModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SingleExcitationResultsModalAnalysis._Cast_SingleExcitationResultsModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SingleExcitationResultsModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SingleExcitationResultsModalAnalysis:
    """Special nested class for casting SingleExcitationResultsModalAnalysis to subclasses."""

    __parent__: "SingleExcitationResultsModalAnalysis"

    @property
    def design_entity_modal_analysis_group_results(
        self: "CastSelf",
    ) -> "_4997.DesignEntityModalAnalysisGroupResults":
        return self.__parent__._cast(_4997.DesignEntityModalAnalysisGroupResults)

    @property
    def single_excitation_results_modal_analysis(
        self: "CastSelf",
    ) -> "SingleExcitationResultsModalAnalysis":
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
class SingleExcitationResultsModalAnalysis(_4997.DesignEntityModalAnalysisGroupResults):
    """SingleExcitationResultsModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SINGLE_EXCITATION_RESULTS_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def harmonic_index(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HarmonicIndex")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def all_rigidly_connected_groups(
        self: "Self",
    ) -> (
        "List[_5000.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]"
    ):
        """List[mastapy.system_model.analyses_and_results.modal_analyses.reporting.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllRigidlyConnectedGroups")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def rigidly_connected_groups_with_significant_energy(
        self: "Self",
    ) -> (
        "List[_5000.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]"
    ):
        """List[mastapy.system_model.analyses_and_results.modal_analyses.reporting.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "RigidlyConnectedGroupsWithSignificantEnergy"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def rigidly_connected_groups_with_significant_kinetic_energy(
        self: "Self",
    ) -> (
        "List[_5000.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]"
    ):
        """List[mastapy.system_model.analyses_and_results.modal_analyses.reporting.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "RigidlyConnectedGroupsWithSignificantKineticEnergy"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def rigidly_connected_groups_with_significant_strain_energy(
        self: "Self",
    ) -> (
        "List[_5000.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]"
    ):
        """List[mastapy.system_model.analyses_and_results.modal_analyses.reporting.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "RigidlyConnectedGroupsWithSignificantStrainEnergy"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_SingleExcitationResultsModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_SingleExcitationResultsModalAnalysis
        """
        return _Cast_SingleExcitationResultsModalAnalysis(self)
