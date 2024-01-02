# Changelog

## [0.10.0] - 2024-01-02
### Changed
- Made arg `screen_resolution` of function `setup_robot` optional. This is intended for testing/development purpouses since some RDP sessions are killed when changing resolution. This change was made with backwards compatibility in mind

## [0.9.0] - 2023-11-16
### Added
- New function `is_account_number_valid` to validate account numbers using a weighted checksum algorithm, ensuring their compliance with ECBS standards.

## [0.8.0] - 2023-09-11
### Added
- [#22](https://github.com/ultimaterpa/urpautils/issues/22) : function `add_timestamp_to_filename` which adds a timestamp to the file name in the given absolute file path.

## [0.7.1] 2023-06-20
### Fixed
- [#20](https://github.com/ultimaterpa/urpautils/issues/20) : function `repeat`

## [0.7.0] 2022-11-10
### Added
- [#19](https://github.com/ultimaterpa/urpautils/issues/19) : function `robot_has_time`

## [0.6.0] 2022-09-15
### Added
- [#15](https://github.com/ultimaterpa/urpautils/pull/15) : decorator `repeat` for repeating an action on element
- [#17](https://github.com/ultimaterpa/urpautils/pull/17) : function `check_elements_reversed` which raises error if an element is found

## [0.5.0] 2022-09-06
### Added
- [#13](https://github.com/ultimaterpa/urpautils/issues/13) : function `justify_ico`

## [0.4.3] 2022-01-19
### Fixed
- [#12](https://github.com/ultimaterpa/urpautils/pull/12) : Fixed sending attachments with `send_email_notification()`

## [0.4.2] 2021-10-27
## Changed
- Option to set debug level for `send_email_notification()` function

## [0.4.1] 2021-10-21
## Changed
- `Csv_dict_writer` now requires `field_names` for initialization

## [0.4.0] 2021-10-14
- Added function `read_json()`
- [#7](https://github.com/ultimaterpa/urpautils/issues/7) : Added option to read csv file as dictionary to function `csv_read_rows()` via `as_dict` arg
- [#7](https://github.com/ultimaterpa/urpautils/issues/7) : Added class `Csv_dict_writer` for writing dictionary to csv
- Added optional arg `sep` to `csv_create_file()`. If provided it writes "sep=<separator>" to first line of the file so it opens correctly in Excel

## [0.3.0] 2021-09-06
### Added
- Optional arg `attachments` to `send_email_notification` function
- [#4](https://github.com/ultimaterpa/urpautils/issues/4) : Decorator function `failed_login_notification` for sending an email notification with error screenshot

### Changed
- Finding the path of an error screenshot is now done via private function `_get_error_screenshot_path`

## [0.2.0] 2021-08-31
### Added
- [#5](https://github.com/ultimaterpa/urpautils/issues/5) : `save_as` function for working with Windows Save As dialogue
- [#5](https://github.com/ultimaterpa/urpautils/issues/5) : `open_file` function for working with Windows Open dialogue
- [#6](https://github.com/ultimaterpa/urpautils/issues/6) : `get_previous_work_day_date` function for getting date of previous work day

## [0.1.3] 2021-08-12
### Changed
- `copy_error_image` now reads main file name from stack trace

### Fixed
- setting screen resolution in `robot_setup` function

## [0.1.2] 2021-08-10

### Changed
- utf-8 encoding for README in setup.py

## [0.1.1] 2021-08-04

### Added
- Typing support
- Preparation for PyPi publishing (setup.py, MANIFEST.in, __about__.py)

### Changed
- Moved imports for tests to tests/__init__.py file

## [0.1.0] 2021-08-03

### Added
- Everything (first release)
