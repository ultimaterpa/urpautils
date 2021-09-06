# Changelog
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
