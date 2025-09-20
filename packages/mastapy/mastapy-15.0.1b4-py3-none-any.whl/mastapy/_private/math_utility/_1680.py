"""ComplexVector"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.math_utility import _1678

_COMPLEX_VECTOR = python_net_import("SMT.MastaAPI.MathUtility", "ComplexVector")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.math_utility import _1681, _1682, _1699

    Self = TypeVar("Self", bound="ComplexVector")
    CastSelf = TypeVar("CastSelf", bound="ComplexVector._Cast_ComplexVector")


__docformat__ = "restructuredtext en"
__all__ = ("ComplexVector",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComplexVector:
    """Special nested class for casting ComplexVector to subclasses."""

    __parent__: "ComplexVector"

    @property
    def complex_matrix(self: "CastSelf") -> "_1678.ComplexMatrix":
        return self.__parent__._cast(_1678.ComplexMatrix)

    @property
    def generic_matrix(self: "CastSelf") -> "_1699.GenericMatrix":
        from mastapy._private.math_utility import _1699

        return self.__parent__._cast(_1699.GenericMatrix)

    @property
    def complex_vector_3d(self: "CastSelf") -> "_1681.ComplexVector3D":
        from mastapy._private.math_utility import _1681

        return self.__parent__._cast(_1681.ComplexVector3D)

    @property
    def complex_vector_6d(self: "CastSelf") -> "_1682.ComplexVector6D":
        from mastapy._private.math_utility import _1682

        return self.__parent__._cast(_1682.ComplexVector6D)

    @property
    def complex_vector(self: "CastSelf") -> "ComplexVector":
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
class ComplexVector(_1678.ComplexMatrix):
    """ComplexVector

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPLEX_VECTOR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ComplexVector":
        """Cast to another type.

        Returns:
            _Cast_ComplexVector
        """
        return _Cast_ComplexVector(self)
