from __future__ import annotations

import logging
import math
import struct
from collections import namedtuple
from enum import IntEnum
from typing import Any, Callable, Collection, Mapping, Optional, Union

import msmart.crc8 as crc8
from msmart.const import DeviceType, FrameType
from msmart.frame import Frame

_LOGGER = logging.getLogger(__name__)


class InvalidResponseException(Exception):
    pass


class ResponseId(IntEnum):
    PROPERTIES_ACK = 0xB0  # In response to property commands
    PROPERTIES = 0xB1
    CAPABILITIES = 0xB5
    STATE = 0xC0
    GROUP_DATA = 0xC1


class CapabilityId(IntEnum):
    SWING_UD_ANGLE = 0x0009
    SWING_LR_ANGLE = 0x000A
    BREEZELESS = 0x0018  # AKA "No Wind Sense"
    SMART_EYE = 0x0030
    WIND_ON_ME = 0x0032
    WIND_OFF_ME = 0x0033
    SELF_CLEAN = 0x0039  # AKA Active Clean
    _UNKNOWN = 0x0040  # Unknown ID from various logs
    BREEZE_AWAY = 0x0042  # AKA "Prevent Straight Wind"
    BREEZE_CONTROL = 0x0043  # AKA "FA No Wind Sense"
    RATE_SELECT = 0x0048
    FRESH_AIR = 0x004B
    PARENT_CONTROL = 0x0051  # ??
    PREVENT_STRAIGHT_WIND_SELECT = 0x0058  # ??
    CASCADE = 0x0059  # AKA "Wind Around"
    JET_COOL = 0x0067  # ??
    PRESET_IECO = 0x00E3
    ICHECK = 0x0091  # ??
    EMERGENT_HEAT_WIND = 0x0093  # ??
    HEAT_PTC_WIND = 0x0094  # ??
    CVP = 0x0098  # ??
    FAN_SPEED_CONTROL = 0x0210
    PRESET_ECO = 0x0212
    PRESET_FREEZE_PROTECTION = 0x0213
    MODES = 0x0214
    SWING_MODES = 0x0215
    ENERGY = 0x0216  # AKA electricity
    FILTER_REMIND = 0x0217
    AUX_ELECTRIC_HEAT = 0x0219  # AKA PTC
    PRESET_TURBO = 0x021A
    FILTER_CHECK = 0x0221
    ANION = 0x021E
    HUMIDITY = 0x021F
    FAHRENHEIT = 0x0222
    DISPLAY_CONTROL = 0x0224
    TEMPERATURES = 0x0225
    BUZZER = 0x022C  # TODO Reference refers to this as "sound". Is this different then buzzer?
    MAIN_HORIZONTAL_GUIDE_STRIP = 0x0230  # ??
    SUP_HORIZONTAL_GUIDE_STRIP = 0x0231  # ??
    TWINS_MACHINE = 0x0232  # ??
    GUIDE_STRIP_TYPE = 0x0233  # ??
    BODY_CHECK = 0x0234  # ??


class PropertyId(IntEnum):
    SWING_UD_ANGLE = 0x0009
    SWING_LR_ANGLE = 0x000A
    INDOOR_HUMIDITY = 0x0015  # TODO Reference refers to a potential bug with this
    BREEZELESS = 0x0018  # AKA "No Wind Sense"
    BUZZER = 0x001A
    SELF_CLEAN = 0x0039
    BREEZE_AWAY = 0x0042  # AKA "Prevent Straight Wind"
    BREEZE_CONTROL = 0x0043  # AKA "FA No Wind Sense"
    RATE_SELECT = 0x0048
    FRESH_AIR = 0x004B
    CASCADE = 0x0059  # AKA "Wind Around"
    JET_COOL = 0x0067  # AKA "Flash Cool"
    IECO = 0x00E3
    ANION = 0x021E

    @property
    def _supported(self) -> bool:
        """Check if a property ID is supported/tested."""
        return self in [
            PropertyId.BREEZE_AWAY,
            PropertyId.BREEZE_CONTROL,
            PropertyId.BREEZELESS,
            PropertyId.BUZZER,
            PropertyId.CASCADE,
            PropertyId.IECO,
            PropertyId.JET_COOL,
            PropertyId.RATE_SELECT,
            PropertyId.SELF_CLEAN,
            PropertyId.SWING_LR_ANGLE,
            PropertyId.SWING_UD_ANGLE,
        ]

    def decode(self, data: bytes) -> Any:
        """Decode raw property data into a convenient form."""
        if not self._supported:
            raise NotImplementedError(f"{repr(self)} decode is not supported.")

        if self in [PropertyId.BREEZELESS, PropertyId.JET_COOL, PropertyId.SELF_CLEAN,]:
            return bool(data[0])
        elif self == PropertyId.BREEZE_AWAY:
            return data[0] == 2
        elif self == PropertyId.BUZZER:
            return None  # Don't decode buzzer
        elif self == PropertyId.IECO:
            # data[0] - ieco_number, data[1] - ieco_switch
            return bool(data[1])
        elif self == PropertyId.CASCADE:
            # data[0] - wind_around, data[1] - wind_around_ud
            return data[1] if data[0] else 0
        else:
            return data[0]

    def encode(self, *args, **kwargs) -> bytes:
        """Encode property into raw form."""
        if not self._supported:
            raise NotImplementedError(f"{repr(self)} encode is not supported.")

        if self == PropertyId.BREEZE_AWAY:
            return bytes([2 if args[0] else 1])
        elif self == PropertyId.IECO:
            # ieco_frame, ieco_number, ieco_switch, ...
            return bytes([0, 1, args[0]]) + bytes(10)
        elif self == PropertyId.CASCADE:
            # data[0] - wind_around, data[1] - wind_around_ud
            return bytes([1 if args[0] else 0, args[0]])
        else:
            return bytes(args[0:1])


class TemperatureType(IntEnum):
    UNKNOWN = 0
    INDOOR = 0x2
    OUTDOOR = 0x3


class Command(Frame):
    """Base class for AC commands."""

    CONTROL_SOURCE = 0x2  # App control

    _message_id = 0

    def __init__(self, frame_type: FrameType) -> None:
        super().__init__(DeviceType.AIR_CONDITIONER, frame_type)

    def tobytes(self, data: Union[bytes, bytearray] = bytes()) -> bytes:
        # Append message ID to payload
        # TODO Message ID in reference is just a random value
        payload = data + bytes([self._next_message_id()])

        # Append CRC
        return super().tobytes(payload + bytes([crc8.calculate(payload)]))

    def _next_message_id(self) -> int:
        Command._message_id += 1
        return Command._message_id & 0xFF


class GetCapabilitiesCommand(Command):
    """Command to query capabilities of the device."""

    def __init__(self, additional: bool = False) -> None:
        super().__init__(frame_type=FrameType.QUERY)

        self._additional = additional

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        if not self._additional:
            # Get capabilities
            payload = bytes([0xB5, 0x01, 0x00])
        else:
            # Get more capabilities
            payload = bytes([0xB5, 0x01, 0x01, 0x1])
        return super().tobytes(payload)


class GetStateCommand(Command):
    """Command to query basic state of the device."""

    def __init__(self) -> None:
        super().__init__(frame_type=FrameType.QUERY)

        self.temperature_type = TemperatureType.INDOOR

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        return super().tobytes(bytes([
            # Get state
            0x41,
            # Unknown
            0x81, 0x00, 0xFF, 0x03, 0xFF, 0x00,
            # Temperature request
            self.temperature_type,
            # Unknown
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Unknown
            0x03,
        ]))


class GetEnergyUsageCommand(Command):
    """Command to query energy usage from device."""

    def __init__(self) -> None:
        super().__init__(frame_type=FrameType.QUERY)

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        payload = bytearray(20)

        payload[0] = 0x41
        payload[1] = 0x21
        payload[2] = 0x01
        payload[3] = 0x44

        return super().tobytes(payload)


class GetHumidityCommand(Command):
    """Command to query indoor humidity from device."""

    def __init__(self) -> None:
        super().__init__(frame_type=FrameType.QUERY)

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        payload = bytearray(20)

        payload[0] = 0x41
        payload[1] = 0x21
        payload[2] = 0x01
        payload[3] = 0x45

        return super().tobytes(payload)


class SetStateCommand(Command):
    """Command to set basic state of the device."""

    def __init__(self) -> None:
        super().__init__(frame_type=FrameType.CONTROL)

        self.beep_on = True
        self.power_on = False
        self.target_temperature = 25.0
        self.operational_mode = 0
        self.fan_speed = 0
        self.eco = True
        self.swing_mode = 0
        self.turbo = False
        self.fahrenheit = True
        self.sleep = False
        self.freeze_protection = False
        self.follow_me = False
        self.purifier = False
        self.target_humidity = 40
        self.aux_heat = False
        self.force_aux_heat = False
        self.independent_aux_heat = False

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        # Build beep and power status bytes
        beep = 0x40 if self.beep_on else 0
        power = 0x1 if self.power_on else 0

        # Get integer and fraction components of target temp
        fractional_temp, integral_temp = math.modf(self.target_temperature)
        integral_temp = int(integral_temp)

        if 17 <= integral_temp <= 30:
            # Use primary method
            temperature = (integral_temp - 16) & 0xF
            temperature_alt = 0
        else:
            # Out of range, use alternate method
            # TODO additional range possible according to Lua code
            temperature = 0
            temperature_alt = (integral_temp - 12) & 0x1F

        # Set half degree bit
        temperature |= 0x10 if (fractional_temp > 0) else 0

        mode = (self.operational_mode & 0x7) << 5

        # Build swing mode byte
        swing_mode = 0x30 | (self.swing_mode & 0x3F)

        # Build eco mode, purifier, and aux heat byte
        eco = 0x80 if self.eco else 0
        purifier = 0x20 if self.purifier else 0
        aux_heat = 0x08 if self.aux_heat else 0
        force_aux_heat = 0x10 if self.force_aux_heat else 0

        # Build sleep, turbo and fahrenheit byte
        sleep = 0x01 if self.sleep else 0
        turbo = 0x02 if self.turbo else 0
        fahrenheit = 0x04 if self.fahrenheit else 0

        # Build alternate turbo byte
        turbo_alt = 0x20 if self.turbo else 0
        follow_me = 0x80 if self.follow_me else 0

        # Build target humidity byte
        humidity = self.target_humidity & 0x7F

        # Build freeze protection byte
        freeze_protect = 0x80 if self.freeze_protection else 0

        # Build independent aux heat
        independent_aux_heat = 0x08 if self.independent_aux_heat else 0

        return super().tobytes(bytes([
            # Set state
            0x40,
            # Beep and power state
            self.CONTROL_SOURCE | beep | power,
            # Temperature and operational mode
            temperature | mode,
            # Fan speed
            self.fan_speed,
            # Timer
            0x7F, 0x7F, 0x00,
            # Swing mode
            swing_mode,
            # Follow me and alternate turbo mode
            follow_me | turbo_alt,
            # ECO mode, purifier/anion, and aux heat
            eco | purifier | force_aux_heat | aux_heat,
            # Sleep mode, turbo mode and fahrenheit
            sleep | turbo | fahrenheit,
            # Unknown
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00,
            # Alternate temperature
            temperature_alt,
            # Target humidity
            humidity,
            # Unknown
            0x00,
            # Frost/freeze protection
            freeze_protect,
            # Independent aux heat
            independent_aux_heat,
            # Unknown
            0x00,
        ]))


class ToggleDisplayCommand(Command):
    """Command to toggle the LED display of the device."""

    def __init__(self) -> None:
        # For whatever reason, toggle display uses a request type...
        super().__init__(frame_type=FrameType.QUERY)

        self.beep_on = True

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        # Set beep bit
        beep = 0x40 if self.beep_on else 0

        return super().tobytes(bytes([
            # Get state
            0x41,
            # Beep and other flags
            self.CONTROL_SOURCE | beep,
            # Unknown
            0x00, 0xFF, 0x02,
            0x00, 0x02, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
        ]))


class GetPropertiesCommand(Command):
    """Command to query specific properties from the device."""

    def __init__(self, props: Collection[PropertyId]) -> None:
        super().__init__(frame_type=FrameType.QUERY)

        self._properties = props

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        payload = bytearray([
            0xB1,  # Property request
            len(self._properties),
        ])

        for prop in self._properties:
            payload += struct.pack("<H", prop)

        return super().tobytes(payload)


class SetPropertiesCommand(Command):
    """Command to set specific properties of the device."""

    def __init__(self, props: Mapping[PropertyId, Union[int, bool]]) -> None:
        super().__init__(frame_type=FrameType.CONTROL)

        self._properties = props

    def tobytes(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride] # nopep8
        payload = bytearray([
            0xB0,  # Property request
            len(self._properties),
        ])

        for prop, value in self._properties.items():
            payload += struct.pack("<H", prop)

            # Encode property value to bytes
            value = prop.encode(value)

            payload += bytes([len(value)])
            payload += value

        return super().tobytes(payload)


class Response():
    """Base class for AC responses."""

    def __init__(self, payload: memoryview) -> None:
        # Set ID and copy the payload
        self._id = payload[0]
        self._payload = bytes(payload)

    def __str__(self) -> str:
        return self.payload.hex()

    @property
    def id(self) -> int:
        return self._id

    @property
    def payload(self) -> bytes:
        return self._payload

    @classmethod
    def validate(cls, payload: memoryview) -> None:
        """Validate a response by checking the frame checksum and payload CRC."""

        # Some devices use a CRC others seem to use a 2nd checksum
        payload_crc = crc8.calculate(payload[0:-1])
        payload_checksum = Frame.checksum(payload[0:-1])
        if payload_crc != payload[-1] and payload_checksum != payload[-1]:
            raise InvalidResponseException(
                f"Payload '{payload.hex()}' failed CRC and checksum. Received: 0x{payload[-1]:X}, Expected: 0x{payload_crc:X} or 0x{payload_checksum:X}.")

    @classmethod
    def construct(cls, frame: bytes) -> Response:
        """Construct a response object from raw data."""

        # Build a memoryview of the frame for zero-copy slicing
        with memoryview(frame) as frame_mv:
            # Validate the frame
            Frame.validate(frame_mv, DeviceType.AIR_CONDITIONER)

            # Default to base class
            response_class = Response

            # Fetch the appropriate response class from the ID
            frame_type = frame_mv[9]
            response_id = frame_mv[10]
            if response_id == ResponseId.STATE:
                response_class = StateResponse
            elif response_id == ResponseId.CAPABILITIES and frame_type == FrameType.QUERY:
                # Some devices have unsolicited "capabilities" responses with a frame type of 0x5
                response_class = CapabilitiesResponse
            elif response_id in [ResponseId.PROPERTIES, ResponseId.PROPERTIES_ACK]:
                response_class = PropertiesResponse
            elif response_id == ResponseId.GROUP_DATA:
                # Response type depends on an additional "group" byte
                group = frame_mv[13] & 0xF
                if group == 4:
                    response_class = EnergyUsageResponse
                elif group == 5:
                    response_class = HumidityResponse

            # Validate the payload CRC
            # ...except for properties which certain devices send invalid CRCs
            if response_class != PropertiesResponse:
                Response.validate(frame_mv[10:-1])

            # Build the response
            return response_class(frame_mv[10:-2])


class CapabilitiesResponse(Response):
    """Response to capabilities query."""

    def __init__(self, payload: memoryview) -> None:
        super().__init__(payload)

        self._capabilities = {}
        self._additional_capabilities = False

        self._parse_capabilities(payload)

    @property
    def raw_capabilities(self) -> Mapping[str, Any]:
        return self._capabilities

    def _parse_capabilities(self, payload: memoryview) -> None:
        # Clear existing capabilities
        self._capabilities.clear()

        # Define some local functions to parse capability values
        def get_value(w) -> Callable[[int], bool]: return lambda v: v == w

        # Define a named tuple that represents a decoder
        reader = namedtuple("decoder", "name read")

        # Create a map of capability ID to decoders
        capability_readers = {
            CapabilityId.ANION: reader("anion", get_value(1)),
            CapabilityId.AUX_ELECTRIC_HEAT: reader("aux_electric_heat", get_value(1)),
            CapabilityId.BREEZE_AWAY: reader("breeze_away", get_value(1)),
            CapabilityId.BREEZE_CONTROL: reader("breeze_control", get_value(1)),
            CapabilityId.BREEZELESS: reader("breezeless", get_value(1)),
            CapabilityId.BUZZER:  reader("buzzer", get_value(1)),
            CapabilityId.CASCADE:  reader("cascade", get_value(1)),
            CapabilityId.DISPLAY_CONTROL: reader("display_control", lambda v: v in [1, 2, 100]),
            CapabilityId.ENERGY: [
                reader("energy_stats", lambda v: v in [2, 3, 4, 5]),
                reader("energy_setting", lambda v: v in [3, 5]),
                reader("energy_bcd", lambda v: v in [2, 3]),
            ],
            CapabilityId.FAHRENHEIT: reader("fahrenheit", get_value(0)),
            CapabilityId.FAN_SPEED_CONTROL: [
                reader("fan_silent", get_value(6)),
                reader("fan_low", lambda v: v in [3, 4, 5, 6, 7]),
                reader("fan_medium", lambda v: v in [5, 6, 7]),
                reader("fan_high", lambda v: v in [3, 4, 5, 6, 7]),
                reader("fan_auto", lambda v: v in [4, 5, 6]),
                reader("fan_custom", get_value(1)),
            ],
            CapabilityId.FILTER_REMIND: [
                reader("filter_notice", lambda v: v in [1, 2, 4]),
                reader("filter_clean", lambda v: v in [3, 4]),
            ],
            CapabilityId.HUMIDITY:
            [
                reader("humidity_auto_set", lambda v: v in [1, 2]),
                reader("humidity_manual_set", lambda v: v in [2, 3]),
            ],
            CapabilityId.JET_COOL: reader("jet_cool", get_value(1)),
            CapabilityId.MODES: [
                reader("heat_mode", lambda v: v in [
                       1, 2, 4, 6, 7, 9, 10, 11, 12, 13]),
                reader("cool_mode", lambda v: v not in [2, 10, 12]),
                reader("dry_mode", lambda v: v in [0, 1, 5, 6, 9, 11, 13]),
                reader("auto_mode", lambda v: v in [0, 1, 2, 7, 8, 9, 13]),
                reader("aux_heat_mode", lambda v: v == 9),  # Heat & Aux
                reader("aux_mode", lambda v: v in [9, 10, 11, 13]),  # Aux only
            ],
            CapabilityId.PRESET_ECO: reader("eco", lambda v: v in [1, 2]),
            CapabilityId.PRESET_FREEZE_PROTECTION: reader("freeze_protection", get_value(1)),
            CapabilityId.PRESET_IECO: reader("ieco", get_value(1)),
            CapabilityId.PRESET_TURBO:  [
                reader("turbo_heat", lambda v: v in [1, 3]),
                reader("turbo_cool", lambda v: v < 2),
            ],
            CapabilityId.RATE_SELECT:  [
                reader("rate_select_2_level", get_value(1)),  # Gear
                reader("rate_select_5_level", lambda v: v in [
                       2, 3]),  # Genmode and Gear5
            ],
            CapabilityId.SELF_CLEAN:  reader("self_clean", get_value(1)),
            CapabilityId.SMART_EYE:  reader("smart_eye", get_value(1)),
            CapabilityId.SWING_LR_ANGLE: reader("swing_horizontal_angle", get_value(1)),
            CapabilityId.SWING_UD_ANGLE: reader("swing_vertical_angle", get_value(1)),
            CapabilityId.SWING_MODES: [
                reader("swing_horizontal", lambda v: v in [1, 3]),
                reader("swing_vertical", lambda v: v < 2),
            ],
            # CapabilityId.TEMPERATURES too complex to be handled here
            CapabilityId.WIND_OFF_ME:  reader("wind_off_me", get_value(1)),
            CapabilityId.WIND_ON_ME:  reader("wind_on_me", get_value(1)),
            # CapabilityId._UNKNOWN is a special case
        }

        count = payload[1]
        caps = payload[2:]

        # Loop through each capability
        for _ in range(0, count):
            # Stop if out of data
            if len(caps) < 3:
                break

            # Skip empty capabilities
            size = caps[2]
            if size == 0:
                caps = caps[3:]
                continue

            # Unpack 16 bit ID
            (raw_id, ) = struct.unpack("<H", caps[0:2])

            # Covert ID to enumerate type
            try:
                capability_id = CapabilityId(raw_id)
            except ValueError:
                _LOGGER.info(
                    "Unknown capability ID: 0x%04X, Size: %d.", raw_id, size)
                # Advanced to next capability
                caps = caps[3+size:]
                continue

            # Fetch first cap value
            value = caps[3]

            # Apply predefined capability reader if it exists
            if capability_id in capability_readers:
                # Local function to apply a reader
                def apply(d, v): return {d.name: d.read(v)}

                reader = capability_readers[capability_id]
                if isinstance(reader, list):
                    # Apply each reader in the list
                    for r in reader:
                        self._capabilities.update(apply(r, value))
                else:
                    # Apply the single reader
                    self._capabilities.update(apply(reader, value))

            elif capability_id == CapabilityId.TEMPERATURES:
                # Skip if capability size is too small
                if size < 6:
                    continue

                self._capabilities["cool_min_temperature"] = caps[3] * 0.5
                self._capabilities["cool_max_temperature"] = caps[4] * 0.5
                self._capabilities["auto_min_temperature"] = caps[5] * 0.5
                self._capabilities["auto_max_temperature"] = caps[6] * 0.5
                self._capabilities["heat_min_temperature"] = caps[7] * 0.5
                self._capabilities["heat_max_temperature"] = caps[8] * 0.5

                # TODO The else of this condition is commented out in reference code
                self._capabilities["decimals"] = (
                    caps[9] if size > 6 else caps[2]) != 0

            elif capability_id == CapabilityId._UNKNOWN:
                # Supress warnings from unknown capability
                _LOGGER.debug(
                    "Ignored unknown capability ID: 0x%04X, Size: %d.", capability_id, size)

            else:
                _LOGGER.info(
                    "Unsupported capability %r, Size: %d.", capability_id, size)

            # Advanced to next capability
            caps = caps[3+size:]

        # Check if there are additional capabilities
        if len(caps) > 1:
            self._additional_capabilities = bool(caps[-2])

    def _get_fan_speed(self, speed) -> bool:
        # If any fan_ capability was received, check against them
        if any(k.startswith("fan_") for k in self._capabilities):
            # Assume that a fan capable of custom speeds is capable of any speed
            return self._capabilities.get(f"fan_{speed}", False) or self._capabilities.get("fan_custom", False)

        # Otherwise return a default set for devices that don't send the capability
        return speed in ["low", "medium", "high", "auto"]

    def merge(self, other: CapabilitiesResponse) -> None:
        # Add other's capabilities to ours
        self._capabilities.update(other._capabilities)

    @property
    def additional_capabilities(self) -> bool:
        return self._additional_capabilities

    @property
    def anion(self) -> bool:
        return self._capabilities.get("anion", False)

    # TODO rethink these properties for fan speed, operation mode and swing mode
    # Surely there's a better way than define props for each possible cap
    @property
    def fan_silent(self) -> bool:
        return self._get_fan_speed("silent")

    @property
    def fan_low(self) -> bool:
        return self._get_fan_speed("low")

    @property
    def fan_medium(self) -> bool:
        return self._get_fan_speed("medium")

    @property
    def fan_high(self) -> bool:
        return self._get_fan_speed("high")

    @property
    def fan_auto(self) -> bool:
        return self._get_fan_speed("auto")

    @property
    def fan_custom(self) -> bool:
        return self._capabilities.get("fan_custom", False)

    @property
    def breeze_away(self) -> bool:
        return self._capabilities.get("breeze_away", False)

    @property
    def breeze_control(self) -> bool:
        return self._capabilities.get("breeze_control", False)

    @property
    def breezeless(self) -> bool:
        return self._capabilities.get("breezeless", False)

    @property
    def cascade(self) -> bool:
        return self._capabilities.get("cascade", False)

    @property
    def swing_horizontal_angle(self) -> bool:
        return self._capabilities.get("swing_horizontal_angle", False)

    @property
    def swing_vertical_angle(self) -> bool:
        return self._capabilities.get("swing_vertical_angle", False)

    @property
    def swing_horizontal(self) -> bool:
        return self._capabilities.get("swing_horizontal", False)

    @property
    def swing_vertical(self) -> bool:
        return self._capabilities.get("swing_vertical", False)

    @property
    def swing_both(self) -> bool:
        return self.swing_vertical and self.swing_horizontal

    @property
    def dry_mode(self) -> bool:
        return self._capabilities.get("dry_mode", False)

    @property
    def cool_mode(self) -> bool:
        return self._capabilities.get("cool_mode", False)

    @property
    def heat_mode(self) -> bool:
        return self._capabilities.get("heat_mode", False)

    @property
    def auto_mode(self) -> bool:
        return self._capabilities.get("auto_mode", False)

    @property
    def aux_heat_mode(self) -> bool:
        return self._capabilities.get("aux_heat_mode", False)

    @property
    def aux_mode(self) -> bool:
        return self._capabilities.get("aux_mode", False)

    @property
    def aux_electric_heat(self) -> bool:
        # TODO How does electric aux heat differ from aux mode?
        return self._capabilities.get("aux_electric_heat", False)

    @property
    def eco(self) -> bool:
        return self._capabilities.get("eco", False)

    @property
    def ieco(self) -> bool:
        return self._capabilities.get("ieco", False)

    @property
    def jet_cool(self) -> bool:
        return self._capabilities.get("jet_cool", False)

    @property
    def turbo(self) -> bool:
        return (self._capabilities.get("turbo_heat", False)
                or self._capabilities.get("turbo_cool", False))

    @property
    def freeze_protection(self) -> bool:
        return self._capabilities.get("freeze_protection", False)

    @property
    def display_control(self) -> bool:
        return self._capabilities.get("display_control", False)

    @property
    def filter_reminder(self) -> bool:
        # TODO unsure of difference between filter_notice and filter_clean
        return self._capabilities.get("filter_notice", False)

    @property
    def min_temperature(self) -> int:
        mode = ["cool", "auto", "heat"]
        return min([self._capabilities.get(f"{m}_min_temperature", 16) for m in mode])

    @property
    def max_temperature(self) -> int:
        mode = ["cool", "auto", "heat"]
        return max([self._capabilities.get(f"{m}_max_temperature", 30) for m in mode])

    @property
    def energy_stats(self) -> bool:
        return self._capabilities.get("energy_stats", False)

    @property
    def humidity(self) -> bool:
        # TODO Unsure the difference between these two
        return (self._capabilities.get("humidity_auto_set", False)
                or self._capabilities.get("humidity_manual_set", False))

    @property
    def target_humidity(self) -> bool:
        return self._capabilities.get("humidity_manual_set", False)

    @property
    def self_clean(self) -> bool:
        return self._capabilities.get("self_clean", False)

    @property
    def rate_select_levels(self) -> Optional[int]:
        if self._capabilities.get("rate_select_5_level", False):
            return 5
        elif self._capabilities.get("rate_select_2_level", False):
            return 2

        return None


class StateResponse(Response):
    """Response to state query."""

    def __init__(self, payload: memoryview) -> None:
        super().__init__(payload)

        self.power_on = None
        self.target_temperature = None
        self.operational_mode = None
        self.fan_speed = None
        self.swing_mode = None
        self.turbo = None
        self.eco = None
        self.sleep = None
        self.fahrenheit = None
        self.indoor_temperature = None
        self.outdoor_temperature = None
        self.filter_alert = None
        self.display_on = None
        self.freeze_protection = None
        self.follow_me = None
        self.purifier = None
        self.target_humidity = None
        self.aux_heat = None
        self.independent_aux_heat = None
        self.error_code = None

        self._parse(payload)

    def _parse_temperature(self, data: int, decimals: float, fahrenheit: bool) -> Optional[float]:
        """Parse a temperature value from the payload using additional precision bits as needed."""
        if data == 0xFF:
            return None

        # Temperature parsing lifted from https://github.com/dudanov/MideaUART
        temperature = (data - 50) / 2

        # In Celcius, use additional precision from decimals if present
        if not fahrenheit and decimals:
            return int(temperature) + (decimals if temperature >= 0 else -decimals)

        if decimals >= 0.5:
            return int(temperature) + (0.5 if temperature >= 0 else -0.5)

        return temperature

    def _parse(self, payload: memoryview) -> None:
        """Parse the state response payload."""

        self.power_on = bool(payload[1] & 0x1)
        # self.imode_resume = payload[1] & 0x4
        # self.timer_mode = (payload[1] & 0x10) > 0
        # self.appliance_error = (payload[1] & 0x80) > 0

        # Unpack target temp and mode byte
        self.target_temperature = (payload[2] & 0xF) + 16.0
        self.target_temperature += 0.5 if payload[2] & 0x10 else 0.0
        self.operational_mode = (payload[2] >> 5) & 0x7

        # Fan speed
        # Fan speed can be auto = 102, or value from 0 - 100
        # On my unit, Low == 40 (LED < 40), Med == 60 (LED < 60), High == 100 (LED < 100)
        self.fan_speed = payload[3] & 0x7F

        # on_timer_value = payload[4]
        # on_timer_minutes = payload[6]
        # self.on_timer = {
        #     'status': ((on_timer_value & 0x80) >> 7) > 0,
        #     'hour': (on_timer_value & 0x7c) >> 2,
        #     'minutes': (on_timer_value & 0x3) | ((on_timer_minutes & 0xf0) >> 4)
        # }

        # off_timer_value = payload[5]
        # off_timer_minutes = payload[6]
        # self.off_timer = {
        #     'status': ((off_timer_value & 0x80) >> 7) > 0,
        #     'hour': (off_timer_value & 0x7c) >> 2,
        #     'minutes': (off_timer_value & 0x3) | (off_timer_minutes & 0xf)
        # }

        # Swing mode
        self.swing_mode = payload[7] & 0xF

        # self.cozy_sleep = payload[8] & 0x03
        # self.save = (payload[8] & 0x08) > 0
        # self.low_frequency_fan = (payload[8] & 0x10) > 0
        self.turbo = bool(payload[8] & 0x20)
        self.independent_aux_heat = bool(payload[8] & 0x40)
        self.follow_me = bool(payload[8] & 0x80)

        self.eco = bool(payload[9] & 0x10)
        self.purifier = bool(payload[9] & 0x20)
        # self.child_sleep = (payload[9] & 0x01) > 0
        # self.exchange_air = (payload[9] & 0x02) > 0
        # self.dry_clean = (payload[9] & 0x04) > 0
        self.aux_heat = bool(payload[9] & 0x08)
        # self.temp_unit = (payload[9] & 0x80) > 0

        self.sleep = bool(payload[10] & 0x1)
        self.turbo |= bool(payload[10] & 0x2)
        self.fahrenheit = bool(payload[10] & 0x4)
        # self.catch_cold = (payload[10] & 0x08) > 0
        # self.night_light = (payload[10] & 0x10) > 0
        # self.peak_elec = (payload[10] & 0x20) > 0
        # self.natural_fan = (payload[10] & 0x40) > 0

        # Decode temperatures using additional precision bits
        self.indoor_temperature = self._parse_temperature(
            payload[11], (payload[15] & 0xF) / 10, self.fahrenheit)
        self.outdoor_temperature = self._parse_temperature(
            payload[12], (payload[15] >> 4) / 10, self.fahrenheit)

        # Decode alternate target temperature
        target_temperature_alt = payload[13] & 0x1F
        if target_temperature_alt != 0:
            # TODO additional range possible according to Lua code
            self.target_temperature = target_temperature_alt + 12
            self.target_temperature += 0.5 if payload[2] & 0x10 else 0.0

        self.filter_alert = bool(payload[13] & 0x20)

        self.display_on = (payload[14] != 0x70)

        self.error_code = payload[16]

        if len(payload) < 20:
            return

        self.target_humidity = payload[19] & 0x7F

        if len(payload) < 22:
            return

        self.freeze_protection = bool(payload[21] & 0x80)


class PropertiesResponse(Response):
    """Response to properties query."""

    def __init__(self, payload: memoryview) -> None:
        super().__init__(payload)

        self._properties = {}

        self._parse(payload)

    def _parse(self, payload: memoryview) -> None:
        # Clear existing properties
        self._properties.clear()

        count = payload[1]
        props = payload[2:]

        # Loop through each property
        for _ in range(0, count):
            # Stop if out of data
            if len(props) < 4:
                break

            # Skip empty properties
            size = props[3]
            if size == 0:
                props = props[4:]
                continue

            # Unpack 16 bit ID
            (raw_id, ) = struct.unpack("<H", props[0:2])

            # Covert ID to enumerate type
            try:
                property = PropertyId(raw_id)
            except ValueError:
                _LOGGER.warning(
                    "Unknown property ID 0x%04X, Size: %d.", raw_id, size)
                # Advanced to next property
                props = props[4+size:]
                continue

            # Check execution result and log any errors
            error = props[2] & 0x10
            if error:
                _LOGGER.error(
                    "Property %r failed, Result: 0x%02X.", property, props[2])

            # Parse the property
            try:
                if (value := property.decode(props[4:])) is not None:
                    self._properties.update({property: value})
            except NotImplementedError:
                _LOGGER.warning(
                    "Unsupported property %r, Size: %d.", property, size)

            # Advanced to next property
            props = props[4+size:]

    def get_property(self, id: PropertyId) -> Optional[Any]:
        return self._properties.get(id, None)


class EnergyUsageResponse(Response):
    """Response to a GetEnergyUsageCommand."""

    def __init__(self, payload: memoryview) -> None:
        super().__init__(payload)

        self.total_energy = None
        self.current_energy = None
        self.real_time_power = None

        self.total_energy_binary = None
        self.current_energy_binary = None
        self.real_time_power_binary = None

        self._parse(payload)

    def _parse(self, payload: memoryview) -> None:
        # Response is technically a "group data 4" response
        # and may contain other interesting data

        def decode_bcd(d: int) -> int:
            return 10 * (d >> 4) + (d & 0xF)

        def parse_energy(d: bytes) -> tuple[float, float]:
            bcd = (10000 * decode_bcd(d[0]) +
                   100 * decode_bcd(d[1]) +
                   1 * decode_bcd(d[2]) +
                   0.01 * decode_bcd(d[3]))
            binary = ((d[0] << 24) +
                      (d[1] << 16) +
                      (d[2] << 8) +
                      d[3]) / 10
            return bcd, binary

        def parse_power(d: bytes) -> tuple[float, float]:
            bcd = (1000 * decode_bcd(d[0]) +
                   10 * decode_bcd(d[1]) +
                   0.1 * decode_bcd(d[2]))
            binary = ((d[0] << 16) +
                      (d[1] << 8) +
                      d[2]) / 10
            return bcd, binary

        # Lua reference decodes real time power field in BCD and binary form
        # JS reference decodes multiple energy/power fields in BCD only.

        # Total energy in bytes 4 - 7
        total_energy_bcd, total_energy_binary = parse_energy(
            payload[4:8])

        # JS references decodes bytes 8 - 11 as "total running energy"
        # Older JS does not decode these bytes, and sample payloads contain bogus data

        # Current run energy consumption bytes 12 - 15
        current_energy_bcd, current_energy_binary = parse_energy(
            payload[12:16])

        # Real time power usage bytes 16 - 18
        real_time_power_bcd, real_time_power_binary = parse_power(
            payload[16:19])

        # Assume energy monitory is valid if at least one stat is non zero
        valid = total_energy_bcd or current_energy_bcd or real_time_power_bcd

        self.total_energy = total_energy_bcd if valid else None
        self.current_energy = current_energy_bcd if valid else None
        self.real_time_power = real_time_power_bcd if valid else None

        self.total_energy_binary = total_energy_binary if valid else None
        self.current_energy_binary = current_energy_binary if valid else None
        self.real_time_power_binary = real_time_power_binary if valid else None


class HumidityResponse(Response):
    """Response to a GetHumidityCommand."""

    def __init__(self, payload: memoryview) -> None:
        super().__init__(payload)

        self.humidity = None

        self._parse(payload)

    def _parse(self, payload: memoryview) -> None:
        # Response is technically a "group data 5" response
        # and may contain other interesting data

        self.humidity = payload[4] if payload[4] != 0 else None
