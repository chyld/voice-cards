import configparser

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_int(self, key, fallback=0):
        return self.config.getint('Settings', key, fallback=fallback)

    def get_str(self, key, fallback=''):
        return self.config.get('Settings', key, fallback=fallback)

    @property
    def record_duration(self):
        return self.get_int('record_duration', fallback=3)

    @property
    def debug(self):
        return self.get_int('debug', fallback=0)

    @property
    def min_value(self):
        return self.get_int('min_value', fallback=0)

    @property
    def max_value(self):
        return self.get_int('max_value', fallback=12)

    @property
    def api_key(self):
        return self.get_str('api_key')

config = ConfigManager()