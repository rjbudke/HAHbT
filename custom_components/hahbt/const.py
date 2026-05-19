"""Constants for the HAHbT integration."""

from __future__ import annotations

DOMAIN = "hahbt"
PLATFORMS = ["sensor", "button"]

CONF_HABIT_ID = "habit_id"
CONF_NAME = "name"
CONF_ICON = "icon"
CONF_NOTES = "notes"
CONF_OCCURRED_AT = "occurred_at"
CONF_NOTE = "note"
CONF_STATUS = "status"

SERVICE_CREATE_HABIT = "create_habit"
SERVICE_UPDATE_HABIT = "update_habit"
SERVICE_ARCHIVE_HABIT = "archive_habit"
SERVICE_LOG_EVENT = "log_event"

STORAGE_VERSION = 1
STORAGE_KEY = DOMAIN
UPDATE_INTERVAL_SECONDS = 60

SOURCE_SERVICE = "service"
SOURCE_BUTTON = "button"
SOURCE_MIGRATION = "migration"

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_ARCHIVED = "archived"

DATA_COORDINATOR = "coordinator"
DATA_SERVICES_REGISTERED = "services_registered"
