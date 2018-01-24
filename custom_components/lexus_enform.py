"""
Support for Lexus cars.

"""
import logging
import voluptuous as vol

from homeassistant.const import (
    ATTR_BATTERY_LEVEL, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL,
    CONF_FORCE_UPDATE)
from homeassistant.helpers import discovery
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

REQUIREMENTS = ['git+https://github.com/nemec/pylexusenform.git'
                '#lexusenform==0.01a6']

DOMAIN = 'lexus_enform'

CONF_PUSH_NOTIFICATIONS = 'push_notifications'
CONF_VINS = 'vins'

CONF_VINS_VIN = 'vin'
CONF_VINS_FRIENDLY_NAME = 'friendly_name'

_LOGGER = logging.getLogger(__name__)

LEXUS_ID_FORMAT = '{}_{}'
LEXUS_ID_LIST_SCHEMA = vol.Schema([int])

LEXUS_CONFIG_FILE = 'lexus_enform.conf'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=300):
            vol.All(cv.positive_int, vol.Clamp(min=300)),
        vol.Optional(CONF_FORCE_UPDATE, default=False): cv.boolean,
        vol.Optional(CONF_PUSH_NOTIFICATIONS, default=False): cv.boolean,
        CONF_VINS: vol.All(cv.ensure_list, [{
            vol.Required(CONF_VINS_VIN): cv.string,
            vol.Optional(CONF_VINS_FRIENDLY_NAME): cv.string,
        }]),
    }),
}, extra=vol.ALLOW_EXTRA)

NOTIFICATION_ID = 'tesla_integration_notification'
NOTIFICATION_TITLE = 'Tesla integration setup'

LEXUS_COMPONENTS = [
    'sensor', 'lock', 'binary_sensor', 'switch', #'device_tracker',
]


def setup(hass, base_config):
    """Set up of Lexus platform."""
    from lexusenform.account import Account
    

    config = base_config.get(DOMAIN)

    email = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    #update_interval = config.get(CONF_SCAN_INTERVAL)
    if hass.data.get(DOMAIN) is None:
        try:
            hass.data[DOMAIN] = {
                'account': Account(
                    email, password, LEXUS_CONFIG_FILE),
                'vehicles': []
            }
            _LOGGER.debug("Connected to the Lexus Enform API.")
        except Exception as ex:
            _LOGGER.error("Unable to communicate with Lexus API: %s",
                          ex)
            return False

    vins = config.get(CONF_VINS)
    _LOGGER.debug("Vins: %s", vins)

    hass.data[DOMAIN]['account'].add_vin_mapping(
        "C71E5D40-1FBF-11E7-9509-0050568F5B13",
        "JTHBE1D27F501939220160805154951")

    all_devices = hass.data[DOMAIN]['account'].vehicles()

    if not all_devices:
        return False

    hass.data[DOMAIN]['vehicles'] = all_devices

    for component in LEXUS_COMPONENTS:
        discovery.load_platform(hass, component, DOMAIN, {}, base_config)

    return True


class LexusDevice(Entity):
    """Representation of a Lexus vehicle."""

    def __init__(self, vehicle, controller):
        """Initialisation of the Tesla device."""
        self.vehicle = vehicle
        self.controller = controller
        self._name = vehicle.model
        self.lexus_id = slugify(vehicle.vehicle_id)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def should_poll(self):
        """Get polling requirement from tesla device."""
        return False # self.tesla_device.should_poll

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = {}

        #if self.tesla_device.has_battery():
        #    attr[ATTR_BATTERY_LEVEL] = self.tesla_device.battery_level()
        return attr

