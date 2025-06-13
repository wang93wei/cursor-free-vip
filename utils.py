import os
import sys
import platform
import random
import shutil # Added shutil import

def get_user_documents_path():
    """Get user documents path, ensuring it's a valid directory."""
    path = None
    if platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
                path, _ = winreg.QueryValueEx(key, "Personal")
        except Exception: # Catch any exception from winreg, including FileNotFoundError or OSError
            path = os.path.expanduser("~\\Documents")
    else: # macOS and Linux
        path = os.path.expanduser("~/Documents")

    if path and os.path.isdir(path):
        return path

    # Fallback for Windows if primary Document folder is not standard or accessible via registry
    # and the default expanduser path is not a dir.
    if platform.system() == "Windows" and path != os.path.expanduser("~\\Documents"): # if registry failed
        path = os.path.expanduser("~\\Documents")
        if path and os.path.isdir(path):
            return path

    # Final check for all OS if the primary method + simple Documents folder didn't work
    # Try just home directory as a last resort, if it's a directory.
    home_path = os.path.expanduser("~")
    if os.path.isdir(home_path): # Check if home path itself is a directory
        # At this point, we couldn't find "Documents", so returning home might be better than None
        # depending on use case. For this function, "Documents" path is specific.
        # So, if "~/Documents" wasn't valid, returning just "~" might be misleading.
        # Let's stick to returning None if "~/Documents" (or windows equivalent) is not a dir.
        pass

    return None # If path is not a valid directory after all attempts
    
def get_default_driver_path(browser_type='chrome'):
    """Get default driver path based on browser type"""
    driver_name = ''
    if browser_type.lower() == 'chrome':
        driver_name = 'chromedriver'
    elif browser_type.lower() == 'edge':
        driver_name = 'msedgedriver'
    elif browser_type.lower() == 'firefox':
        driver_name = 'geckodriver'
    elif browser_type.lower() == 'brave':
        driver_name = 'chromedriver'  # Brave uses chromedriver
    else:
        # Default to Chrome if browser type is unknown or not supported
        driver_name = 'chromedriver'

    if sys.platform == "win32" and not driver_name.endswith(".exe"):
        driver_name += ".exe"

    # 1. Try shutil.which()
    driver_path = shutil.which(driver_name)
    if driver_path:
        return driver_path

    # 2. Check for frozen executable context (e.g., PyInstaller)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') and sys._MEIPASS is not None:
        # sys._MEIPASS is the path to the temporary folder created by PyInstaller
        frozen_path = os.path.join(sys._MEIPASS, 'drivers', driver_name)
        if os.path.exists(frozen_path):
            return frozen_path

    # 3. Check relative to utils.py (development)
    #    or for Linux if not found by shutil.which and not frozen
    dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", driver_name)
    if os.path.exists(dev_path):
        return dev_path

    # 4. For Linux, specific system paths were previously checked,
    #    but shutil.which() should cover /usr/local/bin, /usr/bin, etc.
    #    If it's not found by now on Linux, it's likely not in a standard PATH location
    #    or the specific `drivers` subdirectories.

    return None # If not found in any of the locations

def get_default_chrome_driver_path():
    """Get default Chrome driver path"""
    return get_default_driver_path('chrome')

def get_default_edge_driver_path():
    """Get default Edge driver path"""
    return get_default_driver_path('edge')

def get_default_firefox_driver_path():
    """Get default Firefox driver path"""
    return get_default_driver_path('firefox')

def get_default_brave_driver_path():
    """Get default Brave driver path (uses Chrome driver)"""
    return get_default_driver_path('brave')

def get_default_browser_path(browser_type='chrome'):
    """Get default browser executable path"""
    requested_browser_type = browser_type.lower()

    browser_config = {
        'chrome': {
            'executables': {'win32': 'chrome.exe', 'darwin': 'Google Chrome', 'linux': ['google-chrome', 'chrome', 'chromium-browser', 'chromium']},
            'bundle_ids': {'darwin': 'com.google.Chrome'},
            'win_reg_paths': [r'Google\Chrome\Application'],
            'mac_app_paths': [r'/Applications/Google Chrome.app'],
            'linux_paths': ['/opt/google/chrome/', '/usr/bin/'] # shutil.which should cover /usr/bin
        },
        'edge': {
            'executables': {'win32': 'msedge.exe', 'darwin': 'Microsoft Edge', 'linux': ['microsoft-edge', 'msedge']},
            'bundle_ids': {'darwin': 'com.microsoft.edgemac'},
            'win_reg_paths': [r'Microsoft\Edge\Application'],
            'mac_app_paths': [r'/Applications/Microsoft Edge.app'],
            'linux_paths': ['/opt/microsoft/msedge/', '/usr/bin/'] # shutil.which should cover /usr/bin
        },
        'firefox': {
            'executables': {'win32': 'firefox.exe', 'darwin': 'firefox', 'linux': ['firefox']},
            'bundle_ids': {'darwin': 'org.mozilla.firefox'},
            'win_reg_paths': [r'Mozilla Firefox'],
            'mac_app_paths': [r'/Applications/Firefox.app'],
            'linux_paths': ['/opt/firefox/', '/usr/lib/firefox/', '/usr/bin/'] # shutil.which should cover /usr/bin
        },
        'brave': {
            'executables': {'win32': 'brave.exe', 'darwin': 'Brave Browser', 'linux': ['brave-browser', 'brave']},
            'bundle_ids': {'darwin': 'com.brave.Browser'},
            'win_reg_paths': [r'BraveSoftware\Brave-Browser\Application'],
            'mac_app_paths': [r'/Applications/Brave Browser.app'],
            'linux_paths': ['/opt/brave.com/', '/usr/bin/'] # shutil.which should cover /usr/bin
        },
        'opera': {
            'executables': {'win32': 'opera.exe', 'darwin': 'Opera', 'linux': ['opera']},
            'bundle_ids': {'darwin': 'com.operasoftware.Opera'},
            'win_reg_paths': [r'Opera Software\Opera Stable', r'Programs\Opera'], # Latter for user install
            'mac_app_paths': [r'/Applications/Opera.app'],
            'linux_paths': ['/usr/bin/'] # shutil.which should cover /usr/bin
        },
        'operagx': {
            'executables': {'win32': 'launcher.exe', 'darwin': 'Opera GX', 'linux': ['opera-gx']}, # launcher.exe for Opera GX on Win
            'bundle_ids': {'darwin': 'com.operasoftware.OperaGX'},
            'win_reg_paths': [r'Programs\Opera GX'], # Usually in LOCALAPPDATA
            'mac_app_paths': [r'/Applications/Opera GX.app'],
            'linux_paths': ['/usr/bin/'] # shutil.which should cover /usr/bin
        }
    }

    config = browser_config.get(requested_browser_type)
    if not config:
        return None # Browser type not configured

    # --- Platform-specific search ---
    found_path = None

    # 1. Use shutil.which() as the primary strategy
    platform_executables = config['executables'].get(sys.platform)
    if platform_executables:
        if isinstance(platform_executables, list):
            for exe in platform_executables:
                found_path = shutil.which(exe)
                if found_path:
                    break
        else:
            found_path = shutil.which(platform_executables)

    if found_path and os.path.exists(found_path):
        return found_path

    # --- Platform-specific fallbacks ---
    if sys.platform == 'win32':
        # Executable name for registry and file searches
        exe_name = config['executables']['win32']

        # a. Check common installation paths using Program Files env vars
        program_files_vars = ['PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA']
        for pf_var in program_files_vars:
            base_dir = os.environ.get(pf_var)
            if base_dir:
                for reg_path_suffix in config['win_reg_paths']: # Using win_reg_paths as a hint for subdirectories
                    # For LOCALAPPDATA, path structure might be different (e.g., Opera GX directly under Programs)
                    if pf_var == 'LOCALAPPDATA' and 'Programs' in reg_path_suffix: # Heuristic for Opera-like user installs
                        path_to_check = os.path.join(base_dir, reg_path_suffix, exe_name)
                    elif pf_var != 'LOCALAPPDATA':
                         path_to_check = os.path.join(base_dir, reg_path_suffix, exe_name)
                    else: # For LOCALAPPDATA without "Programs" in suffix, try direct concatenation
                        path_to_check = os.path.join(base_dir, reg_path_suffix, exe_name)
                        # Also check if exe_name is directly in a folder named like the browser (e.g. LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe)
                        # This requires a bit more specific handling if reg_path_suffix is like BraveSoftware\Brave-Browser\Application
                        if not os.path.exists(path_to_check) and len(reg_path_suffix.split('\\')) > 1:
                            path_to_check = os.path.join(base_dir, os.path.dirname(reg_path_suffix), exe_name)


                    if os.path.exists(path_to_check):
                        return path_to_check
                    # Special case for Opera GX launcher.exe vs opera.exe
                    if requested_browser_type == 'operagx' and exe_name == 'launcher.exe':
                        alt_exe_name = 'opera.exe'
                        path_to_check = os.path.join(base_dir, reg_path_suffix, alt_exe_name)
                        if os.path.exists(path_to_check):
                            return path_to_check


        # b. Retain registry lookups
        try:
            import winreg
            registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{}".format(exe_name)),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\{}".format(exe_name)),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\{}".format(exe_name))
            ]
            # Some browsers (like Firefox) might register under their name rather than exe name
            if requested_browser_type == 'firefox':
                registry_keys.append(
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Mozilla Firefox") # Path to main exe is often in (Default) or Path value
                )

            for hive, reg_path_template in registry_keys:
                try:
                    with winreg.OpenKey(hive, reg_path_template.format(exe_name)) as key:
                        # For App Paths, the (Default) value is usually the path
                        value, _ = winreg.QueryValueEx(key, None)
                        if os.path.exists(value):
                            return value
                        # For Firefox, it might be a "PathToExe" or similar value if not (Default)
                        if requested_browser_type == 'firefox':
                             # Try to find a value that ends with firefox.exe (e.g. "PathToExe")
                            for i in range(winreg.QueryInfoKey(key)[1]): # Iterate over values
                                try:
                                    val_name, val_data, _ = winreg.EnumValue(key, i)
                                    if isinstance(val_data, str) and val_data.lower().endswith("firefox.exe") and os.path.exists(val_data):
                                        return val_data
                                except OSError:
                                    continue # Some values might not be readable
                except FileNotFoundError:
                    continue
        except ImportError:
            pass # winreg not available

    elif sys.platform == 'darwin':
        # Executable name for constructing path inside .app bundle
        exe_name_darwin = config['executables']['darwin'] # e.g. "Google Chrome" for chrome

        # a. Check common /Applications and ~/Applications paths for .app bundle
        for app_path_prefix in config['mac_app_paths']: # e.g., ["/Applications/Google Chrome.app"]
            # Construct the full path to the executable inside the .app bundle
            # e.g. /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
            potential_path = os.path.join(app_path_prefix, "Contents", "MacOS", exe_name_darwin)
            if os.path.exists(potential_path):
                return potential_path
            # Check user's Applications directory as well
            user_app_path = os.path.join(os.path.expanduser("~"), app_path_prefix.lstrip('/'))
            user_potential_path = os.path.join(user_app_path, "Contents", "MacOS", exe_name_darwin)
            if os.path.exists(user_potential_path):
                return user_potential_path

        # b. (Optional) mdfind for bundle IDs - keeping it simple for now as per instructions.
        #    Example: `mdfind "kMDItemCFBundleIdentifier == 'com.google.Chrome'"`
        #    Then parse output to get .app path, then construct path to executable.

    elif sys.platform == 'linux':
        # shutil.which() is generally good on Linux.
        # As a fallback, check specific paths if they were defined.
        # Most common ones like /usr/bin are covered by shutil.which.
        # These paths are more for non-standard installations (e.g. /opt)
        linux_exe_names = config['executables']['linux']
        if not isinstance(linux_exe_names, list):
            linux_exe_names = [linux_exe_names]

        for exe_name_linux in linux_exe_names:
            for lpath in config.get('linux_paths', []):
                potential_path = os.path.join(lpath, exe_name_linux)
                if os.path.exists(potential_path) and os.access(potential_path, os.X_OK):
                    return potential_path

    return None # If all methods fail for the requested browser


def get_linux_cursor_path():
    """Get Linux Cursor path"""

    # 1. Try shutil.which("cursor")
    cursor_exe_path = shutil.which("cursor")

    if cursor_exe_path:
        try:
            # Resolve symlinks
            real_exe_path = os.path.realpath(cursor_exe_path)

            # Attempt to navigate to resources/app
            # Common structures:
            # - /opt/Cursor/cursor (exe) -> /opt/Cursor/resources/app
            # - /usr/bin/cursor (symlink) -> /opt/Cursor/cursor (exe) -> /opt/Cursor/resources/app
            # - /home/user/.local/bin/cursor (symlink) -> ...

            # Heuristic: go up two levels from the real executable path and look for resources/app
            # This assumes a layout like .../bin/cursor or .../Cursor/cursor
            potential_app_path = os.path.join(os.path.dirname(os.path.dirname(real_exe_path)), "resources/app")
            if os.path.isdir(potential_app_path):
                return potential_app_path

            # Heuristic: if real_exe_path is directly in a folder like '.../Cursor', and 'resources/app' is a sibling
            # e.g. real_exe_path = /opt/Cursor/cursor, then app_path = /opt/Cursor/resources/app
            potential_app_path_sibling = os.path.join(os.path.dirname(real_exe_path), "resources/app")
            if os.path.isdir(potential_app_path_sibling):
                 return potential_app_path_sibling


        except Exception:
            # If any error occurs during path manipulation, fall through to possible_paths
            pass

    # 2. Iterate through the predefined possible_paths if shutil.which fails or derived path is not found
    possible_paths = [
        "/opt/Cursor/resources/app",
        "/usr/share/cursor/resources/app",
        "/opt/cursor-bin/resources/app", # For some AUR packages or alternative installations
        "/usr/lib/cursor/resources/app",
        os.path.expanduser("~/.local/share/cursor/resources/app"), # User-specific installation
        os.path.expanduser("~/.local/opt/cursor/resources/app"), # Another user-specific possibility
        # Flatpak installations might be harder to detect generally without knowing specific IDs.
        # Snap: /snap/cursor/current/resources/app (but /snap/bin/cursor should be found by which)
    ]
    
    for path in possible_paths:
        if os.path.isdir(path): # Check if it's a directory and exists
            return path

    return None # Return None if no path is found

def get_random_wait_time(config, timing_key):
    """Get random wait time based on configuration timing settings
    
    Args:
        config (dict): Configuration dictionary containing timing settings
        timing_key (str): Key to look up in the timing settings
        
    Returns:
        float: Random wait time in seconds
    """
    try:
        # Get timing value from config
        timing = config.get('Timing', {}).get(timing_key)
        if not timing:
            # Default to 0.5-1.5 seconds if timing not found
            return random.uniform(0.5, 1.5)
            
        # Check if timing is a range (e.g., "0.5-1.5" or "0.5,1.5")
        if isinstance(timing, str):
            if '-' in timing:
                min_time, max_time = map(float, timing.split('-'))
            elif ',' in timing:
                min_time, max_time = map(float, timing.split(','))
            else:
                # Single value, use it as both min and max
                min_time = max_time = float(timing)
        else:
            # If timing is a number, use it as both min and max
            min_time = max_time = float(timing)
            
        return random.uniform(min_time, max_time)
        
    except (ValueError, TypeError, AttributeError):
        # Return default value if any error occurs
        return random.uniform(0.5, 1.5) 