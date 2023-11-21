# Changelog

## [0.2.3] - 2023-11-21

### What's Changed

- Add getting exif information by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/37
- Add cache for items filesizes by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/42
- Use filesize cache to detect updates by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/44
- Update cattrs requirement from ~=23.1.2 to >=23.1.2,<23.3.0 by @dependabot in https://github.com/fortysix2ahead/synophotos/pull/40
- Update rich requirement from ~=13.6.0 to >=13.6,<13.8 by @dependabot in https://github.com/fortysix2ahead/synophotos/pull/41

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.2.2...rel-0.2.3

## [0.2.2] - 2023-11-17

### What's Changed

- init, profile and version commands don't require login() by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/23
- Reverse sync behaviour by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/25
- Use folder id for path creation instead of album id/name by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/26
- Added deduplication of results before download by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/28
- Show user and url in profile command by @fortysix2ahead in https://github.com/fortysix2ahead/synophotos/pull/34

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.2.1...rel-0.2.2

## [0.2.1] - 2023-11-15

### Fixed

- Corrected broken fsio import

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.2.0...rel-0.2.1

## [0.2.0] - 2023-11-15

### Added

- Added sync command
- Added download command
- Added show command
- Added --force global option

### Changed

- Consolidated configuration, only config.yaml is used now, profiles.yaml is obsolete

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.1.2...rel-0.2.0

## [0.1.2] - 2023-11-11

### Fixed

- Removed leftover references to ctx objects, which caused a crash when credentials were wrong

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.1.1...rel-0.1.2

## [0.1.1] - 2023-11-10

### Fixed

- Install typing_extensions as dependency, making synophotos run with Python 3.11

**Full Changelog**: https://github.com/fortysix2ahead/synophotos/compare/rel-0.1.0...rel-0.1.1

## [0.1.0] - 2023-11-10

### Added

- Initial release version
