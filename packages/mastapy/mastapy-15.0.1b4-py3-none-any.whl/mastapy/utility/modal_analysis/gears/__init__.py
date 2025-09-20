"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.modal_analysis.gears._1999 import GearMeshForTE
    from mastapy._private.utility.modal_analysis.gears._2000 import GearOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2001 import GearPositions
    from mastapy._private.utility.modal_analysis.gears._2002 import HarmonicOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2003 import LabelOnlyOrder
    from mastapy._private.utility.modal_analysis.gears._2004 import OrderForTE
    from mastapy._private.utility.modal_analysis.gears._2005 import OrderSelector
    from mastapy._private.utility.modal_analysis.gears._2006 import OrderWithRadius
    from mastapy._private.utility.modal_analysis.gears._2007 import RollingBearingOrder
    from mastapy._private.utility.modal_analysis.gears._2008 import ShaftOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2009 import (
        UserDefinedOrderForTE,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.modal_analysis.gears._1999": ["GearMeshForTE"],
        "_private.utility.modal_analysis.gears._2000": ["GearOrderForTE"],
        "_private.utility.modal_analysis.gears._2001": ["GearPositions"],
        "_private.utility.modal_analysis.gears._2002": ["HarmonicOrderForTE"],
        "_private.utility.modal_analysis.gears._2003": ["LabelOnlyOrder"],
        "_private.utility.modal_analysis.gears._2004": ["OrderForTE"],
        "_private.utility.modal_analysis.gears._2005": ["OrderSelector"],
        "_private.utility.modal_analysis.gears._2006": ["OrderWithRadius"],
        "_private.utility.modal_analysis.gears._2007": ["RollingBearingOrder"],
        "_private.utility.modal_analysis.gears._2008": ["ShaftOrderForTE"],
        "_private.utility.modal_analysis.gears._2009": ["UserDefinedOrderForTE"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "GearMeshForTE",
    "GearOrderForTE",
    "GearPositions",
    "HarmonicOrderForTE",
    "LabelOnlyOrder",
    "OrderForTE",
    "OrderSelector",
    "OrderWithRadius",
    "RollingBearingOrder",
    "ShaftOrderForTE",
    "UserDefinedOrderForTE",
)
