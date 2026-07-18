# Snapchat Streak Automation Plan

This standalone project automates sending daily Snapchat streaks cycling through a catalog of photos using an Android emulator and ADB (Android Debug Bridge).

## Core Architecture
1. **Photo Catalog:** A local folder `images/` containing photos to cycle through.
2. **Cycle Logic:** A Python script tracks the last sent image, picks the next one, and copies it to the Android Emulator's shared gallery folder.
3. **Android Media Scan:** Python triggers an ADB command to force Android to scan the shared folder, making the new photo immediately visible in Snapchat's "Camera Roll".
4. **Snapchat UI Automation:** ADB simulates tap and search inputs to:
   - Launch Snapchat.
   - Open the Gallery / Camera Roll.
   - Select the newly added photo.
   - Tap "Send To".
   - Search for a specific Snapchat shortcut (e.g., "Streaks").
   - Select all friends in that shortcut and tap Send.

## Project Structure
- `snapchat_streak.py` - Core Python script containing ADB shell command sequences.
- `images/` - Directory holding images to cycle through.
- `config.json` - Settings for ADB port, shortcut name, and tracking history.
- `adb/` - (Optional) Portable ADB binaries.

## Setup Requirements
1. **Android Emulator:** Install [LDPlayer](https://www.ldplayer.net/) or [BlueStacks](https://www.bluestacks.com/) (LDPlayer is recommended for lightweight headless execution).
2. **Snapchat App:** Installed and logged in on the emulator.
3. **USB Debugging / ADB Enabled:** Enabled in the emulator's Developer Options.
