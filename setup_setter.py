import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"], "compressed": True, "zip_includes": ('Einstellungen.fis')}


# GUI applications require a different base on Windows (the default is for a
# console application).
# base = None
if sys.platform == "win32":
    base = "Win32GUI"



setup(name="SetterPSEM",
      version="0.1",
      description="Sets the right settings for FINView",
      options={"build_exe": build_exe_options},
      executables=[Executable("create_settings.py", base=None, icon="logo.ico")])