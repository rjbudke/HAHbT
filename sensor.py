# custom_components/hahbt/sensor.py

import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.util import dt as dt_util
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HAHbT sensors based on a config entry."""
    habit_id = entry.data["habit_id"]
    habit_data = hass.data[DOMAIN].get(habit_id)

    if not habit_data:
        _LOGGER.error("Habit data for ID %s not found", habit_id)
        return

    # Define the update interval
    update_interval = timedelta(minutes=5)

    # Create the coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"HAHbT {habit_data['habit_name']}",
        update_method=lambda: async_get_habit_data(hass, habit_id),
        update_interval=update_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        HAHbTMostRecentSensor(habit_data),
        HAHbTCountTodaySensor(habit_data),
        HAHbTCountTotalSensor(habit_data),
        HAHbTIntervalSensor(habit_data),
        HAHbTIntervalAverageSensor(habit_data),
        HAHbTTimeSinceLastSensor(coordinator, habit_data),
    ]

    async_add_entities(sensors, update_before_add=True)

async def async_get_habit_data(hass, habit_id):
    """Fetch habit data."""
    return hass.data[DOMAIN].get(habit_id)

class HAHbTSensorBase(SensorEntity):
    """Base class for HAHbT sensors."""

    def __init__(self, habit_data):
        self._habit_data = habit_data
        self._habit_name = habit_data["habit_name"]
        self._habit_slug = habit_data["habit_name"].lower().replace(" ", "_")
        self._state = None

    @property
    def should_poll(self):
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "habit_id": self._habit_data["habit_id"]
        }

    async def async_added_to_hass(self):
        """Register the sensor to receive updates."""
        self._habit_data["sensors"].append(self)

    def parse_timestamp(self, ts):
        """Parse timestamp and ensure it is timezone-aware in UTC."""
        try:
            parsed = dt_util.parse_datetime(ts)
            if parsed is None:
                # Try appending "+00:00" to assume UTC
                ts_with_tz = ts + "+00:00"
                parsed = dt_util.parse_datetime(ts_with_tz)
                if parsed is None:
                    raise ValueError(f"Unable to parse timestamp '{ts}'")
            if parsed.tzinfo is None:
                # Assume UTC if no timezone info
                parsed = parsed.replace(tzinfo=dt_util.UTC)
            else:
                # Normalize to UTC
                parsed = parsed.astimezone(dt_util.UTC)
            return parsed
        except Exception as e:
            _LOGGER.error("Error parsing timestamp '%s' for sensor '%s': %s", ts, self.name, e)
            return None

class HAHbTCountTodaySensor(HAHbTSensorBase):
    """Sensor for counting occurrences of a habit today."""

    def __init__(self, habit_data):
        super().__init__(habit_data)
        self._attr_icon = "mdi:calendar-today"
        self._attr_name = f"HAHbT {self._habit_name} Count Today"
        self._attr_unique_id = f"{self._habit_data['habit_id']}_count_today"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        return self._state

    async def async_update(self):
        try:
            timestamps = self._habit_data["timestamps"]
            _LOGGER.debug(
                "Updating 'Count Today' sensor '%s' with timestamps: %s",
                self._attr_name,
                timestamps,
            )
            today = dt_util.now().date()
            count = 0
            for ts in timestamps:
                parsed_ts = self.parse_timestamp(ts)
                if parsed_ts is None:
                    continue
                local_ts = parsed_ts.astimezone(dt_util.DEFAULT_TIME_ZONE)
                if local_ts.date() == today:
                    count += 1
            self._state = count
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self._attr_name, e)
            self._state = None

class HAHbTIntervalSensor(HAHbTSensorBase):
    """Sensor for the interval between the two most recent occurrences of a habit."""

    def __init__(self, habit_data):
        super().__init__(habit_data)
        self._attr_icon = "mdi:calendar-expand-horizontal"
        self._attr_name = f"HAHbT Time Between {self._habit_name}"
        self._attr_unique_id = f"{self._habit_data['habit_id']}_interval"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._human_readable_interval = None  # New attribute

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = super().extra_state_attributes
        if self._human_readable_interval is not None:
            attributes["human_readable_interval"] = self._human_readable_interval
        return attributes

    async def async_update(self):
        try:
            timestamps = self._habit_data["timestamps"]
            _LOGGER.debug("Updating 'Interval' sensor '%s' with timestamps: %s", self.name, timestamps)
            if len(timestamps) >= 2:
                last_time = self.parse_timestamp(timestamps[-1])
                prev_time = self.parse_timestamp(timestamps[-2])
                if last_time is None or prev_time is None:
                    self._state = None
                    self._human_readable_interval = None
                else:
                    delta = last_time - prev_time
                    self._state = int(delta.total_seconds() / 60)  # Interval in minutes
                    self._human_readable_interval = self.format_time_delta(delta)
            else:
                self._state = None
                self._human_readable_interval = None
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self.name, e)
            self._state = None
            self._human_readable_interval = None

    def format_time_delta(self, delta):
        """Format a timedelta object into a human-readable string."""
        total_seconds = int(delta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)  # Number of seconds in a day
        hours, remainder = divmod(remainder, 3600)      # Number of seconds in an hour
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 and total_seconds < 60:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        if not parts:
            parts.append("0 seconds")

        return ", ".join(parts)

class HAHbTMostRecentSensor(HAHbTSensorBase):
    """Sensor for the most recent occurrence of a habit."""

    def __init__(self, habit_data):
        super().__init__(habit_data)
        self._attr_icon = "mdi:calendar-clock"
        self._attr_name = f"HAHbT Most Recent {self._habit_name}"
        self._attr_unique_id = f"{self._habit_data['habit_id']}_most_recent"

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        return self._state

    @property
    def device_class(self):
        return SensorDeviceClass.TIMESTAMP

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = super().extra_state_attributes

        timestamps = self._habit_data["timestamps"]
        num_timestamps = len(timestamps)

        # Access the timestamps from the end (most recent)
        if num_timestamps >= 2:
            second_most_recent = self.parse_timestamp(timestamps[-2])
            if second_most_recent:
                attributes["2nd Most Recent"] = second_most_recent.isoformat()
        if num_timestamps >= 3:
            third_most_recent = self.parse_timestamp(timestamps[-3])
            if third_most_recent:
                attributes["3rd Most Recent"] = third_most_recent.isoformat()
        if num_timestamps >= 4:
            fourth_most_recent = self.parse_timestamp(timestamps[-4])
            if fourth_most_recent:
                attributes["4th Most Recent"] = fourth_most_recent.isoformat()

        return attributes

    async def async_update(self):
        try:
            timestamps = self._habit_data["timestamps"]
            _LOGGER.debug("Updating sensor '%s' with timestamps: %s", self.name, timestamps)
            if timestamps:
                last_time_str = timestamps[-1]
                last_time = self.parse_timestamp(last_time_str)
                if last_time is None:
                    self._state = None
                else:
                    self._state = last_time.isoformat()
            else:
                self._state = None
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self.name, e)
            self._state = None

class HAHbTCountTotalSensor(HAHbTSensorBase):
    """Sensor for counting total occurrences of a habit."""

    def __init__(self, habit_data):
        super().__init__(habit_data)
        self._attr_icon = "mdi:sigma"
        self._attr_name = f"HAHbT {self._habit_name} Count Total"
        self._attr_unique_id = f"{self._habit_data['habit_id']}_count_total"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        return self._state

    async def async_update(self):
        try:
            timestamps = self._habit_data["timestamps"]
            _LOGGER.debug(
                "Updating 'Count Total' sensor '%s' with timestamps: %s",
                self._attr_name,
                timestamps,
            )
            self._state = len(timestamps)
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self._attr_name, e)
            self._state = None

class HAHbTIntervalAverageSensor(HAHbTSensorBase):
    """Sensor for the average interval between all occurrences of a habit, including longest and shortest intervals."""

    def __init__(self, habit_data):
        super().__init__(habit_data)
        self._attr_icon = "mdi:calendar-expand-horizontal-outline"
        self._attr_name = f"HAHbT Average Time Between {self._habit_name}"
        self._attr_unique_id = f"{self._habit_data['habit_id']}_interval_average"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._longest_interval = None
        self._shortest_interval = None

    @property
    def native_value(self):
        return self._state  # This is the average interval

    @property
    def extra_state_attributes(self):
        """Return the state attributes including longest and shortest intervals."""
        attributes = super().extra_state_attributes
        attributes.update({
            "longest_interval": self._longest_interval,
            "shortest_interval": self._shortest_interval,
        })
        return attributes

    async def async_update(self):
        try:
            timestamps = self._habit_data["timestamps"]
            _LOGGER.debug(
                "Updating 'Average Interval' sensor '%s' with timestamps: %s",
                self._attr_name,
                timestamps,
            )
            if len(timestamps) >= 2:
                parsed_timestamps = []
                for ts in timestamps:
                    parsed_ts = self.parse_timestamp(ts)
                    if parsed_ts is not None:
                        parsed_timestamps.append(parsed_ts)
                if len(parsed_timestamps) >= 2:
                    parsed_timestamps.sort()
                    intervals = []
                    for i in range(1, len(parsed_timestamps)):
                        delta = (parsed_timestamps[i] - parsed_timestamps[i - 1]).total_seconds()
                        intervals.append(delta)
                    if intervals:
                        total_interval = sum(intervals)
                        average_interval = total_interval / len(intervals)
                        self._state = int(average_interval / 60)  # Average interval in minutes

                        # Calculate longest and shortest intervals
                        longest_interval = max(intervals)
                        shortest_interval = min(intervals)
                        self._longest_interval = int(longest_interval / 60)  # In minutes
                        self._shortest_interval = int(shortest_interval / 60)  # In minutes
                    else:
                        self._state = None
                        self._longest_interval = None
                        self._shortest_interval = None
                else:
                    self._state = None
                    self._longest_interval = None
                    self._shortest_interval = None
            else:
                self._state = None
                self._longest_interval = None
                self._shortest_interval = None
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self._attr_name, e)
            self._state = None
            self._longest_interval = None
            self._shortest_interval = None

class HAHbTTimeSinceLastSensor(CoordinatorEntity, HAHbTSensorBase):
    """Sensor for the time since the last occurrence of a habit."""

    def __init__(self, coordinator, habit_data):
        CoordinatorEntity.__init__(self, coordinator)
        HAHbTSensorBase.__init__(self, habit_data)
        self._attr_icon = "mdi:timer"
        self._attr_name = f"HAHbT Time Since Last {self._habit_name}"
        self._attr_unique_id = f"{habit_data['habit_id']}_time_since_last"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def native_value(self):
        try:
            habit_data = self.coordinator.data
            if not habit_data["timestamps"]:
                return None
            last_time = self.parse_timestamp(habit_data["timestamps"][-1])
            now = dt_util.utcnow()
            delta = now - last_time
            return int(delta.total_seconds() / 60)  # Convert to minutes
        except Exception as e:
            _LOGGER.error("Error updating sensor '%s': %s", self._attr_name, e)
            return None