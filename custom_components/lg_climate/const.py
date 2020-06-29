"""Provides the constants needed for component."""

# States
STATE_AUTO = "auto"
STATE_COOL = "cool"
STATE_DRY = "dry"
STATE_FAN_ONLY = "fan_only"
STATE_HEAT = "heat"

# Fan speeds
HVAC_FAN_AUTO = "auto"
HVAC_FAN_MIN = "min"
HVAC_FAN_MEDIUM = "medium"
HVAC_FAN_MAX = "max"

# Possible fan state
FAN_ON = "on"
FAN_OFF = "off"
FAN_AUTO = "auto"
FAN_LOW = "low"
FAN_MEDIUM = "medium"
FAN_HIGH = "high"
FAN_MIDDLE = "middle"
FAN_FOCUS = "focus"
FAN_DIFFUSE = "diffuse"

# Some devices have "auto" and "fan_only" changed
HVAC_MODE_AUTO_FAN = "auto_fan_only"

# Some devicec have "fan_only" and "auto" changed
HVAC_MODE_FAN_AUTO = "fan_only_auto"

# Some devices say max,but it is high, and auto which is max
HVAC_FAN_MAX_HIGH = "max_high"
HVAC_FAN_AUTO_MAX = "auto_max"

# All activity disabled / Device is off/standby
HVAC_MODE_OFF = "off"

# Heating
HVAC_MODE_HEAT = "heat"

# Cooling
HVAC_MODE_COOL = "cool"

# The device supports heating/cooling to a range
HVAC_MODE_HEAT_COOL = "heat_cool"

# The temperature is set based on a schedule, learned behavior, AI or some
# other related mechanism. User is not able to adjust the temperature
HVAC_MODE_AUTO = "auto"

# Device is in Dry/Humidity mode
HVAC_MODE_DRY = "dry"

# Only the fan is on, not fan and another mode like cool
HVAC_MODE_FAN_ONLY = "fan_only"

# Hvac moed list
HVAC_MODES = [
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_AUTO,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO_FAN,
    HVAC_MODE_FAN_AUTO,
]

# Platform specific config entry names
CONF_COMMAND_TOPIC = "command_topic"
CONF_STATE_TOPIC = "state_topic"
CONF_TEMP_SENSOR = "temperature_sensor"
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_TARGET_TEMP = "target_temp"
CONF_INITIAL_OPERATION_MODE = "initial_operation_mode"
CONF_AWAY_TEMP = "away_temp"
CONF_PRECISION = "precision"
CONF_MODES_LIST = "supported_modes"
CONF_FAN_LIST = "supported_fan_speeds"
CONF_SWING_LIST = "supported_swing_list"

# Platform specific default values
DEFAULT_NAME = "LG IR CLimate"
DEFAULT_STATE_TOPIC = "state"
DEFAULT_COMMAND_TOPIC = "topic"
DEFAULT_TARGET_TEMP = 26
DEFAULT_MIN_TEMP = 18
DEFAULT_MAX_TEMP = 30
DEFAULT_PRECISION = 1
DEFAULT_AWAY_TEMP = 24
DEFAULT_FAN_LIST = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
