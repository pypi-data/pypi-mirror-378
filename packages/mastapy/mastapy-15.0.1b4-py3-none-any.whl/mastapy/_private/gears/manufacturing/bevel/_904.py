"""ManufacturingMachineDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.manufacturing.bevel import _903
from mastapy._private.utility.databases import _2032

_MANUFACTURING_MACHINE_DATABASE = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Bevel", "ManufacturingMachineDatabase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.databases import _2028, _2036

    Self = TypeVar("Self", bound="ManufacturingMachineDatabase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ManufacturingMachineDatabase._Cast_ManufacturingMachineDatabase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ManufacturingMachineDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ManufacturingMachineDatabase:
    """Special nested class for casting ManufacturingMachineDatabase to subclasses."""

    __parent__: "ManufacturingMachineDatabase"

    @property
    def named_database(self: "CastSelf") -> "_2032.NamedDatabase":
        return self.__parent__._cast(_2032.NamedDatabase)

    @property
    def sql_database(self: "CastSelf") -> "_2036.SQLDatabase":
        pass

        from mastapy._private.utility.databases import _2036

        return self.__parent__._cast(_2036.SQLDatabase)

    @property
    def database(self: "CastSelf") -> "_2028.Database":
        pass

        from mastapy._private.utility.databases import _2028

        return self.__parent__._cast(_2028.Database)

    @property
    def manufacturing_machine_database(
        self: "CastSelf",
    ) -> "ManufacturingMachineDatabase":
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
class ManufacturingMachineDatabase(_2032.NamedDatabase[_903.ManufacturingMachine]):
    """ManufacturingMachineDatabase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MANUFACTURING_MACHINE_DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ManufacturingMachineDatabase":
        """Cast to another type.

        Returns:
            _Cast_ManufacturingMachineDatabase
        """
        return _Cast_ManufacturingMachineDatabase(self)
