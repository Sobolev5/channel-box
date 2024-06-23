import pytest
from unittest.mock import MagicMock
from channel_box import Channel, ChannelBox
from starlette.websockets import WebSocket


@pytest.mark.asyncio
async def test_channel_box():
    group_name = "test"
    mock = MagicMock(spec=WebSocket)  # mock starlette.websockets.WebSocket
    mock.send.return_value = None
    channel = Channel(websocket=mock, expires=60 * 60, encoding="json")

    # add channel
    status = await ChannelBox.channel_add(group_name, channel)
    assert status.name == "ADDED"

    # remove channel
    status = await ChannelBox.channel_remove(group_name, channel)
    assert status.name == "GROUP_REMOVED"

    # groups
    await ChannelBox.channel_add(group_name, channel)
    groups = await ChannelBox.groups()
    assert groups

    await ChannelBox.groups_flush()
    groups = await ChannelBox.groups()
    assert not groups

    # group send
    await ChannelBox.channel_add(group_name, channel)
    status = await ChannelBox.group_send(group_name, {"hello": "world"}, history=True)
    assert status.name == "GROUP_SEND"

    # history
    history = await ChannelBox.history()
    assert history

    await ChannelBox.history_flush()
    history = await ChannelBox.history()
    assert not history
