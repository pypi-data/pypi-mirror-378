from . import unit_catalog as uc
from .quantity_meta import quantity


# region // A
@quantity(uc.AccelerationUnits)
class Acceleration:
    """Acceleration quantity with automatic boilerplate."""

    pass


@quantity(uc.AnglePlaneUnits)
class AnglePlane:
    """Angle plane quantity with automatic boilerplate."""

    pass


@quantity(uc.AreaUnits)
class Area:
    """Area quantity with automatic boilerplate."""

    pass


# endregion // A


@quantity(uc.LengthUnits)
class Length:
    """Length quantity with automatic boilerplate."""

    pass


@quantity(uc.DimensionlessUnits)
class Dimensionless:
    """Dimensionless quantity with automatic boilerplate."""

    pass


# region // M


@quantity(uc.MassDensityUnits)
class MassDensity:
    """Mass density quantity with automatic boilerplate."""

    pass


@quantity(uc.MassFlowRateUnits)
class MassFlowRate:
    """Mass flow rate quantity with automatic boilerplate."""

    pass


# endregion // M


# region // P


@quantity(uc.PowerThermalDutyUnits)
class PowerThermalDuty:
    """Power thermal duty quantity with automatic boilerplate."""

    pass


@quantity(uc.PressureUnits)
class Pressure:
    """Pressure quantity with automatic boilerplate."""

    pass


# endregion // P

# region // S


@quantity(uc.SpecificVolumeUnits)
class SpecificVolume:
    """Specific volume quantity with automatic boilerplate."""

    pass


# endregion // S


@quantity(uc.VelocityLinearUnits)
class VelocityLinear:
    """Linear velocity quantity with automatic boilerplate."""

    pass


@quantity(uc.VolumetricFlowRateUnits)
class VolumetricFlowRate:
    """Volumetric flow rate quantity with automatic boilerplate."""

    pass


@quantity(uc.ViscosityDynamicUnits)
class ViscosityDynamic:
    """Dynamic viscosity quantity with automatic boilerplate."""

    pass


@quantity(uc.ViscosityKinematicUnits)
class ViscosityKinematic:
    """Kinematic viscosity quantity with automatic boilerplate."""

    pass


# region // V


# endregion // V
