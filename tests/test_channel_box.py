import time
import pytest
from unittest.mock import MagicMock

from channel_box import Channel, ChannelBox
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect


@pytest.fixture(autouse=True)
def clean_channel_box():
    ChannelBox.CHANNEL_GROUPS = {}
    ChannelBox.CHANNEL_GROUPS_HISTORY = {}
    yield
    ChannelBox.CHANNEL_GROUPS = {}
    ChannelBox.CHANNEL_GROUPS_HISTORY = {}


@pytest.fixture
def mock_websocket():
    return MagicMock(spec=WebSocket)


@pytest.mark.asyncio
async def test_add_and_remove_channel(mock_websocket):
    group_name = "test_group"

    channel = Channel(
        websocket=mock_websocket,
        expires=3600,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    groups = await ChannelBox.get_groups()
    assert group_name in groups
    assert channel in groups[group_name]
    assert "created_at" in groups[group_name][channel]

    await ChannelBox.remove_channel_from_group(channel, group_name)

    groups = await ChannelBox.get_groups()
    assert channel not in groups.get(group_name, {})


@pytest.mark.asyncio
async def test_channel_not_duplicated(mock_websocket):
    group_name = "dedup_group"

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)
    await ChannelBox.add_channel_to_group(channel, group_name)

    groups = await ChannelBox.get_groups()
    assert len(groups[group_name]) == 1


@pytest.mark.asyncio
async def test_flush_groups(mock_websocket):
    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, "group")
    await ChannelBox.flush_groups()

    groups = await ChannelBox.get_groups()
    assert not groups


@pytest.mark.asyncio
async def test_group_send_success_updates_last_active(mock_websocket):
    group_name = "group_ok"

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    last_active_before = channel.last_active

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"ok": True},
    )

    mock_websocket.send_json.assert_called_once()
    assert channel.last_active >= last_active_before


@pytest.mark.asyncio
async def test_group_send_closed_socket_removes_channel(mock_websocket):
    group_name = "group_closed"

    mock_websocket.send_json.side_effect = WebSocketDisconnect(code=1006)

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"msg": "fail"},
    )

    groups = await ChannelBox.get_groups()
    assert group_name not in groups or channel not in groups[group_name]

    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_group_send_partial_disconnect():
    group_name = "mixed_group"

    alive_ws = MagicMock(spec=WebSocket)
    dead_ws = MagicMock(spec=WebSocket)
    dead_ws.send_json.side_effect = RuntimeError("closed")

    alive_channel = Channel(
        websocket=alive_ws,
        expires=60,
        payload_type="json",
    )
    dead_channel = Channel(
        websocket=dead_ws,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(alive_channel, group_name)
    await ChannelBox.add_channel_to_group(dead_channel, group_name)

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"ping": 1},
    )

    groups = await ChannelBox.get_groups()

    assert alive_channel in groups[group_name]
    assert dead_channel not in groups[group_name]

    alive_ws.send_json.assert_called_once()
    dead_ws.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_group_send_text_payload():
    ws = MagicMock(spec=WebSocket)

    channel = Channel(
        websocket=ws,
        expires=60,
        payload_type="text",
    )

    await ChannelBox.add_channel_to_group(channel, "text_group")

    await ChannelBox.group_send(
        group_name="text_group",
        payload="hello",
    )

    ws.send_text.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_group_send_history_saved(mock_websocket):
    group_name = "history_group"

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"hello": "world"},
        save_history=True,
    )

    history = await ChannelBox.get_history(group_name)
    assert len(history) == 1
    assert history[0].payload == {"hello": "world"}


@pytest.mark.asyncio
async def test_group_send_history_not_saved(mock_websocket):
    group_name = "no_history"

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"x": 1},
        save_history=False,
    )

    history = await ChannelBox.get_history(group_name)
    assert not history


@pytest.mark.asyncio
async def test_flush_history(mock_websocket):
    group_name = "flush_history"

    channel = Channel(
        websocket=mock_websocket,
        expires=60,
        payload_type="json",
    )

    await ChannelBox.add_channel_to_group(channel, group_name)

    await ChannelBox.group_send(
        group_name=group_name,
        payload={"x": 1},
        save_history=True,
    )

    await ChannelBox.flush_history()

    history = await ChannelBox.get_history()
    assert not history


@pytest.mark.asyncio
async def test_clean_expired_removes_channel(mock_websocket):
    group_name = "expired_group"

    channel = Channel(
        websocket=mock_websocket,
        expires=0,
        payload_type="json",
    )

    channel.last_active = time.time() - 10

    await ChannelBox.add_channel_to_group(channel, group_name)
    await ChannelBox.clean_expired()

    groups = await ChannelBox.get_groups()
    assert not groups
