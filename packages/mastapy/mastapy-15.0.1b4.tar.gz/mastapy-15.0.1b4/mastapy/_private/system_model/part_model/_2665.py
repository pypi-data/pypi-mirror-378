"""AbstractShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.part_model import _2666

_ABSTRACT_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaft"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2703
    from mastapy._private.system_model.part_model.cycloidal import _2812
    from mastapy._private.system_model.part_model.shaft_model import _2719

    Self = TypeVar("Self", bound="AbstractShaft")
    CastSelf = TypeVar("CastSelf", bound="AbstractShaft._Cast_AbstractShaft")


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaft:
    """Special nested class for casting AbstractShaft to subclasses."""

    __parent__: "AbstractShaft"

    @property
    def abstract_shaft_or_housing(self: "CastSelf") -> "_2666.AbstractShaftOrHousing":
        return self.__parent__._cast(_2666.AbstractShaftOrHousing)

    @property
    def component(self: "CastSelf") -> "_2675.Component":
        from mastapy._private.system_model.part_model import _2675

        return self.__parent__._cast(_2675.Component)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def shaft(self: "CastSelf") -> "_2719.Shaft":
        from mastapy._private.system_model.part_model.shaft_model import _2719

        return self.__parent__._cast(_2719.Shaft)

    @property
    def cycloidal_disc(self: "CastSelf") -> "_2812.CycloidalDisc":
        from mastapy._private.system_model.part_model.cycloidal import _2812

        return self.__parent__._cast(_2812.CycloidalDisc)

    @property
    def abstract_shaft(self: "CastSelf") -> "AbstractShaft":
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
class AbstractShaft(_2666.AbstractShaftOrHousing):
    """AbstractShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_SHAFT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractShaft":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaft
        """
        return _Cast_AbstractShaft(self)
