# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-06-04

### Removed

- Remove RARBG check in the file name

### Changed

- Transition linting to `ruff`
- `ruff` and `black` added to development dependencies
- Default to searching for subtitles via size in the expected folder
- Updated README with features

### Added

- Episode subtitle searching will now fall back to matching folders based on SxxEyy naming,
  if the expected folder by name doesn't exist

## 0.1.0

- Simplified the handling logic
- Updated pre-commit hooks
- Added logic to handle VXT release group subtitles
- Fixes documentation for LinuxServer.io customization

## 0.0.1

- Initial release of a version which at least worked for me
