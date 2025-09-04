import pytest

from unittest.mock import MagicMock
from channel_box import Channel, ChannelBox
from starlette.websockets import WebSocket


@pytest.fixture
def mock_websocket():
    mock = MagicMock(spec=WebSocket)
    mock.send.return_value = None
    return mock


@pytest.mark.asyncio
async def test_channel_box(
    mock_websocket,
):
    group_name = "test_group"

    channel = Channel(
        websocket=mock_websocket,
        expires=60 * 60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(
        channel=channel,
        group_name=group_name,
    )
    groups = await ChannelBox.get_groups()
    assert group_name in groups
    assert "created_at" in groups[group_name][channel]

    await ChannelBox.remove_channel_from_group(
        channel=channel,
        group_name=group_name,
    )
    await ChannelBox.add_channel_to_group(
        channel=channel,
        group_name=group_name,
    )
    groups = await ChannelBox.get_groups()
    assert groups
    assert len(groups) == 1

    await ChannelBox.flush_groups()
    groups = await ChannelBox.get_groups()
    assert not groups

    await ChannelBox.add_channel_to_group(
        channel=channel,
        group_name=group_name,
    )

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"hello": "world"},
        save_history=True,
    )

    history = await ChannelBox.get_history()
    assert history
    assert len(history) == 1

    await ChannelBox.flush_history()

    history = await ChannelBox.get_history()
    assert not history
