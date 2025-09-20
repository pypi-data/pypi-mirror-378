"""CouplingHalf"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import overridable
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.part_model import _2698

_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "CouplingHalf"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2703
    from mastapy._private.system_model.part_model.couplings import (
        _2823,
        _2826,
        _2832,
        _2834,
        _2836,
        _2843,
        _2852,
        _2855,
        _2856,
        _2857,
        _2859,
        _2861,
    )

    Self = TypeVar("Self", bound="CouplingHalf")
    CastSelf = TypeVar("CastSelf", bound="CouplingHalf._Cast_CouplingHalf")


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalf",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalf:
    """Special nested class for casting CouplingHalf to subclasses."""

    __parent__: "CouplingHalf"

    @property
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
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
    def clutch_half(self: "CastSelf") -> "_2823.ClutchHalf":
        from mastapy._private.system_model.part_model.couplings import _2823

        return self.__parent__._cast(_2823.ClutchHalf)

    @property
    def concept_coupling_half(self: "CastSelf") -> "_2826.ConceptCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2826

        return self.__parent__._cast(_2826.ConceptCouplingHalf)

    @property
    def cvt_pulley(self: "CastSelf") -> "_2832.CVTPulley":
        from mastapy._private.system_model.part_model.couplings import _2832

        return self.__parent__._cast(_2832.CVTPulley)

    @property
    def part_to_part_shear_coupling_half(
        self: "CastSelf",
    ) -> "_2834.PartToPartShearCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2834

        return self.__parent__._cast(_2834.PartToPartShearCouplingHalf)

    @property
    def pulley(self: "CastSelf") -> "_2836.Pulley":
        from mastapy._private.system_model.part_model.couplings import _2836

        return self.__parent__._cast(_2836.Pulley)

    @property
    def rolling_ring(self: "CastSelf") -> "_2843.RollingRing":
        from mastapy._private.system_model.part_model.couplings import _2843

        return self.__parent__._cast(_2843.RollingRing)

    @property
    def spring_damper_half(self: "CastSelf") -> "_2852.SpringDamperHalf":
        from mastapy._private.system_model.part_model.couplings import _2852

        return self.__parent__._cast(_2852.SpringDamperHalf)

    @property
    def synchroniser_half(self: "CastSelf") -> "_2855.SynchroniserHalf":
        from mastapy._private.system_model.part_model.couplings import _2855

        return self.__parent__._cast(_2855.SynchroniserHalf)

    @property
    def synchroniser_part(self: "CastSelf") -> "_2856.SynchroniserPart":
        from mastapy._private.system_model.part_model.couplings import _2856

        return self.__parent__._cast(_2856.SynchroniserPart)

    @property
    def synchroniser_sleeve(self: "CastSelf") -> "_2857.SynchroniserSleeve":
        from mastapy._private.system_model.part_model.couplings import _2857

        return self.__parent__._cast(_2857.SynchroniserSleeve)

    @property
    def torque_converter_pump(self: "CastSelf") -> "_2859.TorqueConverterPump":
        from mastapy._private.system_model.part_model.couplings import _2859

        return self.__parent__._cast(_2859.TorqueConverterPump)

    @property
    def torque_converter_turbine(self: "CastSelf") -> "_2861.TorqueConverterTurbine":
        from mastapy._private.system_model.part_model.couplings import _2861

        return self.__parent__._cast(_2861.TorqueConverterTurbine)

    @property
    def coupling_half(self: "CastSelf") -> "CouplingHalf":
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
class CouplingHalf(_2698.MountableComponent):
    """CouplingHalf

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HALF

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bore(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Bore")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @bore.setter
    @exception_bridge
    @enforce_parameter_types
    def bore(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Bore", value)

    @property
    @exception_bridge
    def diameter(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Diameter")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def diameter(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Diameter", value)

    @property
    @exception_bridge
    def width(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Width")

        if temp is None:
            return 0.0

        return temp

    @width.setter
    @exception_bridge
    @enforce_parameter_types
    def width(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Width", float(value) if value is not None else 0.0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingHalf":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalf
        """
        return _Cast_CouplingHalf(self)
