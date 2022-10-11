from touchpanel.libs.configmgr import Config
from pypresence import Client
import asyncio
import requests


class DiscordController:
    def __init__(self) -> None:
        self.config = Config(
            "builtin.discord",
            {
                "clientid": "YOUR-CLIENT-ID",
                "clientsecret": "YOUT-CLIENT-SECRET",
                "oauthtoken": "none",
            },
        )
        self.client = Client(self.config["clientid"], loop=asyncio.new_event_loop())
        self.client.start()
        if self.config["oauthtoken"] == "none":

            authGrant = self.client.authorize(
                self.config["clientid"], ["rpc", "identify", "guilds"]
            )["data"]["code"]
            r = requests.post(
                "https://discordapp.com/api/oauth2/token",
                data=f'client_id={self.config["clientid"]}&grant_type=authorization_code&code={authGrant}&redirect_uri=http%3A%2F%2Flocalhost&client_secret={self.config["clientsecret"]}',
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            self.config["oauthtoken"] = r.json()["access_token"]
            self.config["refreshtoken"] = r.json()["refresh_token"]
            self.config.writeToDisk()

        try:
            self.client.authenticate(self.config["oauthtoken"])
        except:
            try:
                r = requests.post(
                    "https://discordapp.com/api/oauth2/token",
                    data=f'client_id={self.config["clientid"]}&grant_type=refresh_token&refresh_token={self.config["refreshtoken"]}&client_secret={self.config["clientsecret"]}',
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                    },
                )
                self.config["oauthtoken"] = r.json()["access_token"]
                self.config["refreshtoken"] = r.json()["refresh_token"]
                self.config.writeToDisk()
                self.client.authenticate(self.config["oauthtoken"])

            except:
                self.config["oauthtoken"] = "none"
                self.config.writeToDisk()
                raise Exception(
                    "Your oauth2-token didn`t work for some reason. Run again to re-authorize."
                )

    def toggleMic(self) -> None:
        state = self.client.get_voice_settings()["data"]["mute"]
        self.client.set_voice_settings(mute=not state)

    def setMic(self, on: bool) -> None:
        self.client.set_voice_settings(mute=not on)

    def joinVoiceChannel(self, id: str) -> None:
        self.client.select_voice_channel(id)

    def setTextChannel(self, id: str) -> None:
        self.client.select_text_channel(id)

    def getVoiceSettings(self):
        return self.client.get_voice_settings()

    def getSelectedVoiceChannel(self):
        return self.client.get_selected_voice_channel()

    def getGuilds(self):
        return self.client.get_guilds()

    def getChannels(self):
        return self.client.get_channel()

    def __del__(self):
        self.client.close()
