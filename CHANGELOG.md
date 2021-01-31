# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.0] - In progress

### Added

* Ability to open resizer in default browser and toggle between that versus opening it up within the GUI
* Panel sizes are now adjustable
* FFMPEG Settings Window (`SubWindows/FfmpegSettingsWindow`) to modify flags used for FFMPEG when rendering certain files/running certain commands

### Changed

* Heavy refactoring, namely:
    * Reorganized source code; rather than split by class type, split by panel function since each panel is pretty self-contained and do not really interact outside of communication between layouts from the MainWindow
    * Extract `ActionsManager` for `MainWindow`
        * This also handles global settings now
    * Modularize how dropdown VS options are handled
* Set resizer descale default to Despline36

## [v0.2.0] - 2021-01-08
* [Associated Commit hash](https://github.com/000png/vapoursynth-gui-for-gifs/commit/5accb191115d834bbfd88189da72e56ab37120fd)

### Added

* Loading and saving of presets, and history preset loaded automatically
* Can abort process
* Video name labels
* This `CHANGELOG.md`

### Changed

* Trimming now optional and done through VS, not ffmpeg
* Resizing/cropping only rerenders resizer.webm if the video state has changed

## [v0.1.0] - 2020-12-30
* [Associated PR](https://github.com/000png/vapoursynth-gui-for-gifs/pull/1)
* [Associated Commit Hash](https://github.com/000png/vapoursynth-gui-for-gifs/commit/f74cc8dffebfafd3bc6a95b77101806aa9c6dc4c)
* Initial project setup.

### Added
**Vapoursynth/Video Editing**:

* Resizing/cropping via html script in new window (descale and crop)
* Trimming (currently always enabled, does it through ffmpeg)
* Denoise vs KNLM and BM3D
* Sharpening with FineSharp

**GUI**

* Loading overlay during QProcesses
* Dual video monitors, one showing original video, and one after vapoursynth
    * If output is pngs, after-render is not shown
* Ability to toggle one or both video feeds
* Script editor
* Output terminal

**Files**:

* Easy loading video files
* Ability to save scripts
