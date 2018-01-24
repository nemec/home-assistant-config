"""
Sensors for the Tesla sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.tesla/
"""
import logging
from datetime import timedelta

from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from custom_components.lexus_enform import DOMAIN as LEXUS_DOMAIN, LexusDevice
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['lexus_enform']

SCAN_INTERVAL = timedelta(minutes=5)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Tesla sensor platform."""
    account = hass.data[LEXUS_DOMAIN]['account']
    devices = []

    for vehicle in hass.data[LEXUS_DOMAIN]['vehicles']:
        devices.append(LexusSensor(vehicle, account, lambda s: s.odometer, 'Odometer', 'Odometer'))
        devices.append(LexusSensor(vehicle, account, lambda s: s.fuel_gauge, 'Fuel', 'Fuel Gauge'))
        devices.append(LexusSensor(vehicle, account, lambda s: s.drive_range, 'Range', 'Drive Range'))
        devices.append(LexusSensor(vehicle, account, lambda s: s.trip_a, 'Trip_A', 'Trip A'))
        devices.append(LexusSensor(vehicle, account, lambda s: s.trip_b, 'Trip_B', 'Trip B'))
    add_devices(devices, True)


class LexusSensor(LexusDevice, Entity):
    """Representation of Lexus sensors."""

    def __init__(self, vehicle, controller, selector=None, sensor_type=None, name=None):
        """Initialisation of the sensor."""
        self.current_value = None
        self._unit = None
        self.last_changed_time = None
        self._selector = selector
        self.type = sensor_type
        super().__init__(vehicle, controller)

        if name is not None:
            self._name = name
        elif sensor_type is not None:
            self._name = '{} ({})'.format(vehicle.model, sensor_type)

        if sensor_type:
            self.entity_id = ENTITY_ID_FORMAT.format(
                '{}_{}'.format(self.lexus_id, sensor_type))
        else:
            self.entity_id = ENTITY_ID_FORMAT.format(self.lexus_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._unit

    def update(self):
        """Update the state from the sensor."""
        _LOGGER.debug("Updating sensor: %s", self._name)
        status = self.vehicle.status()
        value, unit = self._selector(status)
        self.current_value = value
        self._unit = unit
