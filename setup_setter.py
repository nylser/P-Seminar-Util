import sys
import shutil
from cx_Freeze import setup, Executable

target_directory = "setter_dist"

# Clean target_directory
shutil.rmtree(target_directory)

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"],
 "compressed": True,
 "zip_includes": ('Einstellungen.fis'),
 "include_msvcr": True,
 "optimize": 2,
 "build_exe": target_directory,
 "copy_dependent_files":True,
 "include_in_shared_zip":True,
 "create_shared_zip":True,
}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"



setup(name="SetterPSEM",
      version="0.1",
      description="Sets the right settings for FINView (P-Seminar)",
      author="Korbinian Stein",
      options={"build_exe": build_exe_options},
      executables=[Executable("create_settings.py",
      base=base,
      icon="logo.ico",
      compress=True,
      copyDependentFiles=True,
      targetDir=target_directory,
      )])