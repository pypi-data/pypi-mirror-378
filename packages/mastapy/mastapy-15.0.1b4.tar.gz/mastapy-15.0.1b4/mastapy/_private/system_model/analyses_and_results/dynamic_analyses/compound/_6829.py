"""SpiralBevelGearMeshCompoundDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6744,
)

_SPIRAL_BEVEL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "SpiralBevelGearMeshCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6698,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6732,
        _6760,
        _6762,
        _6786,
        _6792,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2549

    Self = TypeVar("Self", bound="SpiralBevelGearMeshCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SpiralBevelGearMeshCompoundDynamicAnalysis._Cast_SpiralBevelGearMeshCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpiralBevelGearMeshCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpiralBevelGearMeshCompoundDynamicAnalysis:
    """Special nested class for casting SpiralBevelGearMeshCompoundDynamicAnalysis to subclasses."""

    __parent__: "SpiralBevelGearMeshCompoundDynamicAnalysis"

    @property
    def bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6744.BevelGearMeshCompoundDynamicAnalysis":
        return self.__parent__._cast(_6744.BevelGearMeshCompoundDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6732.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6732,
        )

        return self.__parent__._cast(
            _6732.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6760.ConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6760,
        )

        return self.__parent__._cast(_6760.ConicalGearMeshCompoundDynamicAnalysis)

    @property
    def gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6786.GearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6786,
        )

        return self.__parent__._cast(_6786.GearMeshCompoundDynamicAnalysis)

    @property
    def inter_mountable_component_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6792.InterMountableComponentConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6792,
        )

        return self.__parent__._cast(
            _6792.InterMountableComponentConnectionCompoundDynamicAnalysis
        )

    @property
    def connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6762.ConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6762,
        )

        return self.__parent__._cast(_6762.ConnectionCompoundDynamicAnalysis)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7886,
        )

        return self.__parent__._cast(_7886.ConnectionCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7890.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7890,
        )

        return self.__parent__._cast(_7890.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def spiral_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "SpiralBevelGearMeshCompoundDynamicAnalysis":
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
class SpiralBevelGearMeshCompoundDynamicAnalysis(
    _6744.BevelGearMeshCompoundDynamicAnalysis
):
    """SpiralBevelGearMeshCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPIRAL_BEVEL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2549.SpiralBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.SpiralBevelGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2549.SpiralBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.SpiralBevelGearMesh

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
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6698.SpiralBevelGearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.SpiralBevelGearMeshDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6698.SpiralBevelGearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.SpiralBevelGearMeshDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_SpiralBevelGearMeshCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_SpiralBevelGearMeshCompoundDynamicAnalysis
        """
        return _Cast_SpiralBevelGearMeshCompoundDynamicAnalysis(self)
