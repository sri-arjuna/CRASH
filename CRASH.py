"""
    TODO / Notes:
    - Static Variables (like logdir, probably as Arg... OR RegEx search patterns)
    - ERROR handler
    - ????
    - Dict Fixes        (containing DataClass entries, would be a nice approach to easy check and update according values???)
    - Dict Patches        (same obvoiusly)
    - Dict Notes
    - Functions / Tools
    - Main()
    - Call MainLoop to handle files, according to Arg-Flags

    Check for TODO to adjust things after testing !!
"""

#!/usr/bin/env python
"""
    CRASH - Crashlog Report Assertion for Starfield Heroes
    ------------------------------------------------------
    A colaboration of Poet (TheSoundOfSnow) and Sephrajin

    With best intentions to help, but without any warranty or garantuee.

    License:         MIT
    Created:         2023 August 19

    Source Code:    Github
    Exectuable:        https://www.nexusmods.com/starfield/mods/64

    Python:            3.11
    Line-Width:        100'ish (80 is just way too short nowadays)
    Indention:        Space - Size 4
"""
######################################
### Script Variables
######################################
script_name_short = "CRASH"
script_name_full = "Crashlog Report Assertion for Starfield Heroes"
script_name = script_name_short + " - " + script_name_full
script_version = "0.2"
# Script_Version and Changed are used within the Report
script_changed = "2023.08.29"
script_title = script_name + " (" + script_version + ") WIP" # / " + script_changed
# Copyright will onle be shown on console/gui output
script_copyright = "2023"
######################################
### Imports
######################################
import platform
import sys
import os
import re
import winreg
import configparser
from pathlib import Path
from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
from multiprocessing import freeze_support  # pip install multiprocessing
from cpuinfo import get_cpu_info  # pip install py-cpuinfo
######################################
### Python Version Check
### Do thhis now before we're going to deep
######################################
if sys.version_info[:2] >= (3, 11):
    # All good
    pass
else:
    txt_wrong_ver_Python = "Please download and install it from https://www.python.org/downloads/"
    print(f"Req: Python 3.11: \tYou: {sys.version[0:4].strip()}")
    print(txt_wrong_ver_Python)
    os.system("pause")
    sys.exit(1)
######################################
### Import
### AspireTUI by sri-arjuna (Sephrajin)
######################################
# TODO :: pip install AspireTUI
from AspireTUI.aspire import Aspire as tui
from AspireTUI.aspire_core import AspireCore
from AspireTUI.aspire_data_status import StatusEnum
from AspireTUI.aspire_data_status import dict_status as StatusDict
# initiialze, to get AC.with_line values (..full and ..inner)
AC = AspireCore()

####################################################################################################
### Data Structures
####################################################################################################
"""
    Define Structures here
    Directly followed by their content if applicable

"""
# Access config with:
CRASH_CONFIG = None
######################################
### Directories
######################################
DIR_EXE = None
# DIR_LOGS is either same as 'DIR_EXE' or
# will by overwritten by passed arguments
DIR_LOGS = None
DIR_LOG_OFFICIAL = None
DIR_GAME = None
DIR_GAME_VENDOR = None
DIR_REPORTS = None
######################################
### Provider... Steam, Xbox
######################################
# Prepare access to registry entries for game dir
Provider = namedtuple("Provider", ["name", "reg_hive", "reg_key", "reg_entry"])
# Registry access map
HKEY_MAP = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
}
# Define provider instances
# TODO   /// backup or remove
# ALT-- probably better:
# -SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4
#- SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 1946180
# -installed path
#https://discord.com/channels/916686954421157930/916686955851432011/1143433355023634512
ntp_steam = Provider(
    name = "Steam", 
    reg_hive = "HKEY_LOCAL_MACHINE",
    reg_key = r"SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4",
    reg_entry = "installed path"
    )
# TODO XBOX
# HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\BethesdaSoftworks.ProjectGold_1.6.35.0_x64__3275kfvn8vcwc
ntp_xbox  = Provider(
    name = "Xbox", 
    reg_hive = "HKEY_LOCAL_MACHINE",
    reg_key = r"SOFTWARE\Microsoft\Xbox", 
    reg_entry = "InstallDir" #TODO
    )
ntp_game_providers = [ntp_steam, ntp_xbox]
######################################
### Get registry value
######################################
def reg_value_get(hive_key, key_path, value_name):
    try:
        if hive_key in HKEY_MAP:
            hkey = HKEY_MAP[hive_key]
            # Open the specified registry key
            with winreg.OpenKey(hkey, key_path) as key:
                # Read the value of the specified name
                value, value_type = winreg.QueryValueEx(key, value_name)
                return f"{value}"
        else:
            print("Invalid HKEY")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
######################################
### Get vendor
######################################
def crash_init_vendor():
    for index, vendor in enumerate(ntp_game_providers, start=0):
        try:
            DIR_GAME = reg_value_get(vendor.reg_hive, vendor.reg_key, vendor.reg_entry)
            if DIR_GAME is not None:
                # Return both the index and the vendor name
                return index, vendor.name 
        except Exception:
            tui.print("TODO Improve Vendor:", vendor.name)
    # Return 0 and an empty string if no valid vendor was detected
    return 0, "" 
######################################
### Get official log dir...
### %userprofile%\Documents\My Games\Game Name\Script Extender
######################################
def crash_init_dir_log() -> str :
    # https://discord.com/channels/267624335836053506/267624335836053506/1145931328747995177

    #pathlib
    Official_Logs = namedtuple("Official_Logs", ["reg_hive", "reg_key", "reg_entry", "game_log_path"])
    ntp_logdir = Official_Logs(
        reg_hive="HKEY_CURRENT_USER",
        reg_key=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        reg_entry="Personal",
        game_log_path="My Games\Skyrim Special Edition\SKSE"
    )

    DIR_DOCS = reg_value_get(
        ntp_logdir.reg_hive,
        ntp_logdir.reg_key,
        ntp_logdir.reg_entry
    )
    game_log_path = Path(ntp_logdir.game_log_path)
    tui.print(f"DEBUG :: {Path(DIR_DOCS) / game_log_path}")
    return Path(DIR_DOCS) / game_log_path

######################################
### Fixes & Patches
######################################
@dataclass
class dc_Fixes:
    Name: str
    Desciption: str
    Version: float
    URL_Nexus: str
    URL_Source: str
    CheckFile: str
    CRASH_NOTE: str
# Actual DATA
class CORE_FIXES(Enum):
    SFSE = dc_Fixes(
        "Starfield Script Extender",
        "Most required tool to run the most interesting mods.",
        0.1,
        "https://sfse.silverlock.org/",
        "https://github.com/ianpatt/sfse",
        "sfse_*.dll",
        "100% Required"
    )
    Community = dc_Fixes(
        "Starfield Community Patch",
        "A patch written by the NexusMods community",
        0.1,
        "https://nexusmods.com/starfield/mods/1",
        "https://www.starfieldpatch.dev/",
        "SCP.esm",
        "100% required"
    )
    Unofficial = dc_Fixes(
        "Unofficial Fixes and Patches for Starfield",
        "A collection of fixes and patches by the community for the community",
        0.1,
        "nexusmods.com/blabla",
        "url to source",
        "UFPSF.esm",
        "Highly recommended"
    )
    EngineFix = dc_Fixes(
        "Engine Fixes for SF",
        "Fixes physics and other stuff",
        0.1,
        "nexusmods.com/blabla",
        "url to source",
        "EFSF.esp",
        "Can help, not required"
    )
######################################
### Config file
######################################
@dataclass
class dc_Crash_Config:
    GameDIR: str
    Vendor: str
    bLogUseExeDir: bool
    bSkipWindowsVerWarning: bool

####################################################################################################
### Data Sets
### --> Fill the data structures with data
####################################################################################################


######################################
### Error Handling
######################################
# TODO fix crash loger URL
class ERROR_MESSAGE(Enum):
    NoCrashLogger = """Fatal:
Could not detect CrashLogger. 
Please use:
    https://www.nexusmods.com/skyrimspecialedition/mods/59818
"""
    NoFiles = """FATAL:
No crashlogs could be found!
Are you sure you wanted to scan: %s
"""
    NoPerm = """PermissionError:
Path exists, but you have no write permission to: %s
Please check your User Access Control (UAC) notifications (next to the clock in the taskbar).
"""
    Usage = """Usage: 
CRASH.py [\"C:\\some existing dir\\to\\logs\"]

You have provided:
CRASH.py %s
"""
    # Transform Enums to contain passed arguments, usualy directory
    def format(self, err_msg):
        return self.value % err_msg


####################################################################################################
### Functions
### Internal - early
### As in First Time functions and configuration
####################################################################################################
"""
    class dc_Crash_Config:
        GameDIR: str
        Vendor: str
        bLogUseExeDir: bool
        bSkipWindowsVerWarning: bool
"""

# First start
def CRASH_FIRST_START(*args):
    DIR_LOG_OFFICIAL = f"{args[0]}"
    # Get Vendor, then DIR_GAME
    vendor_index, vendor_name = crash_init_vendor()
    tui.status(2, f"Vendor: \t\t\t{vendor_name}")
    if vendor_index == 0: 
        # i0 = Steam, should work
        DIR_GAME = reg_value_get(
            ntp_game_providers[vendor_index].reg_hive, 
            ntp_game_providers[vendor_index].reg_key, 
            ntp_game_providers[vendor_index].reg_entry
        )
    elif vendor_index == 1:
        # i1 = Xbox, has dynamic reg-paths for each version... meh
        tui.status(111, "Can't detect DIR_GAME for Xbox, please edit CRASH.ini for DIR_GAME")
        DIR_GAME = ""
    else:
        tui.status(False, "Could not detect vendor, please edit CRASH.ini for DIR_GAME.")
        DIR_GAME = ""
    tui.status(2, f"DIR_GAME: \t\t\t{DIR_GAME}")

    # Check windows version, and save possible Skip bool
    bSkipWindowsVerWarning = False
    ver_WindowsBuild_Str = platform.release()
    txt_wrong_ver_Windows = """
We understand that you are eager to play, but even with Win10 you dont get to use DX12 to its full extend...
We are truely sorry, but we will not support handling crashlogs on THAT kind of lower tier.
"""
    # Get bool if proper versions
    bCheckWindows = check_ver_Windows()
    # Show result of Windows check, if fails, ask to leaave
    if not tui.status(bCheckWindows, f"Windows 10+ \t\tVer: {ver_WindowsBuild_Str}"):
        tui.print(txt_wrong_ver_Windows)
        if not tui.yesno("Continue anyway"):
            # No, lets exit now
            sys.exit(1)
        else:
            # Yes, save for later use
            bSkipWindowsVerWarning = True
    tui.status(2, f"bSkipWindowsVerWarning: \t{bSkipWindowsVerWarning}")

    # Which ini file will be used?
    # This is forced according to write success or choice now
    # If it fails to write, possible UAC
    if not crash_config_set(f"{DIR_LOG_OFFICIAL}", "CRASH.ini", DIR_GAME, vendor_name, False, bSkipWindowsVerWarning):
        # Probably UAC Active
        #tui.status(False, f"Failed writing:\t{DIR_LOG_OFFICIAL}\CRASH.ini")
        ERROR_HANDLER(ERROR_MESSAGE.NoPerm, DIR_LOG_OFFICIAL)
        #tui.print("Please check your Windows UAC settings notification- next to your clock.")
        tui.status(2, "Possible UAC detected.")
        if tui.yesno("Do you want to use the official log dir as output for CRASH-Reports?"):
            tui.print("Then please allow the tool access via that notification and restart CRASH again.")
            tui.press()
        else:
            # User does not want CRASH to write in official log dir
            # Hence we only write the config in DIR_EXE
            # However, we now force use EXE dir as True because UAC and unwillingness to allow perm
            crash_config_set(DIR_LOGS, "CRASH.ini", DIR_GAME, vendor, True, bSkipWindowsVerWarning)

######################################
### Read / Write CRASH-Config
######################################
# (Attenmpt to) Read Config file and return dataclass Crash Config
# Return None if nothing was found.
def crash_config_get(c_path: str, c_file: str) -> dc_Crash_Config:
    this_file = f"{c_path}\{c_file}"
    try:
        with open(this_file, 'r', encoding="utf-8", errors="ignore") as this_CONFIG:
            gamedir = ini_read(f"{c_path}", c_file, "CRASH", "DIR_GAME")
            vendor = ini_read(f"{c_path}", c_file, "CRASH", "VENDOR")
            bLogUseExeDir = ini_read(f"{c_path}", c_file, "CRASH", "bLogUseExeDir")
            bSkipWinWarning = ini_read(f"{c_path}", c_file, "CRASH", "bSkipWinWarning")
        tui.status(True, f"Retreived config:", f"{this_file}")
        return dc_Crash_Config(f"{gamedir}", vendor, bLogUseExeDir, bSkipWinWarning)
    except Exception as e:
        tui.status(False, f"No config in:", f"{this_file}")
        return None

# Attempt to write config file, return True if succeeded
# Return False if it failed (exception).
def crash_config_set(c_path: str, c_file: str, gamedir: str, vendor: str, bLogUseExeDir: bool, bSkipWinWarning: bool):
    this_file = f"{c_path}\{c_file}"
    try:
        ini_write(c_path, c_file, "CRASH", "DIR_GAME", gamedir)
        ini_write(c_path, c_file, "CRASH", "VENDOR", vendor)
        ini_write(c_path, c_file, "CRASH", "bLogUseExeDir", str(bLogUseExeDir))
        ini_write(c_path, c_file, "CRASH", "bSkipWinWarning", str(bSkipWinWarning))
        tui.status(True, "Written:", f"{this_file}")
        return True
    except Exception as e:
        # Probably UAC active...
        tui.status(False, "Written:" f"{this_file}")
        return False


######################################
### Handle INI config
######################################
def ini_read(c_path, c_file, c_key, c_variable):
    ini_path = f"{c_path}/{c_file}"
    try:
        config = configparser.ConfigParser()
        config.read(ini_path)
        if c_key in config and c_variable in config[c_key]:
            return config[c_key][c_variable]
        return None
    except FileNotFoundError:
        return None

def ini_write(c_path, c_file, c_key, c_variable, c_value):
    config = configparser.ConfigParser()
    ini_path = f"{c_path}/{c_file}"
    
    try:
        config.read(ini_path)
        if not config.has_section(c_key):
            config.add_section(c_key)
        config.set(c_key, c_variable, c_value)
        with open(ini_path, 'w') as config_file:
            config.write(config_file)
        return True
    except Exception:
        return False


######################################
### Print Error Message
######################################
def ERROR_HANDLER(err: ERROR_MESSAGE, err_msg=""):
    full_error_message = err.format(err_msg)
    error_lines = full_error_message.split('\n')
    tui.title(error_lines[0])
    for line in error_lines[1:]:
        tui.print(line)
    os.system("pause")
    sys.exit(1)


######################################
### Version & Dimension Checks
######################################
def check_terminal_width():
    # I guess i fixed moxst issues of THIS aspect...
    return
    if AC.width_line_full < 102:
        # TODO : I probably need to adjust the line split functionality of Aspire...
        # for right now, this is "suffice"...
        # Heck, this was a lot more easier in bash shell
        print("Window is too small to display properly.")
        print("Please resize your console window and try again.")
        print("We really need a window width of about 102 chars.")
        os.system("pause")
        sys.exit(1)
# Windows Version
def check_ver_Windows():
    if int(platform.release().split('.')[0]) >= 6:
        return True
    else:
        return False

####################################################################################################
### Load Environment
####################################################################################################
# Internal flags:
bCheckWindows = False

# Default dirs
DIR_EXE = os.getcwd()
# Official log dir in %userprofile%... actualy... personal documents
#DIR_LOG_OFFICIAL = crash_init_dir_log()
DIR_DOCS = reg_value_get(
    "HKEY_CURRENT_USER",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders", 
    "Personal"
    )
# TODO - fix to Starfield
if DIR_DOCS != "" or DIR_DOCS is not None:
    DIR_LOG_OFFICIAL = f"{DIR_DOCS}\My Games\Skyrim Special Edition\SKSE"
    #return f"{return_dir}" #DIR_LOG_OFFICIAL
else:
    #return None
    DIR_LOG_OFFICIAL = f"EMPTY: {DIR_DOCS}"
print(DIR_DOCS, flush=True)
print(DIR_LOG_OFFICIAL, flush=True)


#print(DIR_LOG_OFFICIAL )#, repr(DIR_LOG_OFFICIAL))
######################################
### Arguments
######################################
if len(sys.argv) == 2:
    if os.path.isdir(sys.argv[1]):
        # Argument is passed
        # and the directory exists
        DIR_LOGS = sys.argv[1]
    else:
        # Show error for wrong argument or path not existing
        ERROR_HANDLER(ERROR_MESSAGE.Usage, sys.argv[1])
else:
    # Default behaviour, use 'exe' dir to check for logs
    DIR_LOGS = DIR_EXE


######################################
### Start Console output
######################################
tui.header(f" {script_title} ", f" © {script_copyright} by Poet & Sephrajin ")
tui.title("Initialize Framework")

# Parse logdirs for config file
try_config_dir1 = crash_config_get(f"{DIR_LOG_OFFICIAL}", "CRASH.ini")
try_config_dir2 = crash_config_get(f"{DIR_LOGS}", "CRASH.ini")

if try_config_dir1 is None and try_config_dir2 is None:
    tui.title("First Time Setup")
    CRASH_FIRST_START(f"{DIR_LOG_OFFICIAL}")
    tui.print()
    tui.status(StatusEnum.Info, "In order to apply the settings, we need to restart CRASH.")
    tui.print()
    tui.press()
    sys.exit(1)
elif try_config_dir2 is not None and try_config_dir2.bLogUseExeDir:
    # Even though this file exists and wants to use the exe dir
    CRASH_CONFIG = try_config_dir2
    DIR_REPORTS = DIR_LOGS
elif try_config_dir1 is not None:
    # We have the config in the official dir
    # and the config does not want the exedir as report output
    CRASH_CONFIG = try_config_dir1
    DIR_REPORTS = DIR_LOG_OFFICIAL
else:
    # UAC is still active.
    tui.title("Error")
    tui.print("Failed to read configurations. Please check your configuration files.")
    sys.exit(1)


# The 'CRASH_CONFIG' variable should now contain valid configurations
tui.title("Loaded Config")
tui.print("Vendor", f"{CRASH_CONFIG.Vendor}")
tui.print("Game Dir", f"{CRASH_CONFIG.GameDIR}")
tui.print("Use Exe Dir for logs", f"{CRASH_CONFIG.bLogUseExeDir}")
tui.print("Skip Windows Version Warning", f"{CRASH_CONFIG.bSkipWindowsVerWarning}")


tui.title("Loading Required Fixes and Patches")
for fix in CORE_FIXES:
    fix_cur = fix.value
    tui.status(True, f"Fixes & Patches: \t\t({fix})\t\t{fix_cur.Name}")

