"""CylindricalGearMeshModalAnalysisAtAStiffness"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
    _5196,
)

_CYLINDRICAL_GEAR_MESH_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
    "CylindricalGearMeshModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7885,
        _7888,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5172,
        _5203,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7737
    from mastapy._private.system_model.connections_and_sockets.gears import _2535

    Self = TypeVar("Self", bound="CylindricalGearMeshModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearMeshModalAnalysisAtAStiffness._Cast_CylindricalGearMeshModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMeshModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMeshModalAnalysisAtAStiffness:
    """Special nested class for casting CylindricalGearMeshModalAnalysisAtAStiffness to subclasses."""

    __parent__: "CylindricalGearMeshModalAnalysisAtAStiffness"

    @property
    def gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5196.GearMeshModalAnalysisAtAStiffness":
        return self.__parent__._cast(_5196.GearMeshModalAnalysisAtAStiffness)

    @property
    def inter_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5203.InterMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5203,
        )

        return self.__parent__._cast(
            _5203.InterMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5172.ConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5172,
        )

        return self.__parent__._cast(_5172.ConnectionModalAnalysisAtAStiffness)

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7888.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7888,
        )

        return self.__parent__._cast(_7888.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7885.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7885,
        )

        return self.__parent__._cast(_7885.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2895.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2895

        return self.__parent__._cast(_2895.ConnectionAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2899.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2899

        return self.__parent__._cast(_2899.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def cylindrical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "CylindricalGearMeshModalAnalysisAtAStiffness":
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
class CylindricalGearMeshModalAnalysisAtAStiffness(
    _5196.GearMeshModalAnalysisAtAStiffness
):
    """CylindricalGearMeshModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH_MODAL_ANALYSIS_AT_A_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2535.CylindricalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.CylindricalGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_load_case(self: "Self") -> "_7737.CylindricalGearMeshLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.CylindricalGearMeshLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(
        self: "Self",
    ) -> "List[CylindricalGearMeshModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.CylindricalGearMeshModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMeshModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMeshModalAnalysisAtAStiffness
        """
        return _Cast_CylindricalGearMeshModalAnalysisAtAStiffness(self)
