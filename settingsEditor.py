import configparser
import tkinter as tk
from tkinter import ttk, Entry, Checkbutton

class GameSettingsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Settings Editor")

        # Load the Game.ini file
        self.config = configparser.ConfigParser()
        self.config.read('Game.ini')

        # Create a dictionary to hold the settings
        self.settings = {}

        # Set the maximum number of columns
        self.max_columns = 8

        # Build the GUI
        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self.root, width=1200, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame = ttk.Frame(canvas)
        frame.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Set the canvas scrolling region
        canvas.configure(yscrollcommand=scrollbar.set, scrollregion=canvas.bbox("all"))
        row = 0

        # Iterate through sections in the Game.ini file
        for row, section in enumerate(self.config.sections()):
            # Add a label for the section
            ttk.Label(frame, text=f"[{section}]").grid(row=row, column=0, columnspan=self.max_columns, sticky="w", pady=(0, 5))

            # Iterate through options in each section
            col = 0
            for option in self.config.options(section):
                # Display the option and its current value
                ttk.Label(frame, text=f"{option} = {self.config.get(section, option)}").grid(row=row+1, column=col, sticky="w", pady=(0, 10))

                # Determine the type of the configuration option
                value_type = self.get_value_type(self.config.get(section, option))

                # Create the appropriate widget for editing
                if value_type == bool:
                    checkbox_var = tk.BooleanVar(value=bool(self.config.getboolean(section, option)))
                    ttk.Checkbutton(frame, variable=checkbox_var, text="Enable").grid(row=row+1, column=col + 1, sticky="w")
                    self.settings[(section, option)] = checkbox_var
                elif value_type == float:
                    # Use a horizontal slider for float values
                    slider_var = tk.DoubleVar(value=float(self.config.get(section, option)))
                    ttk.Label(frame, text=f"{option}").grid(row=row+1, column=col + 2, sticky="w")
                    ttk.Scale(frame, variable=slider_var, from_=0, to=100, orient="horizontal", length=200).grid(row=row, column=col + 3, sticky="w")
                    self.settings[(section, option)] = slider_var
                else:
                    entry_var = tk.StringVar(value=self.config.get(section, option))
                    ttk.Entry(frame, textvariable=entry_var).grid(row=row+1, column=col + 1, sticky="w", pady=(5,0), padx=(3,5))
                    self.settings[(section, option)] = entry_var

                col += 4  # Increment by 4 for label, widget, label, and widget

                if col >= self.max_columns * 4:
                    col = 0
                    row += 1

        # Save button
        ttk.Button(frame, text="Save Settings", command=self.save_settings).grid(row=row+2, column=0, columnspan=self.max_columns, sticky="w", pady=(10, 0))

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def get_value_type(self, value):
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
        # Update the configuration with values from widgets
        for widget in self.master.winfo_children():
            if isinstance(widget, Entry):
                option = widget.master.children['!label'].cget('text')
                value = widget.get()
                self.config['GameSettings'][option] = value
            elif isinstance(widget, Checkbutton):
                option = widget.master.children['!label'].cget('text')
                value = 'true' if widget.var.get() else 'false'
                self.config['GameSettings'][option] = value

        # Save the configuration to the file
        with open('PathOfTitans/Game.ini', 'w') as configfile:
            self.config.write(configfile)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameSettingsEditor(root)
    root.mainloop()
