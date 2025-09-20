"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.shaft_model._2719 import Shaft
    from mastapy._private.system_model.part_model.shaft_model._2720 import ShaftBow
    from mastapy._private.system_model.part_model.shaft_model._2721 import (
        WindageLossCalculationOilParameters,
    )
    from mastapy._private.system_model.part_model.shaft_model._2722 import (
        WindageLossCalculationParametersForCurvedSurfaceOfSection,
    )
    from mastapy._private.system_model.part_model.shaft_model._2723 import (
        WindageLossCalculationParametersForEndOfSection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.shaft_model._2719": ["Shaft"],
        "_private.system_model.part_model.shaft_model._2720": ["ShaftBow"],
        "_private.system_model.part_model.shaft_model._2721": [
            "WindageLossCalculationOilParameters"
        ],
        "_private.system_model.part_model.shaft_model._2722": [
            "WindageLossCalculationParametersForCurvedSurfaceOfSection"
        ],
        "_private.system_model.part_model.shaft_model._2723": [
            "WindageLossCalculationParametersForEndOfSection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Shaft",
    "ShaftBow",
    "WindageLossCalculationOilParameters",
    "WindageLossCalculationParametersForCurvedSurfaceOfSection",
    "WindageLossCalculationParametersForEndOfSection",
)
