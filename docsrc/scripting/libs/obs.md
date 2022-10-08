# OBS controller library

## About

With this library you can automate your OBS.

## Requirements

OBS with websockets enabled.
DISCLAIMER: Only works with WebSockets V4 at the moment (Al least it should). Will be updating soon.

## Import

```py
from touchpanel.libs import obs
```

## Classes

```py
class obs.ObsController:
    def __init__(self, host: str = "localhost", port: int = 4444, password: str = "") -> None

    def getScenes() -> dict
    def getSources() -> dict
    def getCurrentScene() -> dict
    def setProfile(name: str) -> None
    def setScene(name: str) -> None

# VideoStreamState Enum class
class obs.VideoStreamState(Enum):
    STOPPED = 1
    PAUSED = 2
    RUNNING = 3

# Is the class of ObsController.recording
class obs.Recording:
    def getState() -> VideoStreamState, str(time) | NoneType(None)
    def pause() -> None
    def start() -> None
    def end() -> None

# Is the class of ObsController.stream
class obs.Stream:
    def getState(self) -> bool(isRunning), str(time) | NoneType(None)
    def start()  -> None
    def end() -> None
```