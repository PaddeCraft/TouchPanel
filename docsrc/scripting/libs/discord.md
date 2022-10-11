# Discord RPC Remote

## About

With this library you can automate Discord, e.g. mute your microphone or join a voice channel.

## Setup

1. Go to [the Discord developer portal](https://discord.com/developers/applications)
2. Create a new application
3. In the sidebar, navigate to OAuth2
4. Add a redirect to `http://localhost`
5. Save Client ID and Client Secret, we'll need these later
6. Create an action using one of the features of this library
8. Run the previously created action
9. Navigate to ~/.PaddeCraftSoftware/TouchPanel/
10. Fill in the Client ID and Client Secret under the section "builtin.discord" in the file plugincfg.toml
11. Open the Discord app on your computer, the website won't work
12. Run the previously created action again
13. Click 'Authorize' in the discord app
14. You're ready to go!

## Import

```py
from touchpanel.libs import discord
```

## Classes

```py
class discord.DiscordController:
    def __init__() -> None:

    def toggleMic() -> None
    def setMic(on: bool) -> None
    def joinVoiceChannel(id: str) -> None
    def setTextChannel(id: str) -> None
    def getVoiceSettings() -> pypresence.Response
    def getSelectedVoiceChannel() -> pypresence.Response
    def getGuilds() -> pypresence.Response
    def getChannels() -> pypresence.Response
```
