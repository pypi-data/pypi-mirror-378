"""ComponentFromCAD"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.part_model.import_from_cad import _2736

_COMPONENT_FROM_CAD = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD", "ComponentFromCAD"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.part_model.import_from_cad import (
        _2733,
        _2734,
        _2737,
        _2738,
        _2739,
        _2740,
        _2741,
        _2742,
        _2743,
        _2745,
        _2746,
        _2747,
        _2748,
        _2749,
        _2750,
    )

    Self = TypeVar("Self", bound="ComponentFromCAD")
    CastSelf = TypeVar("CastSelf", bound="ComponentFromCAD._Cast_ComponentFromCAD")


__docformat__ = "restructuredtext en"
__all__ = ("ComponentFromCAD",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentFromCAD:
    """Special nested class for casting ComponentFromCAD to subclasses."""

    __parent__: "ComponentFromCAD"

    @property
    def component_from_cad_base(self: "CastSelf") -> "_2736.ComponentFromCADBase":
        return self.__parent__._cast(_2736.ComponentFromCADBase)

    @property
    def abstract_shaft_from_cad(self: "CastSelf") -> "_2733.AbstractShaftFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2733

        return self.__parent__._cast(_2733.AbstractShaftFromCAD)

    @property
    def clutch_from_cad(self: "CastSelf") -> "_2734.ClutchFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2734

        return self.__parent__._cast(_2734.ClutchFromCAD)

    @property
    def concept_bearing_from_cad(self: "CastSelf") -> "_2737.ConceptBearingFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2737

        return self.__parent__._cast(_2737.ConceptBearingFromCAD)

    @property
    def connector_from_cad(self: "CastSelf") -> "_2738.ConnectorFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2738

        return self.__parent__._cast(_2738.ConnectorFromCAD)

    @property
    def cylindrical_gear_from_cad(self: "CastSelf") -> "_2739.CylindricalGearFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2739

        return self.__parent__._cast(_2739.CylindricalGearFromCAD)

    @property
    def cylindrical_gear_in_planetary_set_from_cad(
        self: "CastSelf",
    ) -> "_2740.CylindricalGearInPlanetarySetFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2740

        return self.__parent__._cast(_2740.CylindricalGearInPlanetarySetFromCAD)

    @property
    def cylindrical_planet_gear_from_cad(
        self: "CastSelf",
    ) -> "_2741.CylindricalPlanetGearFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2741

        return self.__parent__._cast(_2741.CylindricalPlanetGearFromCAD)

    @property
    def cylindrical_ring_gear_from_cad(
        self: "CastSelf",
    ) -> "_2742.CylindricalRingGearFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2742

        return self.__parent__._cast(_2742.CylindricalRingGearFromCAD)

    @property
    def cylindrical_sun_gear_from_cad(
        self: "CastSelf",
    ) -> "_2743.CylindricalSunGearFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2743

        return self.__parent__._cast(_2743.CylindricalSunGearFromCAD)

    @property
    def mountable_component_from_cad(
        self: "CastSelf",
    ) -> "_2745.MountableComponentFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2745

        return self.__parent__._cast(_2745.MountableComponentFromCAD)

    @property
    def planet_shaft_from_cad(self: "CastSelf") -> "_2746.PlanetShaftFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2746

        return self.__parent__._cast(_2746.PlanetShaftFromCAD)

    @property
    def pulley_from_cad(self: "CastSelf") -> "_2747.PulleyFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2747

        return self.__parent__._cast(_2747.PulleyFromCAD)

    @property
    def rigid_connector_from_cad(self: "CastSelf") -> "_2748.RigidConnectorFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2748

        return self.__parent__._cast(_2748.RigidConnectorFromCAD)

    @property
    def rolling_bearing_from_cad(self: "CastSelf") -> "_2749.RollingBearingFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2749

        return self.__parent__._cast(_2749.RollingBearingFromCAD)

    @property
    def shaft_from_cad(self: "CastSelf") -> "_2750.ShaftFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2750

        return self.__parent__._cast(_2750.ShaftFromCAD)

    @property
    def component_from_cad(self: "CastSelf") -> "ComponentFromCAD":
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
class ComponentFromCAD(_2736.ComponentFromCADBase):
    """ComponentFromCAD

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_FROM_CAD

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def length(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Length")

        if temp is None:
            return 0.0

        return temp

    @length.setter
    @exception_bridge
    @enforce_parameter_types
    def length(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Length", float(value) if value is not None else 0.0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentFromCAD":
        """Cast to another type.

        Returns:
            _Cast_ComponentFromCAD
        """
        return _Cast_ComponentFromCAD(self)
