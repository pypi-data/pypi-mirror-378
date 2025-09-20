"""AbstractAssembly"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.part_model import _2703

_ABSTRACT_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractAssembly"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import (
        _2663,
        _2673,
        _2675,
        _2686,
        _2697,
        _2711,
        _2713,
    )
    from mastapy._private.system_model.part_model.couplings import (
        _2820,
        _2822,
        _2825,
        _2828,
        _2831,
        _2833,
        _2844,
        _2851,
        _2853,
        _2858,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2811
    from mastapy._private.system_model.part_model.gears import (
        _2756,
        _2758,
        _2762,
        _2764,
        _2766,
        _2768,
        _2771,
        _2774,
        _2777,
        _2779,
        _2781,
        _2783,
        _2784,
        _2787,
        _2789,
        _2791,
        _2795,
        _2797,
    )

    Self = TypeVar("Self", bound="AbstractAssembly")
    CastSelf = TypeVar("CastSelf", bound="AbstractAssembly._Cast_AbstractAssembly")


__docformat__ = "restructuredtext en"
__all__ = ("AbstractAssembly",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractAssembly:
    """Special nested class for casting AbstractAssembly to subclasses."""

    __parent__: "AbstractAssembly"

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def assembly(self: "CastSelf") -> "_2663.Assembly":
        from mastapy._private.system_model.part_model import _2663

        return self.__parent__._cast(_2663.Assembly)

    @property
    def bolted_joint(self: "CastSelf") -> "_2673.BoltedJoint":
        from mastapy._private.system_model.part_model import _2673

        return self.__parent__._cast(_2673.BoltedJoint)

    @property
    def flexible_pin_assembly(self: "CastSelf") -> "_2686.FlexiblePinAssembly":
        from mastapy._private.system_model.part_model import _2686

        return self.__parent__._cast(_2686.FlexiblePinAssembly)

    @property
    def microphone_array(self: "CastSelf") -> "_2697.MicrophoneArray":
        from mastapy._private.system_model.part_model import _2697

        return self.__parent__._cast(_2697.MicrophoneArray)

    @property
    def root_assembly(self: "CastSelf") -> "_2711.RootAssembly":
        from mastapy._private.system_model.part_model import _2711

        return self.__parent__._cast(_2711.RootAssembly)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2713.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2713

        return self.__parent__._cast(_2713.SpecialisedAssembly)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2756.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2756

        return self.__parent__._cast(_2756.AGMAGleasonConicalGearSet)

    @property
    def bevel_differential_gear_set(
        self: "CastSelf",
    ) -> "_2758.BevelDifferentialGearSet":
        from mastapy._private.system_model.part_model.gears import _2758

        return self.__parent__._cast(_2758.BevelDifferentialGearSet)

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2762.BevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2762

        return self.__parent__._cast(_2762.BevelGearSet)

    @property
    def concept_gear_set(self: "CastSelf") -> "_2764.ConceptGearSet":
        from mastapy._private.system_model.part_model.gears import _2764

        return self.__parent__._cast(_2764.ConceptGearSet)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2766.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2766

        return self.__parent__._cast(_2766.ConicalGearSet)

    @property
    def cylindrical_gear_set(self: "CastSelf") -> "_2768.CylindricalGearSet":
        from mastapy._private.system_model.part_model.gears import _2768

        return self.__parent__._cast(_2768.CylindricalGearSet)

    @property
    def face_gear_set(self: "CastSelf") -> "_2771.FaceGearSet":
        from mastapy._private.system_model.part_model.gears import _2771

        return self.__parent__._cast(_2771.FaceGearSet)

    @property
    def gear_set(self: "CastSelf") -> "_2774.GearSet":
        from mastapy._private.system_model.part_model.gears import _2774

        return self.__parent__._cast(_2774.GearSet)

    @property
    def hypoid_gear_set(self: "CastSelf") -> "_2777.HypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2777

        return self.__parent__._cast(_2777.HypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set(
        self: "CastSelf",
    ) -> "_2779.KlingelnbergCycloPalloidConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2779

        return self.__parent__._cast(_2779.KlingelnbergCycloPalloidConicalGearSet)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "CastSelf",
    ) -> "_2781.KlingelnbergCycloPalloidHypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2781

        return self.__parent__._cast(_2781.KlingelnbergCycloPalloidHypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "CastSelf",
    ) -> "_2783.KlingelnbergCycloPalloidSpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2783

        return self.__parent__._cast(_2783.KlingelnbergCycloPalloidSpiralBevelGearSet)

    @property
    def planetary_gear_set(self: "CastSelf") -> "_2784.PlanetaryGearSet":
        from mastapy._private.system_model.part_model.gears import _2784

        return self.__parent__._cast(_2784.PlanetaryGearSet)

    @property
    def spiral_bevel_gear_set(self: "CastSelf") -> "_2787.SpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2787

        return self.__parent__._cast(_2787.SpiralBevelGearSet)

    @property
    def straight_bevel_diff_gear_set(
        self: "CastSelf",
    ) -> "_2789.StraightBevelDiffGearSet":
        from mastapy._private.system_model.part_model.gears import _2789

        return self.__parent__._cast(_2789.StraightBevelDiffGearSet)

    @property
    def straight_bevel_gear_set(self: "CastSelf") -> "_2791.StraightBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2791

        return self.__parent__._cast(_2791.StraightBevelGearSet)

    @property
    def worm_gear_set(self: "CastSelf") -> "_2795.WormGearSet":
        from mastapy._private.system_model.part_model.gears import _2795

        return self.__parent__._cast(_2795.WormGearSet)

    @property
    def zerol_bevel_gear_set(self: "CastSelf") -> "_2797.ZerolBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2797

        return self.__parent__._cast(_2797.ZerolBevelGearSet)

    @property
    def cycloidal_assembly(self: "CastSelf") -> "_2811.CycloidalAssembly":
        from mastapy._private.system_model.part_model.cycloidal import _2811

        return self.__parent__._cast(_2811.CycloidalAssembly)

    @property
    def belt_drive(self: "CastSelf") -> "_2820.BeltDrive":
        from mastapy._private.system_model.part_model.couplings import _2820

        return self.__parent__._cast(_2820.BeltDrive)

    @property
    def clutch(self: "CastSelf") -> "_2822.Clutch":
        from mastapy._private.system_model.part_model.couplings import _2822

        return self.__parent__._cast(_2822.Clutch)

    @property
    def concept_coupling(self: "CastSelf") -> "_2825.ConceptCoupling":
        from mastapy._private.system_model.part_model.couplings import _2825

        return self.__parent__._cast(_2825.ConceptCoupling)

    @property
    def coupling(self: "CastSelf") -> "_2828.Coupling":
        from mastapy._private.system_model.part_model.couplings import _2828

        return self.__parent__._cast(_2828.Coupling)

    @property
    def cvt(self: "CastSelf") -> "_2831.CVT":
        from mastapy._private.system_model.part_model.couplings import _2831

        return self.__parent__._cast(_2831.CVT)

    @property
    def part_to_part_shear_coupling(
        self: "CastSelf",
    ) -> "_2833.PartToPartShearCoupling":
        from mastapy._private.system_model.part_model.couplings import _2833

        return self.__parent__._cast(_2833.PartToPartShearCoupling)

    @property
    def rolling_ring_assembly(self: "CastSelf") -> "_2844.RollingRingAssembly":
        from mastapy._private.system_model.part_model.couplings import _2844

        return self.__parent__._cast(_2844.RollingRingAssembly)

    @property
    def spring_damper(self: "CastSelf") -> "_2851.SpringDamper":
        from mastapy._private.system_model.part_model.couplings import _2851

        return self.__parent__._cast(_2851.SpringDamper)

    @property
    def synchroniser(self: "CastSelf") -> "_2853.Synchroniser":
        from mastapy._private.system_model.part_model.couplings import _2853

        return self.__parent__._cast(_2853.Synchroniser)

    @property
    def torque_converter(self: "CastSelf") -> "_2858.TorqueConverter":
        from mastapy._private.system_model.part_model.couplings import _2858

        return self.__parent__._cast(_2858.TorqueConverter)

    @property
    def abstract_assembly(self: "CastSelf") -> "AbstractAssembly":
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
class AbstractAssembly(_2703.Part):
    """AbstractAssembly

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_ASSEMBLY

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def mass_of_assembly(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MassOfAssembly")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def components_with_unknown_mass_properties(
        self: "Self",
    ) -> "List[_2675.Component]":
        """List[mastapy.system_model.part_model.Component]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ComponentsWithUnknownMassProperties"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def components_with_zero_mass_properties(self: "Self") -> "List[_2675.Component]":
        """List[mastapy.system_model.part_model.Component]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentsWithZeroMassProperties")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractAssembly":
        """Cast to another type.

        Returns:
            _Cast_AbstractAssembly
        """
        return _Cast_AbstractAssembly(self)
