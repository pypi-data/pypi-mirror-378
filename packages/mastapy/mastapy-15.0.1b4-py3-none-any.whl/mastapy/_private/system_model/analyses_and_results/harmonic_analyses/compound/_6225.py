"""ConnectionCompoundHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7886

_CONNECTION_COMPOUND_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound",
    "ConnectionCompoundHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6010,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
        _6193,
        _6195,
        _6199,
        _6202,
        _6207,
        _6212,
        _6214,
        _6217,
        _6220,
        _6223,
        _6228,
        _6230,
        _6234,
        _6236,
        _6238,
        _6244,
        _6249,
        _6253,
        _6255,
        _6257,
        _6260,
        _6263,
        _6273,
        _6275,
        _6282,
        _6285,
        _6289,
        _6292,
        _6295,
        _6298,
        _6301,
        _6310,
        _6316,
        _6319,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundHarmonicAnalysis._Cast_ConnectionCompoundHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundHarmonicAnalysis:
    """Special nested class for casting ConnectionCompoundHarmonicAnalysis to subclasses."""

    __parent__: "ConnectionCompoundHarmonicAnalysis"

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
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
    def abstract_shaft_to_mountable_component_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6193.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6193,
        )

        return self.__parent__._cast(
            _6193.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysis
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6195.AGMAGleasonConicalGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6195,
        )

        return self.__parent__._cast(
            _6195.AGMAGleasonConicalGearMeshCompoundHarmonicAnalysis
        )

    @property
    def belt_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6199.BeltConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6199,
        )

        return self.__parent__._cast(_6199.BeltConnectionCompoundHarmonicAnalysis)

    @property
    def bevel_differential_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6202.BevelDifferentialGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6202,
        )

        return self.__parent__._cast(
            _6202.BevelDifferentialGearMeshCompoundHarmonicAnalysis
        )

    @property
    def bevel_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6207.BevelGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6207,
        )

        return self.__parent__._cast(_6207.BevelGearMeshCompoundHarmonicAnalysis)

    @property
    def clutch_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6212.ClutchConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6212,
        )

        return self.__parent__._cast(_6212.ClutchConnectionCompoundHarmonicAnalysis)

    @property
    def coaxial_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6214.CoaxialConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6214,
        )

        return self.__parent__._cast(_6214.CoaxialConnectionCompoundHarmonicAnalysis)

    @property
    def concept_coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6217.ConceptCouplingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6217,
        )

        return self.__parent__._cast(
            _6217.ConceptCouplingConnectionCompoundHarmonicAnalysis
        )

    @property
    def concept_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6220.ConceptGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6220,
        )

        return self.__parent__._cast(_6220.ConceptGearMeshCompoundHarmonicAnalysis)

    @property
    def conical_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6223.ConicalGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6223,
        )

        return self.__parent__._cast(_6223.ConicalGearMeshCompoundHarmonicAnalysis)

    @property
    def coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6228.CouplingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6228,
        )

        return self.__parent__._cast(_6228.CouplingConnectionCompoundHarmonicAnalysis)

    @property
    def cvt_belt_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6230.CVTBeltConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6230,
        )

        return self.__parent__._cast(_6230.CVTBeltConnectionCompoundHarmonicAnalysis)

    @property
    def cycloidal_disc_central_bearing_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6234.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6234,
        )

        return self.__parent__._cast(
            _6234.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysis
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6236.CycloidalDiscPlanetaryBearingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6236,
        )

        return self.__parent__._cast(
            _6236.CycloidalDiscPlanetaryBearingConnectionCompoundHarmonicAnalysis
        )

    @property
    def cylindrical_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6238.CylindricalGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6238,
        )

        return self.__parent__._cast(_6238.CylindricalGearMeshCompoundHarmonicAnalysis)

    @property
    def face_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6244.FaceGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6244,
        )

        return self.__parent__._cast(_6244.FaceGearMeshCompoundHarmonicAnalysis)

    @property
    def gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6249.GearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6249,
        )

        return self.__parent__._cast(_6249.GearMeshCompoundHarmonicAnalysis)

    @property
    def hypoid_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6253.HypoidGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6253,
        )

        return self.__parent__._cast(_6253.HypoidGearMeshCompoundHarmonicAnalysis)

    @property
    def inter_mountable_component_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6255.InterMountableComponentConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6255,
        )

        return self.__parent__._cast(
            _6255.InterMountableComponentConnectionCompoundHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6257.KlingelnbergCycloPalloidConicalGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6257,
        )

        return self.__parent__._cast(
            _6257.KlingelnbergCycloPalloidConicalGearMeshCompoundHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6260.KlingelnbergCycloPalloidHypoidGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6260,
        )

        return self.__parent__._cast(
            _6260.KlingelnbergCycloPalloidHypoidGearMeshCompoundHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6263.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6263,
        )

        return self.__parent__._cast(
            _6263.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundHarmonicAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6273.PartToPartShearCouplingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6273,
        )

        return self.__parent__._cast(
            _6273.PartToPartShearCouplingConnectionCompoundHarmonicAnalysis
        )

    @property
    def planetary_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6275.PlanetaryConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6275,
        )

        return self.__parent__._cast(_6275.PlanetaryConnectionCompoundHarmonicAnalysis)

    @property
    def ring_pins_to_disc_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6282.RingPinsToDiscConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6282,
        )

        return self.__parent__._cast(
            _6282.RingPinsToDiscConnectionCompoundHarmonicAnalysis
        )

    @property
    def rolling_ring_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6285.RollingRingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6285,
        )

        return self.__parent__._cast(
            _6285.RollingRingConnectionCompoundHarmonicAnalysis
        )

    @property
    def shaft_to_mountable_component_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6289.ShaftToMountableComponentConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6289,
        )

        return self.__parent__._cast(
            _6289.ShaftToMountableComponentConnectionCompoundHarmonicAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6292.SpiralBevelGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6292,
        )

        return self.__parent__._cast(_6292.SpiralBevelGearMeshCompoundHarmonicAnalysis)

    @property
    def spring_damper_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6295.SpringDamperConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6295,
        )

        return self.__parent__._cast(
            _6295.SpringDamperConnectionCompoundHarmonicAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6298.StraightBevelDiffGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6298,
        )

        return self.__parent__._cast(
            _6298.StraightBevelDiffGearMeshCompoundHarmonicAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6301.StraightBevelGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6301,
        )

        return self.__parent__._cast(
            _6301.StraightBevelGearMeshCompoundHarmonicAnalysis
        )

    @property
    def torque_converter_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6310.TorqueConverterConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6310,
        )

        return self.__parent__._cast(
            _6310.TorqueConverterConnectionCompoundHarmonicAnalysis
        )

    @property
    def worm_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6316.WormGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6316,
        )

        return self.__parent__._cast(_6316.WormGearMeshCompoundHarmonicAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6319.ZerolBevelGearMeshCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6319,
        )

        return self.__parent__._cast(_6319.ZerolBevelGearMeshCompoundHarmonicAnalysis)

    @property
    def connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "ConnectionCompoundHarmonicAnalysis":
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
class ConnectionCompoundHarmonicAnalysis(_7886.ConnectionCompoundAnalysis):
    """ConnectionCompoundHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6010.ConnectionHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ConnectionHarmonicAnalysis]

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
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6010.ConnectionHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ConnectionHarmonicAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_ConnectionCompoundHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundHarmonicAnalysis
        """
        return _Cast_ConnectionCompoundHarmonicAnalysis(self)
