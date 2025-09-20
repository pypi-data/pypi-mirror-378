"""MaterialDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility.databases import _2032

_MATERIAL_DATABASE = python_net_import("SMT.MastaAPI.Materials", "MaterialDatabase")

if TYPE_CHECKING:
    from typing import Any, Type

    from mastapy._private.cycloidal import _1642, _1649
    from mastapy._private.electric_machines import _1405, _1419, _1438, _1453
    from mastapy._private.gears.materials import _677, _679, _683, _684, _686, _687
    from mastapy._private.materials import _359
    from mastapy._private.shafts import _25
    from mastapy._private.utility.databases import _2028, _2036

    Self = TypeVar("Self", bound="MaterialDatabase")
    CastSelf = TypeVar("CastSelf", bound="MaterialDatabase._Cast_MaterialDatabase")

T = TypeVar("T", bound="_359.Material")

__docformat__ = "restructuredtext en"
__all__ = ("MaterialDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MaterialDatabase:
    """Special nested class for casting MaterialDatabase to subclasses."""

    __parent__: "MaterialDatabase"

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
    def shaft_material_database(self: "CastSelf") -> "_25.ShaftMaterialDatabase":
        from mastapy._private.shafts import _25

        return self.__parent__._cast(_25.ShaftMaterialDatabase)

    @property
    def bevel_gear_abstract_material_database(
        self: "CastSelf",
    ) -> "_677.BevelGearAbstractMaterialDatabase":
        from mastapy._private.gears.materials import _677

        return self.__parent__._cast(_677.BevelGearAbstractMaterialDatabase)

    @property
    def bevel_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_679.BevelGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _679

        return self.__parent__._cast(_679.BevelGearISOMaterialDatabase)

    @property
    def cylindrical_gear_agma_material_database(
        self: "CastSelf",
    ) -> "_683.CylindricalGearAGMAMaterialDatabase":
        from mastapy._private.gears.materials import _683

        return self.__parent__._cast(_683.CylindricalGearAGMAMaterialDatabase)

    @property
    def cylindrical_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_684.CylindricalGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _684

        return self.__parent__._cast(_684.CylindricalGearISOMaterialDatabase)

    @property
    def cylindrical_gear_material_database(
        self: "CastSelf",
    ) -> "_686.CylindricalGearMaterialDatabase":
        from mastapy._private.gears.materials import _686

        return self.__parent__._cast(_686.CylindricalGearMaterialDatabase)

    @property
    def cylindrical_gear_plastic_material_database(
        self: "CastSelf",
    ) -> "_687.CylindricalGearPlasticMaterialDatabase":
        from mastapy._private.gears.materials import _687

        return self.__parent__._cast(_687.CylindricalGearPlasticMaterialDatabase)

    @property
    def general_electric_machine_material_database(
        self: "CastSelf",
    ) -> "_1405.GeneralElectricMachineMaterialDatabase":
        from mastapy._private.electric_machines import _1405

        return self.__parent__._cast(_1405.GeneralElectricMachineMaterialDatabase)

    @property
    def magnet_material_database(self: "CastSelf") -> "_1419.MagnetMaterialDatabase":
        from mastapy._private.electric_machines import _1419

        return self.__parent__._cast(_1419.MagnetMaterialDatabase)

    @property
    def stator_rotor_material_database(
        self: "CastSelf",
    ) -> "_1438.StatorRotorMaterialDatabase":
        from mastapy._private.electric_machines import _1438

        return self.__parent__._cast(_1438.StatorRotorMaterialDatabase)

    @property
    def winding_material_database(self: "CastSelf") -> "_1453.WindingMaterialDatabase":
        from mastapy._private.electric_machines import _1453

        return self.__parent__._cast(_1453.WindingMaterialDatabase)

    @property
    def cycloidal_disc_material_database(
        self: "CastSelf",
    ) -> "_1642.CycloidalDiscMaterialDatabase":
        from mastapy._private.cycloidal import _1642

        return self.__parent__._cast(_1642.CycloidalDiscMaterialDatabase)

    @property
    def ring_pins_material_database(
        self: "CastSelf",
    ) -> "_1649.RingPinsMaterialDatabase":
        from mastapy._private.cycloidal import _1649

        return self.__parent__._cast(_1649.RingPinsMaterialDatabase)

    @property
    def material_database(self: "CastSelf") -> "MaterialDatabase":
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
class MaterialDatabase(_2032.NamedDatabase[T]):
    """MaterialDatabase

    This is a mastapy class.

    Generic Types:
        T
    """

    TYPE: ClassVar["Type"] = _MATERIAL_DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MaterialDatabase":
        """Cast to another type.

        Returns:
            _Cast_MaterialDatabase
        """
        return _Cast_MaterialDatabase(self)
