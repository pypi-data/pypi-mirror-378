"""ComponentMaterialDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.materials import _359
from mastapy._private.utility.databases import _2032

_COMPONENT_MATERIAL_DATABASE = python_net_import(
    "SMT.MastaAPI.Materials", "ComponentMaterialDatabase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.databases import _2028, _2036

    Self = TypeVar("Self", bound="ComponentMaterialDatabase")
    CastSelf = TypeVar(
        "CastSelf", bound="ComponentMaterialDatabase._Cast_ComponentMaterialDatabase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentMaterialDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentMaterialDatabase:
    """Special nested class for casting ComponentMaterialDatabase to subclasses."""

    __parent__: "ComponentMaterialDatabase"

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
    def component_material_database(self: "CastSelf") -> "ComponentMaterialDatabase":
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
class ComponentMaterialDatabase(_2032.NamedDatabase[_359.Material]):
    """ComponentMaterialDatabase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_MATERIAL_DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentMaterialDatabase":
        """Cast to another type.

        Returns:
            _Cast_ComponentMaterialDatabase
        """
        return _Cast_ComponentMaterialDatabase(self)
