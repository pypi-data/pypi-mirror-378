
# Changelog
All notable changes to rattail-mailchimp will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.3.4 (2025-09-20)

### Fix

- fix config extension entry point
- avoid deprecated base class for config extension

## v0.3.3 (2024-07-05)

### Fix

- define `host_key` for MailChimp -> Rattail import

## v0.3.2 (2024-07-01)

### Fix

- remove legacy command definitions

## v0.3.1 (2024-06-14)

### Fix

- fallback to `importlib_metadata` on older python

## v0.3.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml + hatchling

## [0.2.1] - 2024-06-04
### Changed
- Setup default handler for Mailchimp -> Rattail import.

## [0.2.0] - 2024-06-03
### Changed
- Migrate all commands to use `typer`.

## [0.1.5] - 2023-11-30
### Changed
- Update subcommand entry point group names, per wuttjamaican.

## [0.1.4] - 2023-06-01
### Changed
- Replace `setup.py` contents with `setup.cfg`.

## [0.1.3] - 2023-05-13
### Changed
- Avoid deprecated import for `OrderedDict`.

## [0.1.2] - 2023-02-21
### Changed
- Tweak ORM relationship backrefs per SA 2.0 warnings.

## [0.1.1] - 2022-08-06
### Changed
- Register email profiles provided by this pkg.

## [0.1.0] - 2021-11-09
### Added
- Initial version; basic list + member tables, import from MailChimp API.
