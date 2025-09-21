import re
from .exceptions import ValidationError

_AM_URL = re.compile(r"^https?://music\.apple\.com/")

def require_nonempty_str(name: str, value: str):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")

def validate_volume(v: float):
    if not isinstance(v, (int, float)):
        raise ValidationError("volume must be a number between 0.0 and 1.0")
    if v < 0.0 or v > 1.0:
        raise ValidationError("volume must be in [0.0, 1.0]")

def validate_rating(r: int):
    if r not in (-1, 0, 1):
        raise ValidationError("rating must be -1 (dislike), 0 (none), or 1 (like)")

def validate_queue_index(i: int):
    if not isinstance(i, int) or i < 1:
        raise ValidationError("queue index must be a positive 1-based integer")

def validate_item_type(t: str):
    allowed = {"songs", "albums", "playlists", "stations", "music-videos", "artists"}
    if t not in allowed:
        raise ValidationError(f"item_type must be one of {sorted(allowed)}")

def validate_am_url(url: str):
    if not _AM_URL.match(url):
        raise ValidationError("url must be an Apple Music URL (https://music.apple.com/...)")
