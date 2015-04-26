import configparser
from io import BufferedReader
import sys
import os
import re

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname('.')

    return os.path.join(datadir, filename)

if __name__ == "__main__":
    with open("Einstellungen.fis", "r", encoding="latin-1") as f:
        content = f.read()
    content = re.sub(r"STRASSEN\.Vector\.Source=.*", "STRASSEN.Vector.Source=%s" % os.path.abspath('.').lower(), content)
    content = re.sub(r"STRASSEN\.Vector\.InfoFolder=.*", "STRASSEN.Vector.InfoFolder=%s" % os.path.abspath('.').upper(), content)
    with open("Einstellungen.fis", "wb") as f:
        for line in content.splitlines():
            f.write((line.strip('\n')+"\r\n").encode("latin-1"))


    """config.read(find_data_file("Einstellungen_PSEM.fis"))
    config["Connections"]["STRASSEN.Vector.Source"] = os.path.dirname('.')
    config["Connections"]["Strassen.Vector.InfoFolder"] = os.path.dirname(".").upper()
    with open("Einstellungen_PSEM.fis") as f:
        config.write(f)"""
