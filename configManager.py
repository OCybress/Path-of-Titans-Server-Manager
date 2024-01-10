'''
Author:     OCybress
Date:       01-08-2024
Summary:    Configuration manager. Reads and writes program Configuration file.
Updates: 
'''

import configparser

class ConfigManager:
    """
    A class that manages configuration files.

    Args:
        config_file_path (str): The path to the configuration file.

    Attributes:
        config_file_path (str): The path to the configuration file.
        config (ConfigParser): The ConfigParser object used to read and write the configuration file.

    Methods:
        save_config: Saves a configuration value to the file.
        read_config: Reads a configuration value from the file.
        read_entire_config: Reads the entire configuration file.

    """

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

    def save_config(self, section, key, value):
        """
        Saves a configuration value to the file.

        Args:
            section (str): The section name.
            key (str): The key name.
            value (str): The value to be saved.

        Returns:
            None

        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    def read_config(self, section, key):
        """
        Reads a configuration value from the file.

        Args:
            section (str): The section name.
            key (str): The key name.

        Returns:
            str or None: The value if found, None otherwise.

        """
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        return None

    def read_entire_config(self):
        """
        Reads the entire configuration file.

        Returns:
            dict: A dictionary containing the configuration values.

        """
        self.config.read(self.config_file_path)
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = {}
            for option in self.config.options(section):
                config_dict[section][option] = self.config.get(section, option)
        return config_dict