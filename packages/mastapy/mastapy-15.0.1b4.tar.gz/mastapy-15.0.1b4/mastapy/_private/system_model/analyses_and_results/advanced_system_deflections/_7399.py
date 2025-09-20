"""AbstractShaftOrHousingAdvancedSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
    _7425,
)

_ABSTRACT_SHAFT_OR_HOUSING_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections",
    "AbstractShaftOrHousingAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7398,
        _7445,
        _7458,
        _7484,
        _7500,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7895,
    )
    from mastapy._private.system_model.part_model import _2666

    Self = TypeVar("Self", bound="AbstractShaftOrHousingAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftOrHousingAdvancedSystemDeflection._Cast_AbstractShaftOrHousingAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftOrHousingAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftOrHousingAdvancedSystemDeflection:
    """Special nested class for casting AbstractShaftOrHousingAdvancedSystemDeflection to subclasses."""

    __parent__: "AbstractShaftOrHousingAdvancedSystemDeflection"

    @property
    def component_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7425.ComponentAdvancedSystemDeflection":
        return self.__parent__._cast(_7425.ComponentAdvancedSystemDeflection)

    @property
    def part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7484.PartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7484,
        )

        return self.__parent__._cast(_7484.PartAdvancedSystemDeflection)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7895.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7895,
        )

        return self.__parent__._cast(_7895.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7892.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7892,
        )

        return self.__parent__._cast(_7892.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2903.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2903

        return self.__parent__._cast(_2903.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2899.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2899

        return self.__parent__._cast(_2899.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def abstract_shaft_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7398.AbstractShaftAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7398,
        )

        return self.__parent__._cast(_7398.AbstractShaftAdvancedSystemDeflection)

    @property
    def cycloidal_disc_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7445.CycloidalDiscAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7445,
        )

        return self.__parent__._cast(_7445.CycloidalDiscAdvancedSystemDeflection)

    @property
    def fe_part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7458.FEPartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7458,
        )

        return self.__parent__._cast(_7458.FEPartAdvancedSystemDeflection)

    @property
    def shaft_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7500.ShaftAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7500,
        )

        return self.__parent__._cast(_7500.ShaftAdvancedSystemDeflection)

    @property
    def abstract_shaft_or_housing_advanced_system_deflection(
        self: "CastSelf",
    ) -> "AbstractShaftOrHousingAdvancedSystemDeflection":
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
class AbstractShaftOrHousingAdvancedSystemDeflection(
    _7425.ComponentAdvancedSystemDeflection
):
    """AbstractShaftOrHousingAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_SHAFT_OR_HOUSING_ADVANCED_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2666.AbstractShaftOrHousing":
        """mastapy.system_model.part_model.AbstractShaftOrHousing

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractShaftOrHousingAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftOrHousingAdvancedSystemDeflection
        """
        return _Cast_AbstractShaftOrHousingAdvancedSystemDeflection(self)
