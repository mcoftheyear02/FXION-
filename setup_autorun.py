# FXION-ONYX -- Install/Remove Startup Auto-Run
# Run as: python setup_autorun.py install   -> adds to Windows startup
#         python setup_autorun.py remove    -> removes from startup

import sys, os, shutil

# Resolve Windows Startup folder
APPDATA = os.environ.get("APPDATA")
if not APPDATA:
    print("[ERROR] APPDATA environment variable not set. Are you on Windows?")
    sys.exit(1)

STARTUP_FOLDER = os.path.join(APPDATA, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
BAT_NAME = "fxion_startup.bat"
ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, BAT_NAME)
DEST = os.path.join(STARTUP_FOLDER, BAT_NAME)


def install():
    # Verify source .bat exists
    if not os.path.isfile(SOURCE):
        print(f"[ERROR] {SOURCE} not found")
        sys.exit(1)

    # Verify startup folder exists
    if not os.path.isdir(STARTUP_FOLDER):
        print(f"[ERROR] Startup folder not found: {STARTUP_FOLDER}")
        sys.exit(1)

    # Copy to startup
    shutil.copy2(SOURCE, DEST)
    print(f"[OK] Installed to Windows Startup:")
    print(f"     {DEST}")
    print(f"     FXION Q8 will auto-run on every login.")

    # Verify it was written
    if os.path.isfile(DEST):
        print(f"[VERIFIED] File exists ({os.path.getsize(DEST)} bytes)")
    else:
        print(f"[ERROR] Copy failed -- file not found at destination")
        sys.exit(1)


def remove():
    if os.path.isfile(DEST):
        os.remove(DEST)
        if not os.path.isfile(DEST):
            print(f"[OK] Removed from Windows Startup.")
        else:
            print(f"[ERROR] Failed to remove: {DEST}")
    else:
        print(f"[INFO] Not installed -- nothing to remove.")


def status():
    print(f"[INFO] Startup folder: {STARTUP_FOLDER}")
    print(f"[INFO] Source .bat:    {SOURCE} {'(EXISTS)' if os.path.isfile(SOURCE) else '(MISSING)'}")
    print(f"[INFO] Installed:      {DEST} {'(YES)' if os.path.isfile(DEST) else '(NO)'}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("install", "remove", "status"):
        print("Usage: python setup_autorun.py install|remove|status")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "install":
        install()
    elif cmd == "remove":
        remove()
    elif cmd == "status":
        status()
