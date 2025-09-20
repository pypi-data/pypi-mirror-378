import logging
import unittest
from typing import cast

from msmart.const import DeviceType, FrameType
from msmart.frame import Frame, InvalidFrameException

from .command import *


class _TestResponseBase(unittest.TestCase):
    """Base class that provides some common methods for derived classes."""

    def assertHasAttr(self, obj, attr) -> None:
        """Assert that an object has an attribute."""
        self.assertTrue(hasattr(obj, attr),
                        msg=f"Object {obj} lacks attribute '{attr}'.")

    def _test_build_response(self, msg) -> Response:
        """Build a response from the frame and assert it exists."""
        resp = Response.construct(msg)
        self.assertIsNotNone(resp)
        return resp

    def _test_check_attributes(self, obj, expected_attrs) -> None:
        """Assert that an object has all expected attributes."""
        for attr in expected_attrs:
            self.assertHasAttr(obj, attr)


class TestCommand(unittest.TestCase):

    def test_frame(self) -> None:
        """Test that we frame a command properly."""

        EXPECTED_PAYLOAD = bytes.fromhex(
            "418100ff03ff00020000000000000000000000000311f4")

        # Override message id to match test data
        Command._message_id = 0x10

        # Build frame from command
        command = GetStateCommand()
        frame = command.tobytes()
        self.assertIsNotNone(frame)

        # Assert that frame is valid
        with memoryview(frame) as frame_mv:
            Frame.validate(frame_mv, DeviceType.AIR_CONDITIONER)

        # Check frame payload to ensure it matches expected
        self.assertEqual(frame[10:-1], EXPECTED_PAYLOAD)

        # Check length byte
        self.assertEqual(frame[1], len(
            EXPECTED_PAYLOAD) + Frame._HEADER_LENGTH)

        # Check device type
        self.assertEqual(frame[2], DeviceType.AIR_CONDITIONER)

        # Check frame type
        self.assertEqual(frame[9], FrameType.QUERY)


class TestStateResponse(_TestResponseBase):
    """Test device state response messages."""

    # Attributes expected in state response objects
    EXPECTED_ATTRS = [
        "power_on",
        "target_temperature",
        "operational_mode",
        "fan_speed",
        "swing_mode",
        "turbo",
        "eco",
        "sleep",
        "fahrenheit",
        "indoor_temperature",
        "outdoor_temperature",
        "filter_alert",
        "display_on",
        "freeze_protection",
        "follow_me",
        "purifier",
        "target_humidity",
        "aux_heat",
        "independent_aux_heat",
        "error_code",
    ]

    def _test_response(self, msg) -> StateResponse:
        resp = self._test_build_response(msg)
        self._test_check_attributes(resp, self.EXPECTED_ATTRS)
        return cast(StateResponse, resp)

    def test_message_checksum(self) -> None:
        # https://github.com/mill1000/midea-ac-py/issues/11#issuecomment-1650647625
        # V3 state response with checksum as CRC, and shorter than expected
        TEST_MESSAGE_CHECKSUM_AS_CRC = bytes.fromhex(
            "aa1eac00000000000003c0004b1e7f7f000000000069630000000000000d33")
        resp = self._test_response(TEST_MESSAGE_CHECKSUM_AS_CRC)

        # Assert response is a state response
        self.assertEqual(type(resp), StateResponse)

        # Suppress type errors
        resp = cast(StateResponse, resp)

        self.assertEqual(resp.target_temperature, 27.0)
        self.assertEqual(resp.indoor_temperature, 27.5)
        self.assertEqual(resp.outdoor_temperature, 24.5)

    def test_message_v2(self) -> None:
        # V2 state response
        TEST_MESSAGE_V2 = bytes.fromhex(
            "aa22ac00000000000303c0014566000000300010045eff00000000000000000069fdb9")
        resp = self._test_response(TEST_MESSAGE_V2)

        # Assert response is a state response
        self.assertEqual(type(resp), StateResponse)

        # Suppress type errors
        resp = cast(StateResponse, resp)

        self.assertEqual(resp.target_temperature, 21.0)
        self.assertEqual(resp.indoor_temperature, 22.0)
        self.assertEqual(resp.outdoor_temperature, None)

    def test_message_v3(self) -> None:
        # V3 state response
        TEST_MESSAGE_V3 = bytes.fromhex(
            "aa23ac00000000000303c00145660000003c0010045c6b20000000000000000000020d79")
        resp = self._test_response(TEST_MESSAGE_V3)

        # Assert response is a state response
        self.assertEqual(type(resp), StateResponse)

        # Suppress type errors
        resp = cast(StateResponse, resp)

        self.assertEqual(resp.target_temperature, 21.0)
        self.assertEqual(resp.indoor_temperature, 21.0)
        self.assertEqual(resp.outdoor_temperature, 28.5)

    def test_message_additional_precision(self) -> None:
        """Test decoding of temperatures with higher precision."""
        # Messages with additional temperature precision bits
        TEST_MESSAGES = {
            # https://github.com/mill1000/midea-msmart/issues/89#issuecomment-1783316836
            (24.0, 24.6, 9.5): bytes.fromhex(
                "aa23ac00000000000203c00188647f7f000000000063450c0056190000000000000497c3"),
            # https://github.com/mill1000/midea-msmart/issues/89#issuecomment-1782352164
            (24.0, 26.5, 9.7): bytes.fromhex(
                "aa23ac00000000000203c00188647f7f000000000067450c00750000000000000001a3b0"),
            (24.0, 25.0, 9.5): bytes.fromhex(
                "aa23ac00000000000203c00188647f7f000080000064450c00501d00000000000001508e"),
        }

        for targets, message in TEST_MESSAGES.items():
            # Create response from the message
            resp = self._test_response(message)

            # Assert response is a state response
            self.assertEqual(type(resp), StateResponse)

            # Suppress type errors
            resp = cast(StateResponse, resp)

            target, indoor, outdoor = targets

            self.assertEqual(resp.target_temperature, target)
            self.assertEqual(resp.indoor_temperature, indoor)
            self.assertEqual(resp.outdoor_temperature, outdoor)

        # Raw responses with additional temperature precision bits
        TEST_RESPONSES = {
            # https://github.com/mill1000/midea-ac-py/issues/39#issuecomment-1729884851
            # Corrected target values from user reported values
            (16.0, 23.2, 18.4): bytes.fromhex("c00181667f7f003c00000060560400420000000000000048"),
            (16.5, 23.4, 18.4): bytes.fromhex("c00191667f7f003c00000060560400440000000000000049"),
            (17.0, 23.6, 18.3): bytes.fromhex("c00181667f7f003c0000006156050036000000000000004a"),
            (17.5, 23.8, 18.2): bytes.fromhex("c00191667f7f003c0000006156050028000000000000004b"),
            (18.0, 23.8, 18.2): bytes.fromhex("c00182667f7f003c0000006156060028000000000000004c"),
            (18.5, 23.8, 18.2): bytes.fromhex("c00192667f7f003c0000006156060028000000000000004d"),
            (19.0, 23.8, 18.2): bytes.fromhex("c00183667f7f003c0000006156070028000000000000004e"),
            (19.5, 23.5, 18.5): bytes.fromhex("c00193667f7f003c00000061570700550000000000000050"),
        }

        for targets, payload in TEST_RESPONSES.items():
            # Create response
            with memoryview(payload) as mv_payload:
                resp = StateResponse(mv_payload)

            # Assert that it exists
            self.assertIsNotNone(resp)

            # Assert response is a state response
            self.assertEqual(type(resp), StateResponse)

            # Suppress type errors
            resp = cast(StateResponse, resp)

            target, indoor, outdoor = targets

            self.assertEqual(resp.target_temperature, target)
            self.assertEqual(resp.indoor_temperature, indoor)
            self.assertEqual(resp.outdoor_temperature, outdoor)

    def test_target_temperature(self) -> None:
        """Test decoding of target temperature from a variety of state responses."""
        TEST_PAYLOADS = {
            # https://github.com/mill1000/midea-ac-py/issues/39#issuecomment-1729884851
            # Corrected target values from user reported values
            16.0: bytes.fromhex("c00181667f7f003c00000060560400420000000000000048"),
            16.5: bytes.fromhex("c00191667f7f003c00000060560400440000000000000049"),
            17.0: bytes.fromhex("c00181667f7f003c0000006156050036000000000000004a"),
            17.5: bytes.fromhex("c00191667f7f003c0000006156050028000000000000004b"),
            18.0: bytes.fromhex("c00182667f7f003c0000006156060028000000000000004c"),
            18.5: bytes.fromhex("c00192667f7f003c0000006156060028000000000000004d"),
            19.0: bytes.fromhex("c00183667f7f003c0000006156070028000000000000004e"),
            19.5: bytes.fromhex("c00193667f7f003c00000061570700550000000000000050"),

            # Midea U-Shaped
            16.0: bytes.fromhex("c00040660000003c00000062680400000000000000000004"),
            16.5: bytes.fromhex("c00050660000003c00000062670400000000000000000004"),
        }

        for target, payload in TEST_PAYLOADS.items():
            # Create response
            with memoryview(payload) as mv_payload:
                resp = StateResponse(mv_payload)

            # Assert that it exists
            self.assertIsNotNone(resp)

            # Assert response is a state response
            self.assertEqual(type(resp), StateResponse)

            # Suppress type errors
            resp = cast(StateResponse, resp)

            # Assert that expected target temperature matches
            self.assertEqual(resp.target_temperature, target)


class TestCapabilitiesResponse(_TestResponseBase):
    """Test device capabilities response messages."""

    # Properties expected in capabilities responses
    EXPECTED_ATTRS = [
        "anion",
        "fan_silent", "fan_low", "fan_medium", "fan_high", "fan_auto", "fan_custom",
        "breeze_away", "breeze_control", "breezeless", "cascade",
        "swing_horizontal_angle", "swing_vertical_angle",
        "swing_horizontal", "swing_vertical", "swing_both",
        "dry_mode", "cool_mode", "heat_mode", "auto_mode",
        "aux_heat_mode", "aux_mode", "aux_electric_heat",
        "eco", "ieco", "turbo", "freeze_protection",
        "display_control", "filter_reminder",
        "min_temperature", "max_temperature",
        "energy_stats", "humidity", "target_humidity", "self_clean",
        "rate_select_levels",
    ]

    def test_properties(self) -> None:
        """Test that the capabilities response has the expected properties."""

        # Construct a response from a dummy payload with no caps
        with memoryview(b"\xb5\x00") as data:
            resp = CapabilitiesResponse(data)
        self.assertIsNotNone(resp)

        # Check that the object has all the expected properties
        self._test_check_attributes(resp, self.EXPECTED_ATTRS)

    def test_capabilities_parsers(self) -> None:
        """Test the generic capabilities parsers. e.g. bool, get_value"""

        def _build_capability_response(cap, value) -> CapabilitiesResponse:
            data = b"\xBA\x01" + \
                cap.to_bytes(2, "little") + b"\x01" + bytes([value])
            with memoryview(data) as mv_data:
                resp = CapabilitiesResponse(mv_data)
            self.assertIsNotNone(resp)
            return resp

        # Test BREEZELESS capability which uses a get_value parser. e.g. X == 1
        self.assertEqual(_build_capability_response(
            CapabilityId.BREEZELESS, 0)._capabilities["breezeless"], False)
        self.assertEqual(_build_capability_response(
            CapabilityId.BREEZELESS, 1)._capabilities["breezeless"], True)
        self.assertEqual(_build_capability_response(
            CapabilityId.BREEZELESS, 100)._capabilities["breezeless"], False)

        # Test PRESET_ECO capability which uses an array parser
        resp = _build_capability_response(CapabilityId.PRESET_ECO, 0)
        self.assertEqual(resp._capabilities["eco"], False)

        resp = _build_capability_response(CapabilityId.PRESET_ECO, 1)
        self.assertEqual(resp._capabilities["eco"], True)

        resp = _build_capability_response(CapabilityId.PRESET_ECO, 2)
        self.assertEqual(resp._capabilities["eco"], True)

        # Test PRESET_TURBO capability which uses 2 custom parsers.
        # e.g. turbo_heat -> X == 1 or X == 3, turbo_cool -> X < 2
        resp = _build_capability_response(CapabilityId.PRESET_TURBO, 0)
        self.assertEqual(resp._capabilities["turbo_heat"], False)
        self.assertEqual(resp._capabilities["turbo_cool"], True)

        resp = _build_capability_response(CapabilityId.PRESET_TURBO, 1)
        self.assertEqual(resp._capabilities["turbo_heat"], True)
        self.assertEqual(resp._capabilities["turbo_cool"], True)

        resp = _build_capability_response(CapabilityId.PRESET_TURBO, 3)
        self.assertEqual(resp._capabilities["turbo_heat"], True)
        self.assertEqual(resp._capabilities["turbo_cool"], False)

        resp = _build_capability_response(CapabilityId.PRESET_TURBO, 4)
        self.assertEqual(resp._capabilities["turbo_heat"], False)
        self.assertEqual(resp._capabilities["turbo_cool"], False)

    def test_capabilities(self) -> None:
        """Test that we decode capabilities responses as expected."""
        # https://github.com/mill1000/midea-ac-py/issues/13#issuecomment-1657485359
        # Identical payload received in https://github.com/mill1000/midea-msmart/issues/88#issuecomment-1781972832

        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa29ac00000000000303b5071202010113020101140201011502010116020101170201001a020101dedb")
        resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
        resp = cast(CapabilitiesResponse, resp)

        EXPECTED_RAW_CAPABILITIES = {
            "eco": True,
            "freeze_protection": True, "heat_mode": True,
            "cool_mode": True, "dry_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "auto_mode": True,
            "swing_horizontal": True, "swing_vertical": True,
            "energy_stats": False, "energy_setting": False, "energy_bcd": False,
            "filter_notice": False, "filter_clean": False,
            "turbo_heat": True, "turbo_cool": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": False,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": False, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": True, "swing_vertical": True,
            "swing_both": True,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "turbo": True, "freeze_protection": True,
            "display_control": False, "filter_reminder": False,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, False)

    def test_capabilities_2(self) -> None:
        """Test that we decode capabilities responses as expected."""
        # https://github.com/mac-zhou/midea-ac-py/pull/177#issuecomment-1259772244
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa3dac00000000000203b50a12020101180001001402010115020101160201001a020101100201011f020100250207203c203c203c00400001000100c83a")

        # Test case includes an unknown capability 0x40 that generates a warning
        with self.assertLogs("msmart", logging.DEBUG) as log:
            resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
            resp = cast(CapabilitiesResponse, resp)

            # Check debug message is generated for ID 0x0040
            self.assertRegex("\n".join(log.output),
                             "Ignored unknown capability ID: 0x0040")

        EXPECTED_RAW_CAPABILITIES = {
            "eco": True, "breezeless": False,
            "heat_mode": True, "cool_mode": True, "dry_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "auto_mode": True, "swing_horizontal": True, "swing_vertical": True,
            "energy_stats": False, "energy_setting": False, "energy_bcd": False,
            "turbo_heat": True, "turbo_cool": True,
            "fan_custom": True, "fan_silent": False, "fan_low": False,
            "fan_medium": False,  "fan_high": False, "fan_auto": False,
            "humidity_auto_set": False, "humidity_manual_set": False,
            "cool_min_temperature": 16.0, "cool_max_temperature": 30.0,
            "auto_min_temperature": 16.0, "auto_max_temperature": 30.0,
            "heat_min_temperature": 16.0, "heat_max_temperature": 30.0,
            "decimals": False
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": True,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": True, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": True, "swing_vertical": True,
            "swing_both": True,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "turbo": True, "freeze_protection": False,
            "display_control": False, "filter_reminder": False,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

    def test_capabilities_3(self) -> None:
        """Test that we decode capabilities responses as expected."""
        # Toshiba Smart Window Unit (2019)
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa29ac00000000000303b507120201021402010015020102170201021a0201021002010524020101990d")
        resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
        resp = cast(CapabilitiesResponse, resp)

        EXPECTED_RAW_CAPABILITIES = {
            "eco": True, "heat_mode": False,
            "cool_mode": True, "dry_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "swing_horizontal": False, "swing_vertical": False,
            "filter_notice": True, "filter_clean": False, "turbo_heat": False,
            "turbo_cool": False,
            "fan_custom": False, "fan_silent": False, "fan_low": True,
            "fan_medium": True,  "fan_high": True, "fan_auto": True,
            "display_control": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": False,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": False, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": False, "swing_vertical": False,
            "swing_both": False,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": False, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "turbo": False, "freeze_protection": False,
            "display_control": True, "filter_reminder": True,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, False)

    def test_capabilities_4(self) -> None:
        """Test that we decode capabilities responses as expected."""
        # Midea U-shaped Window Unit (2022)
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa39ac00000000000303b50912020102130201001402010015020100170201021a02010010020101250207203c203c203c00240201010102a1a0")
        resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
        resp = cast(CapabilitiesResponse, resp)

        EXPECTED_RAW_CAPABILITIES = {
            "eco": True, "freeze_protection": False,
            "heat_mode": False, "cool_mode": True, "dry_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "swing_horizontal": False, "swing_vertical": True, "filter_notice": True,
            "filter_clean": False, "turbo_heat": False, "turbo_cool": True,
            "fan_custom": True, "fan_silent": False, "fan_low": False,
            "fan_medium": False,  "fan_high": False, "fan_auto": False,
            "cool_min_temperature": 16.0, "cool_max_temperature": 30.0,
            "auto_min_temperature": 16.0, "auto_max_temperature": 30.0,
            "heat_min_temperature": 16.0, "heat_max_temperature": 30.0,
            "decimals": False, "display_control": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": True,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": True, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": False, "swing_vertical": True,
            "swing_both": False,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": False, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "turbo": True, "freeze_protection": False,
            "display_control": True, "filter_reminder": True,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

    def test_additional_capabilities(self) -> None:
        self.maxDiff = None
        """Test that we decode capabilities and additional capabilities responses as expected."""
        # https://github.com/mill1000/midea-ac-py/issues/60#issuecomment-1867498321
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa3dac00000000000303b50a12020101430001011402010115020101160201001a020101100201011f020103250207203c203c203c05400001000100c805")

        # Test case includes an unknown capability 0x40 that generates a log
        with self.assertLogs("msmart", logging.DEBUG) as log:
            resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
            resp = cast(CapabilitiesResponse, resp)

            # Check debug message is generated for ID 0x0040
            self.assertRegex("\n".join(log.output),
                             "Ignored unknown capability ID: 0x0040")

        EXPECTED_RAW_CAPABILITIES = {
            "eco": True,
            "breeze_control": True,
            "heat_mode": True, "cool_mode": True, "dry_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "swing_horizontal": True, "swing_vertical": True,
            "energy_stats": False, "energy_setting": False, "energy_bcd": False,
            "turbo_heat": True, "turbo_cool": True,
            "fan_silent": False, "fan_low": False, "fan_medium": False, "fan_high": False, "fan_auto": False, "fan_custom": True,
            "humidity_auto_set": False, "humidity_manual_set": True,
            "cool_min_temperature": 16.0, "cool_max_temperature": 30.0,
            "auto_min_temperature": 16.0, "auto_max_temperature": 30.0,
            "heat_min_temperature": 16.0, "heat_max_temperature": 30.0,
            "decimals": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

        # Additional capabilities response
        TEST_ADDITIONAL_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa23ac00000000000303b5051e020101130201012202010019020100390001010000febe")
        additional_resp = self._test_build_response(
            TEST_ADDITIONAL_CAPABILITIES_RESPONSE)
        additional_resp = cast(CapabilitiesResponse, additional_resp)

        EXPECTED_ADDITIONAL_RAW_CAPABILITIES = {
            "freeze_protection": True,
            "fahrenheit": True,
            "aux_electric_heat": False,
            "self_clean": True,
            "anion": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(additional_resp._capabilities,
                         EXPECTED_ADDITIONAL_RAW_CAPABILITIES)

        # Ensure the additional capabilities response doesn't also want more capabilities
        self.assertEqual(additional_resp.additional_capabilities, False)

        # Check that merging the capabilities produced expected results
        resp.merge(additional_resp)

        EXPECTED_MERGED_RAW_CAPABILITIES = {
            "eco": True,
            "breeze_control": True,
            "heat_mode": True, "cool_mode": True, "dry_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "swing_horizontal": True, "swing_vertical": True,
            "energy_stats": False, "energy_setting": False, "energy_bcd": False,
            "turbo_heat": True, "turbo_cool": True,
            "fan_silent": False, "fan_low": False, "fan_medium": False, "fan_high": False, "fan_auto": False, "fan_custom": True,
            "humidity_auto_set": False, "humidity_manual_set": True,
            "cool_min_temperature": 16.0, "cool_max_temperature": 30.0,
            "auto_min_temperature": 16.0, "auto_max_temperature": 30.0,
            "heat_min_temperature": 16.0, "heat_max_temperature": 30.0,
            "decimals": True,
            "freeze_protection": True,
            "fahrenheit": True,
            "aux_electric_heat": False,
            "self_clean": True,
            "anion": True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_MERGED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": True, "fan_silent": True,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": True, "breeze_away": False,
            "breeze_control": True, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": True, "swing_vertical": True,
            "swing_both": True,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "turbo": True, "freeze_protection": True,
            "display_control": False, "filter_reminder": False,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": True,
            "target_humidity": True, "self_clean": True,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

    def test_capabilities_aux_heat(self) -> None:
        """Test that we decode capabilities that include aux heating support."""
        self.maxDiff = None

        # https://github.com/mill1000/midea-ac-py/issues/297#issuecomment-2622720960
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa29ac00000000000303b50514020109150201021a020101250207203c203c203c003402010101007b1d")

        # Test case includes an unknown capability 0x40 that generates a log
        with self.assertLogs("msmart", logging.DEBUG) as log:
            resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
            resp = cast(CapabilitiesResponse, resp)

            # Check debug message is generated for some unsupported capabilities
            self.assertRegex("\n".join(log.output),
                             "Unsupported capability <CapabilityId.BODY_CHECK: 564>, Size: 1.")

        EXPECTED_RAW_CAPABILITIES = {
            'heat_mode': True, 'cool_mode': True, 'dry_mode': True, 'auto_mode': True,
            "aux_heat_mode": True, "aux_mode": True,
            'swing_horizontal': False, 'swing_vertical': False,
            'turbo_heat': True, 'turbo_cool': True,
            'cool_min_temperature': 16.0,
            'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0,
            'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0,
            'heat_max_temperature': 30.0,
            'decimals': False
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

        # Additional capabilities response
        TEST_ADDITIONAL_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa2fac00000000000303b508100201051f020100300001001302010019020101390001009300010194000101000095ca")

        # Test case includes an unknown capability 0x40 that generates a log
        with self.assertLogs("msmart", logging.DEBUG) as log:
            additional_resp = self._test_build_response(
                TEST_ADDITIONAL_CAPABILITIES_RESPONSE)
            additional_resp = cast(CapabilitiesResponse, additional_resp)

            # Check debug message is generated for some unsupported capabilities
            self.assertRegex("\n".join(log.output),
                             "Unsupported capability <CapabilityId.EMERGENT_HEAT_WIND: 147>, Size: 1.")

            self.assertRegex("\n".join(log.output),
                             "Unsupported capability <CapabilityId.HEAT_PTC_WIND: 148>, Size: 1.")

        EXPECTED_ADDITIONAL_RAW_CAPABILITIES = {
            'fan_silent': False, 'fan_low': True, 'fan_medium': True, 'fan_high': True, 'fan_auto': True, 'fan_custom': False,
            'humidity_auto_set': False, 'humidity_manual_set': False,
            'smart_eye': False, 'freeze_protection': False,
            'aux_electric_heat': True, 'self_clean': False
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(additional_resp._capabilities,
                         EXPECTED_ADDITIONAL_RAW_CAPABILITIES)

        # Ensure the additional capabilities response doesn't also want more capabilities
        self.assertEqual(additional_resp.additional_capabilities, False)

        # Check that merging the capabilities produced expected results
        resp.merge(additional_resp)

        EXPECTED_MERGED_RAW_CAPABILITIES = {
            'heat_mode': True, 'cool_mode': True, 'dry_mode': True, 'auto_mode': True,
            "aux_heat_mode": True, "aux_mode": True,
            'swing_horizontal': False, 'swing_vertical': False,
            'turbo_heat': True, 'turbo_cool': True,
            'cool_min_temperature': 16.0,
            'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0,
            'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0,
            'heat_max_temperature': 30.0,
            'decimals': False,
            'fan_silent': False, 'fan_low': True, 'fan_medium': True, 'fan_high': True, 'fan_auto': True, 'fan_custom': False,
            'humidity_auto_set': False, 'humidity_manual_set': False,
            'smart_eye': False, 'freeze_protection': False,
            'aux_electric_heat': True, 'self_clean': False
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_MERGED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": False,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": False, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": False, "swing_vertical": False,
            "swing_both": False,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": True, "auto_mode": True,
            "aux_heat_mode": True, "aux_mode": True,
            "aux_electric_heat": True,
            "eco": False, "ieco": False,
            "turbo": True, "freeze_protection": False,
            "display_control": False, "filter_reminder": False,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

    def test_capabilities_jet_cool(self) -> None:
        """Test that we decode capabilities that include jet cool support."""
        self.maxDiff = None

        # https://github.com/mill1000/midea-ac-py/issues/343#issuecomment-2864149742
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa39ac00000000000303b5091202010214020100150201001e020100170201021a02010210020101250207203c203c203c002402010101019b9a")

        resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
        resp = cast(CapabilitiesResponse, resp)

        EXPECTED_RAW_CAPABILITIES = {
            'eco': True, 'heat_mode': False,
            'cool_mode': True, 'dry_mode': True,
            'auto_mode': True, 'aux_heat_mode': False,
            'aux_mode': False, 'swing_horizontal': False,
            'swing_vertical': True, 'anion': False,
            'filter_notice': True, 'filter_clean': False,
            'turbo_heat': False, 'turbo_cool': False,
            'fan_silent': False, 'fan_low': False,
            'fan_medium': False, 'fan_high': False,
            'fan_auto': False, 'fan_custom': True,
            'cool_min_temperature': 16.0, 'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0, 'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0, 'heat_max_temperature': 30.0,
            'decimals': False, 'display_control': True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

        # Additional capabilities response
        TEST_ADDITIONAL_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa27ac00000000000303b5051f0201002c020101670001011602010451000101e30001010004f564")

        # Test case includes an unsupported capability
        with self.assertLogs("msmart", logging.DEBUG) as log:
            additional_resp = self._test_build_response(
                TEST_ADDITIONAL_CAPABILITIES_RESPONSE)
            additional_resp = cast(CapabilitiesResponse, additional_resp)

            # Check debug message is generated for some unsupported capabilities
            self.assertRegex("\n".join(log.output),
                             "Unsupported capability <CapabilityId.PARENT_CONTROL: 81>, Size: 1.")

        EXPECTED_ADDITIONAL_RAW_CAPABILITIES = {
            'humidity_auto_set': False, 'humidity_manual_set': False,
            'jet_cool': True,
            'buzzer': True, 'energy_stats': True,
            'energy_setting': False, 'energy_bcd': False,
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(additional_resp._capabilities,
                         EXPECTED_ADDITIONAL_RAW_CAPABILITIES)

        # Ensure the additional capabilities response doesn't also want more capabilities
        self.assertEqual(additional_resp.additional_capabilities, False)

        # Check that merging the capabilities produced expected results
        resp.merge(additional_resp)

        EXPECTED_MERGED_RAW_CAPABILITIES = {
            'eco': True, 'heat_mode': False,
            'cool_mode': True, 'dry_mode': True,
            'auto_mode': True, 'aux_heat_mode': False,
            'aux_mode': False, 'swing_horizontal': False,
            'swing_vertical': True, 'anion': False,
            'filter_notice': True, 'filter_clean': False,
            'turbo_heat': False, 'turbo_cool': False,
            'fan_silent': False, 'fan_low': False,
            'fan_medium': False, 'fan_high': False,
            'fan_auto': False, 'fan_custom': True,
            'cool_min_temperature': 16.0, 'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0, 'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0, 'heat_max_temperature': 30.0,
            'decimals': False, 'display_control': True,
            'humidity_auto_set': False, 'humidity_manual_set': False,
            'jet_cool': True,
            'buzzer': True, 'energy_stats': True,
            'energy_setting': False, 'energy_bcd': False
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_MERGED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": False, "fan_silent": True,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": True, "breeze_away": False,
            "breeze_control": False, "breezeless": False, "cascade": False,
            "swing_horizontal_angle": False, "swing_vertical_angle": False,
            "swing_horizontal": False, "swing_vertical": True,
            "swing_both": False,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": False, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "jet_cool": True, "turbo": False,
            "freeze_protection": False,
            "display_control": True, "filter_reminder": True,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": True, "humidity": False,
            "target_humidity": False, "self_clean": False,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)

    def test_capabilities_cascade(self) -> None:
        """Test that we decode capabilities that include cascade support."""
        self.maxDiff = None

        # https://github.com/mill1000/midea-ac-py/issues/359#issuecomment-3028509967
        TEST_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa3dac00000000000303b50a12020101430001001402010115020101160201001a020101100201011f020103250207203c203c203c05400001000100e1ed")

        resp = self._test_build_response(TEST_CAPABILITIES_RESPONSE)
        resp = cast(CapabilitiesResponse, resp)

        EXPECTED_RAW_CAPABILITIES = {
            'eco': True, 'heat_mode': True,
            'cool_mode': True, 'dry_mode': True,
            'auto_mode': True, 'aux_heat_mode': False,
            'aux_mode': False, 'breeze_control': False,
            'swing_horizontal': True, 'swing_vertical': True,
            'turbo_heat': True, 'turbo_cool': True,
            'fan_silent': False, 'fan_low': False,
            'fan_medium': False, 'fan_high': False,
            'fan_auto': False, 'fan_custom': True,
            'humidity_auto_set': False, 'humidity_manual_set': True,
            'cool_min_temperature': 16.0, 'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0, 'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0, 'heat_max_temperature': 30.0,
            'decimals': True,
            'energy_bcd': False, 'energy_setting': False, 'energy_stats': False,
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_RAW_CAPABILITIES)

        # Check if there are additional capabilities
        self.assertEqual(resp.additional_capabilities, True)

        # Additional capabilities response
        TEST_ADDITIONAL_CAPABILITIES_RESPONSE = bytes.fromhex(
            "aa3bac00000000000303b50a1e02010113020101220201001902010039000101580001024200010159000101090001010a000101000000000000cfbf")

        # Test case includes an unsupported capability
        with self.assertLogs("msmart", logging.DEBUG) as log:
            additional_resp = self._test_build_response(
                TEST_ADDITIONAL_CAPABILITIES_RESPONSE)
            additional_resp = cast(CapabilitiesResponse, additional_resp)

            # Check debug message is generated for some unsupported capabilities
            self.assertRegex("\n".join(log.output),
                             "Unsupported capability <CapabilityId.PREVENT_STRAIGHT_WIND_SELECT: 88>, Size: 1.")

        EXPECTED_ADDITIONAL_RAW_CAPABILITIES = {
            'anion': True, 'aux_electric_heat': False,
            'breeze_away': True, 'cascade': True,
            'fahrenheit': True, 'freeze_protection': True, 'self_clean': True,
            'swing_horizontal_angle': True, 'swing_vertical_angle': True
        }

        # Ensure raw decoded capabilities match
        self.assertEqual(additional_resp._capabilities,
                         EXPECTED_ADDITIONAL_RAW_CAPABILITIES)

        # Ensure the additional capabilities response doesn't also want more capabilities
        self.assertEqual(additional_resp.additional_capabilities, False)

        # Check that merging the capabilities produced expected results
        resp.merge(additional_resp)

        EXPECTED_MERGED_RAW_CAPABILITIES = {
            'eco': True, 'heat_mode': True,
            'cool_mode': True, 'dry_mode': True,
            'auto_mode': True, 'aux_heat_mode': False,
            'aux_mode': False, 'swing_horizontal': True,
            'swing_vertical': True, 'anion': True,
            'turbo_heat': True, 'turbo_cool': True,
            'fan_silent': False, 'fan_low': False,
            'fan_medium': False, 'fan_high': False,
            'fan_auto': False, 'fan_custom': True,
            'cool_min_temperature': 16.0, 'cool_max_temperature': 30.0,
            'auto_min_temperature': 16.0, 'auto_max_temperature': 30.0,
            'heat_min_temperature': 16.0, 'heat_max_temperature': 30.0,
            'decimals': True,
            'humidity_auto_set': False, 'humidity_manual_set': True,
            'energy_stats': False, 'energy_setting': False, 'energy_bcd': False,
            'aux_electric_heat': False,
            'breeze_control': False,
            'breeze_away': True, 'cascade': True,
            'fahrenheit': True, 'freeze_protection': True, 'self_clean': True,
            'swing_horizontal_angle': True, 'swing_vertical_angle': True
        }
        # Ensure raw decoded capabilities match
        self.assertEqual(resp._capabilities, EXPECTED_MERGED_RAW_CAPABILITIES)

        EXPECTED_CAPABILITIES = {
            "anion": True, "fan_silent": True,
            "fan_low": True, "fan_medium": True,
            "fan_high": True, "fan_auto": True,
            "fan_custom": True, "breeze_away": True,
            "breeze_control": False, "breezeless": False, "cascade": True,
            "swing_horizontal_angle": True, "swing_vertical_angle": True,
            "swing_horizontal": True, "swing_vertical": True,
            "swing_both": True,
            "dry_mode": True, "cool_mode": True,
            "heat_mode": True, "auto_mode": True,
            "aux_heat_mode": False, "aux_mode": False,
            "aux_electric_heat": False,
            "eco": True, "ieco": False,
            "jet_cool": True, "turbo": True,
            "freeze_protection": True,
            "display_control": False, "filter_reminder": False,
            "min_temperature": 16.0, "max_temperature": 30.0,
            "energy_stats": False, "humidity": True,
            "target_humidity": True, "self_clean": True,
            "rate_select_levels": None,
        }
        # Check capabilities properties match
        for prop in self.EXPECTED_ATTRS:
            self.assertEqual(getattr(resp, prop),
                             EXPECTED_CAPABILITIES[prop], prop)


class TestGetPropertiesCommand(unittest.TestCase):

    def test_payload(self) -> None:
        """Test that we encode properties payloads correctly."""
        # TODO this test is not based on a real world sample
        PROPS = [PropertyId.INDOOR_HUMIDITY, PropertyId.SWING_UD_ANGLE]

        # Build command
        command = GetPropertiesCommand(PROPS)

        # Fetch payload
        payload = command.tobytes()[10:-1]

        # Assert payload header looks correct
        self.assertEqual(payload[0], 0xB1)
        self.assertEqual(payload[1], len(PROPS))

        # Assert that property ID was packed correctly
        self.assertEqual(payload[2], PropertyId.INDOOR_HUMIDITY & 0xFF)
        self.assertEqual(payload[3], PropertyId.INDOOR_HUMIDITY >> 8 & 0xFF)


class TestSetPropertiesCommand(unittest.TestCase):

    def test_encode(self) -> None:
        """Test encoding of property values to bytes objects."""
        TEST_ENCODES = {
            # Breeze away: 0x02 - On, 0x01 - Off
            (PropertyId.BREEZE_AWAY, True): bytes([0x02]),
            (PropertyId.BREEZE_AWAY, False): bytes([0x01]),

            # Breezeless: Boolean
            (PropertyId.BREEZELESS, True): bytes([0x01]),
            (PropertyId.BREEZELESS, False): bytes([0x00]),

            # Breeze control: Passthru
            (PropertyId.BREEZE_CONTROL, 0x04): bytes([0x04]),
            (PropertyId.BREEZE_CONTROL, 0x00): bytes([0x00]),

            # IECO: 13 bytes ieco_frame, ieco_number, ieco_switch, ...
            (PropertyId.IECO, True): bytes([0, 1, 1]) + bytes(10),
            (PropertyId.IECO, False): bytes([0, 1, 0]) + bytes(10),

            # Cascade: 2 bytes wind_around, wind_around_ud
            (PropertyId.CASCADE, 0): bytes([0, 0]),
            (PropertyId.CASCADE, 1): bytes([1, 1]),
            (PropertyId.CASCADE, 2): bytes([1, 2]),
        }

        for (prop, value), expected_data in TEST_ENCODES.items():
            self.assertEqual(prop.encode(value), expected_data, msg=f"""Encode {
                             repr(prop)}, Value: {value}, Expected: {expected_data}""")

        # Validate "unsupported" properties raise exceptions
        with self.assertRaisesRegex(NotImplementedError, ".* encode is not supported."):
            PropertyId.ANION.encode(True)

    def test_payload(self) -> None:
        """Test that we encode set properties payloads correctly."""
        # TODO this test is not based on a real world sample
        PROPS = {PropertyId.SWING_UD_ANGLE: 25, PropertyId.SWING_LR_ANGLE: 75}

        # Build command
        command = SetPropertiesCommand(PROPS)

        # Fetch payload
        payload = command.tobytes()[10:-1]

        # Assert payload header looks correct
        self.assertEqual(payload[0], 0xB0)
        self.assertEqual(payload[1], len(PROPS))

        # Assert that property ID was packed correctly
        self.assertEqual(payload[2], PropertyId.SWING_UD_ANGLE & 0xFF)
        self.assertEqual(payload[3], PropertyId.SWING_UD_ANGLE >> 8 & 0xFF)

        # Assert length is correct and data is correct
        self.assertEqual(payload[4], 1)
        self.assertEqual(payload[5], PROPS[PropertyId.SWING_UD_ANGLE])


class TestPropertiesResponse(_TestResponseBase):
    """Test properties response messages."""

    def test_decode(self) -> None:
        """Test decoding of bytes objects to property values."""
        TEST_DECODES = {
            # Breeze away 0x02 - On, 0x01 - Off
            (PropertyId.BREEZE_AWAY, bytes([0x02])): True,
            (PropertyId.BREEZE_AWAY, bytes([0x01])): False,

            # Breezeless: Boolean
            (PropertyId.BREEZELESS, bytes([0x01])): True,
            (PropertyId.BREEZELESS, bytes([0x00])): False,
            (PropertyId.BREEZELESS, bytes([0x02])): True,

            # Breeze control: Passthru
            (PropertyId.BREEZE_CONTROL, bytes([0x04])): 0x04,
            (PropertyId.BREEZE_CONTROL, bytes([0x00])): 0x00,

            # Buzzer: Don't decode
            (PropertyId.BUZZER, bytes([0x00])): None,

            # IECO: 2 bytes
            (PropertyId.IECO, bytes([0x00, 0x00])): False,
            (PropertyId.IECO, bytes([0x00, 0x01])): True,

            # Cascade: 2 bytes
            (PropertyId.CASCADE, bytes([0x00, 0x00])): 0,
            (PropertyId.CASCADE, bytes([0x01, 0x01])): 1,
            (PropertyId.CASCADE, bytes([0x01, 0x02])): 2,
        }

        for (prop, data), expected_value in TEST_DECODES.items():
            self.assertEqual(prop.decode(data), expected_value, msg=f"""Decode {
                             repr(prop)}, Data: {data}, Expected: {expected_value}""")

        # Validate "unsupported" properties raise exceptions
        with self.assertRaisesRegex(NotImplementedError, ".* decode is not supported."):
            PropertyId.INDOOR_HUMIDITY.decode(bytes([1]))

    def test_properties_parsing(self) -> None:
        """Test we decode properties responses correctly."""
        # https://github.com/mill1000/midea-ac-py/issues/60#issuecomment-1936976587
        TEST_RESPONSE = bytes.fromhex(
            "aa21ac00000000000303b10409000001000a00000100150000012b1e020000005fa3")

        # Response contains an unsupported property so check the log for warnings
        with self.assertLogs("msmart", logging.WARNING) as log:
            resp = self._test_build_response(TEST_RESPONSE)

            self.assertRegex("\n".join(log.output),
                             "Unsupported property .*INDOOR_HUMIDITY.*")

        # Assert response is a correct type
        self.assertEqual(type(resp), PropertiesResponse)
        resp = cast(PropertiesResponse, resp)

        EXPECTED_RAW_PROPERTIES = {
            PropertyId.SWING_LR_ANGLE: 0,
            PropertyId.SWING_UD_ANGLE: 0,
        }
        # Ensure raw decoded properties match
        self.assertEqual(resp._properties, EXPECTED_RAW_PROPERTIES)

        # Check state
        self.assertEqual(resp.get_property(PropertyId.SWING_LR_ANGLE), 0)
        self.assertEqual(resp.get_property(PropertyId.SWING_UD_ANGLE), 0)

    def test_properties_ack(self) -> None:
        """Test we decode an acknowledgement from a set properties command correctly."""
        # https://github.com/mill1000/midea-msmart/issues/97#issuecomment-1949495900
        TEST_RESPONSE = bytes.fromhex(
            "aa18ac00000000000302b0020a0000013209001101000089a4")

        # Device did not support SWING_UD_ANGLE, check that an error was reported
        with self.assertLogs("msmart", logging.WARNING) as log:
            resp = self._test_build_response(TEST_RESPONSE)
            resp = cast(PropertiesResponse, resp)

            self.assertRegex(
                log.output[0], "Property .*SWING_UD_ANGLE.* failed, Result: 0x11.")

        # Assert response is a correct type
        self.assertEqual(type(resp), PropertiesResponse)

        EXPECTED_RAW_PROPERTIES = {
            PropertyId.SWING_LR_ANGLE: 50,
            PropertyId.SWING_UD_ANGLE: 0,
        }
        # Ensure raw decoded properties match
        self.assertEqual(resp._properties, EXPECTED_RAW_PROPERTIES)

        # Check state
        self.assertEqual(resp.get_property(PropertyId.SWING_LR_ANGLE), 50)
        self.assertEqual(resp.get_property(PropertyId.SWING_UD_ANGLE), 0)

    def test_properties_notify(self) -> None:
        """Test we ignore property notifications."""
        # https://github.com/mill1000/midea-msmart/issues/122
        TEST_RESPONSE = bytes.fromhex(
            "aa1aac00000000000205b50310060101090001010a000101dcbcb4")

        resp = self._test_build_response(TEST_RESPONSE)

        # Assert response is generic
        self.assertEqual(type(resp), Response)

    def test_properties_unknown_and_invalid(self) -> None:
        """Test we warn when decoding unknown properties and that invalid properties are not stored."""
        # https://github.com/mill1000/midea-ac-py/issues/128#issuecomment-2098342003
        TEST_RESPONSE = bytes.fromhex(
            "aa1bac00000000000202b0021e001004001000001a00000100000e18")

        with self.assertLogs("msmart", logging.WARNING) as log:
            resp = self._test_build_response(TEST_RESPONSE)
            resp = cast(PropertiesResponse, resp)

            # Check warning is generated for ID 0x001E
            self.assertRegex(log.output[0], "Unknown property ID 0x001E")

        # Assert response is a correct type
        self.assertEqual(type(resp), PropertiesResponse)

        # Assert that the buzzer property is not decoded
        self.assertIsNone(resp.get_property(PropertyId.BUZZER))

    def test_properties_execution_failed(self) -> None:
        """Test we error when decoding properties that had an execution error."""
        # https://github.com/mill1000/midea-msmart/issues/161#issuecomment-2282839178
        TEST_RESPONSE = bytes.fromhex(
            "aa18ac00000000000302b00243001101041a00000100002ce5")

        with self.assertLogs("msmart", logging.WARNING) as log:
            resp = self._test_build_response(TEST_RESPONSE)
            resp = cast(PropertiesResponse, resp)

            self.assertRegex(
                log.output[0], "Property .*BREEZE_CONTROL.* failed, Result: 0x11.")

        # Assert response is a correct type
        self.assertEqual(type(resp), PropertiesResponse)


class TestResponseConstruct(_TestResponseBase):
    """Test construction of responses from raw data."""

    def test_invalid_checksum(self) -> None:
        """Test that invalid checksums raise exceptions."""
        TEST_RESPONSE_BAD_CHECKSUM = bytes.fromhex(
            "aa14ac00000000000303b10109000001003c0000FF")

        with self.assertRaises(InvalidFrameException):
            Response.construct(TEST_RESPONSE_BAD_CHECKSUM)

    def test_properties_response_invalid_crc(self) -> None:
        """Test that PropertiesResponses with invalid CRCs are accepted."""
        # PropertiesResponse with invalid CRC
        # https://github.com/mill1000/midea-ac-py/issues/101#issuecomment-1994824924
        TEST_RESPONSE_PROPERTIES_BAD_CRC = bytes.fromhex(
            "aa14ac00000000000303b10109000001003c000042")
        # Mocked up StateResponse with invalid CRC
        TEST_RESPONSE_STATE_BAD_CRC = bytes.fromhex(
            "aa22ac00000000000303c0014566000000300010045eff00000000000000000069aa0c")

        # Assert that constructing a StateResponse with invalid CRC raises an exception
        with self.assertRaises(InvalidResponseException):
            resp = Response.construct(TEST_RESPONSE_STATE_BAD_CRC)

        # Now construct a PropertiesResponse with an invalid CRC
        resp = Response.construct(TEST_RESPONSE_PROPERTIES_BAD_CRC)

        self.assertIsNotNone(resp)
        self.assertEqual(type(resp), PropertiesResponse)

    def test_short_packet(self) -> None:
        """Test that a short frame raise exceptions."""
        # https://github.com/mill1000/midea-msmart/issues/234#issuecomment-3299199631
        TEST_RESPONSE_SHORT_FRAME = bytes.fromhex("01000000")

        with self.assertRaises(InvalidFrameException):
            Response.construct(TEST_RESPONSE_SHORT_FRAME)

    def test_invalid_device_type(self) -> None:
        """Test that responses with an incorrect device type raise exceptions."""
        # https://github.com/mill1000/midea-ac-py/issues/374#issuecomment-3240831784
        TEST_RESPONSE_TYPE_CC = bytes.fromhex(
            "aa63cc0000000000000301fe00000043005000728c8000bc00728c728c808000010141ff010203000603010000000000000001000103010000000000000000000001000100010000000000000000000000000001000200000100000101000102ff02ffa2")

        with self.assertRaises(InvalidFrameException):
            Response.construct(TEST_RESPONSE_TYPE_CC)


class TestGroupDataResponse(_TestResponseBase):
    """Test group data response messages."""

    def test_energy_usage(self) -> None:
        """Test we decode energy usage responses correctly."""
        TEST_RESPONSES = {
            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2181633174
            (679.2, 0, 0): bytes.fromhex("aa1fac00000000000303c121014400067920000000000000000000000000aabf"),

            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2191412432
            (5650.02, 1514.0, 0): bytes.fromhex("aa20ac00000000000203c121014400564a02640000000014ae0000000000041a22"),

            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2218753545
            (None, None, None): bytes.fromhex("aa20ac00000000000303c1210144000000000000000000000000000000000843bc"),
        }

        for power, response in TEST_RESPONSES.items():
            resp = self._test_build_response(response)

            # Assert response is a correct type
            self.assertEqual(type(resp), EnergyUsageResponse)
            resp = cast(EnergyUsageResponse, resp)

            total, current, real_time = power

            self.assertEqual(resp.total_energy, total)
            self.assertEqual(resp.current_energy, current)
            self.assertEqual(resp.real_time_power, real_time)

    def test_binary_energy_usage(self) -> None:
        """Test we decode binary energy usage responses correctly."""
        TEST_RESPONSES = {
            # https://github.com/mill1000/midea-ac-py/issues/204#issuecomment-2314705021
            (150.4, .6, 279.5): bytes.fromhex("aa22ac00000000000803c1210144000005e00000000000000006000aeb000000487a5e"),

            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2218753545
            (None, None, None): bytes.fromhex("aa20ac00000000000303c1210144000000000000000000000000000000000843bc"),
        }

        for power, response in TEST_RESPONSES.items():
            resp = self._test_build_response(response)

            # Assert response is a correct type
            self.assertEqual(type(resp), EnergyUsageResponse)
            resp = cast(EnergyUsageResponse, resp)

            total, current, real_time = power

            self.assertEqual(resp.total_energy_binary, total)
            self.assertEqual(resp.current_energy_binary, current)
            self.assertEqual(resp.real_time_power_binary, real_time)

    def test_humidity(self) -> None:
        """Test we decode humidity responses correctly."""
        TEST_RESPONSES = {
            # Device supports humidity
            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2218019069
            63: bytes.fromhex("aa20ac00000000000303c12101453f546c005d0a000000de1f0000ba9a0004af9c"),

            # Device does not support humidity
            # https://github.com/mill1000/midea-msmart/pull/116#issuecomment-2192724566
            None: bytes.fromhex("aa1fac00000000000303c1210145000000000000000000000000000000001aed"),
        }

        for humidity, response in TEST_RESPONSES.items():
            resp = self._test_build_response(response)

            # Assert response is a correct type
            self.assertEqual(type(resp), HumidityResponse)
            resp = cast(HumidityResponse, resp)

            self.assertEqual(resp.humidity, humidity)


if __name__ == "__main__":
    unittest.main()
