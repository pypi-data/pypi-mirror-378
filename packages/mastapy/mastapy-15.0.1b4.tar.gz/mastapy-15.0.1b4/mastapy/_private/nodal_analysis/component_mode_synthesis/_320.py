"""RealCMSResults"""

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
from mastapy._private.nodal_analysis.component_mode_synthesis import _316

_REAL_CMS_RESULTS = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis", "RealCMSResults"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.component_mode_synthesis import _319, _323
    from mastapy._private.nodal_analysis.states import _129

    Self = TypeVar("Self", bound="RealCMSResults")
    CastSelf = TypeVar("CastSelf", bound="RealCMSResults._Cast_RealCMSResults")


__docformat__ = "restructuredtext en"
__all__ = ("RealCMSResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RealCMSResults:
    """Special nested class for casting RealCMSResults to subclasses."""

    __parent__: "RealCMSResults"

    @property
    def cms_results(self: "CastSelf") -> "_316.CMSResults":
        return self.__parent__._cast(_316.CMSResults)

    @property
    def modal_cms_results(self: "CastSelf") -> "_319.ModalCMSResults":
        from mastapy._private.nodal_analysis.component_mode_synthesis import _319

        return self.__parent__._cast(_319.ModalCMSResults)

    @property
    def static_cms_results(self: "CastSelf") -> "_323.StaticCMSResults":
        from mastapy._private.nodal_analysis.component_mode_synthesis import _323

        return self.__parent__._cast(_323.StaticCMSResults)

    @property
    def real_cms_results(self: "CastSelf") -> "RealCMSResults":
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
class RealCMSResults(_316.CMSResults):
    """RealCMSResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _REAL_CMS_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def node_displacements(self: "Self") -> "_129.NodeVectorState":
        """mastapy.nodal_analysis.states.NodeVectorState

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NodeDisplacements")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_RealCMSResults":
        """Cast to another type.

        Returns:
            _Cast_RealCMSResults
        """
        return _Cast_RealCMSResults(self)
