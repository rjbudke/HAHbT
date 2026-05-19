"""Minimal Home Assistant and dependency stubs for lightweight unit tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import sys
import types


class _GenericStub:
    @classmethod
    def __class_getitem__(cls, item):
        return cls


class ConfigEntry(_GenericStub):
    runtime_data = None


class HomeAssistant:
    pass


class ServiceCall:
    def __init__(self, data=None):
        self.data = data or {}


class DataUpdateCoordinator(_GenericStub):
    def __init__(self, *args, **kwargs):
        self.data = {}

    async def async_config_entry_first_refresh(self):
        return None

    async def async_request_refresh(self):
        return None

    def async_add_listener(self, listener):
        return lambda: None


class CoordinatorEntity(_GenericStub):
    def __init__(self, coordinator=None):
        self.coordinator = coordinator

    @property
    def available(self):
        return True


class Store(_GenericStub):
    def __init__(self, *args, **kwargs):
        pass

    async def async_load(self):
        return {}

    async def async_save(self, data):
        return None


@dataclass
class DeviceInfo:
    identifiers: set | None = None
    name: str | None = None
    manufacturer: str | None = None
    model: str | None = None


class ButtonEntity:
    pass


class SensorEntity:
    pass


@dataclass(frozen=True, kw_only=True)
class SensorEntityDescription:
    key: str = ""
    name: str | None = None
    icon: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    native_unit_of_measurement: str | None = None
    suggested_unit_of_measurement: str | None = None
    entity_registry_enabled_default: bool = True


class SensorDeviceClass:
    TIMESTAMP = "timestamp"
    DURATION = "duration"


class SensorStateClass:
    MEASUREMENT = "measurement"


class UnitOfTime:
    HOURS = "h"


class Schema:
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, value):
        return value


class Optional:
    def __init__(self, key):
        self.key = key


class Required:
    def __init__(self, key):
        self.key = key


def Any(*values):
    return values


def In(values):
    return values


def _cv_string(value):
    return value


def _cv_datetime(value):
    return value


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _utcnow():
    return datetime.now(UTC)


def _as_local(value):
    return value


class AddEntitiesCallback:
    pass


def install() -> None:
    homeassistant = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    core = types.ModuleType("homeassistant.core")
    helpers = types.ModuleType("homeassistant.helpers")
    update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
    storage = types.ModuleType("homeassistant.helpers.storage")
    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    config_validation = types.ModuleType("homeassistant.helpers.config_validation")
    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    components = types.ModuleType("homeassistant.components")
    button = types.ModuleType("homeassistant.components.button")
    sensor = types.ModuleType("homeassistant.components.sensor")
    const = types.ModuleType("homeassistant.const")
    util = types.ModuleType("homeassistant.util")
    dt = types.ModuleType("homeassistant.util.dt")
    voluptuous = types.ModuleType("voluptuous")

    config_entries.ConfigEntry = ConfigEntry
    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall
    update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
    update_coordinator.CoordinatorEntity = CoordinatorEntity
    storage.Store = Store
    device_registry.DeviceInfo = DeviceInfo
    config_validation.string = _cv_string
    config_validation.datetime = _cv_datetime
    entity_platform.AddEntitiesCallback = AddEntitiesCallback
    button.ButtonEntity = ButtonEntity
    sensor.ButtonEntity = ButtonEntity
    sensor.SensorEntity = SensorEntity
    sensor.SensorEntityDescription = SensorEntityDescription
    sensor.SensorDeviceClass = SensorDeviceClass
    sensor.SensorStateClass = SensorStateClass
    const.UnitOfTime = UnitOfTime
    dt.as_utc = _as_utc
    dt.utcnow = _utcnow
    dt.as_local = _as_local
    voluptuous.Schema = Schema
    voluptuous.Optional = Optional
    voluptuous.Required = Required
    voluptuous.Any = Any
    voluptuous.In = In

    sys.modules.setdefault("homeassistant", homeassistant)
    sys.modules.setdefault("homeassistant.config_entries", config_entries)
    sys.modules.setdefault("homeassistant.core", core)
    sys.modules.setdefault("homeassistant.helpers", helpers)
    sys.modules.setdefault("homeassistant.helpers.update_coordinator", update_coordinator)
    sys.modules.setdefault("homeassistant.helpers.storage", storage)
    sys.modules.setdefault("homeassistant.helpers.device_registry", device_registry)
    sys.modules.setdefault("homeassistant.helpers.config_validation", config_validation)
    sys.modules.setdefault("homeassistant.helpers.entity_platform", entity_platform)
    sys.modules.setdefault("homeassistant.components", components)
    sys.modules.setdefault("homeassistant.components.button", button)
    sys.modules.setdefault("homeassistant.components.sensor", sensor)
    sys.modules.setdefault("homeassistant.const", const)
    sys.modules.setdefault("homeassistant.util", util)
    sys.modules.setdefault("homeassistant.util.dt", dt)
    sys.modules.setdefault("voluptuous", voluptuous)
