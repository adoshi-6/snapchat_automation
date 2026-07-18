# Snapchat Streak Automation

An automated tool to cycle through local photos and send them as daily Snapchat Streaks to a specific Snapchat Shortcut group. The script runs on Windows and controls an Android environment (either a standard emulator like LDPlayer, a physical Android device, or a headless Docker container running ReDroid) via ADB (Android Debug Bridge).

**Note:** This tool is only compatible with Android environments. It does not support iOS devices (iPhones).

---

## Features
- Cycles through images in a local folder (`images/`).
- Triggers the Android media library to index newly pushed files, making them immediately visible in the Snapchat Camera Roll.
- Simulates screen taps, text input, and searches via ADB.
- Supports target device selection, allowing multiple emulators or containers to run concurrently.
- Includes a daily scheduling daemon (`--daemon`) that calculates wait times between runs.
- Includes a PowerShell script to register the automation natively with Windows Task Scheduler to run daily at a set time.
- Configured to support UTF-8 stdout encoding on Windows systems to prevent logging character crashes.

---

## File Structure
- `snapchat_streak.py`: Main execution script.
- `config.json`: Configuration settings for the ADB path, Snapchat shortcut, run history, and tap coordinates.
- `setup_scheduler.ps1`: PowerShell script to register the Windows Scheduled Task.
- `images/`: Directory holding the images to cycle through (tracked in Git, but contents are ignored).
- `scheduler.log`: Log file tracking script run status.

---

## Configuration

Settings are stored in `config.json`. Update the fields to match your environment:

```json
{
    "adb_path": "adb.exe",
    "adb_device_id": "localhost:5555",
    "shortcut_name": "Streaks",
    "last_sent_index": -1,
    "coordinates": {
        "gallery_icon": "200 1800",
        "camera_roll_tab": "540 180",
        "first_photo": "200 350",
        "edit_send_button": "900 1800",
        "search_bar": "300 120",
        "first_search_result": "250 250",
        "select_all_shortcut": "920 250",
        "send_arrow": "950 1800"
    }
}
```

- `adb_path`: Path to your local `adb.exe`. If placed in the project folder, set to `"adb.exe"`.
- `adb_device_id`: Leave empty (`""`) to connect to the default local emulator, or set to a target IP/port (e.g. `"localhost:5555"`) for Docker.
- `shortcut_name`: The exact name of your Snapchat shortcut group.
- `coordinates`: Pixel coordinates of target UI elements. If buttons are missed, enable Pointer Location in your Android Developer Settings to find the correct coordinates for your device.

---

## Setup Instructions

Choose either **Method A (Standard Emulator)** or **Method B (Headless Docker Container)**.

### Method A: Standard Android Emulator (LDPlayer 9)

#### 1. Enable Virtualization Technology (VT)
Android emulators require hardware virtualization to run.
1. Open Windows Settings, go to Update & Security, and select Recovery.
2. Under Advanced startup, click Restart now.
3. Select Troubleshoot > Advanced options > UEFI Firmware Settings, and click Restart.
4. In the BIOS utility, locate and enable **Intel Virtualization Technology** (for Intel CPUs) or **SVM Mode** (for AMD CPUs).
5. Save changes and exit.

#### 2. Install LDPlayer 9
1. Download and install LDPlayer 9.
2. Open settings (gear icon), select the Advanced tab, set the resolution to Mobile (1080 x 1920), and restart the emulator.

#### 3. Bypassing Google Play Store Login / Restrictions
If you cannot sign in to the Google Play Store on your emulator due to parental supervision or account restrictions:
1. Download the latest stable Snapchat APK from APKMirror.
2. Drag the downloaded .apk file and drop it into the LDPlayer window to install it directly without logging in to a Google account.

#### 4. Configure Snapchat and Android Settings
1. Open Snapchat, log in, and create a Shortcut containing all friends you want to send streaks to. Name it "Streaks" (or update `config.json` to match).
2. Enable USB Debugging in the emulator:
   - Go to Settings > About Tablet.
   - Click Build Number 7 times.
   - Go back, open Developer Options, and toggle USB Debugging to On.

---

### Method B: Headless Android Container (ReDroid in Docker)
For a lightweight, headless server setup running in the background without drawing GUI windows.

#### 1. Setup Docker
1. Install Docker Desktop for Windows (ensure WSL2 backend is selected).
2. Update WSL to the latest version by running `wsl --update` in an Administrator Command Prompt.

#### 2. Start the ReDroid Container
Run the following command to download and start a headless Android 11 container with port 5555 forwarded:
```powershell
docker run -itd --privileged --name redroid-container -p 5555:5555 redroid/redroid:11.0.0-latest
```

#### 3. Download ADB Tool
1. Download the Google Android Platform Tools for Windows.
2. Extract the ZIP and copy `adb.exe`, `AdbWinApi.dll`, and `AdbWinOutApi.dll` directly into the `snapchat_automation` project folder.

#### 4. Configure and Connect
1. Connect ADB to the container:
   ```bash
   adb connect localhost:5555
   ```
2. Download Snapchat APK from APKMirror and install it:
   ```bash
   adb -s localhost:5555 install path/to/snapchat.apk
   ```
3. To log in and configure your shortcut on the headless screen, download the open-source tool **scrcpy** (Screen Copy). Run `scrcpy.exe -s localhost:5555` to display the virtual Android screen on your desktop, log in, set up your "Streaks" shortcut, and close the stream.

---

## Usage

### Adding Photos
Add your photos (such as JPEGs or PNGs) to the pre-created `images/` folder. The folder itself is tracked in Git, but its contents are ignored so your personal photos will not be committed. The script will automatically cycle through the images inside this directory.

### Running the Automation

#### Single Execution (Test Run)
To run the script once:
```bash
python snapchat_streak.py --once
```

#### Daemon Mode (Daily Schedule Loop)
To run the script continuously in a background loop that sleeps automatically until the scheduled time each day:
```bash
python snapchat_streak.py --daemon --time 10:00
```

#### Windows Task Scheduler (Recommended)
To run the script automatically in the background even if your terminal is closed:
1. Open PowerShell as Administrator.
2. Execute the setup script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
   ```
3. Enter your preferred daily execution time when prompted.
