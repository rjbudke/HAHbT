# HAHbT

HAHbT is a Home Assistant custom integration for tracking real-world recurring events as structured habit history.

The core idea is simple: a habit is not a checklist item. It is an event stream with meaning.

Examples:

- lawn mowed
- haircut
- changed HVAC filter
- took medication
- watered plants
- date night
- ate at a favorite restaurant

HAHbT is being rebuilt as a greenfield integration on top of the existing project identity. The old flat prototype remains in this repository for reference during the transition, but the active integration code now lives under `custom_components/hahbt/`.

## Current direction

The current `v1` target is intentionally narrow:

- one integration entry manages many habits
- event-based habits only
- backdated logging is supported
- edit or delete of past events is deferred
- habits support `active`, `inactive`, and `archived` lifecycle states
- inactive habits remain visible for history but are not loggable until reactivated
- service-based logging and button entities both exist in `v1`
- no target cadence or overdue semantics in `v1`
- per-event notes exist as plumbing but are not a primary `v1` UX

## Planned `v1` surface

Services:

- `hahbt.create_habit`
- `hahbt.update_habit`
- `hahbt.archive_habit`
- `hahbt.log_event`

Per-habit entities:

- latest occurrence sensor
- time since last occurrence sensor
- count today sensor
- count this week sensor
- count total sensor
- average interval sensor
- quick-log button for active habits

## Development workflow

1. Build locally in this repo.
2. Push to GitHub as the source of truth.
3. Install into Home Assistant from the repo.
4. Validate behavior in Home Assistant.
5. Capture decisions and refinements in project docs.

## Repository layout

```text
custom_components/hahbt/
  __init__.py
  button.py
  config_flow.py
  const.py
  coordinator.py
  diagnostics.py
  entity.py
  manifest.json
  models.py
  sensor.py
  services.py
  services.yaml
  storage.py
  translations/en.json
```

## Status

This is the start of the clean rebuild, not a finished release. The repo now has the correct custom integration layout and an explicit `v1` product contract. The next implementation slice is hardening the service layer, validating the entity behavior in Home Assistant, and adding tests.
