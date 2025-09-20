"""PartToPartShearCoupling"""

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
from mastapy._private.system_model.part_model.couplings import _2828

_PART_TO_PART_SHEAR_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCoupling"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets.couplings import _2574
    from mastapy._private.system_model.part_model import _2664, _2703, _2713

    Self = TypeVar("Self", bound="PartToPartShearCoupling")
    CastSelf = TypeVar(
        "CastSelf", bound="PartToPartShearCoupling._Cast_PartToPartShearCoupling"
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartToPartShearCoupling",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartToPartShearCoupling:
    """Special nested class for casting PartToPartShearCoupling to subclasses."""

    __parent__: "PartToPartShearCoupling"

    @property
    def coupling(self: "CastSelf") -> "_2828.Coupling":
        return self.__parent__._cast(_2828.Coupling)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2713.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2713

        return self.__parent__._cast(_2713.SpecialisedAssembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2664.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2664

        return self.__parent__._cast(_2664.AbstractAssembly)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def part_to_part_shear_coupling(self: "CastSelf") -> "PartToPartShearCoupling":
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
class PartToPartShearCoupling(_2828.Coupling):
    """PartToPartShearCoupling

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_TO_PART_SHEAR_COUPLING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def part_to_part_shear_coupling_connection(
        self: "Self",
    ) -> "_2574.PartToPartShearCouplingConnection":
        """mastapy.system_model.connections_and_sockets.couplings.PartToPartShearCouplingConnection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PartToPartShearCouplingConnection")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_PartToPartShearCoupling":
        """Cast to another type.

        Returns:
            _Cast_PartToPartShearCoupling
        """
        return _Cast_PartToPartShearCoupling(self)
