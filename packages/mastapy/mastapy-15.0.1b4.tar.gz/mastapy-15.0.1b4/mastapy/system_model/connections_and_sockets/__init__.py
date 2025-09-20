"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.connections_and_sockets._2491 import (
        AbstractShaftToMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2492 import (
        BearingInnerSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2493 import (
        BearingOuterSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2494 import (
        BeltConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2495 import (
        CoaxialConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2496 import (
        ComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2497 import (
        ComponentMeasurer,
    )
    from mastapy._private.system_model.connections_and_sockets._2498 import Connection
    from mastapy._private.system_model.connections_and_sockets._2499 import (
        CVTBeltConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2500 import (
        CVTPulleySocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2501 import (
        CylindricalComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2502 import (
        CylindricalSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2503 import (
        DatumMeasurement,
    )
    from mastapy._private.system_model.connections_and_sockets._2504 import (
        ElectricMachineStatorSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2505 import (
        InnerShaftSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2506 import (
        InnerShaftSocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2507 import (
        InterMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2508 import (
        MountableComponentInnerSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2509 import (
        MountableComponentOuterSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2510 import (
        MountableComponentSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2511 import (
        OuterShaftSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2512 import (
        OuterShaftSocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2513 import (
        PlanetaryConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2514 import (
        PlanetarySocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2515 import (
        PlanetarySocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2516 import PulleySocket
    from mastapy._private.system_model.connections_and_sockets._2517 import (
        RealignmentResult,
    )
    from mastapy._private.system_model.connections_and_sockets._2518 import (
        RollingRingConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2519 import (
        RollingRingSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2520 import ShaftSocket
    from mastapy._private.system_model.connections_and_sockets._2521 import (
        ShaftToMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2522 import Socket
    from mastapy._private.system_model.connections_and_sockets._2523 import (
        SocketConnectionOptions,
    )
    from mastapy._private.system_model.connections_and_sockets._2524 import (
        SocketConnectionSelection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.connections_and_sockets._2491": [
            "AbstractShaftToMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2492": ["BearingInnerSocket"],
        "_private.system_model.connections_and_sockets._2493": ["BearingOuterSocket"],
        "_private.system_model.connections_and_sockets._2494": ["BeltConnection"],
        "_private.system_model.connections_and_sockets._2495": ["CoaxialConnection"],
        "_private.system_model.connections_and_sockets._2496": ["ComponentConnection"],
        "_private.system_model.connections_and_sockets._2497": ["ComponentMeasurer"],
        "_private.system_model.connections_and_sockets._2498": ["Connection"],
        "_private.system_model.connections_and_sockets._2499": ["CVTBeltConnection"],
        "_private.system_model.connections_and_sockets._2500": ["CVTPulleySocket"],
        "_private.system_model.connections_and_sockets._2501": [
            "CylindricalComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2502": ["CylindricalSocket"],
        "_private.system_model.connections_and_sockets._2503": ["DatumMeasurement"],
        "_private.system_model.connections_and_sockets._2504": [
            "ElectricMachineStatorSocket"
        ],
        "_private.system_model.connections_and_sockets._2505": ["InnerShaftSocket"],
        "_private.system_model.connections_and_sockets._2506": ["InnerShaftSocketBase"],
        "_private.system_model.connections_and_sockets._2507": [
            "InterMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2508": [
            "MountableComponentInnerSocket"
        ],
        "_private.system_model.connections_and_sockets._2509": [
            "MountableComponentOuterSocket"
        ],
        "_private.system_model.connections_and_sockets._2510": [
            "MountableComponentSocket"
        ],
        "_private.system_model.connections_and_sockets._2511": ["OuterShaftSocket"],
        "_private.system_model.connections_and_sockets._2512": ["OuterShaftSocketBase"],
        "_private.system_model.connections_and_sockets._2513": ["PlanetaryConnection"],
        "_private.system_model.connections_and_sockets._2514": ["PlanetarySocket"],
        "_private.system_model.connections_and_sockets._2515": ["PlanetarySocketBase"],
        "_private.system_model.connections_and_sockets._2516": ["PulleySocket"],
        "_private.system_model.connections_and_sockets._2517": ["RealignmentResult"],
        "_private.system_model.connections_and_sockets._2518": [
            "RollingRingConnection"
        ],
        "_private.system_model.connections_and_sockets._2519": ["RollingRingSocket"],
        "_private.system_model.connections_and_sockets._2520": ["ShaftSocket"],
        "_private.system_model.connections_and_sockets._2521": [
            "ShaftToMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2522": ["Socket"],
        "_private.system_model.connections_and_sockets._2523": [
            "SocketConnectionOptions"
        ],
        "_private.system_model.connections_and_sockets._2524": [
            "SocketConnectionSelection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractShaftToMountableComponentConnection",
    "BearingInnerSocket",
    "BearingOuterSocket",
    "BeltConnection",
    "CoaxialConnection",
    "ComponentConnection",
    "ComponentMeasurer",
    "Connection",
    "CVTBeltConnection",
    "CVTPulleySocket",
    "CylindricalComponentConnection",
    "CylindricalSocket",
    "DatumMeasurement",
    "ElectricMachineStatorSocket",
    "InnerShaftSocket",
    "InnerShaftSocketBase",
    "InterMountableComponentConnection",
    "MountableComponentInnerSocket",
    "MountableComponentOuterSocket",
    "MountableComponentSocket",
    "OuterShaftSocket",
    "OuterShaftSocketBase",
    "PlanetaryConnection",
    "PlanetarySocket",
    "PlanetarySocketBase",
    "PulleySocket",
    "RealignmentResult",
    "RollingRingConnection",
    "RollingRingSocket",
    "ShaftSocket",
    "ShaftToMountableComponentConnection",
    "Socket",
    "SocketConnectionOptions",
    "SocketConnectionSelection",
)
