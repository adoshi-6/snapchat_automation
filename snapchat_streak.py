import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime, timedelta

# Set UTF-8 encoding on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONFIG_PATH = "config.json"
IMAGES_DIR = "images"

def run_adb_command(cmd_args, adb_path="adb", device_id=""):
    """Runs a command via ADB and returns the stdout."""
    target_args = ["-s", device_id] if device_id else []
    full_cmd = [adb_path] + target_args + cmd_args
    try:
        result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ADB Command Failed: {' '.join(full_cmd)}")
        print(f"Error output: {e.stderr.strip()}")
        return None

def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Default configuration
        default_config = {
            "adb_path": "adb",  # adb path in system or local folder
            "adb_device_id": "", # target device ID (e.g. localhost:5555)
            "shortcut_name": "Streaks",
            "last_sent_index": -1,
            "coordinates": {
                "gallery_icon": "200 1800",       # click coordinates
                "camera_roll_tab": "540 180",
                "first_photo": "200 350",
                "edit_send_button": "900 1800",
                "search_bar": "300 120",
                "first_search_result": "250 250",
                "select_all_shortcut": "920 250",  # select all button in shortcut
                "send_arrow": "950 1800"
            }
        }
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
        
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def get_next_image(config):
    """Retrieves the path of the next image to send."""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"[INFO] Created '{IMAGES_DIR}/' folder. Please place your images there.")
        return None
        
    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if not images:
        print(f"[WARNING] No images found in '{IMAGES_DIR}/' folder. Please add some pictures.")
        return None
        
    next_index = (config["last_sent_index"] + 1) % len(images)
    config["last_sent_index"] = next_index
    save_config(config)
    
    return os.path.join(IMAGES_DIR, images[next_index])

def tap_coordinate(coord_str, adb_path, device_id=""):
    """Helper to tap a coordinate string formatted as 'X Y'"""
    run_adb_command(["shell", "input", "tap", coord_str], adb_path, device_id)
    time.sleep(1.0)

def execute_streak():
    config = load_config()
    adb_path = config["adb_path"]
    device_id = config.get("adb_device_id", "")
    
    # Select next image
    image_path = get_next_image(config)
    if not image_path:
        return False
        
    print(f"[INFO] Preparing to send: {os.path.basename(image_path)}")
    
    # Check ADB connection
    devices = run_adb_command(["devices"], adb_path, device_id)
    if not devices or len(devices.splitlines()) <= 1:
        print("[ERROR] No ADB devices detected! Please launch your emulator and make sure USB debugging is on.")
        return False
        
    print("[INFO] ADB Device detected. Proceeding...")

    # Destination on Android
    android_dest = "/sdcard/Pictures/streak.jpg"
    
    # Push image to emulator
    print(f"[INFO] Pushing image to emulator -> {android_dest}")
    run_adb_command(["push", image_path, android_dest], adb_path, device_id)
    
    # Trigger media scan
    print("[INFO] Forcing Android Media scan...")
    # Broadcast scanner
    run_adb_command(["shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{android_dest}"], adb_path, device_id)
    # Content provider scanner
    run_adb_command(["shell", "content", "call", "--uri", "content://media", "--method", "scan_file", "--arg", android_dest], adb_path, device_id)
    time.sleep(2.0)
    
    # Launch Snapchat
    print("[INFO] Launching Snapchat...")
    run_adb_command(["shell", "am", "start", "-n", "com.snapchat.android/com.snap.mushroom.MainActivity"], adb_path, device_id)
    time.sleep(5.0) # Wait for Snapchat to load

    coords = config["coordinates"]
    
    # Simulate UI Actions
    print("[INFO] Navigating Snapchat UI...")
    
    print("  Tapping Gallery Icon...")
    tap_coordinate(coords["gallery_icon"], adb_path, device_id)
    
    print("  Tapping Camera Roll Tab...")
    tap_coordinate(coords["camera_roll_tab"], adb_path, device_id)
    
    print("  Selecting First Photo...")
    tap_coordinate(coords["first_photo"], adb_path, device_id)
    
    print("  Tapping Edit / Send Button...")
    tap_coordinate(coords["edit_send_button"], adb_path, device_id)
    
    print("  Tapping Search Bar...")
    tap_coordinate(coords["search_bar"], adb_path, device_id)
    
    print(f"  Typing Shortcut Name: '{config['shortcut_name']}'...")
    run_adb_command(["shell", "input", "text", config["shortcut_name"]], adb_path, device_id)
    time.sleep(2.0)
    
    print("  Selecting Shortcut from search results...")
    tap_coordinate(coords["first_search_result"], adb_path, device_id)
    
    print("  Tapping Select All inside the shortcut...")
    tap_coordinate(coords["select_all_shortcut"], adb_path, device_id)
    
    print("  Tapping Send Arrow...")
    tap_coordinate(coords["send_arrow"], adb_path, device_id)
    
    print("[SUCCESS] Daily Streak Sent successfully!")
    return True

def log_run(status, message=""):
    """Logs run status to scheduler.log."""
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STATUS: {status} | {message}\n")

def sleep_until_time(target_time_str):
    """Sleeps until the target daily time (HH:MM)."""
    try:
        hour, minute = map(int, target_time_str.split(':'))
    except ValueError:
        print(f"[ERROR] Invalid time format: {target_time_str}. Expected HH:MM.")
        sys.exit(1)
        
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if target_time <= now:
        # Target time has already passed today, scheduled for tomorrow
        target_time += timedelta(days=1)
        
    wait_seconds = (target_time - now).total_seconds()
    print(f"[INFO] Sleeping until target run time: {target_time.strftime('%Y-%m-%d %H:%M:%S')} ({wait_seconds:.0f} seconds)...")
    time.sleep(wait_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapchat Streak Automation Daemon")
    parser.add_argument("--once", action="store_true", help="Run the streak once and exit (default)")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode daily at specified time")
    parser.add_argument("--time", type=str, default="10:00", help="Target daily execution time in HH:MM format (default: 10:00)")
    args = parser.parse_args()

    if args.daemon:
        print(f"[INFO] Starting Snapchat Streak Automation in daemon mode. Target time: {args.time} daily.")
        log_run("STARTED", f"Daemon mode enabled for daily time: {args.time}")
        while True:
            sleep_until_time(args.time)
            print("[INFO] Triggering daily streak run...")
            try:
                success = execute_streak()
                if success:
                    log_run("SUCCESS", "Daily streak executed successfully.")
                else:
                    log_run("FAILED", "Daily streak execution failed (see terminal output for details).")
            except Exception as e:
                print(f"[ERROR] Error during execution: {e}")
                log_run("ERROR", f"Exception during run: {e}")
    else:
        # Run once
        success = execute_streak()
        if success:
            log_run("ONCE_SUCCESS", "Executed streak once successfully.")
        else:
            log_run("ONCE_FAILED", "Executed streak once with failures.")
