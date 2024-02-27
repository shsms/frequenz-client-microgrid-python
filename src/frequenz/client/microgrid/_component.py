# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines the components that can be used in a microgrid."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# pylint: disable=no-name-in-module
from frequenz.api.common.components_pb2 import ComponentCategory as PbComponentCategory
from frequenz.api.microgrid.grid_pb2 import Metadata as PbGridMetadata
from frequenz.api.microgrid.inverter_pb2 import Metadata as PbInverterMetadata
from frequenz.api.microgrid.inverter_pb2 import Type as PbInverterType

# pylint: enable=no-name-in-module


class ComponentType(Enum):
    """A base class from which individual component types are derived."""


class InverterType(ComponentType):
    """Enum representing inverter types."""

    NONE = PbInverterType.TYPE_UNSPECIFIED
    """Unspecified inverter type."""

    BATTERY = PbInverterType.TYPE_BATTERY
    """Battery inverter."""

    SOLAR = PbInverterType.TYPE_SOLAR
    """Solar inverter."""

    HYBRID = PbInverterType.TYPE_HYBRID
    """Hybrid inverter."""


def _component_type_from_protobuf(
    component_category: PbComponentCategory.ValueType,
    component_metadata: PbInverterMetadata,
) -> ComponentType | None:
    """Convert a protobuf InverterType message to Component enum.

    For internal-only use by the `microgrid` package.

    Args:
        component_category: category the type belongs to.
        component_metadata: protobuf metadata to fetch type from.

    Returns:
        Enum value corresponding to the protobuf message.
    """
    # ComponentType values in the protobuf definition are not unique across categories
    # as of v0.11.0, so we need to check the component category first, before doing any
    # component type checks.
    if component_category == PbComponentCategory.COMPONENT_CATEGORY_INVERTER:
        if not any(int(t.value) == int(component_metadata.type) for t in InverterType):
            return None

        return InverterType(component_metadata.type)

    return None


class ComponentCategory(Enum):
    """Possible types of microgrid component."""

    NONE = PbComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED
    """Unspecified component category."""

    GRID = PbComponentCategory.COMPONENT_CATEGORY_GRID
    """Grid component."""

    METER = PbComponentCategory.COMPONENT_CATEGORY_METER
    """Meter component."""

    INVERTER = PbComponentCategory.COMPONENT_CATEGORY_INVERTER
    """Inverter component."""

    BATTERY = PbComponentCategory.COMPONENT_CATEGORY_BATTERY
    """Battery component."""

    EV_CHARGER = PbComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
    """EV charger component."""

    CHP = PbComponentCategory.COMPONENT_CATEGORY_CHP
    """CHP component."""


def _component_category_from_protobuf(
    component_category: PbComponentCategory.ValueType,
) -> ComponentCategory:
    """Convert a protobuf ComponentCategory message to ComponentCategory enum.

    For internal-only use by the `microgrid` package.

    Args:
        component_category: protobuf enum to convert

    Returns:
        Enum value corresponding to the protobuf message.

    Raises:
        ValueError: if `component_category` is a sensor (this is not considered
            a valid component category as it does not form part of the
            microgrid itself)
    """
    if component_category == PbComponentCategory.COMPONENT_CATEGORY_SENSOR:
        raise ValueError("Cannot create a component from a sensor!")

    if not any(t.value == component_category for t in ComponentCategory):
        return ComponentCategory.NONE

    return ComponentCategory(component_category)


@dataclass(frozen=True)
class Fuse:
    """Fuse data class."""

    max_current: float
    """Rated current of the fuse."""


@dataclass(frozen=True)
class ComponentMetadata:
    """Base class for component metadata classes."""

    fuse: Fuse | None = None
    """The fuse at the grid connection point."""


@dataclass(frozen=True)
class GridMetadata(ComponentMetadata):
    """Metadata for a grid connection point."""


def _component_metadata_from_protobuf(
    component_category: PbComponentCategory.ValueType,
    component_metadata: PbGridMetadata,
) -> GridMetadata | None:
    if component_category == PbComponentCategory.COMPONENT_CATEGORY_GRID:
        max_current = component_metadata.rated_fuse_current
        fuse = Fuse(max_current)
        return GridMetadata(fuse)

    return None


@dataclass(frozen=True)
class Component:
    """Metadata for a single microgrid component."""

    component_id: int
    """The ID of this component."""

    category: ComponentCategory
    """The category of this component."""

    type: ComponentType | None = None
    """The type of this component."""

    metadata: ComponentMetadata | None = None
    """The metadata of this component."""

    def is_valid(self) -> bool:
        """Check if this instance contains valid data.

        Returns:
            `True` if `id > 0` and `type` is a valid `ComponentCategory`, or if `id
                == 0` and `type` is `GRID`, `False` otherwise
        """
        return (
            self.component_id > 0 and any(t == self.category for t in ComponentCategory)
        ) or (self.component_id == 0 and self.category == ComponentCategory.GRID)

    def __hash__(self) -> int:
        """Compute a hash of this instance, obtained by hashing the `component_id` field.

        Returns:
            Hash of this instance.
        """
        return hash(self.component_id)


class ComponentMetricId(Enum):
    """An enum representing the various metrics available in the microgrid."""

    ACTIVE_POWER = "active_power"
    """Active power."""

    ACTIVE_POWER_PHASE_1 = "active_power_phase_1"
    """Active power in phase 1."""
    ACTIVE_POWER_PHASE_2 = "active_power_phase_2"
    """Active power in phase 2."""
    ACTIVE_POWER_PHASE_3 = "active_power_phase_3"
    """Active power in phase 3."""

    CURRENT_PHASE_1 = "current_phase_1"
    """Current in phase 1."""
    CURRENT_PHASE_2 = "current_phase_2"
    """Current in phase 2."""
    CURRENT_PHASE_3 = "current_phase_3"
    """Current in phase 3."""

    VOLTAGE_PHASE_1 = "voltage_phase_1"
    """Voltage in phase 1."""
    VOLTAGE_PHASE_2 = "voltage_phase_2"
    """Voltage in phase 2."""
    VOLTAGE_PHASE_3 = "voltage_phase_3"
    """Voltage in phase 3."""

    FREQUENCY = "frequency"

    SOC = "soc"
    """State of charge."""
    SOC_LOWER_BOUND = "soc_lower_bound"
    """Lower bound of state of charge."""
    SOC_UPPER_BOUND = "soc_upper_bound"
    """Upper bound of state of charge."""
    CAPACITY = "capacity"
    """Capacity."""

    POWER_INCLUSION_LOWER_BOUND = "power_inclusion_lower_bound"
    """Power inclusion lower bound."""
    POWER_EXCLUSION_LOWER_BOUND = "power_exclusion_lower_bound"
    """Power exclusion lower bound."""
    POWER_EXCLUSION_UPPER_BOUND = "power_exclusion_upper_bound"
    """Power exclusion upper bound."""
    POWER_INCLUSION_UPPER_BOUND = "power_inclusion_upper_bound"
    """Power inclusion upper bound."""

    ACTIVE_POWER_INCLUSION_LOWER_BOUND = "active_power_inclusion_lower_bound"
    """Active power inclusion lower bound."""
    ACTIVE_POWER_EXCLUSION_LOWER_BOUND = "active_power_exclusion_lower_bound"
    """Active power exclusion lower bound."""
    ACTIVE_POWER_EXCLUSION_UPPER_BOUND = "active_power_exclusion_upper_bound"
    """Active power exclusion upper bound."""
    ACTIVE_POWER_INCLUSION_UPPER_BOUND = "active_power_inclusion_upper_bound"
    """Active power inclusion upper bound."""

    TEMPERATURE = "temperature"
    """Temperature."""
