from obswebsocket import obsws, requests

from enum import Enum


class VideoStreamState(Enum):
    STOPPED = 1
    PAUSED = 2
    RUNNING = 3


class Recording:
    def __init__(self, controller) -> None:
        self.controller = controller

    def getState(self):
        state = self.controller.ws.call(requests.GetRecordingStatus())
        time = state.recordTimecode
        if state.isRecording == False:
            return VideoStreamState.STOPPED, None
        else:
            if state.isRecordingPaused == True:
                return VideoStreamState.PAUSED, time
            else:
                return VideoStreamState.RUNNING, time

    def pause(self) -> None:
        state, time = self.getState()
        if state == VideoStreamState.RUNNING:
            self.controller.ws.call(requests.PauseRecording())

    def start(self) -> None:
        state, time = self.getState()
        if not state == VideoStreamState.RUNNING:
            self.controller.ws.call(requests.StartRecording())

    def end(self) -> None:
        state, time = self.getState()
        if not state == VideoStreamState.STOPPED:
            self.controller.ws.call(requests.StopRecording())


class Stream:
    def __init__(self, controller) -> None:
        self.controller = controller

    def getState(self):
        state = self.controller.ws.call(requests.GetStreamingStatus())
        if state.streaming:
            return True, state.stream_timecode
        else:
            return False, None

    def start(self) -> None:
        running, time = self.getState()
        if not running:
            self.controller.ws.call(requests.StartStreaming())

    def end(self) -> None:
        running, time = self.getState()
        if running:
            self.controller.ws.call(requests.StopStreaming())


class ObsController:
    def __init__(
        self, host: str = "localhost", port: int = 4444, password: str = ""
    ) -> None:
        self.ws = obsws(host, port, password)
        self.ws.connect()
        self.recording = Recording(self)
        self.stream = Stream(self)

    def getScenes(self) -> dict:
        return self.ws.call(requests.GetSceneList())

    def getSources(self) -> dict:
        return self.ws.call(requests.GetMediaSourcesList())

    def getCurrentScene(self) -> dict:
        return self.ws.call(requests.GetCurrentScene())

    def setProfile(self, name: str) -> None:
        return self.ws.call(requests.SetCurrentProfile(name))

    def setScene(self, name: str) -> None:
        self.ws.call(requests.SetCurrentScene(name))

    def __del__(self):
        self.ws.disconnect()
