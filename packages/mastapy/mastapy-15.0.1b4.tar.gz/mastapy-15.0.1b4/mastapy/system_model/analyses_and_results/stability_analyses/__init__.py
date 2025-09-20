"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4025 import (
        AbstractAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4026 import (
        AbstractShaftOrHousingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4027 import (
        AbstractShaftStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4028 import (
        AbstractShaftToMountableComponentConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4029 import (
        AGMAGleasonConicalGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4030 import (
        AGMAGleasonConicalGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4031 import (
        AGMAGleasonConicalGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4032 import (
        AssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4033 import (
        BearingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4034 import (
        BeltConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4035 import (
        BeltDriveStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4036 import (
        BevelDifferentialGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4037 import (
        BevelDifferentialGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4038 import (
        BevelDifferentialGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4039 import (
        BevelDifferentialPlanetGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4040 import (
        BevelDifferentialSunGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4041 import (
        BevelGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4042 import (
        BevelGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4043 import (
        BevelGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4044 import (
        BoltedJointStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4045 import (
        BoltStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4046 import (
        ClutchConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4047 import (
        ClutchHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4048 import (
        ClutchStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4049 import (
        CoaxialConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4050 import (
        ComponentStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4051 import (
        ConceptCouplingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4052 import (
        ConceptCouplingHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4053 import (
        ConceptCouplingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4054 import (
        ConceptGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4055 import (
        ConceptGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4056 import (
        ConceptGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4057 import (
        ConicalGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4058 import (
        ConicalGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4059 import (
        ConicalGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4060 import (
        ConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4061 import (
        ConnectorStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4062 import (
        CouplingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4063 import (
        CouplingHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4064 import (
        CouplingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4065 import (
        CriticalSpeed,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4066 import (
        CVTBeltConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4067 import (
        CVTPulleyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4068 import (
        CVTStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4069 import (
        CycloidalAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4070 import (
        CycloidalDiscCentralBearingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4071 import (
        CycloidalDiscPlanetaryBearingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4072 import (
        CycloidalDiscStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4073 import (
        CylindricalGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4074 import (
        CylindricalGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4075 import (
        CylindricalGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4076 import (
        CylindricalPlanetGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4077 import (
        DatumStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4078 import (
        DynamicModelForStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4079 import (
        ExternalCADModelStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4080 import (
        FaceGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4081 import (
        FaceGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4082 import (
        FaceGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4083 import (
        FEPartStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4084 import (
        FlexiblePinAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4085 import (
        GearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4086 import (
        GearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4087 import (
        GearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4088 import (
        GuideDxfModelStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4089 import (
        HypoidGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4090 import (
        HypoidGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4091 import (
        HypoidGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4092 import (
        InterMountableComponentConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4093 import (
        KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4094 import (
        KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4095 import (
        KlingelnbergCycloPalloidConicalGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4096 import (
        KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4097 import (
        KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4098 import (
        KlingelnbergCycloPalloidHypoidGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4099 import (
        KlingelnbergCycloPalloidSpiralBevelGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4100 import (
        KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4101 import (
        KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4102 import (
        MassDiscStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4103 import (
        MeasurementComponentStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4104 import (
        MicrophoneArrayStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4105 import (
        MicrophoneStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4106 import (
        MountableComponentStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4107 import (
        OilSealStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4108 import (
        PartStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4109 import (
        PartToPartShearCouplingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4110 import (
        PartToPartShearCouplingHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4111 import (
        PartToPartShearCouplingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4112 import (
        PlanetaryConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4113 import (
        PlanetaryGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4114 import (
        PlanetCarrierStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4115 import (
        PointLoadStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4116 import (
        PowerLoadStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4117 import (
        PulleyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4118 import (
        RingPinsStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4119 import (
        RingPinsToDiscConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4120 import (
        RollingRingAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4121 import (
        RollingRingConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4122 import (
        RollingRingStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4123 import (
        RootAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4124 import (
        ShaftHubConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4125 import (
        ShaftStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4126 import (
        ShaftToMountableComponentConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4127 import (
        SpecialisedAssemblyStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4128 import (
        SpiralBevelGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4129 import (
        SpiralBevelGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4130 import (
        SpiralBevelGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4131 import (
        SpringDamperConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4132 import (
        SpringDamperHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4133 import (
        SpringDamperStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4134 import (
        StabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4135 import (
        StabilityAnalysisDrawStyle,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4136 import (
        StabilityAnalysisOptions,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4137 import (
        StraightBevelDiffGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4138 import (
        StraightBevelDiffGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4139 import (
        StraightBevelDiffGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4140 import (
        StraightBevelGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4141 import (
        StraightBevelGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4142 import (
        StraightBevelGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4143 import (
        StraightBevelPlanetGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4144 import (
        StraightBevelSunGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4145 import (
        SynchroniserHalfStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4146 import (
        SynchroniserPartStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4147 import (
        SynchroniserSleeveStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4148 import (
        SynchroniserStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4149 import (
        TorqueConverterConnectionStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4150 import (
        TorqueConverterPumpStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4151 import (
        TorqueConverterStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4152 import (
        TorqueConverterTurbineStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4153 import (
        UnbalancedMassStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4154 import (
        VirtualComponentStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4155 import (
        WormGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4156 import (
        WormGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4157 import (
        WormGearStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4158 import (
        ZerolBevelGearMeshStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4159 import (
        ZerolBevelGearSetStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses._4160 import (
        ZerolBevelGearStabilityAnalysis,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.stability_analyses._4025": [
            "AbstractAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4026": [
            "AbstractShaftOrHousingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4027": [
            "AbstractShaftStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4028": [
            "AbstractShaftToMountableComponentConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4029": [
            "AGMAGleasonConicalGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4030": [
            "AGMAGleasonConicalGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4031": [
            "AGMAGleasonConicalGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4032": [
            "AssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4033": [
            "BearingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4034": [
            "BeltConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4035": [
            "BeltDriveStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4036": [
            "BevelDifferentialGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4037": [
            "BevelDifferentialGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4038": [
            "BevelDifferentialGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4039": [
            "BevelDifferentialPlanetGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4040": [
            "BevelDifferentialSunGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4041": [
            "BevelGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4042": [
            "BevelGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4043": [
            "BevelGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4044": [
            "BoltedJointStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4045": [
            "BoltStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4046": [
            "ClutchConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4047": [
            "ClutchHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4048": [
            "ClutchStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4049": [
            "CoaxialConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4050": [
            "ComponentStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4051": [
            "ConceptCouplingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4052": [
            "ConceptCouplingHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4053": [
            "ConceptCouplingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4054": [
            "ConceptGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4055": [
            "ConceptGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4056": [
            "ConceptGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4057": [
            "ConicalGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4058": [
            "ConicalGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4059": [
            "ConicalGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4060": [
            "ConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4061": [
            "ConnectorStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4062": [
            "CouplingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4063": [
            "CouplingHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4064": [
            "CouplingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4065": [
            "CriticalSpeed"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4066": [
            "CVTBeltConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4067": [
            "CVTPulleyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4068": [
            "CVTStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4069": [
            "CycloidalAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4070": [
            "CycloidalDiscCentralBearingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4071": [
            "CycloidalDiscPlanetaryBearingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4072": [
            "CycloidalDiscStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4073": [
            "CylindricalGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4074": [
            "CylindricalGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4075": [
            "CylindricalGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4076": [
            "CylindricalPlanetGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4077": [
            "DatumStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4078": [
            "DynamicModelForStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4079": [
            "ExternalCADModelStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4080": [
            "FaceGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4081": [
            "FaceGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4082": [
            "FaceGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4083": [
            "FEPartStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4084": [
            "FlexiblePinAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4085": [
            "GearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4086": [
            "GearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4087": [
            "GearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4088": [
            "GuideDxfModelStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4089": [
            "HypoidGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4090": [
            "HypoidGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4091": [
            "HypoidGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4092": [
            "InterMountableComponentConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4093": [
            "KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4094": [
            "KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4095": [
            "KlingelnbergCycloPalloidConicalGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4096": [
            "KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4097": [
            "KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4098": [
            "KlingelnbergCycloPalloidHypoidGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4099": [
            "KlingelnbergCycloPalloidSpiralBevelGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4100": [
            "KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4101": [
            "KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4102": [
            "MassDiscStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4103": [
            "MeasurementComponentStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4104": [
            "MicrophoneArrayStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4105": [
            "MicrophoneStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4106": [
            "MountableComponentStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4107": [
            "OilSealStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4108": [
            "PartStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4109": [
            "PartToPartShearCouplingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4110": [
            "PartToPartShearCouplingHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4111": [
            "PartToPartShearCouplingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4112": [
            "PlanetaryConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4113": [
            "PlanetaryGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4114": [
            "PlanetCarrierStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4115": [
            "PointLoadStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4116": [
            "PowerLoadStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4117": [
            "PulleyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4118": [
            "RingPinsStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4119": [
            "RingPinsToDiscConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4120": [
            "RollingRingAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4121": [
            "RollingRingConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4122": [
            "RollingRingStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4123": [
            "RootAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4124": [
            "ShaftHubConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4125": [
            "ShaftStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4126": [
            "ShaftToMountableComponentConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4127": [
            "SpecialisedAssemblyStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4128": [
            "SpiralBevelGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4129": [
            "SpiralBevelGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4130": [
            "SpiralBevelGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4131": [
            "SpringDamperConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4132": [
            "SpringDamperHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4133": [
            "SpringDamperStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4134": [
            "StabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4135": [
            "StabilityAnalysisDrawStyle"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4136": [
            "StabilityAnalysisOptions"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4137": [
            "StraightBevelDiffGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4138": [
            "StraightBevelDiffGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4139": [
            "StraightBevelDiffGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4140": [
            "StraightBevelGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4141": [
            "StraightBevelGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4142": [
            "StraightBevelGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4143": [
            "StraightBevelPlanetGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4144": [
            "StraightBevelSunGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4145": [
            "SynchroniserHalfStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4146": [
            "SynchroniserPartStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4147": [
            "SynchroniserSleeveStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4148": [
            "SynchroniserStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4149": [
            "TorqueConverterConnectionStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4150": [
            "TorqueConverterPumpStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4151": [
            "TorqueConverterStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4152": [
            "TorqueConverterTurbineStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4153": [
            "UnbalancedMassStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4154": [
            "VirtualComponentStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4155": [
            "WormGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4156": [
            "WormGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4157": [
            "WormGearStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4158": [
            "ZerolBevelGearMeshStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4159": [
            "ZerolBevelGearSetStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results.stability_analyses._4160": [
            "ZerolBevelGearStabilityAnalysis"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractAssemblyStabilityAnalysis",
    "AbstractShaftOrHousingStabilityAnalysis",
    "AbstractShaftStabilityAnalysis",
    "AbstractShaftToMountableComponentConnectionStabilityAnalysis",
    "AGMAGleasonConicalGearMeshStabilityAnalysis",
    "AGMAGleasonConicalGearSetStabilityAnalysis",
    "AGMAGleasonConicalGearStabilityAnalysis",
    "AssemblyStabilityAnalysis",
    "BearingStabilityAnalysis",
    "BeltConnectionStabilityAnalysis",
    "BeltDriveStabilityAnalysis",
    "BevelDifferentialGearMeshStabilityAnalysis",
    "BevelDifferentialGearSetStabilityAnalysis",
    "BevelDifferentialGearStabilityAnalysis",
    "BevelDifferentialPlanetGearStabilityAnalysis",
    "BevelDifferentialSunGearStabilityAnalysis",
    "BevelGearMeshStabilityAnalysis",
    "BevelGearSetStabilityAnalysis",
    "BevelGearStabilityAnalysis",
    "BoltedJointStabilityAnalysis",
    "BoltStabilityAnalysis",
    "ClutchConnectionStabilityAnalysis",
    "ClutchHalfStabilityAnalysis",
    "ClutchStabilityAnalysis",
    "CoaxialConnectionStabilityAnalysis",
    "ComponentStabilityAnalysis",
    "ConceptCouplingConnectionStabilityAnalysis",
    "ConceptCouplingHalfStabilityAnalysis",
    "ConceptCouplingStabilityAnalysis",
    "ConceptGearMeshStabilityAnalysis",
    "ConceptGearSetStabilityAnalysis",
    "ConceptGearStabilityAnalysis",
    "ConicalGearMeshStabilityAnalysis",
    "ConicalGearSetStabilityAnalysis",
    "ConicalGearStabilityAnalysis",
    "ConnectionStabilityAnalysis",
    "ConnectorStabilityAnalysis",
    "CouplingConnectionStabilityAnalysis",
    "CouplingHalfStabilityAnalysis",
    "CouplingStabilityAnalysis",
    "CriticalSpeed",
    "CVTBeltConnectionStabilityAnalysis",
    "CVTPulleyStabilityAnalysis",
    "CVTStabilityAnalysis",
    "CycloidalAssemblyStabilityAnalysis",
    "CycloidalDiscCentralBearingConnectionStabilityAnalysis",
    "CycloidalDiscPlanetaryBearingConnectionStabilityAnalysis",
    "CycloidalDiscStabilityAnalysis",
    "CylindricalGearMeshStabilityAnalysis",
    "CylindricalGearSetStabilityAnalysis",
    "CylindricalGearStabilityAnalysis",
    "CylindricalPlanetGearStabilityAnalysis",
    "DatumStabilityAnalysis",
    "DynamicModelForStabilityAnalysis",
    "ExternalCADModelStabilityAnalysis",
    "FaceGearMeshStabilityAnalysis",
    "FaceGearSetStabilityAnalysis",
    "FaceGearStabilityAnalysis",
    "FEPartStabilityAnalysis",
    "FlexiblePinAssemblyStabilityAnalysis",
    "GearMeshStabilityAnalysis",
    "GearSetStabilityAnalysis",
    "GearStabilityAnalysis",
    "GuideDxfModelStabilityAnalysis",
    "HypoidGearMeshStabilityAnalysis",
    "HypoidGearSetStabilityAnalysis",
    "HypoidGearStabilityAnalysis",
    "InterMountableComponentConnectionStabilityAnalysis",
    "KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis",
    "KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis",
    "KlingelnbergCycloPalloidConicalGearStabilityAnalysis",
    "KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis",
    "KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis",
    "KlingelnbergCycloPalloidHypoidGearStabilityAnalysis",
    "KlingelnbergCycloPalloidSpiralBevelGearMeshStabilityAnalysis",
    "KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis",
    "KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis",
    "MassDiscStabilityAnalysis",
    "MeasurementComponentStabilityAnalysis",
    "MicrophoneArrayStabilityAnalysis",
    "MicrophoneStabilityAnalysis",
    "MountableComponentStabilityAnalysis",
    "OilSealStabilityAnalysis",
    "PartStabilityAnalysis",
    "PartToPartShearCouplingConnectionStabilityAnalysis",
    "PartToPartShearCouplingHalfStabilityAnalysis",
    "PartToPartShearCouplingStabilityAnalysis",
    "PlanetaryConnectionStabilityAnalysis",
    "PlanetaryGearSetStabilityAnalysis",
    "PlanetCarrierStabilityAnalysis",
    "PointLoadStabilityAnalysis",
    "PowerLoadStabilityAnalysis",
    "PulleyStabilityAnalysis",
    "RingPinsStabilityAnalysis",
    "RingPinsToDiscConnectionStabilityAnalysis",
    "RollingRingAssemblyStabilityAnalysis",
    "RollingRingConnectionStabilityAnalysis",
    "RollingRingStabilityAnalysis",
    "RootAssemblyStabilityAnalysis",
    "ShaftHubConnectionStabilityAnalysis",
    "ShaftStabilityAnalysis",
    "ShaftToMountableComponentConnectionStabilityAnalysis",
    "SpecialisedAssemblyStabilityAnalysis",
    "SpiralBevelGearMeshStabilityAnalysis",
    "SpiralBevelGearSetStabilityAnalysis",
    "SpiralBevelGearStabilityAnalysis",
    "SpringDamperConnectionStabilityAnalysis",
    "SpringDamperHalfStabilityAnalysis",
    "SpringDamperStabilityAnalysis",
    "StabilityAnalysis",
    "StabilityAnalysisDrawStyle",
    "StabilityAnalysisOptions",
    "StraightBevelDiffGearMeshStabilityAnalysis",
    "StraightBevelDiffGearSetStabilityAnalysis",
    "StraightBevelDiffGearStabilityAnalysis",
    "StraightBevelGearMeshStabilityAnalysis",
    "StraightBevelGearSetStabilityAnalysis",
    "StraightBevelGearStabilityAnalysis",
    "StraightBevelPlanetGearStabilityAnalysis",
    "StraightBevelSunGearStabilityAnalysis",
    "SynchroniserHalfStabilityAnalysis",
    "SynchroniserPartStabilityAnalysis",
    "SynchroniserSleeveStabilityAnalysis",
    "SynchroniserStabilityAnalysis",
    "TorqueConverterConnectionStabilityAnalysis",
    "TorqueConverterPumpStabilityAnalysis",
    "TorqueConverterStabilityAnalysis",
    "TorqueConverterTurbineStabilityAnalysis",
    "UnbalancedMassStabilityAnalysis",
    "VirtualComponentStabilityAnalysis",
    "WormGearMeshStabilityAnalysis",
    "WormGearSetStabilityAnalysis",
    "WormGearStabilityAnalysis",
    "ZerolBevelGearMeshStabilityAnalysis",
    "ZerolBevelGearSetStabilityAnalysis",
    "ZerolBevelGearStabilityAnalysis",
)
