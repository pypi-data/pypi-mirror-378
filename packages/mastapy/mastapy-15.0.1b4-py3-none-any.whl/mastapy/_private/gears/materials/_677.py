"""BevelGearAbstractMaterialDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.materials import _360

_BEVEL_GEAR_ABSTRACT_MATERIAL_DATABASE = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "BevelGearAbstractMaterialDatabase"
)

if TYPE_CHECKING:
    from typing import Any, Type

    from mastapy._private.gears.materials import _679, _680
    from mastapy._private.utility.databases import _2028, _2032, _2036

    Self = TypeVar("Self", bound="BevelGearAbstractMaterialDatabase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearAbstractMaterialDatabase._Cast_BevelGearAbstractMaterialDatabase",
    )

T = TypeVar("T", bound="_680.BevelGearMaterial")

__docformat__ = "restructuredtext en"
__all__ = ("BevelGearAbstractMaterialDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearAbstractMaterialDatabase:
    """Special nested class for casting BevelGearAbstractMaterialDatabase to subclasses."""

    __parent__: "BevelGearAbstractMaterialDatabase"

    @property
    def material_database(self: "CastSelf") -> "_360.MaterialDatabase":
        return self.__parent__._cast(_360.MaterialDatabase)

    @property
    def named_database(self: "CastSelf") -> "_2032.NamedDatabase":
        from mastapy._private.utility.databases import _2032

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
    def bevel_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_679.BevelGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _679

        return self.__parent__._cast(_679.BevelGearISOMaterialDatabase)

    @property
    def bevel_gear_abstract_material_database(
        self: "CastSelf",
    ) -> "BevelGearAbstractMaterialDatabase":
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
class BevelGearAbstractMaterialDatabase(_360.MaterialDatabase[T]):
    """BevelGearAbstractMaterialDatabase

    This is a mastapy class.

    Generic Types:
        T
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_ABSTRACT_MATERIAL_DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearAbstractMaterialDatabase":
        """Cast to another type.

        Returns:
            _Cast_BevelGearAbstractMaterialDatabase
        """
        return _Cast_BevelGearAbstractMaterialDatabase(self)
