import codecs
import shutil
from pathlib import Path


class ConfigReader:
    """
    Simple class for loading saved parameters from a text file. Uses "base-config.txt" for default values,
    then loads any user values from "local-config.txt"
    """
    BASE_CONFIG = "base-config.txt"
    LOCAL_CONFIG = "local-config.txt"

    def __init__(self):
        self.values = {}

        # Start by parsing the base config file, then overwriting with any local versions
        self.parse_config_file(self.BASE_CONFIG)
        self.parse_config_file(self.LOCAL_CONFIG)

    def parse_config_file(self, filename):
        if not Path(filename).exists():
            return

        with codecs.open(filename, encoding="utf-8") as file:
            for line in file.readlines():

                # If the line is blank or is a comment, ignore
                if not line.strip() or line.startswith("#"):
                    continue

                # Split off anything after any # values
                line = line.split("#")[0]

                if "=" not in line:
                    print("Error parsing config: line is not parsable:")
                    print(line)
                    continue

                key, value = line.split("=", 1)
                self.values[key.strip()] = value.strip()

    def get_break_length(self):
        return int(self.values["BREAK_LENGTH"]) * 60 * 1000

    def get_work_length(self):
        return int(self.values["WORK_LENGTH"]) * 60 * 1000

    def get_stand_frequency(self):
        return int(self.values["STAND_FREQUENCY"])

    def get_stand_length(self):
        return int(self.values["STAND_TIME"]) * 60 * 1000

    def get_break_prompt_text(self):
        return self.values["BREAK_PROMPT_TEXT"].replace("\\n", "\n")

    def get_work_start_text(self):
        return self.values["WORK_START_TEXT"].replace("\\n", "\n")

    def get_stand_up_text(self):
        return self.values["STAND_UP_TEXT"].replace("\\n", "\n")

    def get_position_one_offsets(self):
        offset_x = int(self.values["POSITION_ONE_OFFSET_X"])
        offset_y = int(self.values["POSITION_ONE_OFFSET_Y"])
        return offset_x, offset_y

    def get_position_two_offsets(self):
        offset_x = int(self.values["POSITION_TWO_OFFSET_X"])
        offset_y = int(self.values["POSITION_TWO_OFFSET_Y"])
        return offset_x, offset_y

    def get_saved_position(self):
        return int(self.values["CURRENT_POSITION"])

    def set_current_position(self, value):
        # If a local config doesn't exist, create it
        if not Path(self.LOCAL_CONFIG).exists():
            shutil.copyfile(self.BASE_CONFIG, self.LOCAL_CONFIG)

        # Open local config file and change only the changed position
        with codecs.open(self.LOCAL_CONFIG, encoding="utf-8") as file:
            lines = file.readlines()

        # TODO: If an older version is used and CURRENT_POSITION doesn't exist,
        # it should add it
        with codecs.open(self.LOCAL_CONFIG, "w", encoding="utf-8") as file:
            for line in lines:
                if "CURRENT_POSITION" in line:
                    file.write(f"CURRENT_POSITION={value}\n")
                else:
                    file.write(line)


