"""KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool"""

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
from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
    _4639,
)

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools",
    "KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7885
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4598,
        _4601,
        _4631,
        _4638,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7790
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3017,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2545

    Self = TypeVar(
        "Self", bound="KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool._Cast_KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool:
    """Special nested class for casting KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool to subclasses."""

    __parent__: "KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4639.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool":
        return self.__parent__._cast(
            _4639.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool
        )

    @property
    def conical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4598.ConicalGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4598,
        )

        return self.__parent__._cast(_4598.ConicalGearMeshParametricStudyTool)

    @property
    def gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4631.GearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4631,
        )

        return self.__parent__._cast(_4631.GearMeshParametricStudyTool)

    @property
    def inter_mountable_component_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4638.InterMountableComponentConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4638,
        )

        return self.__parent__._cast(
            _4638.InterMountableComponentConnectionParametricStudyTool
        )

    @property
    def connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4601.ConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4601,
        )

        return self.__parent__._cast(_4601.ConnectionParametricStudyTool)

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
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool":
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
class KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool(
    _4639.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool
):
    """KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH_PARAMETRIC_STUDY_TOOL
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(
        self: "Self",
    ) -> "_2545.KlingelnbergCycloPalloidHypoidGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidHypoidGearMesh

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
    def connection_load_case(
        self: "Self",
    ) -> "_7790.KlingelnbergCycloPalloidHypoidGearMeshLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.KlingelnbergCycloPalloidHypoidGearMeshLoadCase

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
    def connection_system_deflection_results(
        self: "Self",
    ) -> "List[_3017.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionSystemDeflectionResults")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool
        """
        return _Cast_KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool(self)
