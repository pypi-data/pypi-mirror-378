"""ConceptGearSetCompoundHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
    _6250,
)

_CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound",
    "ConceptGearSetCompoundHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6006,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
        _6190,
        _6219,
        _6220,
        _6271,
        _6290,
    )
    from mastapy._private.system_model.part_model.gears import _2764

    Self = TypeVar("Self", bound="ConceptGearSetCompoundHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConceptGearSetCompoundHarmonicAnalysis._Cast_ConceptGearSetCompoundHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConceptGearSetCompoundHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConceptGearSetCompoundHarmonicAnalysis:
    """Special nested class for casting ConceptGearSetCompoundHarmonicAnalysis to subclasses."""

    __parent__: "ConceptGearSetCompoundHarmonicAnalysis"

    @property
    def gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6250.GearSetCompoundHarmonicAnalysis":
        return self.__parent__._cast(_6250.GearSetCompoundHarmonicAnalysis)

    @property
    def specialised_assembly_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6290.SpecialisedAssemblyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6290,
        )

        return self.__parent__._cast(_6290.SpecialisedAssemblyCompoundHarmonicAnalysis)

    @property
    def abstract_assembly_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6190.AbstractAssemblyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6190,
        )

        return self.__parent__._cast(_6190.AbstractAssemblyCompoundHarmonicAnalysis)

    @property
    def part_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6271.PartCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6271,
        )

        return self.__parent__._cast(_6271.PartCompoundHarmonicAnalysis)

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
    def concept_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "ConceptGearSetCompoundHarmonicAnalysis":
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
class ConceptGearSetCompoundHarmonicAnalysis(_6250.GearSetCompoundHarmonicAnalysis):
    """ConceptGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2764.ConceptGearSet":
        """mastapy.system_model.part_model.gears.ConceptGearSet

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
    def assembly_design(self: "Self") -> "_2764.ConceptGearSet":
        """mastapy.system_model.part_model.gears.ConceptGearSet

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
    ) -> "List[_6006.ConceptGearSetHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ConceptGearSetHarmonicAnalysis]

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
    def concept_gears_compound_harmonic_analysis(
        self: "Self",
    ) -> "List[_6219.ConceptGearCompoundHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.compound.ConceptGearCompoundHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ConceptGearsCompoundHarmonicAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def concept_meshes_compound_harmonic_analysis(
        self: "Self",
    ) -> "List[_6220.ConceptGearMeshCompoundHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.compound.ConceptGearMeshCompoundHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ConceptMeshesCompoundHarmonicAnalysis"
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
    ) -> "List[_6006.ConceptGearSetHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ConceptGearSetHarmonicAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_ConceptGearSetCompoundHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConceptGearSetCompoundHarmonicAnalysis
        """
        return _Cast_ConceptGearSetCompoundHarmonicAnalysis(self)
