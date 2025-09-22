"""Representation of an Afero Thermostat and its corresponding updates."""

from dataclasses import dataclass

from aioafero.util import calculate_hubspace_fahrenheit
from aioafero.v1.models import features

from .resource import ResourceTypes
from .standard_mixin import StandardMixin


@dataclass(kw_only=True)
class Thermostat(StandardMixin):
    """Representation of an Afero Thermostat."""

    type: ResourceTypes = ResourceTypes.THERMOSTAT

    display_celsius: bool | None = None
    current_temperature: features.CurrentTemperatureFeature | None = None
    fan_running: bool | None = None
    fan_mode: features.ModeFeature | None = None
    hvac_action: str | None = None
    hvac_mode: features.HVACModeFeature | None = None
    safety_max_temp: features.TargetTemperatureFeature | None = None
    safety_min_temp: features.TargetTemperatureFeature | None = None
    target_temperature_auto_heating: features.TargetTemperatureFeature | None = None
    target_temperature_auto_cooling: features.TargetTemperatureFeature | None = None
    target_temperature_heating: features.TargetTemperatureFeature | None = None
    target_temperature_cooling: features.TargetTemperatureFeature | None = None

    @property
    def target_temperature(self) -> float | None:
        """Temperature which the HVAC will try to achieve."""
        if self.hvac_mode is None or self.hvac_mode.mode not in [
            "cool",
            "heat",
            "fan",
            "off",
        ]:
            return None
        celsius: float = getattr(
            self._get_target_feature(self.get_mode_to_check()), "value", None
        )
        if celsius is None:
            return None
        if self.display_celsius:
            return celsius
        return calculate_hubspace_fahrenheit(celsius)

    def get_mode_to_check(self) -> str | None:
        """Determine the current mode of the thermostat."""
        if not self.hvac_mode:
            return None
        if self.hvac_mode.mode in ["cool", "heat"]:
            return self.hvac_mode.mode
        if self.hvac_mode.previous_mode in ["cool", "heat"]:
            return self.hvac_mode.previous_mode
        return None

    def _get_target_feature(self, mode: str) -> float | None:
        if mode == "cool":
            return self.target_temperature_cooling
        if mode == "heat":
            return self.target_temperature_heating
        return None

    @property
    def target_temperature_range(self) -> tuple[float, float]:
        """Range which the thermostat supports."""
        if self.display_celsius:
            return (
                self.target_temperature_auto_heating.value,
                self.target_temperature_auto_cooling.value,
            )
        return (
            calculate_hubspace_fahrenheit(self.target_temperature_auto_heating.value),
            calculate_hubspace_fahrenheit(self.target_temperature_auto_cooling.value),
        )

    @property
    def target_temperature_step(self) -> float:
        """Smallest increment for adjusting the temperature."""
        set_mode = self.get_mode_to_check()
        if not set_mode:
            val = 0.5  # Default from Hubspace
        else:
            val = getattr(
                self._get_target_feature(self.get_mode_to_check()), "step", None
            )
        if self.display_celsius:
            return val
        return 1

    @property
    def target_temperature_max(self) -> float:
        """Maximum target temperature."""
        set_mode = self.get_mode_to_check()
        if not set_mode or self.hvac_mode.mode == "auto":
            val = self.target_temperature_auto_cooling.max
        else:
            val = getattr(self._get_target_feature(set_mode), "max", None)
        if self.display_celsius:
            return val
        return calculate_hubspace_fahrenheit(val)

    @property
    def target_temperature_min(self) -> float:
        """Minimum target temperature."""
        set_mode = self.get_mode_to_check()
        if not set_mode or self.hvac_mode.mode == "auto":
            val = self.target_temperature_auto_heating.min
        else:
            val = getattr(
                self._get_target_feature(self.get_mode_to_check()), "min", None
            )
        if self.display_celsius:
            return val
        return calculate_hubspace_fahrenheit(val)

    @property
    def supports_fan_mode(self) -> bool:
        """Can enable fan-only mode."""
        return self.fan_mode is not None

    @property
    def supports_temperature_range(self) -> bool:
        """Range which the thermostat will heat / cool."""
        if not self.hvac_mode or "auto" not in self.hvac_mode.supported_modes:
            return False
        return (
            self.target_temperature_auto_cooling is not None
            and self.target_temperature_auto_heating is not None
        )

    @property
    def temperature(self) -> float | None:
        """Current temperature of the selected mode."""
        if self.display_celsius:
            return self.current_temperature.temperature
        return calculate_hubspace_fahrenheit(self.current_temperature.temperature)


@dataclass
class ThermostatPut:
    """States that can be updated for a Thermostat."""

    fan_mode: features.ModeFeature | None = None
    hvac_mode: features.HVACModeFeature | None = None
    safety_max_temp: features.TargetTemperatureFeature | None = None
    safety_min_temp: features.TargetTemperatureFeature | None = None
    target_temperature_auto_heating: features.TargetTemperatureFeature | None = None
    target_temperature_auto_cooling: features.TargetTemperatureFeature | None = None
    target_temperature_heating: features.TargetTemperatureFeature | None = None
    target_temperature_cooling: features.TargetTemperatureFeature | None = None
