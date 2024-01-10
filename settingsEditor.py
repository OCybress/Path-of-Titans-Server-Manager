'''
Author:     OCybress
Date:       01-08-2024
Summary:    Game Setting Editor, reads in Game.ini propagates settings 
            as labels and entries ( sliders floats ) and allows editing without 
            needing to manually edit Game.ini
Updates: 

'''

import configparser
import tkinter as tk
from tkinter import ttk, Entry, Checkbutton

class GameSettingsEditor:
    def __init__(self, root, update_message_func, install_dir='./'):
        """
        Initializes the Game Settings Editor.

        Args:
            root (Tk): The root Tkinter window.
            update_message_func (function): A function to update the message.
            install_dir (str, optional): The installation directory of the game. Defaults to './'.
        """
        self.root = root
        self.root.title("Game Settings Editor")
        self.game_ini_path = f'{install_dir}/PathOfTitans/Saved/Config/WindowsServer/Game.ini'
        self.update_message = update_message_func
        self.update_message(f'Got Game.ini dir : {self.game_ini_path}')

        # Load the Game.ini file
        self.config = configparser.ConfigParser()
        self.config.read(self.game_ini_path)

        # Create a dictionary to hold the settings
        self.settings = {}
        self.entry_widgets = []
        self.checkbutton_widgets = []

        # Set the maximum number of columns
        self.max_columns = 8

        # Build the GUI
        self.canvas = None
        self.frame = None
        self.create_widgets()

    def create_widgets(self):
        """
        Create and configure the widgets for the settings editor.

        This method creates a canvas, scrollbar, and frame to hold the settings widgets.
        It iterates through the sections and options in the configuration file and creates
        the appropriate widgets for editing each option. The widgets include labels, checkbuttons,
        sliders, and entry fields. Finally, it adds a save button to save the settings.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.canvas = tk.Canvas(self.root, width=1200, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame = ttk.Frame(self.canvas)
        self.frame.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Set the canvas scrolling region
        self.canvas.configure(yscrollcommand=scrollbar.set, scrollregion=self.canvas.bbox("all"))
        row = 0

        # Iterate through sections in the Game.ini file
        for section in self.config.sections():
            # Add a label for the section
            ttk.Label(self.frame, text=f"[{section}]").grid(row=row, column=0, columnspan=self.max_columns, sticky="w", pady=(0, 5))

            # Iterate through options in each section
            col = 0
            for option in self.config.options(section):
                # Display the option and its current value
                ttk.Label(self.frame, text=f"{option}").grid(row=row + 1, column=col, sticky="w", pady=(0, 10))

                # Determine the type of the configuration option
                value_type = self.get_value_type(self.config.get(section, option))

                # Create the appropriate widget for editing
                if value_type == bool:
                    checkbox_var = tk.BooleanVar(value=bool(self.config.getboolean(section, option)))
                    checkbutton = ttk.Checkbutton(self.frame, variable=checkbox_var, text="Enable")
                    checkbutton.grid(row=row + 1, column=col + 1, sticky="w")
                    self.settings[(section, option)] = checkbox_var
                    self.checkbutton_widgets.append(checkbutton)
                elif value_type == float:
                    # Use a horizontal slider for float values
                    slider_var = tk.DoubleVar(value=float(self.config.get(section, option)))
                    ttk.Label(self.frame, text=f"{option}").grid(row=row + 1, column=col + 2, sticky="w")
                    slider = ttk.Scale(self.frame, variable=slider_var, from_=0, to=100, orient="horizontal", length=200)
                    slider.grid(row=row + 1, column=col + 3, sticky="w")
                    self.settings[(section, option)] = slider_var
                    self.entry_widgets.append(slider)
                else:
                    entry_var = tk.StringVar(value=self.config.get(section, option))
                    entry = ttk.Entry(self.frame, textvariable=entry_var)
                    entry.grid(row=row + 1, column=col + 1, sticky="w", pady=(5, 0), padx=(3, 5))
                    self.settings[(section, option)] = entry_var
                    self.entry_widgets.append(entry)

                col += 4  # Increment by 4 for label, widget, label, and widget

                if col >= self.max_columns * 4:
                    col = 0
                    row += 1

        # Save button
        ttk.Button(self.frame, text="Save Settings", command=self.save_settings).grid(row=row + 2, column=0, columnspan=self.max_columns, sticky="w", pady=(10, 0))

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_value_type(self, value):
            """
            Determines the type of the given value.

            Args:
                value: The value to determine the type of.

            Returns:
                The type of the value. It can be bool, float, or str.
            """
            try:
                # Attempt to convert the value to boolean
                bool_value = self.config.getboolean('temp_section', 'temp_option')
                if bool_value in (True, False):
                    return bool
            except ValueError:
                pass
            except configparser.NoSectionError:
                pass

            try:
                # Attempt to convert the value to float
                float_value = float(self.config.get('temp_section', 'temp_option'))
                return float
            except ValueError:
                pass
            except configparser.NoSectionError:
                pass

            # Default to string if not boolean or float
            return str

    def save_settings(self):
        """
        Save the settings by updating the configuration with values from widgets and writing the changes to the file.

        Raises:
            Exception: If there is an error while saving the settings.
        """
        try:
            # Update the configuration with values from widgets
            self.update_message('Updating Game.ini')
            for widget in self.frame.winfo_children():  # Access frame as self.frame
                if isinstance(widget, ttk.Entry):
                    option = widget.grid_info()['row'] - 1  # Adjust for the label row
                    section = widget.grid_info()['column'] // 4
                    option_name = self.config.options(self.config.sections()[section])[option]
                    value = widget.get()
                    self.config.set(self.config.sections()[section], option_name, value)
                elif isinstance(widget, ttk.Checkbutton):
                    option = widget.grid_info()['row'] - 1  # Adjust for the label row
                    section = widget.grid_info()['column'] // 4
                    option_name = self.config.options(self.config.sections()[section])[option]
                    value = 'true' if widget.var.get() else 'false'
                    self.config.set(self.config.sections()[section], option_name, value)

            # Save the configuration to the file
            with open(self.game_ini_path, 'w') as configfile:
                self.update_message(f'Writing changes to: {self.game_ini_path}')
                self.config.write(configfile)
        except Exception as e:
            self.update_message(e)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameSettingsEditor(root)
    root.mainloop()
