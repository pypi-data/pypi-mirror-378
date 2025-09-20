"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.bevel.control_parameters._921 import (
        ConicalGearManufacturingControlParameters,
    )
    from mastapy._private.gears.manufacturing.bevel.control_parameters._922 import (
        ConicalManufacturingSGMControlParameters,
    )
    from mastapy._private.gears.manufacturing.bevel.control_parameters._923 import (
        ConicalManufacturingSGTControlParameters,
    )
    from mastapy._private.gears.manufacturing.bevel.control_parameters._924 import (
        ConicalManufacturingSMTControlParameters,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.bevel.control_parameters._921": [
            "ConicalGearManufacturingControlParameters"
        ],
        "_private.gears.manufacturing.bevel.control_parameters._922": [
            "ConicalManufacturingSGMControlParameters"
        ],
        "_private.gears.manufacturing.bevel.control_parameters._923": [
            "ConicalManufacturingSGTControlParameters"
        ],
        "_private.gears.manufacturing.bevel.control_parameters._924": [
            "ConicalManufacturingSMTControlParameters"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearManufacturingControlParameters",
    "ConicalManufacturingSGMControlParameters",
    "ConicalManufacturingSGTControlParameters",
    "ConicalManufacturingSMTControlParameters",
)
