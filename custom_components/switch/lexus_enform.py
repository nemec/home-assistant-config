"""
Support for Tesla charger switch.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.tesla/
"""
import logging

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
from custom_components.lexus_enform import DOMAIN as LEXUS_DOMAIN, LexusDevice
from homeassistant.const import STATE_ON, STATE_OFF

_LOGGER = logging.getLogger(__name__)
DEPENDENCIES = ['lexus_enform']


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Lexus switch platform."""
    devices = [RemoteStartSwitch(device, hass.data[LEXUS_DOMAIN]['account'])
               for device in hass.data[LEXUS_DOMAIN]['vehicles']]
    add_devices(devices, True)


class RemoteStartSwitch(LexusDevice, SwitchDevice):
    """Representation of a Lexus remote start switch."""

    def __init__(self, vehicle, controller):
        """Initialisation of the switch."""
        self._state = None
        super().__init__(vehicle, controller)
        self.entity_id = ENTITY_ID_FORMAT.format('{}_{}'.format(self.lexus_id, 'remote_start'))

    def turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Remote start: %s", self._name)
        self.vehicle.remote_start()

    def turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.debug("Remote stop for: %s", self._name)
        #self.vehicle.remote_stop()
        # todo detect when vehicle on and remote started

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._state == STATE_ON

    def update(self):
        """Updating state of the switch."""
        _LOGGER.debug("Updating state for: %s", self._name)
        self._state = STATE_OFF
        #self.tesla_device.update()
        #self._state = STATE_ON if self.tesla_device.is_charging() \
        #    else STATE_OFF
