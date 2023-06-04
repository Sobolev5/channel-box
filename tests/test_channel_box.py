import pytest
from channel_box import ChannelBox

@pytest.mark.asyncio
async def test():  
    channel_box = ChannelBox()
    await channel_box.channel_send("test", {"hello":"world"}, history=True)
    history = await channel_box.history()
    assert history    

    # TODO complex test