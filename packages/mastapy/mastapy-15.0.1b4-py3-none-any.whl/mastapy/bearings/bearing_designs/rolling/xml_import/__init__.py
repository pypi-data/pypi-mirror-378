"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2392 import (
        AbstractXmlVariableAssignment,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2393 import (
        BearingImportFile,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2394 import (
        RollingBearingImporter,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2395 import (
        XmlBearingTypeMapping,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2396 import (
        XMLVariableAssignment,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.bearing_designs.rolling.xml_import._2392": [
            "AbstractXmlVariableAssignment"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2393": [
            "BearingImportFile"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2394": [
            "RollingBearingImporter"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2395": [
            "XmlBearingTypeMapping"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2396": [
            "XMLVariableAssignment"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractXmlVariableAssignment",
    "BearingImportFile",
    "RollingBearingImporter",
    "XmlBearingTypeMapping",
    "XMLVariableAssignment",
)
