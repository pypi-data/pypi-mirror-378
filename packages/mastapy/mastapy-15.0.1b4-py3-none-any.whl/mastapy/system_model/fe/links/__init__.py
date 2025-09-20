"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.fe.links._2648 import FELink
    from mastapy._private.system_model.fe.links._2649 import ElectricMachineStatorFELink
    from mastapy._private.system_model.fe.links._2650 import FELinkWithSelection
    from mastapy._private.system_model.fe.links._2651 import GearMeshFELink
    from mastapy._private.system_model.fe.links._2652 import (
        GearWithDuplicatedMeshesFELink,
    )
    from mastapy._private.system_model.fe.links._2653 import MultiAngleConnectionFELink
    from mastapy._private.system_model.fe.links._2654 import MultiNodeConnectorFELink
    from mastapy._private.system_model.fe.links._2655 import MultiNodeFELink
    from mastapy._private.system_model.fe.links._2656 import (
        PlanetaryConnectorMultiNodeFELink,
    )
    from mastapy._private.system_model.fe.links._2657 import PlanetBasedFELink
    from mastapy._private.system_model.fe.links._2658 import PlanetCarrierFELink
    from mastapy._private.system_model.fe.links._2659 import PointLoadFELink
    from mastapy._private.system_model.fe.links._2660 import RollingRingConnectionFELink
    from mastapy._private.system_model.fe.links._2661 import ShaftHubConnectionFELink
    from mastapy._private.system_model.fe.links._2662 import SingleNodeFELink
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.fe.links._2648": ["FELink"],
        "_private.system_model.fe.links._2649": ["ElectricMachineStatorFELink"],
        "_private.system_model.fe.links._2650": ["FELinkWithSelection"],
        "_private.system_model.fe.links._2651": ["GearMeshFELink"],
        "_private.system_model.fe.links._2652": ["GearWithDuplicatedMeshesFELink"],
        "_private.system_model.fe.links._2653": ["MultiAngleConnectionFELink"],
        "_private.system_model.fe.links._2654": ["MultiNodeConnectorFELink"],
        "_private.system_model.fe.links._2655": ["MultiNodeFELink"],
        "_private.system_model.fe.links._2656": ["PlanetaryConnectorMultiNodeFELink"],
        "_private.system_model.fe.links._2657": ["PlanetBasedFELink"],
        "_private.system_model.fe.links._2658": ["PlanetCarrierFELink"],
        "_private.system_model.fe.links._2659": ["PointLoadFELink"],
        "_private.system_model.fe.links._2660": ["RollingRingConnectionFELink"],
        "_private.system_model.fe.links._2661": ["ShaftHubConnectionFELink"],
        "_private.system_model.fe.links._2662": ["SingleNodeFELink"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "FELink",
    "ElectricMachineStatorFELink",
    "FELinkWithSelection",
    "GearMeshFELink",
    "GearWithDuplicatedMeshesFELink",
    "MultiAngleConnectionFELink",
    "MultiNodeConnectorFELink",
    "MultiNodeFELink",
    "PlanetaryConnectorMultiNodeFELink",
    "PlanetBasedFELink",
    "PlanetCarrierFELink",
    "PointLoadFELink",
    "RollingRingConnectionFELink",
    "ShaftHubConnectionFELink",
    "SingleNodeFELink",
)
