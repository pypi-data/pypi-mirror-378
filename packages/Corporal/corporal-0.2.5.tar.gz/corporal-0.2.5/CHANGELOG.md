
# Changelog
All notable changes to Corporal will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.2.5 (2025-09-20)

### Fix

- fix config extension entry point

## v0.2.4 (2024-09-15)

### Fix

- update project source links, kallithea -> forgejo

## v0.2.3 (2024-08-18)

### Fix

- avoid deprecated base class for config extension

## v0.2.2 (2024-08-13)

### Fix

- update config default for vendor catalog batch handler

## v0.2.1 (2024-07-01)

### Fix

- use rattail function to create top-level command

## v0.2.0 (2024-06-10)

### Feat

- replace corporal commands with typer equivalents
- switch from setup.cfg to pyproject.toml + hatchling

## [0.1.16] - 2024-04-16
### Changed
- Update subcommand entry point group names, per wuttjamaican.
- Remove version cap for pyramid.

## [0.1.15] - 2023-08-24
### Changed
- Remove rattail-fabric2 as hard dependency.

## [0.1.14] - 2023-06-12
### Changed
- Add "typicals" view set for corporal.

## [0.1.13] - 2023-05-30
### Changed
- Improve project generator for CORE "poser".
- Replace `setup.py` contents with `setup.cfg`.
- Remove version cap for `invoke` lib.

## [0.1.12] - 2023-05-08
### Changed
- Add custom project generator for apps based on Corporal.
- Add basic generator for CORE-POS "Poser" projects.
- Tweak essentials views, per tailbone changes.
- Move "other" menu logic to separate method.

## [0.1.11] - 2023-05-02
### Changed
- Cap version of invoke, until next fabric2 release.

## [0.1.10] - 2023-02-10
### Changed
- Remove version cap for SQLAlchemy.

## [0.1.9] - 2023-01-18
### Changed
- Use handler to build menus.
- Include sample config files in manifest.
- Tweak view config per upstream changes.
- Remove reference to `rattail[auth]` extra.
- Add support for new-style `corporal install` command.

## [0.1.8] - 2023-01-02
### Changed
- Register entry points for emails.
- Expose app setting for default grid pagesize.
- Add ASGI app wrapper.

## [0.1.7] - 2022-03-10
### Changed
- Remove DB config from web app startup.
- Move CORE-specific vendor catalog view logic to tailbone-corepos.
- Tweak how product lookup happens for vendor catalog batch.
- Rename routes for `poser_reports` per upstream changes.

## [0.1.6] - 2022-03-02
### Changed
- Add import/export views and menu link.
- Add views, menus for Poser Reports.

## [0.1.5] - 2021-11-04
### Changed
- Add menu entry for CORE Member Batches.

## [0.1.4] - 2021-08-02
### Changed
- Parse the Fannie config file to get lane definitions for rattail.conf (when deploying).
- Include email setting for CORE Office -> Lane export.
- Add CORE Office URL to deployed Corporal config.

## [0.1.3] - 2021-06-15
### Changed
- Just show default favicon and header image.

## [0.1.2] - 2021-06-15
### Changed
- More fabric tweaks for basic Corporal app install.
- Remove version restriction for mysql-connector-python.

## [0.1.1] - 2021-06-11
### Changed
- Freeze sqlalchemy version per pip issues

## [0.1.0] - 2021-06-11
### Added
- Initial release, to test install
