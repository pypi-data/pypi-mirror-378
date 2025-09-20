"""CMSElementFaceGroupOfAllFreeFaces"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.nodal_analysis.component_mode_synthesis import _311

_CMS_ELEMENT_FACE_GROUP_OF_ALL_FREE_FACES = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis",
    "CMSElementFaceGroupOfAllFreeFaces",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.dev_tools_analyses import _266, _268

    Self = TypeVar("Self", bound="CMSElementFaceGroupOfAllFreeFaces")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CMSElementFaceGroupOfAllFreeFaces._Cast_CMSElementFaceGroupOfAllFreeFaces",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CMSElementFaceGroupOfAllFreeFaces",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CMSElementFaceGroupOfAllFreeFaces:
    """Special nested class for casting CMSElementFaceGroupOfAllFreeFaces to subclasses."""

    __parent__: "CMSElementFaceGroupOfAllFreeFaces"

    @property
    def cms_element_face_group(self: "CastSelf") -> "_311.CMSElementFaceGroup":
        return self.__parent__._cast(_311.CMSElementFaceGroup)

    @property
    def element_face_group(self: "CastSelf") -> "_266.ElementFaceGroup":
        from mastapy._private.nodal_analysis.dev_tools_analyses import _266

        return self.__parent__._cast(_266.ElementFaceGroup)

    @property
    def fe_entity_group(self: "CastSelf") -> "_268.FEEntityGroup":
        pass

        from mastapy._private.nodal_analysis.dev_tools_analyses import _268

        return self.__parent__._cast(_268.FEEntityGroup)

    @property
    def cms_element_face_group_of_all_free_faces(
        self: "CastSelf",
    ) -> "CMSElementFaceGroupOfAllFreeFaces":
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
class CMSElementFaceGroupOfAllFreeFaces(_311.CMSElementFaceGroup):
    """CMSElementFaceGroupOfAllFreeFaces

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CMS_ELEMENT_FACE_GROUP_OF_ALL_FREE_FACES

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CMSElementFaceGroupOfAllFreeFaces":
        """Cast to another type.

        Returns:
            _Cast_CMSElementFaceGroupOfAllFreeFaces
        """
        return _Cast_CMSElementFaceGroupOfAllFreeFaces(self)
