import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": [""], "compressed": True}
bdist_msi_options = {"upgrade_code": "upgr8de_table2bdf"}

# GUI applications require a different base on Windows (the default is for a
# console application).
#base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(  name = "Table2DBF",
        version = "0.2",
        description = "Coole App fürs PSEM!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("table2dbf.py", base=None, shortcutName="Table2DBF",
            shortcutDir="DesktopFolder", icon="logo.ico")])