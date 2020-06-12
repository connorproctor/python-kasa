import pytest

from kasa import SmartDimmer

from .conftest import dimmer, handle_turn_on


@dimmer
async def test_set_brightness(dev):
    await handle_turn_on(dev, False)
    await dev.set_brightness(99)

    assert dev.brightness == 99
    assert not dev.is_on


@dimmer
async def test_set_brightness_transition_to_on(dev, mocker):
    await handle_turn_on(dev, False)
    query_helper = mocker.spy(SmartDimmer, "_query_helper")

    await dev.set_brightness(99, transition=1000)

    assert dev.brightness == 99
    assert dev.is_on
    query_helper.assert_called_with(
        mocker.ANY,
        "smartlife.iot.dimmer",
        "set_dimmer_transition",
        {"brightness": 99, "duration": 1000},
    )


@dimmer
async def test_set_brightness_transition_to_off(dev, mocker):
    await handle_turn_on(dev, True)
    query_helper = mocker.spy(SmartDimmer, "_query_helper")
    original_brightness = dev.brightness

    await dev.set_brightness(0, transition=1000)

    assert dev.brightness == original_brightness
    assert dev.is_off
    query_helper.assert_called_with(
        mocker.ANY,
        "smartlife.iot.dimmer",
        "set_dimmer_transition",
        {"brightness": 0, "duration": 1000},
    )


@dimmer
async def test_set_brightness_invalid(dev, mocker):
    for invalid_brightness in [-1, 101, 0.5]:
        with pytest.raises(ValueError):
            await dev.set_brightness(invalid_brightness)

    for invalid_transition in [-1, 0, 0.5]:
        with pytest.raises(ValueError):
            await dev.set_brightness(1, transition=invalid_transition)
