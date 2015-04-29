import configparser
from datetime import datetime
import json
import os
import easygui as g
import sys

default_config = {"last_select_dir": os.path.expanduser("~"), "last_username": "", "last_password": ""}

config = configparser.ConfigParser()


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
                 'lautstaerk': "Lautstärke/Lärmbelästigung",
                 'geruch': "Geruch",
                 'verschmutz': "Verschmutzung",
                 'beleuchtun': "Beleuchtung",
                 'qualitaet': "Straßenqualität",
                 'haue_gaert': "Häuser/Gärten Zustand",
                 'gruenflaec': "Grünflachen",
                 'dschnitt': "Durchschnitt",
                 'bwdatum': "Bewertungsdatum"}

ATT_INV = {'name': 0,
                  'lautstaerk': 1,
                  'geruch': 2,
                  'verschmutz': 3,
                  'beleuchtun': 4,
                  'qualitaet': 5,
                  'haue_gaert': 6,
                  'gruenflaec': 7,
                  'dschnitt': 8,
                  'bwdatum': 9}







ATT = {v: k for k, v in ATT_INV.items()}


def convert_date(input):
    try:
        print(datetime.strptime(input, "%d.%m.%Y"))
        return datetime.strptime(input, "%d.%m.%Y")
    except Exception as e:
        print(e)
        return None
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


def ask_dbf(last_dir='.'):
    title = "Select DBF File"
    result = None
    while not result:
        result = g.fileopenbox(title=title, default=last_dir + "/*.dbf")
        if not result:
            if not g.ynbox(title="No file selected!", msg="Do you want to try again?"):
                sys.exit(0)

    return result


class AskFileBox:
    def __init__(self, type='open', default='', filetypes=(), title=''):
        if type == "open":
            self.action = g.fileopenbox
        elif type == "save":
            self.action = g.filesavebox
        else:
            raise ValueError("Invalid Type!")
        self.default = default
        self.filetypes = filetypes
        if title:
            self.title = title
        else:
            if type == 'open':
                self.title = "Open File"
            else:
                self.title = "Save File"

    def ask(self):
        result = None
        while not result:
            result = self.action(title=self.title, default=self.default, filetypes=self.filetypes)
            if not result or not os.path.isfile(result):
                result = None
                if not g.ynbox(title="No valid file selected!", msg="Do you want to try again?"):
                    sys.exit(0)
        print(result)
        return result

ATT_CONV = {}