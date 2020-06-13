"""Module for dimmers (currently only HS220)."""
from typing import Any, Dict

from kasa.smartdevice import DeviceType, SmartDeviceException, requires_update
from kasa.smartplug import SmartPlug


class SmartDimmer(SmartPlug):
    """Representation of a TP-Link Smart Dimmer.

    Dimmers work similarly to plugs, but provide also support for
    adjusting the brightness. This class extends SmartPlug interface.

    Example:
    ```
    dimmer = SmartDimmer("192.168.1.105")
    await dimmer.turn_on()
    print("Current brightness: %s" % dimmer.brightness)

    await dimmer.set_brightness(100)
    ```

    Refer to SmartPlug for the full API.
    """

    DIMMER_SERVICE = "smartlife.iot.dimmer"

    def __init__(self, host: str) -> None:
        super().__init__(host)
        self._device_type = DeviceType.Dimmer

    @property  # type: ignore
    @requires_update
    def brightness(self) -> int:
        """Return current brightness on dimmers.

        Will return a range between 0 - 100.
        """
        if not self.is_dimmable:
            raise SmartDeviceException("Device is not dimmable.")

        sys_info = self.sys_info
        return int(sys_info["brightness"])

    @requires_update
    async def set_brightness(self, brightness: int, *, transition: int = None):
        """Set the new dimmer brightness level in percentage > 0.

        :param int transition: transition duration in milliseconds.
            This will cause the light to turn on.
            See `set_dimmer_transition()` for more details.
        """
        if not self.is_dimmable:
            raise SmartDeviceException("Device is not dimmable.")

        if not isinstance(brightness, int):
            raise ValueError(
                "Brightness must be integer, " "not of %s.", type(brightness)
            )

        if not 0 < brightness <= 100:
            raise ValueError("Brightness value %s is not valid." % brightness)

        if transition:
            return await self.set_dimmer_transition(brightness, transition)
        else:
            return await self._query_helper(
                self.DIMMER_SERVICE, "set_brightness", {"brightness": brightness}
            )

    async def turn_off(self, *, transition: int = None) -> None:
        """Turn the bulb off."""
        if transition:
            await self.set_dimmer_transition(brightness=0, transition=transition)
        else:
            await super().turn_off()

    @requires_update
    async def turn_on(self, *, transition: int = None) -> None:
        """Turn the bulb on."""
        if transition:
            await self.set_dimmer_transition(
                brightness=self.brightness, transition=transition
            )
        else:
            await super().turn_on()

    async def set_dimmer_transition(self, brightness: int, transition: int):
        """Turn the bulb to brightness percentage over transition milliseconds."""
        if not isinstance(brightness, int):
            raise ValueError(
                "Brightness must be integer, " "not of %s.", type(brightness)
            )

        if not 0 <= brightness <= 100:
            raise ValueError("Brightness value %s is not valid." % brightness)

        if not isinstance(transition, int):
            raise ValueError(
                "Transition must be integer, " "not of %s.", type(transition)
            )
        if transition <= 0:
            raise ValueError("Transition value %s is not valid." % transition)

        return await self._query_helper(
            self.DIMMER_SERVICE,
            "set_dimmer_transition",
            {"brightness": brightness, "duration": transition},
        )

    @property  # type: ignore
    @requires_update
    def is_dimmable(self) -> bool:
        """Whether the switch supports brightness changes."""
        sys_info = self.sys_info
        return "brightness" in sys_info

    @property  # type: ignore
    @requires_update
    def state_information(self) -> Dict[str, Any]:
        """Return switch-specific state information."""
        info = super().state_information
        info["Brightness"] = self.brightness

        return info
