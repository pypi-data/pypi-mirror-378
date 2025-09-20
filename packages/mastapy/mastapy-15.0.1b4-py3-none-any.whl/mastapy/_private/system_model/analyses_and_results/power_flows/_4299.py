"""AbstractShaftOrHousingPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows import _4323

_ABSTRACT_SHAFT_OR_HOUSING_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows",
    "AbstractShaftOrHousingPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7895,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import (
        _4300,
        _4344,
        _4357,
        _4382,
        _4401,
    )
    from mastapy._private.system_model.part_model import _2666

    Self = TypeVar("Self", bound="AbstractShaftOrHousingPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftOrHousingPowerFlow._Cast_AbstractShaftOrHousingPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftOrHousingPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftOrHousingPowerFlow:
    """Special nested class for casting AbstractShaftOrHousingPowerFlow to subclasses."""

    __parent__: "AbstractShaftOrHousingPowerFlow"

    @property
    def component_power_flow(self: "CastSelf") -> "_4323.ComponentPowerFlow":
        return self.__parent__._cast(_4323.ComponentPowerFlow)

    @property
    def part_power_flow(self: "CastSelf") -> "_4382.PartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4382

        return self.__parent__._cast(_4382.PartPowerFlow)

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
    def abstract_shaft_power_flow(self: "CastSelf") -> "_4300.AbstractShaftPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4300

        return self.__parent__._cast(_4300.AbstractShaftPowerFlow)

    @property
    def cycloidal_disc_power_flow(self: "CastSelf") -> "_4344.CycloidalDiscPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4344

        return self.__parent__._cast(_4344.CycloidalDiscPowerFlow)

    @property
    def fe_part_power_flow(self: "CastSelf") -> "_4357.FEPartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4357

        return self.__parent__._cast(_4357.FEPartPowerFlow)

    @property
    def shaft_power_flow(self: "CastSelf") -> "_4401.ShaftPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4401

        return self.__parent__._cast(_4401.ShaftPowerFlow)

    @property
    def abstract_shaft_or_housing_power_flow(
        self: "CastSelf",
    ) -> "AbstractShaftOrHousingPowerFlow":
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
class AbstractShaftOrHousingPowerFlow(_4323.ComponentPowerFlow):
    """AbstractShaftOrHousingPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_SHAFT_OR_HOUSING_POWER_FLOW

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
    def cast_to(self: "Self") -> "_Cast_AbstractShaftOrHousingPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftOrHousingPowerFlow
        """
        return _Cast_AbstractShaftOrHousingPowerFlow(self)
