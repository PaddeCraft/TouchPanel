import os
import toml

cfgFile = os.path.join(
    os.path.expanduser("~"), ".PaddeCraftSoftware", "TouchPanel", "plugincfg.toml"
)


class Config:
    def __init__(self, id: str, defaultCfg: dict) -> None:
        """Create a config controller

        Args:
            id (str): The plugin/library id.
            Naming scheme:
                built-in library: builtin.<name>
                plugin/extension: Like java packages, e.g. de.paddecraft.tp-discord
        """
        self.id = id
        if not os.path.isfile(cfgFile):
            with open(cfgFile, "w+", encoding="UTF-8") as f:
                f.write("")
        with open(cfgFile, "r+", encoding="UTF-8") as f:
            cfg = toml.load(f)
            if not id in cfg:
                cfg[id] = defaultCfg
                toml.dump(cfg, f)
            self.config = cfg[id]

    def __getitem__(self, item) -> any:
        return self.config[item]

    def __setitem__(self, key, value) -> None:
        self.config[key] = value

    def writeToDisk(self) -> None:
        with open(cfgFile, "w", encoding="UTF-8") as f:
            cfg = toml.load(cfgFile)
            cfg[self.id] = self.config
            toml.dump(cfg, f)
