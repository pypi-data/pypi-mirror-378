"""NodalComposite"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.nodal_analysis.nodal_entities import _155

_NODAL_COMPOSITE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "NodalComposite"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import (
        _134,
        _135,
        _136,
        _140,
        _141,
        _142,
        _143,
        _147,
        _149,
        _150,
        _161,
        _162,
        _167,
        _168,
        _169,
        _170,
    )

    Self = TypeVar("Self", bound="NodalComposite")
    CastSelf = TypeVar("CastSelf", bound="NodalComposite._Cast_NodalComposite")


__docformat__ = "restructuredtext en"
__all__ = ("NodalComposite",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NodalComposite:
    """Special nested class for casting NodalComposite to subclasses."""

    __parent__: "NodalComposite"

    @property
    def nodal_entity(self: "CastSelf") -> "_155.NodalEntity":
        return self.__parent__._cast(_155.NodalEntity)

    @property
    def bar_elastic_mbd(self: "CastSelf") -> "_134.BarElasticMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _134

        return self.__parent__._cast(_134.BarElasticMBD)

    @property
    def bar_mbd(self: "CastSelf") -> "_135.BarMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _135

        return self.__parent__._cast(_135.BarMBD)

    @property
    def bar_rigid_mbd(self: "CastSelf") -> "_136.BarRigidMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _136

        return self.__parent__._cast(_136.BarRigidMBD)

    @property
    def component_nodal_composite(self: "CastSelf") -> "_140.ComponentNodalComposite":
        from mastapy._private.nodal_analysis.nodal_entities import _140

        return self.__parent__._cast(_140.ComponentNodalComposite)

    @property
    def component_nodal_composite_base(
        self: "CastSelf",
    ) -> "_141.ComponentNodalCompositeBase":
        from mastapy._private.nodal_analysis.nodal_entities import _141

        return self.__parent__._cast(_141.ComponentNodalCompositeBase)

    @property
    def concentric_connection_nodal_component(
        self: "CastSelf",
    ) -> "_142.ConcentricConnectionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _142

        return self.__parent__._cast(_142.ConcentricConnectionNodalComponent)

    @property
    def concentric_connection_nodal_component_base(
        self: "CastSelf",
    ) -> "_143.ConcentricConnectionNodalComponentBase":
        from mastapy._private.nodal_analysis.nodal_entities import _143

        return self.__parent__._cast(_143.ConcentricConnectionNodalComponentBase)

    @property
    def gear_mesh_nodal_component(self: "CastSelf") -> "_147.GearMeshNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _147

        return self.__parent__._cast(_147.GearMeshNodalComponent)

    @property
    def gear_mesh_point_on_flank_contact(
        self: "CastSelf",
    ) -> "_149.GearMeshPointOnFlankContact":
        from mastapy._private.nodal_analysis.nodal_entities import _149

        return self.__parent__._cast(_149.GearMeshPointOnFlankContact)

    @property
    def gear_mesh_single_flank_contact(
        self: "CastSelf",
    ) -> "_150.GearMeshSingleFlankContact":
        from mastapy._private.nodal_analysis.nodal_entities import _150

        return self.__parent__._cast(_150.GearMeshSingleFlankContact)

    @property
    def simple_bar(self: "CastSelf") -> "_161.SimpleBar":
        from mastapy._private.nodal_analysis.nodal_entities import _161

        return self.__parent__._cast(_161.SimpleBar)

    @property
    def spline_contact_nodal_component(
        self: "CastSelf",
    ) -> "_162.SplineContactNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _162

        return self.__parent__._cast(_162.SplineContactNodalComponent)

    @property
    def torsional_friction_node_pair(
        self: "CastSelf",
    ) -> "_167.TorsionalFrictionNodePair":
        from mastapy._private.nodal_analysis.nodal_entities import _167

        return self.__parent__._cast(_167.TorsionalFrictionNodePair)

    @property
    def torsional_friction_node_pair_base(
        self: "CastSelf",
    ) -> "_168.TorsionalFrictionNodePairBase":
        from mastapy._private.nodal_analysis.nodal_entities import _168

        return self.__parent__._cast(_168.TorsionalFrictionNodePairBase)

    @property
    def torsional_friction_node_pair_simple_locked_stiffness(
        self: "CastSelf",
    ) -> "_169.TorsionalFrictionNodePairSimpleLockedStiffness":
        from mastapy._private.nodal_analysis.nodal_entities import _169

        return self.__parent__._cast(
            _169.TorsionalFrictionNodePairSimpleLockedStiffness
        )

    @property
    def two_body_connection_nodal_component(
        self: "CastSelf",
    ) -> "_170.TwoBodyConnectionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _170

        return self.__parent__._cast(_170.TwoBodyConnectionNodalComponent)

    @property
    def nodal_composite(self: "CastSelf") -> "NodalComposite":
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
class NodalComposite(_155.NodalEntity):
    """NodalComposite

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NODAL_COMPOSITE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_NodalComposite":
        """Cast to another type.

        Returns:
            _Cast_NodalComposite
        """
        return _Cast_NodalComposite(self)
