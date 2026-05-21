# Changelog

All notable changes to HAHbT will be documented in this file.

The format is loosely based on Keep a Changelog and uses semantic versioning in a practical, lightweight way for the project’s current stage.

## [0.2.1] - 2026-05-21

### Added
- Added `CHANGELOG.md` to establish versioned release notes in the repository.
- Added `images/icon-transparent.png` as a transparent-background icon asset.
- Added a transparent `logo.png` variant aligned with the selected official icon.
- Added packaged brand assets under `custom_components/hahbt/brand/` so Home Assistant can load the integration icon and logo directly on supported versions.

### Changed
- Polished the public-facing packaging around the first beta release.
- Updated README version references from `0.2.0` to `0.2.1`.
- Kept the selected HAHbT icon as the official square icon and clarified the asset set for distribution.

### Notes
- This is a packaging and documentation patch release on top of the first public beta foundation.
- No integration behavior changes are introduced in `0.2.1` beyond versioned project metadata and asset publication.
- Local packaged brand assets require Home Assistant `2026.3` or newer; older versions may continue to show the default placeholder image for custom integrations.

## [0.2.0] - 2026-05-21

### Added
- Established the first official public beta version for HAHbT.
- Added the official HAHbT icon to the repository.
- Added the first public GitHub release and version tag.
- Added baseline automated tests for storage behavior, button visibility rules, and sensor visibility rules.

### Changed
- Rebuilt HAHbT onto a clean Home Assistant custom integration foundation.
- Reworked the README into a public-facing beta document with project framing, scope, and roadmap.
- Replaced the original flat prototype layout with a proper `custom_components/hahbt/` structure.

### Fixed
- Fixed sensor entity creation after the lifecycle model changed from `archived` to `status`.
- Fixed sensor entity description compatibility with newer Home Assistant expectations.

## [0.1.0] - 2026-05-13

### Added
- Created the first greenfield custom integration scaffold for the rebuilt HAHbT project.
- Added initial storage, service, sensor, button, diagnostics, and config-flow structure.
- Added HACS metadata and a basic validation workflow.

### Notes
- `0.1.0` was the internal rebuild baseline, not the first public beta release.
