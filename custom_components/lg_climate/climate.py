"""Adds support for generic thermostat units."""
import json
import logging

import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateDevice
from homeassistant.components.climate.const import (
    ATTR_PRESET_MODE,
    FAN_DIFFUSE,
    FAN_FOCUS,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_MIDDLE,
    FAN_OFF,
    FAN_ON,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_NONE,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_NAME,
    EVENT_HOMEASSISTANT_START,
    PRECISION_HALVES,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_AWAY_TEMP,
    CONF_COMMAND_TOPIC,
    CONF_FAN_LIST,
    CONF_INITIAL_OPERATION_MODE,
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_MODES_LIST,
    CONF_PRECISION,
    CONF_STATE_TOPIC,
    CONF_SWING_LIST,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    DEFAULT_AWAY_TEMP,
    DEFAULT_COMMAND_TOPIC,
    DEFAULT_FAN_LIST,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_NAME,
    DEFAULT_PRECISION,
    DEFAULT_STATE_TOPIC,
    DEFAULT_TARGET_TEMP,
    HVAC_FAN_AUTO,
    HVAC_FAN_AUTO_MAX,
    HVAC_FAN_MAX,
    HVAC_FAN_MAX_HIGH,
    HVAC_FAN_MEDIUM,
    HVAC_FAN_MIN,
    HVAC_MODE_AUTO_FAN,
    HVAC_MODE_FAN_AUTO,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO,
    HVAC_MODES,
    STATE_AUTO,
    STATE_COOL,
    STATE_DRY,
    STATE_FAN_ONLY,
    STATE_HEAT,
    FAN_AUTO,
)

DEFAULT_MODES_LIST = [
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
]

DEFAULT_SWING_LIST = [SWING_OFF, SWING_VERTICAL]
DEFAULT_INITIAL_OPERATION_MODE = STATE_OFF

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = (
    SUPPORT_TARGET_TEMPERATURE
    | SUPPORT_FAN_MODE
    | SUPPORT_SWING_MODE
    | SUPPORT_PRESET_MODE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(
            CONF_COMMAND_TOPIC, default=DEFAULT_COMMAND_TOPIC
        ): mqtt.valid_publish_topic,
        vol.Required(CONF_TEMP_SENSOR): cv.entity_id,
        vol.Optional(
            CONF_STATE_TOPIC, default=DEFAULT_STATE_TOPIC
        ): mqtt.valid_subscribe_topic,
        vol.Optional(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): vol.Coerce(float),
        vol.Optional(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): vol.Coerce(float),
        vol.Optional(CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP): vol.Coerce(float),
        vol.Optional(
            CONF_INITIAL_OPERATION_MODE, default=DEFAULT_INITIAL_OPERATION_MODE
        ): vol.In(
            [STATE_HEAT, STATE_COOL, STATE_AUTO, STATE_DRY, STATE_FAN_ONLY, STATE_OFF]
        ),
        vol.Optional(CONF_AWAY_TEMP, default=DEFAULT_AWAY_TEMP): vol.Coerce(float),
        vol.Optional(CONF_PRECISION, default=DEFAULT_PRECISION): vol.In(
            [PRECISION_TENTHS, PRECISION_HALVES, PRECISION_WHOLE]
        ),
        vol.Optional(CONF_MODES_LIST, default=DEFAULT_MODES_LIST): vol.All(
            cv.ensure_list, [vol.In(HVAC_MODES)]
        ),
        vol.Optional(CONF_FAN_LIST, default=DEFAULT_FAN_LIST): vol.All(
            cv.ensure_list,
            [
                vol.In(
                    [
                        FAN_ON,
                        FAN_OFF,
                        FAN_AUTO,
                        FAN_LOW,
                        FAN_MEDIUM,
                        FAN_HIGH,
                        FAN_MIDDLE,
                        FAN_FOCUS,
                        FAN_DIFFUSE,
                        HVAC_FAN_MIN,
                        HVAC_FAN_MEDIUM,
                        HVAC_FAN_MAX,
                        HVAC_FAN_AUTO,
                        HVAC_FAN_MAX_HIGH,
                        HVAC_FAN_AUTO_MAX,
                    ]
                )
            ],
        ),
        vol.Optional(CONF_SWING_LIST, default=DEFAULT_SWING_LIST): vol.All(
            cv.ensure_list,
            [vol.In([SWING_OFF, SWING_BOTH, SWING_VERTICAL, SWING_HORIZONTAL])],
        )
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the generic thermostat platform."""
    name = config.get(CONF_NAME)
    topic = config.get(CONF_COMMAND_TOPIC)
    sensor_entity_id = config.get(CONF_TEMP_SENSOR)
    state_topic = config[CONF_STATE_TOPIC]
    min_temp = config[CONF_MIN_TEMP]
    max_temp = config[CONF_MAX_TEMP]
    target_temp = config[CONF_TARGET_TEMP]
    initial_operation_mode = config[CONF_INITIAL_OPERATION_MODE]
    away_temp = config[CONF_AWAY_TEMP]
    precision = config[CONF_PRECISION]
    modes_list = config[CONF_MODES_LIST]
    fan_list = config[CONF_FAN_LIST]
    swing_list = config[CONF_SWING_LIST]

    async_add_entities(
        [
            LGClimate(
                hass,
                topic,
                name,
                sensor_entity_id,
                state_topic,
                min_temp,
                max_temp,
                target_temp,
                initial_operation_mode,
                away_temp,
                precision,
                modes_list,
                fan_list,
                swing_list,
            )
        ]
    )


class LGClimate(ClimateDevice, RestoreEntity):
    """Representation of a Generic Thermostat device."""

    def __init__(
        self,
        hass,
        topic,
        name,
        sensor_entity_id,
        state_topic,
        min_temp,
        max_temp,
        target_temp,
        initial_operation_mode,
        away_temp,
        precision,
        modes_list,
        fan_list,
        swing_list,
    ):
        """Initialize the thermostat."""
        self.topic = topic
        self.hass = hass
        self._name = name
        self.sensor_entity_id = sensor_entity_id
        self.state_topic = state_topic
        self._hvac_mode = initial_operation_mode
        self._saved_target_temp = target_temp or away_temp
        self._temp_precision = precision
        self._hvac_list = modes_list
        self._fan_list = fan_list
        self._fan_mode = fan_list[0]
        self._swing_list = swing_list
        self._swing_mode = swing_list[0]
        self._enabled = False
        self.power_mode = STATE_OFF
        if initial_operation_mode is not STATE_OFF:
            self.power_mode = STATE_ON
            self._enabled = True
        self._active = False
        self._cur_temp = None
        self._min_temp = min_temp
        self._max_temp = max_temp
        self._target_temp = target_temp
        self._unit = hass.config.units.temperature_unit
        self._support_flags = SUPPORT_FLAGS
        if away_temp is not None:
            self._support_flags = SUPPORT_FLAGS | SUPPORT_PRESET_MODE
        self._away_temp = away_temp
        self._is_away = False
        self._modes_list = modes_list
        self._fan_list = fan_list
        self._swing_list = swing_list
        self._sub_state = None
        self._fixed_code = ""

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        # Add listener
        async_track_state_change(
            self.hass, self.sensor_entity_id, self._async_sensor_changed
        )
        await self._subscribe_topics()

        @callback
        def _async_startup(event):
            """Init on startup."""
            sensor_state = self.hass.states.get(self.sensor_entity_id)
            if sensor_state and sensor_state.state != STATE_UNKNOWN:
                self._async_update_temp(sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        # Check If we have an old state
        old_state = await self.async_get_last_state()
        if old_state is not None:
            # If we have no initial temperature, restore
            if old_state.attributes.get(ATTR_TEMPERATURE) is not None:
                self._target_temp = float(old_state.attributes[ATTR_TEMPERATURE])
            if old_state.attributes.get(ATTR_PRESET_MODE) == PRESET_AWAY:
                self._is_away = True
            if not self._hvac_mode and old_state.state:
                self._hvac_mode = old_state.state
                self._enabled = self._hvac_mode != STATE_OFF
        else:
            # No previous state, try and restore defaults
            if self._target_temp is None:
                self._target_temp = 26.0
            _LOGGER.warning(
                "No previously saved temperature, setting to %s", self._target_temp
            )
        # Set default state to off
        if not self._hvac_mode:
            self._hvac_mode = HVAC_MODE_OFF

    async def _subscribe_topics(self):
        """(Re)Subscribe to topics."""

        @callback
        def state_message_received(msg):
            """Handle new MQTT state messages."""
            json_payload = json.loads(msg.payload)
            _LOGGER.debug(json_payload)
            if 'IrReceived' not in json_payload:
                return
            payload = json_payload['IrReceived']
            if 'Protocol' not in payload:
                return
            if payload['Protocol'] != "LG":
                return
            if payload['Bits'] != 28:
                return
            if payload['Repeat'] != 0:
                return

            code = payload['Data']

            #remove optional prefix "0x"
            if code.startswith('0x'):
                while code.startswith('0x'):
                    code = code[2:]

            if len(code) != 7:
                return

            if code.startswith('88') is False:
                return

            if code == "88C0051":
                # POWE OFF
                self._hvac_mode = HVAC_MODE_OFF #4
                self.power_mode = STATE_OFF
                self._swing_mode = SWING_VERTICAL
                # Update HA UI and State
                self.schedule_update_ha_state()
                return
            elif code == "881315A":
                #SWING OFF
                self._swing_mode = SWING_OFF
                # Update HA UI and State
                self.schedule_update_ha_state()
                return
            elif code == "8813149":
                #SWING ON
                self._swing_mode = SWING_VERTICAL
                # Update HA UI and State
                self.schedule_update_ha_state()
                return

            #devide code on every 1 letters
            receive_buffer = []
            while code:
                receive_buffer.append(code[:1])
                code = code[1:]

            #CHECK
            check = (int('0x0' + receive_buffer[3], 16) + int('0x0' + receive_buffer[4], 16) + int('0x0' + receive_buffer[5], 16)) & 0x0f
            letter_check = str(hex(check))[2:].upper()
            if letter_check != receive_buffer[6]:
                return

            #MODE
            self.power_mode = STATE_ON
            if receive_buffer[3] == '8':
                self._hvac_mode = HVAC_MODE_COOL
            if receive_buffer[3] == '0':
                self._hvac_mode = HVAC_MODE_COOL #turn on on cooling
            elif receive_buffer[3] == '9':
                self._hvac_mode = HVAC_MODE_DRY
            elif receive_buffer[3] == 'A':
                self._hvac_mode = HVAC_MODE_FAN_ONLY
            elif receive_buffer[3] == 'C':
                self._hvac_mode = HVAC_MODE_HEAT
            elif receive_buffer[3] == '4':
                self._hvac_mode = HVAC_MODE_HEAT #turn on on heating
            elif receive_buffer[3] == 'B':
                self._hvac_mode = HVAC_MODE_AUTO
            else:
                self._hvac_mode = HVAC_MODE_AUTO

            #TEMPERATURE
            self._target_temp = int('0x0' + receive_buffer[4], 16) + 15

            #FAN
            if receive_buffer[5] == '0':
                self._fan_mode = FAN_LOW
            elif receive_buffer[5] == '2':
                self._fan_mode = FAN_MEDIUM
            elif receive_buffer[5] == '4':
                self._fan_mode = FAN_HIGH
            else:
                self._fan_mode = FAN_AUTO

            # Set default state to off
            if self.power_mode == STATE_OFF:
                self._enabled = False
            else:
                self._enabled = True

            # Update HA UI and State
            self.schedule_update_ha_state()

        self._sub_state = await mqtt.subscription.async_subscribe_topics(
            self.hass,
            self._sub_state,
            {
                CONF_STATE_TOPIC: {
                    "topic": self.state_topic,
                    "msg_callback": state_message_received,
                    "qos": 1,
                }
            },
        )

    async def async_will_remove_from_hass(self):
        """Unsubscribe when removed."""
        self._sub_state = await mqtt.subscription.async_unsubscribe_topics(
            self.hass, self._sub_state
        )

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def precision(self):
        """Return the precision of the system."""
        if self._temp_precision is not None:
            return self._temp_precision
        return super().precision

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def current_temperature(self):
        """Return the sensor temperature."""
        return self._cur_temp

    @property
    def hvac_mode(self):
        """Return current operation."""
        return self._hvac_mode

    @property
    def hvac_action(self):
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        return self._hvac_mode

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temp

    @property
    def hvac_modes(self):
        """List of available operation modes."""
        return self._hvac_list

    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return PRESET_AWAY if self._is_away else PRESET_NONE

    @property
    def preset_modes(self):
        """Return a list of available preset modes or PRESET_NONE if _away_temp is undefined."""
        return [PRESET_NONE, PRESET_AWAY] if self._away_temp else PRESET_NONE

    @property
    def fan_mode(self):
        """Return the list of available fan modes.

        Requires SUPPORT_FAN_MODE.
        """
        return self._fan_mode

    @property
    def fan_modes(self):
        """Return the list of available fan modes.

        Requires SUPPORT_FAN_MODE.
        """
        # tweek for some ELECTRA_AC devices
        if HVAC_FAN_MAX_HIGH in self._fan_list and HVAC_FAN_AUTO_MAX in self._fan_list:
            new_fan_list = []
            for val in self._fan_list:
                if val == HVAC_FAN_MAX_HIGH:
                    new_fan_list.append(FAN_HIGH)
                elif val == HVAC_FAN_AUTO_MAX:
                    new_fan_list.append(HVAC_FAN_MAX)
                else:
                    new_fan_list.append(val)
            return new_fan_list
        return self._fan_list

    @property
    def swing_mode(self):
        """Return the swing setting.

        Requires SUPPORT_SWING_MODE.
        """
        return self._swing_mode

    @property
    def swing_modes(self):
        """Return the list of available swing modes.

        Requires SUPPORT_SWING_MODE.
        """
        return self._swing_list

    async def async_set_hvac_mode(self, hvac_mode):
        """Set hvac mode."""
        if hvac_mode not in self._hvac_list or hvac_mode == HVAC_MODE_OFF:
            self._hvac_mode = HVAC_MODE_OFF
            self._enabled = False
            self.power_mode = STATE_OFF
            self._fixed_code = "88C0051"
        else:
            self._hvac_mode = hvac_mode
            self._enabled = True
            self.power_mode = STATE_ON
        # Ensure we update the current operation after changing the mode
        self.schedule_update_ha_state()
        await self.hass.async_add_executor_job(self.send_ir)

    async def async_turn_on(self):
        """Turn thermostat on."""
        self.power_mode = STATE_ON
        await self.async_update_ha_state()
        await self.hass.async_add_executor_job(self.send_ir)

    async def async_turn_off(self):
        """Turn thermostat off."""
        self._hvac_mode = STATE_OFF
        self.power_mode = STATE_OFF
        self._fixed_code = "88C0051"
        await self.async_update_ha_state()
        await self.hass.async_add_executor_job(self.send_ir)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._target_temp = temperature
        self.power_mode = STATE_ON
        await self.hass.async_add_executor_job(self.send_ir)
        await self.async_update_ha_state()

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        if fan_mode not in self._fan_list:
            _LOGGER.error(
                "Invalid swing mode selected. Got '%s'. Allowed modes are:", fan_mode
            )
            _LOGGER.error(self._fan_list)
            return
        self._fan_mode = fan_mode
        self.power_mode = STATE_ON
        await self.hass.async_add_executor_job(self.send_ir)
        await self.async_update_ha_state()

    async def async_set_swing_mode(self, swing_mode):
        """Set new target swing operation."""
        if swing_mode not in self._swing_list:
            _LOGGER.error(
                "Invalid swing mode selected. Got '%s'. Allowed modes are:", swing_mode
            )
            _LOGGER.error(self._swing_list)
            return
        self._swing_mode = swing_mode
        self.power_mode = STATE_ON

        if swing_mode == SWING_VERTICAL:
            self._fixed_code = "8813149"
        else:
            self._fixed_code = "881315A" #SWING_OFF

        await self.hass.async_add_executor_job(self.send_ir)
        await self.async_update_ha_state()

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if self._min_temp:
            return self._min_temp

        # get default temp from super class
        return super().min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._max_temp:
            return self._max_temp

        # Get default temp from super class
        return super().max_temp

    async def _async_sensor_changed(self, entity_id, old_state, new_state):
        """Handle temperature changes."""
        if new_state is None:
            return

        self._async_update_temp(new_state)
        await self.async_update_ha_state()

    @callback
    def _async_update_temp(self, state):
        """Update thermostat with latest state from sensor."""
        try:
            self._cur_temp = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    @property
    def _is_device_active(self):
        """If the toggleable device is currently active."""
        return self.power_mode == STATE_ON

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    async def async_set_preset_mode(self):
        """Set new preset mode.

        This method must be run in the event loop and returns a coroutine.
        """
        if preset_mode == PRESET_AWAY and not self._is_away:
            self._is_away = True
            self._saved_target_temp = self._target_temp
            self._target_temp = self._away_temp
        elif preset_mode == PRESET_NONE and self._is_away:
            self._is_away = False
            self._target_temp = self._saved_target_temp
        await self.hass.async_add_executor_job(self.send_ir)
        await self.async_update_ha_state()

    def send_ir(self, fixed_code=""):
        """Send the payload to tasmota mqtt topic."""
        send_buffer = bytearray([0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00])
        code = ""

        if not self._fixed_code:
            #Set the swing mode - default off
            swing_h = STATE_OFF
            swing_v = STATE_OFF
            if self._swing_mode == SWING_BOTH:
                swing_h = STATE_AUTO
                swing_v = STATE_AUTO
            elif self._swing_mode == SWING_HORIZONTAL:
                swing_h = STATE_AUTO
            elif self._swing_mode == SWING_VERTICAL:
                swing_v = STATE_AUTO

            #Populate the IR HEX code
            code = "880"
            
            #MODE
            if self._hvac_mode == HVAC_MODE_HEAT:
                send_buffer[3] = 0x0C
            elif self._hvac_mode == HVAC_MODE_COOL:
                send_buffer[3] = 0x08
            elif self._hvac_mode == HVAC_MODE_DRY:
                send_buffer[3] = 0x09
            elif self._hvac_mode == HVAC_MODE_FAN_ONLY:
                send_buffer[3] = 0x0A
            elif self._hvac_mode == HVAC_MODE_AUTO:
                send_buffer[3] = 0x0B
            else:
                send_buffer[3] = 0x04 #HVAC_MODE_OF
            code += str(hex(send_buffer[3]))[2:].upper()

            #TEMPERATURE
            send_buffer[4] = int(self._target_temp) - 15
            code += str(hex(send_buffer[4]))[2:].upper()

            #FAN
            if self._fan_mode == FAN_LOW:
                send_buffer[5] = 0x00
            elif self._fan_mode == FAN_MEDIUM:
                send_buffer[5] = 0x02
            elif self._fan_mode == FAN_HIGH:
                send_buffer[5] = 0x04
            else:
                send_buffer[5] = 0x05 #FAN_AUTO
            code += str(hex(send_buffer[5]))[2:].upper()

            #CHECK BYTE
            send_buffer[6] = (send_buffer[3] + send_buffer[4] + send_buffer[5]) & 0x0f
            code += str(hex(send_buffer[6]))[2:].upper()
        else:
            code = self._fixed_code
        
        _LOGGER.debug("code")
        _LOGGER.debug(code)

        # Populate the payload
        payload_data = {
            "Protocol": "LG",
            "Bits": 28,
            "Data": "0x" + code,
            "Repeat": 0,
        }
        
        _LOGGER.debug("payload_data")
        _LOGGER.debug(payload_data)

        payload = json.dumps(payload_data)
        # Publish mqtt message
        mqtt.async_publish(self.hass, self.topic, payload)
        # Reset self._fixed_code
        self._fixed_code = ""
