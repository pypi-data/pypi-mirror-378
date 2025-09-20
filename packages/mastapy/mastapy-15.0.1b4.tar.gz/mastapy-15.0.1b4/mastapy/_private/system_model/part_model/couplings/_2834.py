"""PartToPartShearCouplingHalf"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.part_model.couplings import _2829

_PART_TO_PART_SHEAR_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCouplingHalf"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703

    Self = TypeVar("Self", bound="PartToPartShearCouplingHalf")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartToPartShearCouplingHalf._Cast_PartToPartShearCouplingHalf",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartToPartShearCouplingHalf",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartToPartShearCouplingHalf:
    """Special nested class for casting PartToPartShearCouplingHalf to subclasses."""

    __parent__: "PartToPartShearCouplingHalf"

    @property
    def coupling_half(self: "CastSelf") -> "_2829.CouplingHalf":
        return self.__parent__._cast(_2829.CouplingHalf)

    @property
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
        from mastapy._private.system_model.part_model import _2698

        return self.__parent__._cast(_2698.MountableComponent)

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
    def part_to_part_shear_coupling_half(
        self: "CastSelf",
    ) -> "PartToPartShearCouplingHalf":
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
class PartToPartShearCouplingHalf(_2829.CouplingHalf):
    """PartToPartShearCouplingHalf

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_TO_PART_SHEAR_COUPLING_HALF

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PartToPartShearCouplingHalf":
        """Cast to another type.

        Returns:
            _Cast_PartToPartShearCouplingHalf
        """
        return _Cast_PartToPartShearCouplingHalf(self)
