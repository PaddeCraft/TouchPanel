# OBS controller library WSv4

## About

With this library you can automate your OBS, if you are using OBS WebScokets v4 (mostly version <28).

## Requirements

OBS with websockets v4 enabled.
DISCLAIMER: Only works with WebSockets V4.

## Import

```py
from touchpanel.libs import obs4
```

## Classes

```py
class obs4.ObsController:
    def __init__(self, host: str = "localhost", port: int = 4444, password: str = "") -> None

    def getScenes() -> dict
    def getSources() -> dict
    def getCurrentScene() -> dict
    def setProfile(name: str) -> None
    def setScene(name: str) -> None

# VideoStreamState Enum class
class obs4.VideoStreamState(Enum):
    STOPPED = 1
    PAUSED = 2
    RUNNING = 3

# Is the class of ObsController.recording
class obs4.Recording:
    def getState() -> VideoStreamState, str(time) | NoneType(None)
    def pause() -> None
    def start() -> None
    def end() -> None

# Is the class of ObsController.stream
class obs4.Stream:
    def getState(self) -> bool(isRunning), str(time) | NoneType(None)
    def start()  -> None
    def end() -> None
```