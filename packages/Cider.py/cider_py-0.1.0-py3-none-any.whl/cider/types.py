from enum import IntEnum
from typing import Any, Callable, Dict, Optional, Union, List, Literal, TypedDict

ItemType = Literal["songs", "albums", "playlists", "stations", "music-videos", "artists"]

class RepeatMode(IntEnum):
    OFF = 0
    ONE = 1
    ALL = 2

QueueIndex = int

EventCallback = Callable[..., None]
AsyncEventCallback = Callable[..., Any]

class NowPlayingInfo(TypedDict, total=False):
    status: str
    info: Dict[str, Any]
