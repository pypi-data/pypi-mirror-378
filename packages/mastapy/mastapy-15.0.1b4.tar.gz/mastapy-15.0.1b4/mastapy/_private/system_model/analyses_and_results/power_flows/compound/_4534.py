"""ShaftToMountableComponentConnectionCompoundPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
    _4438,
)

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "ShaftToMountableComponentConnectionCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4402
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4459,
        _4470,
        _4479,
        _4520,
    )

    Self = TypeVar("Self", bound="ShaftToMountableComponentConnectionCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftToMountableComponentConnectionCompoundPowerFlow._Cast_ShaftToMountableComponentConnectionCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftToMountableComponentConnectionCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftToMountableComponentConnectionCompoundPowerFlow:
    """Special nested class for casting ShaftToMountableComponentConnectionCompoundPowerFlow to subclasses."""

    __parent__: "ShaftToMountableComponentConnectionCompoundPowerFlow"

    @property
    def abstract_shaft_to_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4438.AbstractShaftToMountableComponentConnectionCompoundPowerFlow":
        return self.__parent__._cast(
            _4438.AbstractShaftToMountableComponentConnectionCompoundPowerFlow
        )

    @property
    def connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4470.ConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4470,
        )

        return self.__parent__._cast(_4470.ConnectionCompoundPowerFlow)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7886,
        )

        return self.__parent__._cast(_7886.ConnectionCompoundAnalysis)

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
    def coaxial_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4459.CoaxialConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4459,
        )

        return self.__parent__._cast(_4459.CoaxialConnectionCompoundPowerFlow)

    @property
    def cycloidal_disc_central_bearing_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4479.CycloidalDiscCentralBearingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4479,
        )

        return self.__parent__._cast(
            _4479.CycloidalDiscCentralBearingConnectionCompoundPowerFlow
        )

    @property
    def planetary_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4520.PlanetaryConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4520,
        )

        return self.__parent__._cast(_4520.PlanetaryConnectionCompoundPowerFlow)

    @property
    def shaft_to_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "ShaftToMountableComponentConnectionCompoundPowerFlow":
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
class ShaftToMountableComponentConnectionCompoundPowerFlow(
    _4438.AbstractShaftToMountableComponentConnectionCompoundPowerFlow
):
    """ShaftToMountableComponentConnectionCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_POWER_FLOW
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_4402.ShaftToMountableComponentConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.ShaftToMountableComponentConnectionPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4402.ShaftToMountableComponentConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.ShaftToMountableComponentConnectionPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ShaftToMountableComponentConnectionCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_ShaftToMountableComponentConnectionCompoundPowerFlow
        """
        return _Cast_ShaftToMountableComponentConnectionCompoundPowerFlow(self)
