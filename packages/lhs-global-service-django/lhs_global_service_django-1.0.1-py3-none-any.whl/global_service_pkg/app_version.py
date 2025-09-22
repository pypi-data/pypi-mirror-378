import os
import configparser

def get_app_version():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.properties'))
    return config.get('APP VERSION', 'app_version', fallback="Unknown")