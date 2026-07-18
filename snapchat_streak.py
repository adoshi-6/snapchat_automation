import os
import sys
import json
import time
import subprocess

# Config paths
CONFIG_PATH = "config.json"
MONUMENTS_DIR = "monuments"

def run_adb_command(cmd_args, adb_path="adb"):
    """Runs a command via ADB and returns the stdout."""
    full_cmd = [adb_path] + cmd_args
    try:
        result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ ADB Command Failed: {' '.join(full_cmd)}")
        print(f"Error output: {e.stderr.strip()}")
        return None

def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Create default config
        default_config = {
            "adb_path": "adb",  # Assumes adb is in system PATH, or specify full path
            "adb_device_id": "", # Empty uses default/only device
            "shortcut_name": "Streaks",
            "last_sent_index": -1,
            "coordinates": {
                "gallery_icon": "200 1800",       # Adjust based on emulator screen resolution
                "camera_roll_tab": "540 180",
                "first_photo": "200 350",
                "edit_send_button": "900 1800",
                "search_bar": "300 120",
                "first_search_result": "250 250",
                "select_all_shortcut": "920 250",  # Tapping 'select all' button in shortcut
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

def get_next_monument(config):
    """Retrieves the path of the next monument image to send."""
    if not os.path.exists(MONUMENTS_DIR):
        os.makedirs(MONUMENTS_DIR)
        print(f"📁 Created '{MONUMENTS_DIR}/' folder. Please place your monument images there.")
        return None
        
    images = sorted([f for f in os.listdir(MONUMENTS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if not images:
        print(f"⚠️ No images found in '{MONUMENTS_DIR}/' folder. Please add some pictures.")
        return None
        
    next_index = (config["last_sent_index"] + 1) % len(images)
    config["last_sent_index"] = next_index
    save_config(config)
    
    return os.path.join(MONUMENTS_DIR, images[next_index])

def tap_coordinate(coord_str, adb_path):
    """Helper to tap a coordinate string formatted as 'X Y'"""
    run_adb_command(["shell", "input", "tap", coord_str], adb_path)
    time.sleep(1.0)

def execute_streak():
    config = load_config()
    adb_path = config["adb_path"]
    
    # 1. Select the next image
    image_path = get_next_monument(config)
    if not image_path:
        return
        
    print(f"📸 Preparing to send: {os.path.basename(image_path)}")
    
    # 2. Check ADB connection
    devices = run_adb_command(["devices"], adb_path)
    if not devices or len(devices.splitlines()) <= 1:
        print("❌ No ADB devices detected! Please launch your emulator and make sure USB debugging is on.")
        return
        
    print("🤖 ADB Device detected. Proceeding...")

    # Destination on Android
    android_dest = "/sdcard/Pictures/streak.jpg"
    
    # 3. Push image to emulator
    print(f"📤 Pushing image to emulator -> {android_dest}")
    run_adb_command(["push", image_path, android_dest], adb_path)
    
    # 4. Trigger Media Scan to update the gallery instantly
    print("🔄 Forcing Android Media scan...")
    # Standard broadcast scanner
    run_adb_command(["shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{android_dest}"], adb_path)
    # Modern content call scanner just in case
    run_adb_command(["shell", "content", "call", "--uri", "content://media", "--method", "scan_file", "--arg", android_dest], adb_path)
    time.sleep(2.0)
    
    # 5. Launch Snapchat
    print("👻 Launching Snapchat...")
    run_adb_command(["shell", "am", "start", "-n", "com.snapchat.android/com.snap.mushroom.MainActivity"], adb_path)
    time.sleep(5.0) # Wait for snapchat to fully load

    coords = config["coordinates"]
    
    # 6. Simulate UI Actions
    print("👉 Navigating Snapchat UI...")
    
    print("  Tapping Gallery Icon...")
    tap_coordinate(coords["gallery_icon"], adb_path)
    
    print("  Tapping Camera Roll Tab...")
    tap_coordinate(coords["camera_roll_tab"], adb_path)
    
    print("  Selecting First Photo...")
    tap_coordinate(coords["first_photo"], adb_path)
    
    print("  Tapping Edit / Send Button...")
    tap_coordinate(coords["edit_send_button"], adb_path)
    
    print("  Tapping Search Bar...")
    tap_coordinate(coords["search_bar"], adb_path)
    
    print(f"  Typing Shortcut Name: '{config['shortcut_name']}'...")
    run_adb_command(["shell", "input", "text", config["shortcut_name"]], adb_path)
    time.sleep(2.0)
    
    print("  Selecting Shortcut from search results...")
    tap_coordinate(coords["first_search_result"], adb_path)
    
    print("  Tapping Select All inside the shortcut...")
    tap_coordinate(coords["select_all_shortcut"], adb_path)
    
    print("  Tapping Send Arrow...")
    tap_coordinate(coords["send_arrow"], adb_path)
    
    print("✅ Daily Streak Sent successfully!")

if __name__ == "__main__":
    execute_streak()
