"""CouplingCompoundAdvancedSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
    _7635,
)

_COUPLING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound",
    "CouplingCompoundAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7438,
    )
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
        _7535,
        _7556,
        _7561,
        _7616,
        _7617,
        _7639,
        _7654,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )

    Self = TypeVar("Self", bound="CouplingCompoundAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingCompoundAdvancedSystemDeflection._Cast_CouplingCompoundAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingCompoundAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingCompoundAdvancedSystemDeflection:
    """Special nested class for casting CouplingCompoundAdvancedSystemDeflection to subclasses."""

    __parent__: "CouplingCompoundAdvancedSystemDeflection"

    @property
    def specialised_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection":
        return self.__parent__._cast(
            _7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def abstract_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7535.AbstractAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7535,
        )

        return self.__parent__._cast(
            _7535.AbstractAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def part_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7616.PartCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7616,
        )

        return self.__parent__._cast(_7616.PartCompoundAdvancedSystemDeflection)

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
    def clutch_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7556.ClutchCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7556,
        )

        return self.__parent__._cast(_7556.ClutchCompoundAdvancedSystemDeflection)

    @property
    def concept_coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7561.ConceptCouplingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7561,
        )

        return self.__parent__._cast(
            _7561.ConceptCouplingCompoundAdvancedSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7617.PartToPartShearCouplingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7617,
        )

        return self.__parent__._cast(
            _7617.PartToPartShearCouplingCompoundAdvancedSystemDeflection
        )

    @property
    def spring_damper_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7639.SpringDamperCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7639,
        )

        return self.__parent__._cast(_7639.SpringDamperCompoundAdvancedSystemDeflection)

    @property
    def torque_converter_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7654.TorqueConverterCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7654,
        )

        return self.__parent__._cast(
            _7654.TorqueConverterCompoundAdvancedSystemDeflection
        )

    @property
    def coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "CouplingCompoundAdvancedSystemDeflection":
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
class CouplingCompoundAdvancedSystemDeflection(
    _7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection
):
    """CouplingCompoundAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_7438.CouplingAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.CouplingAdvancedSystemDeflection]

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
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_7438.CouplingAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.CouplingAdvancedSystemDeflection]

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
    def cast_to(self: "Self") -> "_Cast_CouplingCompoundAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_CouplingCompoundAdvancedSystemDeflection
        """
        return _Cast_CouplingCompoundAdvancedSystemDeflection(self)
