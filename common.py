import configparser
from datetime import datetime
from PySide.QtCore import QSettings
import os
import sys
import re

default_config = {"last_select_dir": os.path.expanduser("~"), "last_username": "", "last_password": ""}

config = configparser.ConfigParser()
gui_settings = None

def parse_finview(settings):
    sections = {}
    with open(settings, "r", encoding="latin-1") as f:
        regex = r"\[(.*)\]"
        current_section = None
        for line in f.readlines():
            name = re.match(regex, line)
            if name is None:
                if not (current_section is None):
                    match = re.match(r"(.*)=([^\s].*)", line)
                    if not (match is None):
                        sections[current_section][match.group(1)] = match.group(2)
            else:
                current_section = name.group(1)
                sections[current_section] = {}
    return sections


def parse_finview_string(string):
    sections = {}
    regex = r"\[(.*)\]"
    current_section = None
    for line in string.splitlines():
        name = re.match(regex, line)
        if name is None:
            if not (current_section is None):
                match = re.match(r"(.*)=([^\s].*)", line)
                if not (match is None):
                    sections[current_section][match.group(1)] = match.group(2)
        else:
            current_section = name.group(1)
            sections[current_section] = {}
    return sections

def write_finview(config, settings):
    file_string = ""
    for section in config:
        file_string += "[{}]\n".format(section)
        for key in config[section]:
            line = "{}={}".format(key, config[section][key])
            file_string += line + "\n"
        file_string += "\n"
    with open(settings, "wb") as f:
        for line in file_string.splitlines():
            f.write((line.strip('\n')+"\r\n").encode("latin-1"))


def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname('.')

    return os.path.join(datadir, filename)

ATT_HR = {'name': "Straße",
                 'lautsta_db': "Lautstärke dBA",
                 'lautsta_su': "Lautstärke subjektiv",
                 'verschmutz': "Verschmutzung",
                 'beleuchtun': "Beleuchtung",
                 'qualitaet': "Straßenqualität",
                 'haue_gaert': "Häuser/Gärten Zustand",
                 'gruen_oeff': "Grünflächen öffentlich",
                 'gruen_priv': "Grünflächen privat",
                 'dschnitt_2': "Durchschnitt"}

ATT_INV = {'name': 0,
                  'lautsta_db': 1,
                  'lautsta_su': 2,
                  'verschmutz': 3,
                  'beleuchtun': 4,
                  'qualitaet': 5,
                  'haue_gaert': 6,
                  'gruen_oeff': 7,
                  'gruen_priv': 8,
                  'dschnitt_2': 9}


ATT = {v: k for k, v in ATT_INV.items()}


ATT_CONV = {}


ATT_STUFF = []
for i in range(len(ATT)):
    type = ATT[i]
    if i == 0:
        type += " C(30)"
        continue
    elif i == 9:
        type += " C(10)"
    else:
        type += " N(1,0)"
    ATT_STUFF.append(type)

#ATT_STUFF = [att for att in ATT_INV.keys() ]
#ATT_STUFF = ('name C(30)', 'lautstaerk N(1)', 'verschmutz N(1)', "beleuchtun N(1)")


def convert_date(input):
    try:
        print(datetime.strptime(input, "%d.%m.%Y"))
        return datetime.strptime(input, "%d.%m.%Y")
    except Exception as e:
        print(e)
        return None


def get_gui_settings():
    global gui_settings
    if not gui_settings:
        gui_settings = QSettings("Mineguild", "Table2DBF")
    return gui_settings


def load_config():
    global config
    config_path = os.path.join(os.path.expanduser("~"), ".table2dbf.config")
    config.read(config_path)


def save_config():
    config_path = os.path.join(os.path.expanduser("~"), ".table2dbf.config")
    with open(config_path, 'w') as config_file:
        config.write(config_file)


def get_config():
    if len(config.sections()) < 0:
        load_config()
    return config

"""
def dump_json(data):
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    box = AskFileBox(type="save", default=config["DEFAULT"].get("last_json_dir", ".") + "/street_db.json",
                     filetypes=[["*.json", "JavaScript Object File"]], title="Dump data to JSON")
    path = box.ask()
    config["DEFAULT"]["last_json_dir"] = os.path.dirname(path)
    save_config()
    with open(path, "w") as f:
        json.dump(data, f)


def load_json():
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    box = AskFileBox(type="open", default=config["DEFAULT"].get("last_json_dir", ".") + "/*.json",
                     filetypes=[["*.json", "JavaScript Object File"]], title="Load data from JSON")
    path = box.ask()
    config["DEFAULT"]["last_json_dir"] = os.path.dirname(path)
    with open(path, "r") as f:
        data = json.load(f)
    print("Done.")
    return data
"""

