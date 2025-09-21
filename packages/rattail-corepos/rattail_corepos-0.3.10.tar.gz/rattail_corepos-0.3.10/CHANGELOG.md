
# Changelog
All notable changes to rattail-corepos will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.3.10 (2025-09-20)

### Fix

- fix config extension entry point

## v0.3.9 (2024-08-19)

### Fix

- improve logic for matching CORE stock purchase to Rattail payment

## v0.3.8 (2024-08-18)

### Fix

- avoid deprecated base class for config extension
- work around, log error when datasync can't locate member

## v0.3.7 (2024-08-13)

### Fix

- improve `core-office anonymize` command logic

## v0.3.6 (2024-08-06)

### Fix

- fix DELETE triggers for `meminfo`, `employees`
- avoid deprecated `AppProvider.load_object()` method

## v0.3.5 (2024-07-14)

### Fix

- update app provider entry point, per wuttjamaican
- fix CORE op model reference

## v0.3.4 (2024-07-13)

### Fix

- refactor `config.get_model()` => `app.model`
- avoid error when CORE API gives record with no upc

## v0.3.3 (2024-07-05)

### Fix

- add logic to auto-create user for CORE POS cashier login
- fix employee status when importing from CORE API
- add Employee support for CORE API -> Rattail import/datasync
- misc. improvements for CORE API importer, per flaky data
- add command to install mysql triggers for CORE `office_op` DB
- improve ProductCost sorting for import from CORE API
- include `person_uuid` for Member import from CORE API

## v0.3.2 (2024-07-02)

### Fix

- avoid deprecated function for `get_engines()` config

## v0.3.1 (2024-07-01)

### Fix

- remove legacy command definitions

## v0.3.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyrpoject.toml + hatchling

## [0.2.0] - 2024-05-29
### Changed
- Add basic support for importing from CSV to `office_arch.bigArchive`.
- Add `get_model_office_arch()` method for corepos handler.
- Misc. fixes for CORE API -> Theo importers.
- Migrate all commands to use `typer`.

## [0.1.47] - 2024-01-17
### Changed
- Truncate "blue line" text if necessary when updating CORE.

## [0.1.46] - 2023-11-30
### Changed
- Update subcommand entry point group names, per wuttjamaican.

## [0.1.45] - 2023-11-18
### Changed
- Add function for writing value to fannie config file.

## [0.1.44] - 2023-11-15
### Changed
- Add `account_holder_full_name` for CORE -> Rattail customer import.

## [0.1.43] - 2023-11-05
### Changed
- Add corepos handler method to make arch session.

## [0.1.42] - 2023-11-05
### Changed
- Equity batch rows should really get deleted.

## [0.1.41] - 2023-11-01
### Changed
- Import product sale pricing from CORE.
- Import the `Product.not_for_sale` flag from CORE-POS.
- Import Store, ProductCost from CORE DB.
- Make POS batch write more accurate `dtransactions`.

## [0.1.40] - 2023-10-15
### Changed
- Avoid false match when importing equity payments from CORE.

## [0.1.39] - 2023-10-14
### Changed
- Include `person_uuid` when importing members from CORE DB.

## [0.1.38] - 2023-10-12
### Changed
- Avoid error if CORE has invalid `products.tax` FK.
- Import tax rate, food stamp flag for departments from CORE.
- Add customer, member importers from CORE DB.

## [0.1.37] - 2023-10-07
### Changed
- Add custom POS batch handler, to push transactions to CORE.
- Add tender importer from CORE; apply tender in CORE POS batch.
- Add employee importer for CORE -> Rattail, and CORE cashier auth handler.
- Improve the `core-office anonymize` command somewhat.
- Rename config section to `[corepos.db.office_arch]`.
- Add importer for tax rates from CORE.

## [0.1.36] - 2023-09-19
### Changed
- Do not raise error if CORE equity payment not found in rattail.

## [0.1.35] - 2023-09-19
### Changed
- Fix bug when fetching corepos handler.

## [0.1.34] - 2023-09-18
### Changed
- Make CORE API client via app handler, not deprecated function.

## [0.1.33] - 2023-09-17
### Changed
- Let config override the CORE API client factory.
- Remove production hack to prevent equity import batch execution.

## [0.1.32] - 2023-09-17
### Changed
- Add `tender_code` for CORE equity import batch rows.

## [0.1.31] - 2023-09-15
### Changed
- Add "overpaid" status for equity import batch rows.

## [0.1.30] - 2023-09-15
### Changed
- Add rattail provider for CORE-POS Integration.
- Make CORE -> Rattail equity import a bit smarter re: datetime.

## [0.1.29] - 2023-09-13
### Changed
- Add first draft logic for executing CORE equity import batch.
- Add CORE-specific datetime for equity payments.

## [0.1.28] - 2023-09-13
### Changed
- Import member first/last name from CORE API.
- Add model, handler for CORE equity import batch.

## [0.1.27] - 2023-09-11
### Changed
- Add common base for commands which import straight to CORE op/trans DB.

## [0.1.26] - 2023-09-07
### Changed
- Ignore non-CORE equity payments when importing from CORE.

## [0.1.25] - 2023-09-07
### Changed
- Add support for importing MemberEquityPayment from CORE-POS DB.

## [0.1.24] - 2023-09-02
### Changed
- Import `Member.corepos_account_id` from CORE.
- Add `core-office anonymize` command.
- Add problem report for CORE phone numbers too long.

## [0.1.23] - 2023-06-12
### Changed
- Overhaul CORE API <-> Rattail importers, per CustomerShopper model etc.
- Import membership types from CORE API.
- Add new commands (and deprecate old) for CORE <-> CSV import/export.
- Add `core-office ping-install` command, for DB setup.
- Add `core-office patch-customer-gaps` command, to fix customerID.
- Rename model for `custdata` to `CustomerClassic`.

## [0.1.22] - 2023-06-03
### Changed
- Skip customer record with no member type, for blue line update.

## [0.1.21] - 2023-06-02
### Changed
- Add support for htdigest auth when using CORE webservices API.
- Add problem report for invalid `custdata` person number sequence.

## [0.1.20] - 2023-05-18
### Changed
- Add `core-office import-self` command, to fix `custdata.blueLine`.

## [0.1.19] - 2023-05-17
### Changed
- Replace `setup.py` contents with `setup.cfg`.

## [0.1.18] - 2023-05-11
### Changed
- Add behavior options for CORE member importer.

## [0.1.17] - 2023-05-09
### Changed
- Add support for `member_type_id` in CORE `MemberInfoImporter`.

## [0.1.16] - 2023-05-08
### Changed
- Avoid deprecated import for `OrderedDict`.
- Move logic for CORE importing to "more precise" module path.
- Move CORE DB import handler to more general location.

## [0.1.15] - 2023-05-01
### Changed
- Show all deprecation warnings occurring within `corepos` pkg.

## [0.1.14] - 2023-02-12
### Changed
- Refactor `Query.get()` => `Session.get()` per SQLAlchemy 1.4.

## [0.1.13] - 2023-01-03
### Changed
- Define default handler for `corepos_member` batch type.

## [0.1.12] - 2023-01-02
### Changed
- Configure DB connections for CORE trans archive on app startup.
- Fix datasync bug for CORE API -> Rattail.
- Update usage of `short_session()` per upstream changes.

## [0.1.11] - 2022-03-15
### Changed
- Add "raw" card number value to CORE Member Import batch.

## [0.1.10] - 2022-03-01
### Changed
- Some tweaks to expose CORE <-> Rattail import handlers in web app.
- Overhaul import handler config etc.
- Refactor CORE API hack to use `custdata` instead of `Customers` table.
- Avoid error if CORE product data is missing some fields.
- Refactor some importer method calls to avoid deprecation warnings.

## [0.1.9] - 2021-11-05
### Changed
- Add support for 2nd "member type" file in CORE member batch.

## [0.1.8] - 2021-11-04
### Changed
- Add `custdata` importer for CORE Office -> Lane.
- Add batch to update CORE member records directly via SQL.

## [0.1.7] - 2021-08-31
### Changed
- Add CORE Office -> Lane op importer for Department.

## [0.1.6] - 2021-08-02
### Changed
- Add email setting for CORE Office -> CORE Lane export.

## [0.1.5] - 2021-07-21
### Changed
- Add basic support for CORE Office -> CORE Lane export.

## [0.1.4] - 2021-06-11
### Changed
- Several more updates...mostly a "save point" release.

## [0.1.3] - 2020-09-19
### Changed
- Add some common email profiles, for importer diff warnings.

## [0.1.2] - 2020-09-16
### Changed
- Fix manifest to include alembic migrations.

## [0.1.1] - 2020-09-16
### Changed
- A ton of updates, mostly a "save point" release.

## [0.1.0] - 2020-02-27
### Added
- Initial version of the package; defines some basic importer/datasync logic.
