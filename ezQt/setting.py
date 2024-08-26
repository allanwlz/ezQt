import os
import configparser
from pymongo import MongoClient
from multiprocessing import Lock
from ezQt.config import MongoConfig


path = os.path.expanduser('~')
qt_path = '{}{}{}'.format(path, os.sep, '.ezqt')

def generate_path(name):
    return '{}{}{}'.format(qt_path, os.sep, name)

def make_dir(path, exist_ok=True):
    os.makedirs(path, exist_ok=exist_ok)
    
setting_path = generate_path('setting')
make_dir(qt_path, exist_ok=True)
make_dir(setting_path, exist_ok=True)
CONFIGFILE_PATH = '{}{}{}'.format(setting_path, os.sep, 'config.ini')


class EzQtSetting():
    def __init__(self):
        self.lock = Lock()
        self.db_host = MongoConfig.DEFAULT_MONGO_HOST
        self.db_port = MongoConfig.DEFAULT_MONGO_PORT
        self.db_username = MongoConfig.DEFAULT_MONGO_USER
        self.db_password = MongoConfig.DEFAULT_MONGO_PSW

    @property
    def client(self):
        client = MongoClient(
            host=self.db_host,
            port=self.db_port,
            username=self.db_username,
            password=self.db_password,
            authSource='admin' 
        )
        return client

    def get_config(self, section, option, default_value=None):
        config = configparser.ConfigParser()
        config.read(CONFIGFILE_PATH)

        try:
            return config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default_value is not None:
                return default_value
            else:
                raise  # 如果没有默认值，重新抛出异常
    
    def set_config(self, section, option, value):
        config = configparser.ConfigParser()
        config.read(CONFIGFILE_PATH)
        if section not in config.sections():
            config.add_section(section)
        config.set(section, option, value)
        with open(CONFIGFILE_PATH, 'w') as f:
            config.write(f)
            
EzQtSETTING = EzQtSetting()
DATABASE = EzQtSETTING.client.quant