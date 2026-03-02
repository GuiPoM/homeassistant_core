"""Tests for the require_acknowledgment feature in Google Assistant traits."""

import pytest

from homeassistant.components import light, lock, switch
from homeassistant.components.google_assistant import const, error, helpers, trait
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, State

from . import BASIC_CONFIG, MockConfig

from tests.common import async_mock_service

ACK_CONFIG = MockConfig(
    entity_config={
        "light.dimmer": {const.CONF_REQUIRE_ACK: True},
        "switch.test": {const.CONF_REQUIRE_ACK: True},
        "lock.door": {const.CONF_REQUIRE_ACK: True},
    }
)

ACK_DATA = helpers.RequestData(
    ACK_CONFIG,
    "test-agent",
    const.SOURCE_CLOUD,
    "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
    None,
)


async def test_brightness_require_acknowledgment(hass: HomeAssistant) -> None:
    """Test BrightnessTrait with require_acknowledgment enabled."""
    trt = trait.BrightnessTrait(
        hass,
        State("light.dimmer", light.STATE_ON, {light.ATTR_BRIGHTNESS: 243}),
        ACK_CONFIG,
    )

    calls = async_mock_service(hass, light.DOMAIN, light.SERVICE_TURN_ON)

    # No challenge data - should raise ChallengeNeeded with ack_needed=True
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(
            trait.COMMAND_BRIGHTNESS_ABSOLUTE, ACK_DATA, {"brightness": 50}, {}
        )
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.ack_needed is True
    assert err.value.challenge_type == const.CHALLENGE_ACK_NEEDED

    # With acknowledgment data - should execute successfully
    await trt.execute(
        trait.COMMAND_BRIGHTNESS_ABSOLUTE,
        ACK_DATA,
        {"brightness": 50},
        {"ack": True},
    )
    assert len(calls) == 1
    assert calls[0].data == {
        ATTR_ENTITY_ID: "light.dimmer",
        light.ATTR_BRIGHTNESS_PCT: 50,
    }


async def test_onoff_require_acknowledgment(hass: HomeAssistant) -> None:
    """Test OnOffTrait with require_acknowledgment enabled."""
    trt = trait.OnOffTrait(
        hass,
        State("switch.test", "on"),
        ACK_CONFIG,
    )

    calls = async_mock_service(hass, switch.DOMAIN, "turn_off")

    # No challenge data - should raise ChallengeNeeded with ack_needed=True
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(trait.COMMAND_ON_OFF, ACK_DATA, {"on": False}, {})
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.ack_needed is True
    assert err.value.challenge_type == const.CHALLENGE_ACK_NEEDED

    # With acknowledgment data - should execute successfully
    await trt.execute(
        trait.COMMAND_ON_OFF,
        ACK_DATA,
        {"on": False},
        {"ack": True},
    )
    assert len(calls) == 1


async def test_lockunlock_require_acknowledgment(hass: HomeAssistant) -> None:
    """Test LockUnlockTrait with require_acknowledgment enabled."""
    trt = trait.LockUnlockTrait(
        hass,
        State("lock.door", lock.LockState.UNLOCKED),
        ACK_CONFIG,
    )

    calls = async_mock_service(hass, lock.DOMAIN, lock.SERVICE_LOCK)

    # No challenge data - should raise ChallengeNeeded with ack_needed=True
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(trait.COMMAND_LOCK_UNLOCK, ACK_DATA, {"lock": True}, {})
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.ack_needed is True
    assert err.value.challenge_type == const.CHALLENGE_ACK_NEEDED

    # With acknowledgment data - should execute successfully
    await trt.execute(
        trait.COMMAND_LOCK_UNLOCK,
        ACK_DATA,
        {"lock": True},
        {"ack": True},
    )
    assert len(calls) == 1


async def test_require_acknowledgment_disabled(hass: HomeAssistant) -> None:
    """Test that commands execute normally when require_acknowledgment is not set."""
    trt = trait.OnOffTrait(
        hass,
        State("switch.test", "on"),
        BASIC_CONFIG,
    )

    calls = async_mock_service(hass, switch.DOMAIN, "turn_off")

    # Without require_acknowledgment, command should execute without challenge
    basic_data = helpers.RequestData(
        BASIC_CONFIG,
        "test-agent",
        const.SOURCE_CLOUD,
        "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        None,
    )
    await trt.execute(trait.COMMAND_ON_OFF, basic_data, {"on": False}, {})

    assert len(calls) == 1


# Tests for PIN + acknowledgment interaction

PIN_AND_ACK_CONFIG = MockConfig(
    secure_devices_pin="1234",
    entity_config={
        "lock.secure_door": {const.CONF_REQUIRE_ACK: True},
    },
)

PIN_AND_ACK_DATA = helpers.RequestData(
    PIN_AND_ACK_CONFIG,
    "test-agent",
    const.SOURCE_CLOUD,
    "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
    None,
)


async def test_pin_and_ack_both_required_unlock(hass: HomeAssistant) -> None:
    """Test unlock command when both PIN and acknowledgment are required.

    The ack check should run first before PIN verification.
    """
    trt = trait.LockUnlockTrait(
        hass,
        State("lock.secure_door", lock.LockState.LOCKED),
        PIN_AND_ACK_CONFIG,
    )

    calls = async_mock_service(hass, lock.DOMAIN, lock.SERVICE_UNLOCK)

    # No challenge - should request acknowledgment first
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(
            trait.COMMAND_LOCK_UNLOCK, PIN_AND_ACK_DATA, {"lock": False}, {}
        )
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.ack_needed is True
    assert err.value.challenge_type == const.CHALLENGE_ACK_NEEDED

    # With ack but no PIN - should now request PIN (failed attempt since ack dict provided)
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(
            trait.COMMAND_LOCK_UNLOCK,
            PIN_AND_ACK_DATA,
            {"lock": False},
            {"ack": True},
        )
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.pin_needed is True
    # Since we provided a challenge dict (ack), missing PIN is treated as failed PIN
    assert err.value.challenge_type == const.CHALLENGE_FAILED_PIN_NEEDED

    # With ack and valid PIN - should succeed
    await trt.execute(
        trait.COMMAND_LOCK_UNLOCK,
        PIN_AND_ACK_DATA,
        {"lock": False},
        {"ack": True, "pin": "1234"},
    )
    assert len(calls) == 1
    assert calls[0].data == {ATTR_ENTITY_ID: "lock.secure_door"}


async def test_ack_bypass_attempts(hass: HomeAssistant) -> None:
    """Test that various ack bypass attempts fail when ack is required."""
    trt = trait.OnOffTrait(
        hass,
        State("switch.test", "on"),
        ACK_CONFIG,
    )

    calls = async_mock_service(hass, switch.DOMAIN, "turn_off")

    # Test ack=false should fail
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(trait.COMMAND_ON_OFF, ACK_DATA, {"on": False}, {"ack": False})
    assert len(calls) == 0
    assert err.value.ack_needed is True

    # Test ack=None should fail
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(trait.COMMAND_ON_OFF, ACK_DATA, {"on": False}, {"ack": None})
    assert len(calls) == 0
    assert err.value.ack_needed is True

    # Test only PIN (no ack) should fail when ack is required
    pin_only_config = MockConfig(
        secure_devices_pin="1234",
        entity_config={"lock.door": {const.CONF_REQUIRE_ACK: True}},
    )
    pin_only_data = helpers.RequestData(
        pin_only_config,
        "test-agent",
        const.SOURCE_CLOUD,
        "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        None,
    )

    trt_lock = trait.LockUnlockTrait(
        hass,
        State("lock.door", lock.LockState.LOCKED),
        pin_only_config,
    )

    lock_calls = async_mock_service(hass, lock.DOMAIN, lock.SERVICE_UNLOCK)

    # PIN without ack should fail ack check first
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt_lock.execute(
            trait.COMMAND_LOCK_UNLOCK,
            pin_only_data,
            {"lock": False},
            {"pin": "1234"},  # Valid PIN but no ack
        )
    assert len(lock_calls) == 0
    assert err.value.ack_needed is True
    assert err.value.challenge_type == const.CHALLENGE_ACK_NEEDED


async def test_unlock_with_invalid_pin_after_ack(hass: HomeAssistant) -> None:
    """Test that invalid PIN is caught after valid ack is provided."""
    trt = trait.LockUnlockTrait(
        hass,
        State("lock.secure_door", lock.LockState.LOCKED),
        PIN_AND_ACK_CONFIG,
    )

    calls = async_mock_service(hass, lock.DOMAIN, lock.SERVICE_UNLOCK)

    # With ack but wrong PIN - should fail PIN challenge
    with pytest.raises(error.ChallengeNeeded) as err:
        await trt.execute(
            trait.COMMAND_LOCK_UNLOCK,
            PIN_AND_ACK_DATA,
            {"lock": False},
            {"ack": True, "pin": "9999"},
        )
    assert len(calls) == 0
    assert err.value.code == const.ERR_CHALLENGE_NEEDED
    assert err.value.pin_needed is True
    assert err.value.challenge_type == const.CHALLENGE_FAILED_PIN_NEEDED
