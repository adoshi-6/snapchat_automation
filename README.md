# Snapchat Streak Automation

An automated tool to cycle through local photos (e.g., world monuments) and send them as daily Snapchat Streaks to a specific Snapchat Shortcut group. It runs on Windows, utilizing an Android Emulator (like LDPlayer) or a physical Android device connected via ADB (Android Debug Bridge).

---

## Features
- **Photo Cycling:** Dynamically tracks and cycles through images in a local folder (`monuments/`).
- **Media Scan Integration:** Automatically forces the Android media library to index newly pushed files, ensuring they appear instantly in Snapchat's Camera Roll.
- **Snapchat UI Automation:** Simulates screen taps, typing, and searching via ADB.
- **Daily Scheduling Daemon:** Can run in loop mode (`--daemon`) calculating exact sleeping intervals, or register natively with **Windows Task Scheduler** to trigger daily at a set time.
- **UTF-8 Output Support:** Built-in console reconfiguration to prevent Unicode errors when printing status emoji flags on Windows command lines.

---

## Setup Guide

### 1. Enable Virtualization Technology (VT)
Android Emulators require hardware virtualization to run smoothly.
1. In Windows, go to **Settings > Update & Security > Recovery**.
2. Under **Advanced startup**, click **Restart now**.
3. On the reboot screen, select **Troubleshoot > Advanced options > UEFI Firmware Settings**, and click **Restart**.
4. Once inside your BIOS settings:
   - **Intel CPU:** Locate **Intel Virtualization Technology** (or VT-x) and change it to **Enabled**.
   - **AMD CPU:** Locate **SVM Mode** (or Secure Virtual Machine) and change it to **Enabled**.
5. Save changes and exit (**F10**).

### 2. Set Up the Android Emulator (LDPlayer 9)
1. Download and install [LDPlayer 9](https://www.ldplayer.net/).
2. Open LDPlayer settings (gear icon on the right sidebar), navigate to **Advanced**, and set the resolution to **Mobile (1080 x 1920)**. Save and restart the emulator.

#### Bypassing Google Play Store Login / Parental Restrictions:
If you cannot sign in to the Google Play Store (due to parental supervision accounts, managed accounts, or network blocks), you can install Snapchat directly:
1. On your host computer, navigate to [APKMirror Snapchat](https://www.apkmirror.com/apk/snap-inc/snapchat/).
2. Download the latest stable version of the **Snapchat APK** (avoid the *Bundle* and *Beta* options).
3. Open LDPlayer and drag-and-drop the downloaded `.apk` file directly onto the emulator screen to install it instantly.

### 3. Configure Snapchat & Enable Debugging
1. Open Snapchat in the emulator, log in, and create a **Shortcut** containing all friends you wish to send streaks to. Make sure it matches the shortcut name in your config (defaults to `"Streaks"`).
2. **Enable USB Debugging in the Emulator:**
   - Go to **System Apps > Settings > About Tablet**.
   - Scroll to the bottom and click **Build Number** 7 times.
   - Go back, open **Developer Options**, and toggle **USB Debugging** to **On**.

*Note: If your server lacks internet access and you are using Internet Connection Sharing (ICS) from another PC, ensure you share the internet to the **Ethernet** network adapter in your host network settings (`ncpa.cpl`).*

---

## File Structure
- `snapchat_streak.py` - Core execution script.
- `config.json` - ADB path, Snapchat shortcut settings, and screen tap coordinates.
- `setup_scheduler.ps1` - PowerShell helper to register a Windows Scheduled Task.
- `monuments/` - Folder containing the images you want to cycle through.
- `scheduler.log` - File logging success/failure audits.

---

## How to Configure
Tap coordinates are stored inside `config.json`. If buttons are missed, you can turn on **Pointer Location** in the emulator's Developer Options, tap the buttons manually to view their `X Y` pixel coordinates, and update them in `config.json`:

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

---

## Execution & Scheduling

Create a folder named `monuments/` in the same directory as the script and place your cycle photos inside it.

### Run Once
To execute a single test run:
```bash
python snapchat_streak.py --once
```

### Run in Daemon Loop Mode
To keep the script running in a loop, sleeping automatically until the next scheduled daily time:
```bash
python snapchat_streak.py --daemon --time 10:00
```

### Register with Windows Task Scheduler (Recommended)
To register the task to run automatically in the background even if your terminal window is closed, run the following command in PowerShell as Administrator:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
```
*Make sure to specify your daily time when prompted.*
