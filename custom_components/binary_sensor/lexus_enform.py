"""
Support for Tesla binary sensor.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.tesla/
"""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, ENTITY_ID_FORMAT)
from custom_components.lexus_enform import DOMAIN as LEXUS_DOMAIN, LexusDevice

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['lexus_enform']


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Lexus binary sensor."""
    devices = []
    for vehicle in hass.data[LEXUS_DOMAIN]['vehicles']:
        devices.append(LexusBinarySensor(
            vehicle, hass.data[LEXUS_DOMAIN]['account'],
            lambda s: s.doors, 'door open sensor', 'door_open'))
        devices.append(LexusBinarySensor(
            vehicle, hass.data[LEXUS_DOMAIN]['account'],
            lambda s: s.windows, 'window open sensor', 'window_open'))
    add_devices(devices, True)


class LexusBinarySensor(LexusDevice, BinarySensorDevice):
    """Implement a Lexus binary sensor for open doors and windows."""

    def __init__(self, tesla_device, controller, selector, sensor_type, short_name):
        """Initialisation of binary sensor."""
        super().__init__(tesla_device, controller)
        self._state = False
        self._selector = selector
        self.entity_id = ENTITY_ID_FORMAT.format('{}_{}'.format(self.lexus_id, short_name))
        self._sensor_type = sensor_type

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._state

    def update(self):
        """Update the state of the device."""
        _LOGGER.debug("Updating sensor: %s", self._name)
        status = self._selector(self.vehicle.status())
        comp_open = False
        for _, component in status.items():
            if not component.closed:
                comp_open = True
                break

        self._state = comp_open

