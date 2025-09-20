"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.import_from_cad._2733 import (
        AbstractShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2734 import (
        ClutchFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2735 import (
        ComponentFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2736 import (
        ComponentFromCADBase,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2737 import (
        ConceptBearingFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2738 import (
        ConnectorFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2739 import (
        CylindricalGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2740 import (
        CylindricalGearInPlanetarySetFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2741 import (
        CylindricalPlanetGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2742 import (
        CylindricalRingGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2743 import (
        CylindricalSunGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2744 import (
        HousedOrMounted,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2745 import (
        MountableComponentFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2746 import (
        PlanetShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2747 import (
        PulleyFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2748 import (
        RigidConnectorFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2749 import (
        RollingBearingFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2750 import (
        ShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2751 import (
        ShaftFromCADAuto,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.import_from_cad._2733": [
            "AbstractShaftFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2734": ["ClutchFromCAD"],
        "_private.system_model.part_model.import_from_cad._2735": ["ComponentFromCAD"],
        "_private.system_model.part_model.import_from_cad._2736": [
            "ComponentFromCADBase"
        ],
        "_private.system_model.part_model.import_from_cad._2737": [
            "ConceptBearingFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2738": ["ConnectorFromCAD"],
        "_private.system_model.part_model.import_from_cad._2739": [
            "CylindricalGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2740": [
            "CylindricalGearInPlanetarySetFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2741": [
            "CylindricalPlanetGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2742": [
            "CylindricalRingGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2743": [
            "CylindricalSunGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2744": ["HousedOrMounted"],
        "_private.system_model.part_model.import_from_cad._2745": [
            "MountableComponentFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2746": [
            "PlanetShaftFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2747": ["PulleyFromCAD"],
        "_private.system_model.part_model.import_from_cad._2748": [
            "RigidConnectorFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2749": [
            "RollingBearingFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2750": ["ShaftFromCAD"],
        "_private.system_model.part_model.import_from_cad._2751": ["ShaftFromCADAuto"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractShaftFromCAD",
    "ClutchFromCAD",
    "ComponentFromCAD",
    "ComponentFromCADBase",
    "ConceptBearingFromCAD",
    "ConnectorFromCAD",
    "CylindricalGearFromCAD",
    "CylindricalGearInPlanetarySetFromCAD",
    "CylindricalPlanetGearFromCAD",
    "CylindricalRingGearFromCAD",
    "CylindricalSunGearFromCAD",
    "HousedOrMounted",
    "MountableComponentFromCAD",
    "PlanetShaftFromCAD",
    "PulleyFromCAD",
    "RigidConnectorFromCAD",
    "RollingBearingFromCAD",
    "ShaftFromCAD",
    "ShaftFromCADAuto",
)
