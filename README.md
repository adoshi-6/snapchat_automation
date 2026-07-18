# Snapchat Streak Automation

An automated tool to cycle through local photos and send them as daily Snapchat Streaks to a specific Snapchat Shortcut group. The script runs on Windows and controls an Android Emulator (such as LDPlayer) or a physical Android device connected via USB.

**Note:** This tool is only compatible with Android environments. It relies on the Android Debug Bridge (ADB) to simulate screen inputs and does not support iOS devices (iPhones).

## Features
- Cycles through images in a local folder (`monuments/`).
- Triggers the Android media library to index newly pushed files, making them immediately visible in the Snapchat Camera Roll.
- Simulates screen taps, text input, and searches via ADB.
- Includes a daily scheduling daemon (`--daemon`) that calculates wait times between runs.
- Includes a PowerShell script to register the automation natively with Windows Task Scheduler to run daily at a set time.
- Configured to support UTF-8 stdout encoding on Windows systems to handle log outputs correctly.

## Setup Instructions

### 1. Enable Virtualization Technology (VT)
Android emulators require hardware virtualization to run.
1. Open Windows Settings, go to Update & Security, and select Recovery.
2. Under Advanced startup, click Restart now.
3. On the options screen, select Troubleshoot > Advanced options > UEFI Firmware Settings, and click Restart.
4. In the BIOS configuration utility:
   - For Intel CPUs: Enable Intel Virtualization Technology (VT-x or VT-d).
   - For AMD CPUs: Enable SVM Mode (Secure Virtual Machine).
5. Save changes and exit (usually F10).

### 2. Set Up the Android Emulator
1. Download and install LDPlayer 9.
2. Open LDPlayer settings, go to the Advanced tab, set the resolution to Mobile (1080 x 1920), and restart the emulator.

#### Bypassing Google Play Store Login / Account Restrictions
If you cannot sign in to the Google Play Store on your emulator due to parental supervision or account restrictions:
1. Open a browser on your computer and navigate to the Snapchat page on APKMirror.
2. Download the latest stable Snapchat APK (do not download the Bundle or Beta versions).
3. Drag the downloaded .apk file and drop it into the LDPlayer window to install it directly without logging in to a Google account.

### 3. Configure Snapchat and Android Settings
1. Open Snapchat in the emulator, log in, and create a Shortcut containing all friends you want to send streaks to. Verify that the shortcut name matches the setting in your config.json (defaults to "Streaks").
2. Enable USB Debugging in the emulator:
   - Go to Settings > About Tablet.
   - Scroll to the bottom and click Build Number 7 times.
   - Go to Developer Options and toggle USB Debugging to On.

If the emulator cannot connect to the internet and you are sharing your connection from another PC using Windows Internet Connection Sharing (ICS), make sure to configure the sharing settings to point to the Ethernet network adapter.

## File Structure
- `snapchat_streak.py`: Main execution script.
- `config.json`: Configuration settings for the ADB path, Snapchat shortcut, run history, and tap coordinates.
- `setup_scheduler.ps1`: PowerShell script to register the Windows Scheduled Task.
- `monuments/`: Directory holding the images to cycle through.
- `scheduler.log`: Log file tracking script run status.

## Configuration
Screen coordinates are configured in `config.json`. If button positions differ on your screen resolution, enable Pointer Location in the emulator's Developer Options, tap the target elements to find their X/Y coordinates, and update them in the configuration file:

```json
{
    "adb_path": "adb",
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

## Usage

Add your photos (such as monument images) to the pre-created `monuments/` folder. The folder itself is tracked in Git, but its contents are ignored so your personal photos will not be committed.

### Single Run
To run the script once for testing:
```bash
python snapchat_streak.py --once
```

### Daemon Mode
To keep the script running in the background, sleeping until the scheduled time each day:
```bash
python snapchat_streak.py --daemon --time 10:00
```

### Windows Scheduled Task
To register the script to run automatically in the background under your user session:
1. Open PowerShell as Administrator.
2. Execute the setup script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
   ```
3. Enter your preferred daily run time when prompted.
