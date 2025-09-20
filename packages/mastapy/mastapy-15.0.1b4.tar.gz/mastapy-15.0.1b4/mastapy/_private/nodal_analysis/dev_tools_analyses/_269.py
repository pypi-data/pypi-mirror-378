"""FEEntityGroupInteger"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.nodal_analysis.dev_tools_analyses import _268

_FE_ENTITY_GROUP_INTEGER = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses", "FEEntityGroupInteger"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.component_mode_synthesis import _314
    from mastapy._private.nodal_analysis.dev_tools_analyses import _267, _287

    Self = TypeVar("Self", bound="FEEntityGroupInteger")
    CastSelf = TypeVar(
        "CastSelf", bound="FEEntityGroupInteger._Cast_FEEntityGroupInteger"
    )


__docformat__ = "restructuredtext en"
__all__ = ("FEEntityGroupInteger",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FEEntityGroupInteger:
    """Special nested class for casting FEEntityGroupInteger to subclasses."""

    __parent__: "FEEntityGroupInteger"

    @property
    def fe_entity_group(self: "CastSelf") -> "_268.FEEntityGroup":
        return self.__parent__._cast(_268.FEEntityGroup)

    @property
    def element_group(self: "CastSelf") -> "_267.ElementGroup":
        from mastapy._private.nodal_analysis.dev_tools_analyses import _267

        return self.__parent__._cast(_267.ElementGroup)

    @property
    def node_group(self: "CastSelf") -> "_287.NodeGroup":
        from mastapy._private.nodal_analysis.dev_tools_analyses import _287

        return self.__parent__._cast(_287.NodeGroup)

    @property
    def cms_node_group(self: "CastSelf") -> "_314.CMSNodeGroup":
        from mastapy._private.nodal_analysis.component_mode_synthesis import _314

        return self.__parent__._cast(_314.CMSNodeGroup)

    @property
    def fe_entity_group_integer(self: "CastSelf") -> "FEEntityGroupInteger":
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
class FEEntityGroupInteger(_268.FEEntityGroup[int]):
    """FEEntityGroupInteger

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FE_ENTITY_GROUP_INTEGER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_FEEntityGroupInteger":
        """Cast to another type.

        Returns:
            _Cast_FEEntityGroupInteger
        """
        return _Cast_FEEntityGroupInteger(self)
