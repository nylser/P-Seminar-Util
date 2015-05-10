import sys
import shutil

from cx_Freeze import setup, Executable


shutil.rmtree("build")
# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter", 'tcl', 'ttk'],
                     "optimize": 2, "compressed": True, "include_msvcr": True}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"


bdist_msi_options = {"upgrade_code": "b7ff206c-162d-4c65-a81c-839051fe5907"}

setup(name="Table2DBF",
      version="0.4.3",
      description="Table2DBF",
      options={"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
      executables=[Executable("table2dbf_gui.py", base=base, shortcutName="Table2DBF",
                              shortcutDir="DesktopFolder", icon="logo.ico")])