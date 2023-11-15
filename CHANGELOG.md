# Changelog

## rel-0.2.0 - 2023-11-15

### What's Changed

- Consolidate configuration files by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/6
- Add download of thumbnails by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/11
- Add show command by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/14
- Update platformdirs requirement from ~=3.11.0 to >=3.11,<4.1 by @dependabot in https://github.com/fortysix2ahead/synophotos/pull/13
- Add sync command by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/15
- Added force flag by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/18

### New Contributors

- @dependabot made their first contribution in https://github.com/fortysix2ahead/synophotos/pull/13

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.1.2...rel-0.2.0

## [0.2.0] - 2023-11-15

### Added

- Added sync command
- Added download command
- Added show command
- Added --force global option

### Changed

- Consolidated configuration, only config.yaml is used now, profiles.yaml is obsolete

## [0.1.2] - 2023-11-11

### Fixed

- Removed leftover references to ctx objects, which caused a crash when credentials were wrong

## [0.1.1] - 2023-11-10

### Fixed

- Install typing_extensions as dependency, making synophotos run with Python 3.11

## [0.1.0] - 2023-11-10

### Added

- Initial release version
