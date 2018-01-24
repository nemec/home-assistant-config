"""
Support for Tesla door locks.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/lock.tesla/
"""
import logging

from homeassistant.components.lock import ENTITY_ID_FORMAT, LockDevice
from custom_components.lexus_enform import DOMAIN as LEXUS_DOMAIN, LexusDevice
from homeassistant.const import STATE_LOCKED, STATE_UNLOCKED

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['lexus_enform']


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Lexus lock platform."""
    devices = [LexusLock(device, hass.data[LEXUS_DOMAIN]['account'])
               for device in hass.data[LEXUS_DOMAIN]['vehicles']]
    add_devices(devices, True)


class LexusLock(LexusDevice, LockDevice):
    """Representation of a Lexus door lock."""

    def __init__(self, vehicle, controller):
        """Initialisation of the lock."""
        self._state = None
        super().__init__(vehicle, controller)
        self.entity_id = ENTITY_ID_FORMAT.format(self.lexus_id)

    def lock(self, **kwargs):
        """Send the lock command."""
        _LOGGER.debug("Locking doors for: %s", self._name)
        self.vehicle.lock_doors()

    def unlock(self, **kwargs):
        """Send the unlock command."""
        _LOGGER.debug("Unlocking doors for: %s", self._name)
        self.vehicle.unlock_doors()

    @property
    def is_locked(self):
        """Get whether the lock is in locked state."""
        return self._state == STATE_LOCKED

    def update(self):
        """Updating state of the lock."""
        _LOGGER.debug("Updating state for: %s", self._name)
        status = self.vehicle.status()
        locked = True
        for _, component in status.doors.items():
            if not component.locked:
                locked = False
                break

        self._state = STATE_LOCKED if locked else STATE_UNLOCKED

