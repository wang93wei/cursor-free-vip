import os
import sys
import platform
import random
import shutil # Added shutil import

def get_user_documents_path():
    """Get user documents path"""
    if platform.system() == "Windows":
        try:
            import winreg
            # 打开注册表
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
                # 获取 "Personal" 键的值，这指向用户的文档目录
                documents_path, _ = winreg.QueryValueEx(key, "Personal")
                return documents_path
        except Exception as e:
            # fallback
            return os.path.expanduser("~\\Documents")
    else:
        return os.path.expanduser("~/Documents")
    
def get_default_driver_path(browser_type='chrome'):
    """Get default driver path based on browser type"""
    browser_type = browser_type.lower()
    if browser_type == 'chrome':
        return get_default_chrome_driver_path()
    elif browser_type == 'edge':
        return get_default_edge_driver_path()
    elif browser_type == 'firefox':
        return get_default_firefox_driver_path()
    elif browser_type == 'brave':
        # Brave 使用 Chrome 的 driver
        return get_default_chrome_driver_path()
    else:
        # Default to Chrome if browser type is unknown
        return get_default_chrome_driver_path()

def get_default_chrome_driver_path():
    """Get default Chrome driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "chromedriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "chromedriver")
    else:
        return "/usr/local/bin/chromedriver"

def get_default_edge_driver_path():
    """Get default Edge driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "msedgedriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "msedgedriver")
    else:
        return "/usr/local/bin/msedgedriver"
        
def get_default_firefox_driver_path():
    """Get default Firefox driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "geckodriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "geckodriver")
    else:
        return "/usr/local/bin/geckodriver"

def get_default_brave_driver_path():
    """Get default Brave driver path (uses Chrome driver)"""
    # Brave 浏览器基于 Chromium，所以使用相同的 chromedriver
    return get_default_chrome_driver_path()

def get_default_browser_path(browser_type='chrome'):
    """Get default browser executable path"""
    browser_type = browser_type.lower()

    # Define browser details
    browsers = {
        'chrome': {
            'win32': {
                'names': ['chrome.exe'],
                'paths': [
                    r'Google\Chrome\Application',
                    r'Google\Chrome Beta\Application',
                    r'Google\Chrome Dev\Application',
                ]
            },
            'darwin': {
                'names': [
                    'Google Chrome.app/Contents/MacOS/Google Chrome',
                    'Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta',
                    'Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev',
                ],
                'paths': ['/Applications/']
            },
            'linux': {
                'names': ['google-chrome', 'chrome', 'chromium', 'chromium-browser', 'google-chrome-beta', 'google-chrome-dev'],
                'paths': ['/usr/bin/', '/opt/']
            }
        },
        'edge': {
            'win32': {
                'names': ['msedge.exe'],
                'paths': [
                    r'Microsoft\Edge\Application',
                    r'Microsoft\Edge Beta\Application',
                    r'Microsoft\Edge Dev\Application',
                ]
            },
            'darwin': {
                'names': [
                    'Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
                    'Microsoft Edge Beta.app/Contents/MacOS/Microsoft Edge Beta',
                    'Microsoft Edge Dev.app/Contents/MacOS/Microsoft Edge Dev',
                ],
                'paths': ['/Applications/']
            },
            'linux': {
                'names': ['microsoft-edge', 'microsoft-edge-beta', 'microsoft-edge-dev'],
                'paths': ['/usr/bin/', '/opt/']
            }
        }
    }

    # OS-specific environment variables for program files
    program_files_paths = []
    if sys.platform == "win32":
        program_files_paths.extend([
            os.environ.get('PROGRAMFILES', r'C:\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'),
            os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        ])

    def find_browser(browser_details):
        if sys.platform == "win32":
            for name in browser_details['win32']['names']:
                # Check PATH first
                found_path = shutil.which(name)
                if found_path:
                    return found_path
                # Check common installation paths
                for app_path_suffix in browser_details['win32']['paths']:
                    for prog_files_path in program_files_paths:
                        full_path = os.path.join(prog_files_path, app_path_suffix, name)
                        if os.path.exists(full_path):
                            return full_path
                # Registry-based detection for Windows
                import winreg
                registry_paths = [
                    r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{}".format(name),
                    r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{}".format(name),
                ]
                for reg_hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                    for reg_path in registry_paths:
                        try:
                            with winreg.OpenKey(reg_hive, reg_path) as key:
                                reg_value, _ = winreg.QueryValueEx(key, None)
                                if os.path.exists(reg_value):
                                    return reg_value
                        except FileNotFoundError:
                            continue
        elif sys.platform == "darwin":
            for path_prefix in browser_details['darwin']['paths']:
                for name in browser_details['darwin']['names']:
                    full_path = os.path.join(path_prefix, name)
                    if os.path.exists(full_path):
                        return full_path
        else:  # Linux
            for name in browser_details['linux']['names']:
                # Check PATH using shutil.which
                found_path = shutil.which(name)
                if found_path:
                    return found_path
                # Check other common locations
                for path_prefix in browser_details['linux']['paths']:
                    full_path = os.path.join(path_prefix, name)
                    if os.path.exists(full_path): # Check if it's executable as well? os.access(full_path, os.X_OK)
                        return full_path
        return None

    # --- Main search logic ---
    # 1. Search for the requested browser_type
    if browser_type in browsers:
        found_path = find_browser(browsers[browser_type])
        if found_path:
            return found_path

    # 2. Fallback: If specific browser not found, or if a non-chrome/edge type was requested,
    #    try the original logic for other browsers (firefox, opera, etc.)
    #    This part retains the original logic for browsers other than Chrome and Edge.
    if sys.platform == "win32":
        if browser_type == 'firefox':
            return r"C:\Program Files\Mozilla Firefox\firefox.exe"
        elif browser_type == 'opera':
            opera_paths = [
                r"C:\Program Files\Opera\opera.exe",
                r"C:\Program Files (x86)\Opera\opera.exe",
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'launcher.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'opera.exe')
            ]
            for path in opera_paths:
                if os.path.exists(path):
                    return path
            return opera_paths[0]
        elif browser_type == 'operagx':
            operagx_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'launcher.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'opera.exe'),
                r"C:\Program Files\Opera GX\opera.exe",
                r"C:\Program Files (x86)\Opera GX\opera.exe"
            ]
            for path in operagx_paths:
                if os.path.exists(path):
                    return path
            return operagx_paths[0]
        elif browser_type == 'brave':
            paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe')
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            return paths[0] # Fallback to the first defined path
    elif sys.platform == "darwin":
        if browser_type == 'firefox':
            return "/Applications/Firefox.app/Contents/MacOS/firefox"
        elif browser_type == 'brave':
            return "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        elif browser_type == 'opera':
            return "/Applications/Opera.app/Contents/MacOS/Opera"
        elif browser_type == 'operagx': # Note: Original code had /Opera, might be specific to GX version
            return "/Applications/Opera GX.app/Contents/MacOS/Opera"
    else:  # Linux
        # For linux, shutil.which is generally preferred for firefox, opera, brave if they are in PATH
        other_browsers_linux = {
            'firefox': 'firefox',
            'opera': 'opera',
            'operagx': 'opera-gx', # Assuming 'opera-gx' is the command for Opera GX
            'brave': 'brave-browser' # or 'brave'
        }
        if browser_type in other_browsers_linux:
            found_path = shutil.which(other_browsers_linux[browser_type])
            if found_path:
                return found_path
            # Fallback to common hardcoded paths if not in PATH
            if browser_type == 'firefox': return "/usr/bin/firefox"
            if browser_type == 'opera': return "/usr/bin/opera"
            if browser_type == 'operagx': return "/usr/bin/opera-gx" # Example path
            if browser_type == 'brave': return "/usr/bin/brave-browser" # Example path


    # 3. Final Fallback: If the requested browser_type (even if it's chrome/edge) was not found by dynamic search,
    #    and it's not one of the other specific types, try the original hardcoded defaults for Chrome/Edge.
    #    This ensures we still have a default if dynamic searching fails.
    if browser_type == 'chrome':
        if sys.platform == "win32": return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if sys.platform == "darwin": return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return "/usr/bin/google-chrome" # Linux
    if browser_type == 'edge':
        if sys.platform == "win32": return r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if sys.platform == "darwin": return "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        return "/usr/bin/microsoft-edge" # Linux

    # 4. Ultimate Fallback: if the requested browser type is still not found, default to searching for 'chrome'
    #    This is the same behavior as the original end of the function.
    if browser_type not in ['chrome', 'edge']: # Avoid infinite recursion if chrome itself wasn't found
        # This call will perform dynamic search for chrome, then hardcoded chrome.
        return get_default_browser_path('chrome')
    
    # If all else fails (e.g. 'chrome' was requested but not found anywhere)
    # return a sensible default chrome path for the OS as a last resort.
    # This part should ideally not be reached if chrome search is comprehensive.
    if sys.platform == "win32":
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif sys.platform == "darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else: # Linux
        return "/usr/bin/google-chrome"


def get_linux_cursor_path():
    """Get Linux Cursor path"""
    possible_paths = [
        "/opt/Cursor/resources/app",
        "/usr/share/cursor/resources/app",
        "/opt/cursor-bin/resources/app",
        "/usr/lib/cursor/resources/app",
        os.path.expanduser("~/.local/share/cursor/resources/app")
    ]
    
    # return the first path that exists
    return next((path for path in possible_paths if os.path.exists(path)), possible_paths[0])

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