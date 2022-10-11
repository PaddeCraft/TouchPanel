# Configuration Manager

## About

A global configuration manager.

## Import

```py
from touchpanel.libs import configmgr
```

## Classes

```py
class configmgr.Config:
    def __init__(id: str, defaultCfg: dict) -> None

    def __getitem__(item) -> any
    def __setitem__(key, value) -> None
    def writeToDisk() -> None
```

## ID naming scheme

id (str): The plugin/library id.
        Naming scheme:
            built-in library: builtin.<name>
            plugin/extension: Like java packages, e.g. de.paddecraft.tp-discord

## Usage example

```py
config = Config(
            "de.paddecraft.thisisanexample",
            {
                "a": "b",
                "c": {
                    "e": "f"
                }
            },
        )

a = config["a"]
e = config["c"]["e"]

config["c"]["g"] = "h"
config.writeToDisk()
```