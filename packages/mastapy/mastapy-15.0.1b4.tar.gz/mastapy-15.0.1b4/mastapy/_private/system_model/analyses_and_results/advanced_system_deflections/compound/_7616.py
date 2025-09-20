"""PartCompoundAdvancedSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7893

_PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound",
    "PartCompoundAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7484,
    )
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
        _7535,
        _7536,
        _7537,
        _7539,
        _7541,
        _7542,
        _7543,
        _7545,
        _7546,
        _7548,
        _7549,
        _7550,
        _7551,
        _7553,
        _7554,
        _7555,
        _7556,
        _7558,
        _7560,
        _7561,
        _7563,
        _7564,
        _7566,
        _7567,
        _7569,
        _7571,
        _7572,
        _7574,
        _7576,
        _7577,
        _7578,
        _7580,
        _7582,
        _7584,
        _7585,
        _7586,
        _7587,
        _7588,
        _7590,
        _7591,
        _7592,
        _7593,
        _7595,
        _7596,
        _7597,
        _7599,
        _7601,
        _7603,
        _7604,
        _7606,
        _7607,
        _7609,
        _7610,
        _7611,
        _7612,
        _7613,
        _7614,
        _7615,
        _7617,
        _7619,
        _7621,
        _7622,
        _7623,
        _7624,
        _7625,
        _7626,
        _7628,
        _7629,
        _7631,
        _7632,
        _7633,
        _7635,
        _7636,
        _7638,
        _7639,
        _7641,
        _7642,
        _7644,
        _7645,
        _7647,
        _7648,
        _7649,
        _7650,
        _7651,
        _7652,
        _7653,
        _7654,
        _7656,
        _7657,
        _7658,
        _7659,
        _7660,
        _7662,
        _7663,
        _7665,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890

    Self = TypeVar("Self", bound="PartCompoundAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundAdvancedSystemDeflection._Cast_PartCompoundAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundAdvancedSystemDeflection:
    """Special nested class for casting PartCompoundAdvancedSystemDeflection to subclasses."""

    __parent__: "PartCompoundAdvancedSystemDeflection"

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7893.PartCompoundAnalysis":
        return self.__parent__._cast(_7893.PartCompoundAnalysis)

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
    def abstract_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7535.AbstractAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7535,
        )

        return self.__parent__._cast(
            _7535.AbstractAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def abstract_shaft_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7536.AbstractShaftCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7536,
        )

        return self.__parent__._cast(
            _7536.AbstractShaftCompoundAdvancedSystemDeflection
        )

    @property
    def abstract_shaft_or_housing_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7537.AbstractShaftOrHousingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7537,
        )

        return self.__parent__._cast(
            _7537.AbstractShaftOrHousingCompoundAdvancedSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7539.AGMAGleasonConicalGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7539,
        )

        return self.__parent__._cast(
            _7539.AGMAGleasonConicalGearCompoundAdvancedSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7541.AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7541,
        )

        return self.__parent__._cast(
            _7541.AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7542.AssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7542,
        )

        return self.__parent__._cast(_7542.AssemblyCompoundAdvancedSystemDeflection)

    @property
    def bearing_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7543.BearingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7543,
        )

        return self.__parent__._cast(_7543.BearingCompoundAdvancedSystemDeflection)

    @property
    def belt_drive_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7545.BeltDriveCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7545,
        )

        return self.__parent__._cast(_7545.BeltDriveCompoundAdvancedSystemDeflection)

    @property
    def bevel_differential_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7546.BevelDifferentialGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7546,
        )

        return self.__parent__._cast(
            _7546.BevelDifferentialGearCompoundAdvancedSystemDeflection
        )

    @property
    def bevel_differential_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7548.BevelDifferentialGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7548,
        )

        return self.__parent__._cast(
            _7548.BevelDifferentialGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def bevel_differential_planet_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7549.BevelDifferentialPlanetGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7549,
        )

        return self.__parent__._cast(
            _7549.BevelDifferentialPlanetGearCompoundAdvancedSystemDeflection
        )

    @property
    def bevel_differential_sun_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7550.BevelDifferentialSunGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7550,
        )

        return self.__parent__._cast(
            _7550.BevelDifferentialSunGearCompoundAdvancedSystemDeflection
        )

    @property
    def bevel_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7551.BevelGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7551,
        )

        return self.__parent__._cast(_7551.BevelGearCompoundAdvancedSystemDeflection)

    @property
    def bevel_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7553.BevelGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7553,
        )

        return self.__parent__._cast(_7553.BevelGearSetCompoundAdvancedSystemDeflection)

    @property
    def bolt_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7554.BoltCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7554,
        )

        return self.__parent__._cast(_7554.BoltCompoundAdvancedSystemDeflection)

    @property
    def bolted_joint_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7555.BoltedJointCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7555,
        )

        return self.__parent__._cast(_7555.BoltedJointCompoundAdvancedSystemDeflection)

    @property
    def clutch_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7556.ClutchCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7556,
        )

        return self.__parent__._cast(_7556.ClutchCompoundAdvancedSystemDeflection)

    @property
    def clutch_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7558.ClutchHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7558,
        )

        return self.__parent__._cast(_7558.ClutchHalfCompoundAdvancedSystemDeflection)

    @property
    def component_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7560.ComponentCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7560,
        )

        return self.__parent__._cast(_7560.ComponentCompoundAdvancedSystemDeflection)

    @property
    def concept_coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7561.ConceptCouplingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7561,
        )

        return self.__parent__._cast(
            _7561.ConceptCouplingCompoundAdvancedSystemDeflection
        )

    @property
    def concept_coupling_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7563.ConceptCouplingHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7563,
        )

        return self.__parent__._cast(
            _7563.ConceptCouplingHalfCompoundAdvancedSystemDeflection
        )

    @property
    def concept_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7564.ConceptGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7564,
        )

        return self.__parent__._cast(_7564.ConceptGearCompoundAdvancedSystemDeflection)

    @property
    def concept_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7566.ConceptGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7566,
        )

        return self.__parent__._cast(
            _7566.ConceptGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def conical_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7567.ConicalGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7567,
        )

        return self.__parent__._cast(_7567.ConicalGearCompoundAdvancedSystemDeflection)

    @property
    def conical_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7569.ConicalGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7569,
        )

        return self.__parent__._cast(
            _7569.ConicalGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def connector_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7571.ConnectorCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7571,
        )

        return self.__parent__._cast(_7571.ConnectorCompoundAdvancedSystemDeflection)

    @property
    def coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7572.CouplingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7572,
        )

        return self.__parent__._cast(_7572.CouplingCompoundAdvancedSystemDeflection)

    @property
    def coupling_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7574.CouplingHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7574,
        )

        return self.__parent__._cast(_7574.CouplingHalfCompoundAdvancedSystemDeflection)

    @property
    def cvt_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7576.CVTCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7576,
        )

        return self.__parent__._cast(_7576.CVTCompoundAdvancedSystemDeflection)

    @property
    def cvt_pulley_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7577.CVTPulleyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7577,
        )

        return self.__parent__._cast(_7577.CVTPulleyCompoundAdvancedSystemDeflection)

    @property
    def cycloidal_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7578.CycloidalAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7578,
        )

        return self.__parent__._cast(
            _7578.CycloidalAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def cycloidal_disc_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7580.CycloidalDiscCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7580,
        )

        return self.__parent__._cast(
            _7580.CycloidalDiscCompoundAdvancedSystemDeflection
        )

    @property
    def cylindrical_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7582.CylindricalGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7582,
        )

        return self.__parent__._cast(
            _7582.CylindricalGearCompoundAdvancedSystemDeflection
        )

    @property
    def cylindrical_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7584.CylindricalGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7584,
        )

        return self.__parent__._cast(
            _7584.CylindricalGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def cylindrical_planet_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7585.CylindricalPlanetGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7585,
        )

        return self.__parent__._cast(
            _7585.CylindricalPlanetGearCompoundAdvancedSystemDeflection
        )

    @property
    def datum_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7586.DatumCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7586,
        )

        return self.__parent__._cast(_7586.DatumCompoundAdvancedSystemDeflection)

    @property
    def external_cad_model_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7587.ExternalCADModelCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7587,
        )

        return self.__parent__._cast(
            _7587.ExternalCADModelCompoundAdvancedSystemDeflection
        )

    @property
    def face_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7588.FaceGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7588,
        )

        return self.__parent__._cast(_7588.FaceGearCompoundAdvancedSystemDeflection)

    @property
    def face_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7590.FaceGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7590,
        )

        return self.__parent__._cast(_7590.FaceGearSetCompoundAdvancedSystemDeflection)

    @property
    def fe_part_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7591.FEPartCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7591,
        )

        return self.__parent__._cast(_7591.FEPartCompoundAdvancedSystemDeflection)

    @property
    def flexible_pin_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7592.FlexiblePinAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7592,
        )

        return self.__parent__._cast(
            _7592.FlexiblePinAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7593.GearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7593,
        )

        return self.__parent__._cast(_7593.GearCompoundAdvancedSystemDeflection)

    @property
    def gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7595.GearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7595,
        )

        return self.__parent__._cast(_7595.GearSetCompoundAdvancedSystemDeflection)

    @property
    def guide_dxf_model_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7596.GuideDxfModelCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7596,
        )

        return self.__parent__._cast(
            _7596.GuideDxfModelCompoundAdvancedSystemDeflection
        )

    @property
    def hypoid_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7597.HypoidGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7597,
        )

        return self.__parent__._cast(_7597.HypoidGearCompoundAdvancedSystemDeflection)

    @property
    def hypoid_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7599.HypoidGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7599,
        )

        return self.__parent__._cast(
            _7599.HypoidGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7601.KlingelnbergCycloPalloidConicalGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7601,
        )

        return self.__parent__._cast(
            _7601.KlingelnbergCycloPalloidConicalGearCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7603.KlingelnbergCycloPalloidConicalGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7603,
        )

        return self.__parent__._cast(
            _7603.KlingelnbergCycloPalloidConicalGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7604.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7604,
        )

        return self.__parent__._cast(
            _7604.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7606.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7606,
        )

        return self.__parent__._cast(
            _7606.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> (
        "_7607.KlingelnbergCycloPalloidSpiralBevelGearCompoundAdvancedSystemDeflection"
    ):
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7607,
        )

        return self.__parent__._cast(
            _7607.KlingelnbergCycloPalloidSpiralBevelGearCompoundAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7609.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7609,
        )

        return self.__parent__._cast(
            _7609.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def mass_disc_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7610.MassDiscCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7610,
        )

        return self.__parent__._cast(_7610.MassDiscCompoundAdvancedSystemDeflection)

    @property
    def measurement_component_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7611.MeasurementComponentCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7611,
        )

        return self.__parent__._cast(
            _7611.MeasurementComponentCompoundAdvancedSystemDeflection
        )

    @property
    def microphone_array_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7612.MicrophoneArrayCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7612,
        )

        return self.__parent__._cast(
            _7612.MicrophoneArrayCompoundAdvancedSystemDeflection
        )

    @property
    def microphone_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7613.MicrophoneCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7613,
        )

        return self.__parent__._cast(_7613.MicrophoneCompoundAdvancedSystemDeflection)

    @property
    def mountable_component_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7614.MountableComponentCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7614,
        )

        return self.__parent__._cast(
            _7614.MountableComponentCompoundAdvancedSystemDeflection
        )

    @property
    def oil_seal_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7615.OilSealCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7615,
        )

        return self.__parent__._cast(_7615.OilSealCompoundAdvancedSystemDeflection)

    @property
    def part_to_part_shear_coupling_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7617.PartToPartShearCouplingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7617,
        )

        return self.__parent__._cast(
            _7617.PartToPartShearCouplingCompoundAdvancedSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7619.PartToPartShearCouplingHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7619,
        )

        return self.__parent__._cast(
            _7619.PartToPartShearCouplingHalfCompoundAdvancedSystemDeflection
        )

    @property
    def planetary_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7621.PlanetaryGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7621,
        )

        return self.__parent__._cast(
            _7621.PlanetaryGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def planet_carrier_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7622.PlanetCarrierCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7622,
        )

        return self.__parent__._cast(
            _7622.PlanetCarrierCompoundAdvancedSystemDeflection
        )

    @property
    def point_load_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7623.PointLoadCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7623,
        )

        return self.__parent__._cast(_7623.PointLoadCompoundAdvancedSystemDeflection)

    @property
    def power_load_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7624.PowerLoadCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7624,
        )

        return self.__parent__._cast(_7624.PowerLoadCompoundAdvancedSystemDeflection)

    @property
    def pulley_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7625.PulleyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7625,
        )

        return self.__parent__._cast(_7625.PulleyCompoundAdvancedSystemDeflection)

    @property
    def ring_pins_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7626.RingPinsCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7626,
        )

        return self.__parent__._cast(_7626.RingPinsCompoundAdvancedSystemDeflection)

    @property
    def rolling_ring_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7628.RollingRingAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7628,
        )

        return self.__parent__._cast(
            _7628.RollingRingAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def rolling_ring_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7629.RollingRingCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7629,
        )

        return self.__parent__._cast(_7629.RollingRingCompoundAdvancedSystemDeflection)

    @property
    def root_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7631.RootAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7631,
        )

        return self.__parent__._cast(_7631.RootAssemblyCompoundAdvancedSystemDeflection)

    @property
    def shaft_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7632.ShaftCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7632,
        )

        return self.__parent__._cast(_7632.ShaftCompoundAdvancedSystemDeflection)

    @property
    def shaft_hub_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7633.ShaftHubConnectionCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7633,
        )

        return self.__parent__._cast(
            _7633.ShaftHubConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def specialised_assembly_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7635,
        )

        return self.__parent__._cast(
            _7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection
        )

    @property
    def spiral_bevel_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7636.SpiralBevelGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7636,
        )

        return self.__parent__._cast(
            _7636.SpiralBevelGearCompoundAdvancedSystemDeflection
        )

    @property
    def spiral_bevel_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7638.SpiralBevelGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7638,
        )

        return self.__parent__._cast(
            _7638.SpiralBevelGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def spring_damper_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7639.SpringDamperCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7639,
        )

        return self.__parent__._cast(_7639.SpringDamperCompoundAdvancedSystemDeflection)

    @property
    def spring_damper_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7641.SpringDamperHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7641,
        )

        return self.__parent__._cast(
            _7641.SpringDamperHalfCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_diff_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7642.StraightBevelDiffGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7642,
        )

        return self.__parent__._cast(
            _7642.StraightBevelDiffGearCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_diff_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7644.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7644,
        )

        return self.__parent__._cast(
            _7644.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7645.StraightBevelGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7645,
        )

        return self.__parent__._cast(
            _7645.StraightBevelGearCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7647.StraightBevelGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7647,
        )

        return self.__parent__._cast(
            _7647.StraightBevelGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_planet_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7648.StraightBevelPlanetGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7648,
        )

        return self.__parent__._cast(
            _7648.StraightBevelPlanetGearCompoundAdvancedSystemDeflection
        )

    @property
    def straight_bevel_sun_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7649.StraightBevelSunGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7649,
        )

        return self.__parent__._cast(
            _7649.StraightBevelSunGearCompoundAdvancedSystemDeflection
        )

    @property
    def synchroniser_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7650.SynchroniserCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7650,
        )

        return self.__parent__._cast(_7650.SynchroniserCompoundAdvancedSystemDeflection)

    @property
    def synchroniser_half_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7651.SynchroniserHalfCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7651,
        )

        return self.__parent__._cast(
            _7651.SynchroniserHalfCompoundAdvancedSystemDeflection
        )

    @property
    def synchroniser_part_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7652.SynchroniserPartCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7652,
        )

        return self.__parent__._cast(
            _7652.SynchroniserPartCompoundAdvancedSystemDeflection
        )

    @property
    def synchroniser_sleeve_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7653.SynchroniserSleeveCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7653,
        )

        return self.__parent__._cast(
            _7653.SynchroniserSleeveCompoundAdvancedSystemDeflection
        )

    @property
    def torque_converter_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7654.TorqueConverterCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7654,
        )

        return self.__parent__._cast(
            _7654.TorqueConverterCompoundAdvancedSystemDeflection
        )

    @property
    def torque_converter_pump_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7656.TorqueConverterPumpCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7656,
        )

        return self.__parent__._cast(
            _7656.TorqueConverterPumpCompoundAdvancedSystemDeflection
        )

    @property
    def torque_converter_turbine_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7657.TorqueConverterTurbineCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7657,
        )

        return self.__parent__._cast(
            _7657.TorqueConverterTurbineCompoundAdvancedSystemDeflection
        )

    @property
    def unbalanced_mass_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7658.UnbalancedMassCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7658,
        )

        return self.__parent__._cast(
            _7658.UnbalancedMassCompoundAdvancedSystemDeflection
        )

    @property
    def virtual_component_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7659.VirtualComponentCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7659,
        )

        return self.__parent__._cast(
            _7659.VirtualComponentCompoundAdvancedSystemDeflection
        )

    @property
    def worm_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7660.WormGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7660,
        )

        return self.__parent__._cast(_7660.WormGearCompoundAdvancedSystemDeflection)

    @property
    def worm_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7662.WormGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7662,
        )

        return self.__parent__._cast(_7662.WormGearSetCompoundAdvancedSystemDeflection)

    @property
    def zerol_bevel_gear_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7663.ZerolBevelGearCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7663,
        )

        return self.__parent__._cast(
            _7663.ZerolBevelGearCompoundAdvancedSystemDeflection
        )

    @property
    def zerol_bevel_gear_set_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7665.ZerolBevelGearSetCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7665,
        )

        return self.__parent__._cast(
            _7665.ZerolBevelGearSetCompoundAdvancedSystemDeflection
        )

    @property
    def part_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "PartCompoundAdvancedSystemDeflection":
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
class PartCompoundAdvancedSystemDeflection(_7893.PartCompoundAnalysis):
    """PartCompoundAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_7484.PartAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.PartAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_7484.PartAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.PartAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_PartCompoundAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundAdvancedSystemDeflection
        """
        return _Cast_PartCompoundAdvancedSystemDeflection(self)
