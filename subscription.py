import os
import asyncio
from pprint import pprint
from dotenv import load_dotenv

from stxsdk import StxChannelClient
from stxsdk.config.channels import CHANNELS

from stx_types import StxChannel


class StxSubscriptionHandler:
    def __init__(self, email, password):
        if 'success' not in self.client.login(params={
            'email': email,
            'password': password,
        }):
            raise Exception("Failed to login!")
        
        self.channels = list(CHANNELS)
        self.client = StxChannelClient()

    def get_channel_method(self, channel: StxChannel):
        pprint(f"{channel.value}_join")
        return getattr(self.client, f"{channel.value}_join")

    async def on_open(self, _):
        print("Opening connection!")

    async def on_message(self, message):
        pprint(message)

    async def on_close(self, _):
        print("Closing connection!")

    async def on_error(self, message):
        pprint("ERROR!", message)

    async def default(self, message):
        pprint("Unsupported Event", message)


def main():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    handler = StxSubscriptionHandler(email, password)
    method = handler.get_channel_method(StxChannel.active_orders)

    asyncio.run(
        method(
            on_open=handler.on_open,
            on_message=handler.on_message,
            default=handler.default,
        )
    )

if __name__ == '__main__':
    load_dotenv()
    main()
