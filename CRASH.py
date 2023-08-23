"""
	TODO / Notes:
	- Static Variables (like logdir, probably as Arg... OR RegEx search patterns)
	- ERROR handler
	- ????
	- Dict Fixes		(containing DataClass entries, would be a nice approach to easy check and update according values???)
	- Dict Patches		(same obvoiusly)
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

	License: 		MIT
	Created: 		2023 August 19

	Source Code:	Github
	Exectuable:		https://www.nexusmods.com/starfield/mods/64

	Python:			3.11
	Line-Width:		100'ish (80 is just way too short nowadays)
	Indention:		TAB - Size 4
"""
######################################
### Script Variables
######################################
script_name_short = "CRASH"
script_name_full = "Crashlog Report Assertion for Starfield Heroes"
script_name = script_name_short + " - " + script_name_full
script_version = "0.1"
# Script_Version and Changed are used within the Report
script_changed = "2023.08.19"
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
from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
from multiprocessing import freeze_support  # pip install multiprocessing
from cpuinfo import get_cpu_info  # pip install py-cpuinfo
# TODO :: pip install AspireTUI
from AspireTUI.aspire import Aspire as tui
from AspireTUI.aspire_core import AspireCore
from AspireTUI.aspire_data_status import StatusEnum
# initiialze, to get AC.with_line values (..full and ..inner)
AC = AspireCore()

####################################################################################################
### Data Structures
####################################################################################################

######################################
### Data CLasses
######################################
@dataclass
class dc_Fixes:
	Name: str
	Desciption: str
	Version: float
	URL: str
	CheckFile: str
	CRASH_NOTE: str
@dataclass
class dc_Crash_Config:
	GameDIR: str
	bLogUseExeDir: bool
	Vendor: str
	ver_Win: int
	ver_Python: float
######################################
### Named Tuple
######################################
# Prepare access to registry entries for game dir
Provider = namedtuple("Provider", ["name", "reg_hive", "reg_key", "reg_entry"])



####################################################################################################
### Data Sets
### --> Fill the data structures with data
####################################################################################################
# Define provider instances
# TODO
# ALT-- probably better:
# -SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4
#- SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 1946180
# -installed path
#https://discord.com/channels/916686954421157930/916686955851432011/1143433355023634512
ntp_steam = Provider(
	name="Steam", 
	reg_hive="HKEY_LOCAL_MACHINE",
	reg_key=r"SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4",
	reg_entry="installed path"
	)
# TODO XBOX
# HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\BethesdaSoftworks.ProjectGold_1.6.35.0_x64__3275kfvn8vcwc
ntp_xbox  = Provider(
	name="Xbox", 
	reg_hive="HKEY_LOCAL_MACHINE",
	reg_key=r"SOFTWARE\Microsoft\Xbox", 
	reg_entry="InstallDir" #TODO
	)
ntp_game_providers = [ntp_steam, ntp_xbox]

######################################
### Fixes & Patches
######################################
class CORE_FIXES(Enum):
	SFSE = dc_Fixes(
		"Starfield Script Extender",
		"Most required tool to run the most interesting mods.",
		0.1,
		"https://github.com/ianpatt/sfse",
		"sfse_*.dll",
		"100% Required"
	)
	Unofficial = dc_Fixes(
		"Unofficial Fixes and Patches for Starfield",
		"A collection of fixes and patches by the community for the community",
		0.1,
		"nexusmods.com/blabla",
		"UFPSF.esm",
		"Highly recommended"
	)
	EngineFix = dc_Fixes(
		"Engine Fixes for SF",
		"Fixes physics and other stuff",
		0.1,
		"nexusmods.com/blabla",
		"EFSF.esp",
		"Can help, not required"
	)
# Registry access map
HKEY_MAP = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
}


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
# First start
def CRASH_FIRST_START():
	#TODO
	# Text definitions
	txt_wrong_ver_Windows = """
We understand that you are eager to play, but even with Win10 you dont get to use DX12 to its full extend...
We are truely sorry, but we will not support handling crashlogs on THAT kind of lower tier.
"""
	txt_wrong_ver_Python = "Please download and install it from https://www.python.org/downloads/"

	# Get bool if proper versions
	bCheckWindows = check_ver_Windows()
	bCheckPython = check_ver_Python()
	
	# Show result of Windows check, if fails, ask to leaave
	if not tui.status(bCheckWindows, f"Windows 10+ \tVer: {ver_WindowsBuild_Str}"):
		
		tui.print(txt_wrong_ver_Windows)
		if not tui.yesno("Continue anyway"):
			sys.exit(1)
	# Python Version Check

	#tui.status(ver_Python_BOOL, "This script requires Python 3.11 or higher.")
	if not tui.status(bCheckPython, f"Python 3.11: \tVer: {sys.version[0:4].strip()}") :
		tui.status(StatusEnum.Todo , txt_wrong_ver_Python)
		os.system("pause")
		sys.exit(1)
	print("Todo")

######################################
### Read CRASH-Config
######################################
def crash_config_get(c_path: str, c_file: str) -> dc_Crash_Config |None:
	this_file = f"{c_path}\{c_file}"
	try:
		with open(this_file, 'r', encoding="utf-8", errors="ignore") as this_CONFIG:
			tui.status(True, f"Found config: \t{this_file}")
			# Content of current confitg:
			tui.print(this_CONFIG)
			# TODO read config
			gamedir = ini_read(c_path, c_file, "CRASH", "DIR_GAME")
			logdir = ini_read(c_path, c_file, "CRASH", "bLogUseExeDir")
			vendor = ini_read(c_path, c_file, "CRASH", "VENDOR")
			win_ver = ini_read(c_path, c_file, "CRASH", "VER_WIN")
			py_ver = ini_read(c_path, c_file, "CRASH", "VER_PYTHON")
			return dc_Crash_Config(gamedir,logdir,vendor,win_ver,py_ver)
	except Exception as e:
		tui.status(4, f"No config in: \t{this_file}")
		# Guessing its the official LOGDIR with UAC protection
		# or Config does not exist yet.
		# TODO
		return None
	return None

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
                return value
        else:
            print("Invalid HKEY")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
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
	if err_msg != "":
		tui.status(False, err.format(err_msg))
	else:
		tui.status(False, ERROR_MESSAGE)
	os.system("pause")
	sys.exit(1)

######################################
### Version & Dimension Checks
######################################
def check_terminal_width():
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
# Python Version
def check_ver_Python():
	if sys.version_info[:2] >= (3, 11):
		return True
	else:
		return False




####################################################################################################
### Data Structures
####################################################################################################




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

# Get basic dirs
def crash_init_dir_log() -> str | None:
	DIR_DOCS = ""
	DIR_DOCS = reg_value_get(
		"HKEY_CURRENT_USER",
		r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders", 
		"Personal"
		)
	# TODO - fix to Starfield
	if DIR_DOCS != "":
		return_dir = f"{DIR_DOCS}\My Games\Skyrim Special Edition\SKSE"
		return return_dir #DIR_LOG_OFFICIAL
	else:
		return None
# Get Vendor
def crash_init_vendor() -> ntp_game_providers:
	for index, vendor in enumerate(ntp_game_providers, start=1):
		#tui.progress(f"Scanning game vendors: {vendor.name}", index, len(ntp_game_providers))
		tui.print(f"Scaning game providers", f"{vendor.name} [ {index}/{len(ntp_game_providers)} ]", end="")
		try:
			DIR_GAME = reg_value_get(vendor.reg_hive, vendor.reg_key, vendor.reg_entry)
			if DIR_GAME is not None:
				# Do not parse further
				DIR_GAME_VENDOR = vendor.name
				#break
				return True
		except Exception:
			# TODO
			tui.print("TODO Vendor:", DIR_GAME_VENDOR)
			return False
		# Double check if game path was found
		









####################################################################################################
### Load Environment
####################################################################################################
# Internal flags:
bCheckWindows = False
bCheckPython = False
# Strings:
ver_WindowsBuild_Str = platform.release()
DIR_EXE = os.getcwd()
# Official log dir in %userprofile%... actualy... personal documents
DIR_LOG_OFFICIAL = crash_init_dir_log()
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
tui.header(f" {script_title} ", f" © {script_copyright} by Poet and Sephrajin ")
tui.title("Initialize Framework")

# Parse logdirs for config file
list_logsidrs = [DIR_LOG_OFFICIAL, DIR_LOGS]
for try_config_dir in list_logsidrs:
	dummy_ini = None
	temp = crash_config_get(try_config_dir, "CRASH.ini")

if temp == None or temp == "":
	tui.title("First Time Setup")
	CRASH_FIRST_START()





if DIR_GAME == "":
	tui.status(False, f"Gamedir: \t\t{DIR_GAME}")
else:
	tui.status(True, f"Gamedir: \t\t{DIR_GAME}")

# Logdir

DIR_LOGS = None

# Output
tui.status(True, f"Log official: \t{DIR_LOG_OFFICIAL}")
tui.status(True, f"Log detected: \t{DIR_LOGS}")

tui.title("Loading Required Fixes and Patches")
for fix in CORE_FIXES:
	fix_cur = fix.value
	tui.status(True, f"Fixes & Patches:\t({fix})\t\t{fix_cur.Name}")

