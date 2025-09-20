import yaml


class ConfigLoader:
    """Loads and stores configuration from a YAML file."""

    def __init__(self, config_path: str):
        self.config_path: str = config_path
        self.config_dit: dict[str, object] = {}
        self.load_config()

    def load_config(self):
        """
        Initialize the ConfigLoader with a path to the config file.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        try:
            with open(self.config_path, "r") as file:
                self.config_dict = yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")

        return self.config_dict
