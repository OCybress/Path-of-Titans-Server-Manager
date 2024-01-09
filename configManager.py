'''
Author:     OCybress
Date:       01-08-2024
Summary:    Configuration manager. Reads and writes program Configuration file.
Updates: 
'''

import configparser

class ConfigManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

    def save_config(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    def read_config(self, section, key):
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        return None

    def read_entire_config(self):
        self.config.read(self.config_file_path)
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = {}
            for option in self.config.options(section):
                config_dict[section][option] = self.config.get(section, option)
        return config_dict