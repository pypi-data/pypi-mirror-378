"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.geometry_modeller_link._230 import (
        BaseGeometryModellerDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._231 import (
        GearTipRadiusClashTest,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._232 import (
        GeometryModellerAngleDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._233 import (
        GeometryModellerCountDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._234 import (
        GeometryModellerDesignInformation,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._235 import (
        GeometryModellerDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._236 import (
        GeometryModellerDimensions,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._237 import (
        GeometryModellerDimensionType,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._238 import (
        GeometryModellerLengthDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._239 import (
        GeometryModellerSettings,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._240 import (
        GeometryModellerUnitlessDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._241 import (
        GeometryTypeForComponentImport,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._242 import MeshRequest
    from mastapy._private.nodal_analysis.geometry_modeller_link._243 import (
        MeshRequestResult,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._244 import (
        ProfileFromImport,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._245 import (
        RepositionComponentDetails,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.geometry_modeller_link._230": [
            "BaseGeometryModellerDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._231": [
            "GearTipRadiusClashTest"
        ],
        "_private.nodal_analysis.geometry_modeller_link._232": [
            "GeometryModellerAngleDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._233": [
            "GeometryModellerCountDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._234": [
            "GeometryModellerDesignInformation"
        ],
        "_private.nodal_analysis.geometry_modeller_link._235": [
            "GeometryModellerDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._236": [
            "GeometryModellerDimensions"
        ],
        "_private.nodal_analysis.geometry_modeller_link._237": [
            "GeometryModellerDimensionType"
        ],
        "_private.nodal_analysis.geometry_modeller_link._238": [
            "GeometryModellerLengthDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._239": [
            "GeometryModellerSettings"
        ],
        "_private.nodal_analysis.geometry_modeller_link._240": [
            "GeometryModellerUnitlessDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._241": [
            "GeometryTypeForComponentImport"
        ],
        "_private.nodal_analysis.geometry_modeller_link._242": ["MeshRequest"],
        "_private.nodal_analysis.geometry_modeller_link._243": ["MeshRequestResult"],
        "_private.nodal_analysis.geometry_modeller_link._244": ["ProfileFromImport"],
        "_private.nodal_analysis.geometry_modeller_link._245": [
            "RepositionComponentDetails"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BaseGeometryModellerDimension",
    "GearTipRadiusClashTest",
    "GeometryModellerAngleDimension",
    "GeometryModellerCountDimension",
    "GeometryModellerDesignInformation",
    "GeometryModellerDimension",
    "GeometryModellerDimensions",
    "GeometryModellerDimensionType",
    "GeometryModellerLengthDimension",
    "GeometryModellerSettings",
    "GeometryModellerUnitlessDimension",
    "GeometryTypeForComponentImport",
    "MeshRequest",
    "MeshRequestResult",
    "ProfileFromImport",
    "RepositionComponentDetails",
)
