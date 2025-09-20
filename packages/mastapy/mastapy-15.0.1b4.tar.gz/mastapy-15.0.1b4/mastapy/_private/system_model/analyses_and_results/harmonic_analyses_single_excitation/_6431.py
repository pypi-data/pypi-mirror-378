"""StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _6338,
)

_STRAIGHT_BEVEL_DIFF_GEAR_MESH_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation",
        "StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7885,
        _7888,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6326,
        _6354,
        _6356,
        _6380,
        _6387,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7836
    from mastapy._private.system_model.connections_and_sockets.gears import _2551

    Self = TypeVar(
        "Self", bound="StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation._Cast_StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation"

    @property
    def bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6338.BevelGearMeshHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6338.BevelGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def agma_gleason_conical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6326.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6326,
        )

        return self.__parent__._cast(
            _6326.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6354.ConicalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6354,
        )

        return self.__parent__._cast(
            _6354.ConicalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6380.GearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6380,
        )

        return self.__parent__._cast(_6380.GearMeshHarmonicAnalysisOfSingleExcitation)

    @property
    def inter_mountable_component_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6387.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6387,
        )

        return self.__parent__._cast(
            _6387.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6356.ConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6356,
        )

        return self.__parent__._cast(_6356.ConnectionHarmonicAnalysisOfSingleExcitation)

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
    def straight_bevel_diff_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation":
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
class StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation(
    _6338.BevelGearMeshHarmonicAnalysisOfSingleExcitation
):
    """StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _STRAIGHT_BEVEL_DIFF_GEAR_MESH_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation(self)
