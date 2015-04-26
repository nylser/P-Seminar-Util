import configparser
import os


default_config = {"last_select_dir": os.path.expanduser("~"), "last_username": "", "last_password": ""}


def load_config():
    config_path = os.path.join(os.path.expanduser("~"), ".table2dbf.config")
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def save_config(config):
    config_path = os.path.join(os.path.expanduser("~"), ".table2dbf.config")
    with open(config_path, 'w') as config_file:
        config.write(config_file)
