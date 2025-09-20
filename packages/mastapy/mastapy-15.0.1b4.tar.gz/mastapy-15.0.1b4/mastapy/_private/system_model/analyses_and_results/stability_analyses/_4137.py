"""StraightBevelDiffGearMeshStabilityAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.stability_analyses import _4041

_STRAIGHT_BEVEL_DIFF_GEAR_MESH_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses",
    "StraightBevelDiffGearMeshStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7885,
        _7888,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4029,
        _4057,
        _4060,
        _4085,
        _4092,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7836
    from mastapy._private.system_model.connections_and_sockets.gears import _2551

    Self = TypeVar("Self", bound="StraightBevelDiffGearMeshStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearMeshStabilityAnalysis._Cast_StraightBevelDiffGearMeshStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearMeshStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearMeshStabilityAnalysis:
    """Special nested class for casting StraightBevelDiffGearMeshStabilityAnalysis to subclasses."""

    __parent__: "StraightBevelDiffGearMeshStabilityAnalysis"

    @property
    def bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4041.BevelGearMeshStabilityAnalysis":
        return self.__parent__._cast(_4041.BevelGearMeshStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4029.AGMAGleasonConicalGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4029,
        )

        return self.__parent__._cast(_4029.AGMAGleasonConicalGearMeshStabilityAnalysis)

    @property
    def conical_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4057.ConicalGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4057,
        )

        return self.__parent__._cast(_4057.ConicalGearMeshStabilityAnalysis)

    @property
    def gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4085.GearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4085,
        )

        return self.__parent__._cast(_4085.GearMeshStabilityAnalysis)

    @property
    def inter_mountable_component_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4092.InterMountableComponentConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4092,
        )

        return self.__parent__._cast(
            _4092.InterMountableComponentConnectionStabilityAnalysis
        )

    @property
    def connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4060.ConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4060,
        )

        return self.__parent__._cast(_4060.ConnectionStabilityAnalysis)

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
    def straight_bevel_diff_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearMeshStabilityAnalysis":
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
class StraightBevelDiffGearMeshStabilityAnalysis(_4041.BevelGearMeshStabilityAnalysis):
    """StraightBevelDiffGearMeshStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_DIFF_GEAR_MESH_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2551.StraightBevelDiffGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.StraightBevelDiffGearMesh

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
    def connection_load_case(self: "Self") -> "_7836.StraightBevelDiffGearMeshLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.StraightBevelDiffGearMeshLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelDiffGearMeshStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearMeshStabilityAnalysis
        """
        return _Cast_StraightBevelDiffGearMeshStabilityAnalysis(self)
