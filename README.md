# HAHbT

HAHbT stands for Home Assistant Habit Tracker, and is pronounced "HOB-bit."

HAHbT is a Home Assistant custom integration for tracking real-world recurring events as structured habit history.

It is built for the kinds of things in life that matter, repeat, and shape your routines, but do not fit especially well into a normal task app or a generic Home Assistant sensor.

The core idea is simple: a habit is not just a checklist item. It is an event stream with meaning.

## Why HAHbT Exists

A lot of habit tools are built around checkboxes, streaks, and reminders.

HAHbT is aimed at a different kind of problem: real-life recurring things that do not fit cleanly into task apps or standard Home Assistant sensors, but still matter enough that you want to track them, understand them, and automate around them.

That could mean:

- the last time the lawn was mowed
- haircut cadence
- the last time you had pizza from a specific place
- medication, chores, maintenance, or household routines
- anything where elapsed time, frequency, trends, or reminders matter more than a simple done or not-done checkbox

In HAHbT, a habit is closer to an event stream with meaning than a todo item.

## The Real Value

The real power of HAHbT is downstream.

Once lived events become structured history inside Home Assistant, they can drive:

- sensors and stats derived from event history
- automations based on time-since, overdue state, unusual gaps, or changing cadence
- dashboards and summaries
- a richer understanding of personal and household patterns over time

The goal is to bridge physical life and Home Assistant automation by making personal habits first-class tracked events.

## Project State

Current public beta version: `0.2.1`

HAHbT is currently in a strong beta state.

That means:

- the project has a clear product direction and architecture
- the custom integration foundation is in place
- the core logging and lifecycle model is implemented
- baseline tests exist for key behavior
- Home Assistant validation is still the main gating step before this should be treated as production-ready

It is not alpha, but it is not production-ready yet either.

## V1 Scope

### Included in V1

- one integration entry managing many habits
- event-based habits only
- create habit
- update habit metadata
- active, inactive, and archived habit lifecycle states
- log an event now
- log an event with a specific timestamp
- duplicate timestamps allowed when intentional
- quick-log button for active habits
- core sensors for latest occurrence, time since last, count today, count this week, count total, and average interval
- inactive habits remain visible for history and metrics, but cannot be logged until reactivated
- install path through HACS custom repository or manual custom integration copy

### Not Part of V1

- numeric-value habits
- grouped or categorized habits
- edit or delete past events
- target cadence or overdue logic
- streaks
- anomaly detection
- import/export tooling
- custom Lovelace UI
- rich per-event note UX

The point of `v1` is not to ship every dream at once. The point is to build the rails correctly so the larger vision can grow on top of a stable foundation.

## Planned V1 Surface

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

## Roadmap

### Going To Add

Near-term work already planned for the current build path:

- full Home Assistant runtime validation
- tighter service and entity validation inside HA
- better install and usage documentation
- broader tests around calculations and entity behavior
- polish around the first public beta release path

### Talked About Adding

Features that fit the product direction and are likely after `v1` stabilizes:

- backfill workflow with better UX
- delete or correct events safely
- overdue binary sensors
- streaks
- cadence drift detection
- next expected occurrence estimation
- dashboards or Lovelace helpers
- better in-HA habit management UI
- import and export tools

### Thought About

Longer-range ideas that are interesting, but intentionally not committed yet:

- grouped or categorized habits
- maintenance-oriented templates
- household shared habit streams
- summary sensors across habits
- recurring review summaries
- habit health scoring
- AI interpretation layered on top of habit history

## Installation

For now, install HAHbT as a custom integration for testing and development.

HACS:

- add `https://github.com/rjbudke/HAHbT` as a custom repository of type `Integration`
- install `HAHbT`
- restart Home Assistant

Manual:

- copy `custom_components/hahbt/` into your Home Assistant config under `custom_components/hahbt/`
- restart Home Assistant

Branding note:

- Home Assistant `2026.3` and newer can load packaged integration branding from `custom_components/hahbt/brand/`
- older Home Assistant versions may still show the generic placeholder icon for custom integrations

After restart:

- go to `Settings -> Devices & Services`
- add the `HAHbT` integration

## Repository Layout

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

## Assets

Official repository assets:

- `images/icon.png`: official square icon
- `images/logo.png`: transparent logo variant
- `images/icon-transparent.png`: transparent icon variant

## Validation Focus

The current validation goals are:

- integration setup succeeds cleanly in Home Assistant
- services register correctly
- habits can be created, updated, archived, and logged
- active versus inactive versus archived behavior matches the product spec
- core sensors update correctly from stored events

## Notes

This repo is intentionally focused at this stage. The goal right now is to make the foundation correct before expanding the feature surface.
