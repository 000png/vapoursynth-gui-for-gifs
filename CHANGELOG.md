# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.0.2] - in progress

### Added

* Loading and saving of presets, and history preset loaded automatically
* This `CHANGELOG.md`

### Changed

* Trimming now optional (will skip ffmpeg step)
* Resizing/cropping only rerenders resizer.webm if the video state has changed

## [v0.0.1] - 2020-12-30
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
