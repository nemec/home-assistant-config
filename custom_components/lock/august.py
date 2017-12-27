"""
August lock platform.

"""
import logging
import os.path
import os
from datetime import timedelta
from subprocess import Popen, TimeoutExpired

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.lock import LockDevice, PLATFORM_SCHEMA
from homeassistant.const import CONF_FILE_PATH, CONF_TIMEOUT

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'august'
 
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_FILE_PATH): cv.string,
    vol.Optional(CONF_TIMEOUT, default=timedelta(seconds=10)):
        vol.All(cv.time_period, cv.positive_timedelta)
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the August platform."""
    config_file_path = config.get(CONF_FILE_PATH)
    timeout = config.get(CONF_TIMEOUT)
    
    if os.path.exists(config_file_path):
        add_devices([August(config_file_path, timeout)])
    else:
        _LOGGER.error('Error retrieving August lock config file {} during init'
            .format(config_file_path))


class August(LockDevice):
    """Representation of an August lock."""

    LOCK_STATE = 'lock'
    UNLOCK_STATE = 'unlock'

    def __init__(self, config_file_path, timeout):
        """Initialize the lock."""
        self._state = August.LOCK_STATE  # Assume closed TODO
        self.config_file_path = config_file_path
        self.timeout = timeout

    @property
    def name(self):
        """Return the name of the device."""
        return DOMAIN

    @property
    def is_locked(self):
        """Return True if the lock is currently locked, else False."""
        return self._state == August.LOCK_STATE

    def lock(self, **kwargs):
        """Lock the device."""
        self._state = self.do_change_request(August.LOCK_STATE)

    def unlock(self, **kwargs):
        """Unlock the device."""
        self._state = self.do_change_request(August.UNLOCK_STATE)

    def update(self):
        """Update the internal state of the device."""
        pass  # Unable to get status TODO

    def do_change_request(self, requested_state):
        """Execute the change request and pull out the new state."""
        env = os.environ.copy()
        env['AUGUSTCTL_CONFIG'] = self.config_file_path
        with Popen(['augustctl', requested_state], env=env) as process:
            try:
                timeout = self.timeout.total_seconds()
                output, unused_err = process.communicate(timeout=timeout)
                self._state = requested_state
            except TimeoutExpired:
                process.kill()
                output, unused_err = process.communicate()
                _LOGGER.error('Error setting lock state: %s\n%s',
                              requested_state, unused_err)
        return self._state
