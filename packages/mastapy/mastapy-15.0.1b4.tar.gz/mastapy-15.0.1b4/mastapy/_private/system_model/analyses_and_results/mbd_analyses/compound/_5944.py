"""TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
    _5861,
)

_TORQUE_CONVERTER_TURBINE_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7890,
        _7893,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5805
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5847,
        _5901,
        _5903,
    )
    from mastapy._private.system_model.part_model.couplings import _2861

    Self = TypeVar(
        "Self", bound="TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis._Cast_TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis"

    @property
    def coupling_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5861.CouplingHalfCompoundMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5861.CouplingHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def mountable_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5901.MountableComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5901,
        )

        return self.__parent__._cast(
            _5901.MountableComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5847.ComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5847,
        )

        return self.__parent__._cast(_5847.ComponentCompoundMultibodyDynamicsAnalysis)

    @property
    def part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5903.PartCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5903,
        )

        return self.__parent__._cast(_5903.PartCompoundMultibodyDynamicsAnalysis)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7893.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7893,
        )

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
    def torque_converter_turbine_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis":
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
class TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis(
    _5861.CouplingHalfCompoundMultibodyDynamicsAnalysis
):
    """TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _TORQUE_CONVERTER_TURBINE_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2861.TorqueConverterTurbine":
        """mastapy.system_model.part_model.couplings.TorqueConverterTurbine

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5805.TorqueConverterTurbineMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.TorqueConverterTurbineMultibodyDynamicsAnalysis]

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
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_5805.TorqueConverterTurbineMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.TorqueConverterTurbineMultibodyDynamicsAnalysis]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis(self)
