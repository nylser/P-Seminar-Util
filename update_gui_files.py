import glob
import subprocess
import os

pyside_rcc = "C:\\Python34\\Lib\\site-packages\\PySide\\pyside-rcc"

def convert_ui():
    for ui_file in glob.glob("gui/*.ui"):
        print("Converting %s" % ui_file)
        subprocess.call(["pyside-uic", ui_file, "--from-imports", "-o", os.path.splitext(ui_file)[0]+".py"])

def convert_res():
    for res_file in glob.glob("gui/*.qrc"):
        print("Converting %s" % res_file)
        subprocess.call([pyside_rcc, res_file, "-py3", "-o", os.path.splitext(res_file)[0]+"_rc.py"])

if __name__ == "__main__":
    convert_res()
    convert_ui()

