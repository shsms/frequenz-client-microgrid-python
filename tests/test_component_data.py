# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid component data."""

from datetime import datetime, timezone

import pytest

# pylint: disable=no-name-in-module
from frequenz.api.common.metrics.electrical_pb2 import AC
from frequenz.api.common.metrics_pb2 import Bounds, Metric
from frequenz.api.microgrid.inverter_pb2 import (
    COMPONENT_STATE_DISCHARGING,
    Data,
    Error,
    Inverter,
    State,
)
from frequenz.api.microgrid.microgrid_pb2 import ComponentData as PbComponentData
from google.protobuf.timestamp_pb2 import Timestamp

# pylint: enable=no-name-in-module
from frequenz.client.microgrid import ComponentData, InverterData


def test_component_data_abstract_class() -> None:
    """Verify the base class ComponentData may not be instantiated."""
    with pytest.raises(TypeError):
        # pylint: disable=abstract-class-instantiated
        ComponentData(0, datetime.now(timezone.utc))  # type: ignore


def test_inverter_data() -> None:
    """Verify the constructor for the InverterData class."""
    seconds = 1234567890

    raw = PbComponentData(
        id=5,
        ts=Timestamp(seconds=seconds),
        inverter=Inverter(
            state=State(component_state=COMPONENT_STATE_DISCHARGING),
            errors=[Error(msg="error message")],
            data=Data(
                dc_battery=None,
                dc_solar=None,
                temperature=None,
                ac=AC(
                    frequency=Metric(value=50.1),
                    power_active=Metric(
                        value=100.2,
                        system_exclusion_bounds=Bounds(lower=-501.0, upper=501.0),
                        system_inclusion_bounds=Bounds(lower=-51_000.0, upper=51_000.0),
                    ),
                    phase_1=AC.ACPhase(
                        current=Metric(value=12.3),
                        voltage=Metric(value=229.8),
                        power_active=Metric(value=33.1),
                    ),
                    phase_2=AC.ACPhase(
                        current=Metric(value=23.4),
                        voltage=Metric(value=230.0),
                        power_active=Metric(value=33.3),
                    ),
                    phase_3=AC.ACPhase(
                        current=Metric(value=34.5),
                        voltage=Metric(value=230.2),
                        power_active=Metric(value=33.8),
                    ),
                ),
            ),
        ),
    )

    inv_data = InverterData.from_proto(raw)
    assert inv_data.component_id == 5
    assert inv_data.timestamp == datetime.fromtimestamp(seconds, timezone.utc)
    assert (  # pylint: disable=protected-access
        inv_data._component_state == COMPONENT_STATE_DISCHARGING
    )
    assert inv_data._errors == [  # pylint: disable=protected-access
        Error(msg="error message")
    ]
    assert inv_data.frequency == pytest.approx(50.1)
    assert inv_data.active_power == pytest.approx(100.2)
    assert inv_data.active_power_per_phase == pytest.approx((33.1, 33.3, 33.8))
    assert inv_data.current_per_phase == pytest.approx((12.3, 23.4, 34.5))
    assert inv_data.voltage_per_phase == pytest.approx((229.8, 230.0, 230.2))
    assert inv_data.active_power_inclusion_lower_bound == pytest.approx(-51_000.0)
    assert inv_data.active_power_inclusion_upper_bound == pytest.approx(51_000.0)
    assert inv_data.active_power_exclusion_lower_bound == pytest.approx(-501.0)
    assert inv_data.active_power_exclusion_upper_bound == pytest.approx(501.0)
