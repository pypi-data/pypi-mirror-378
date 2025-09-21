
# Changelog
All notable changes to WuttaPOS will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.3.0 (2025-09-20)

### Feat

- add support for dynamic context menu
- begin abstraction for more flexible button menus
- abandon `UserControl` as parent class for custom controls
- use latest flet, try to fix threading issues

### Fix

- fix config extension entry point
- change how snackbar is opened, per upstream changes
- add backward compatibility for Flet 0.19.0
- avoid deprecated `Page.dialog` usage
- change how we set app to be full screen (again)
- add red highlighting for Terminal ID, if not configured

## v0.2.1 (2024-07-01)

### Fix

- use rattail function to create top-level command

## v0.2.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml + hatchling

## [0.1.0] - 2023-09-22
### Added
- Initial version (WIP; testing only).
