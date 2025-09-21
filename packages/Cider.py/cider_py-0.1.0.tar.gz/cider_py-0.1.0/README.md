### An **unofficial** implementation of the [Cider v2 API](https://github.com/ciderapp/Cider-2/blob/main/docs/Cider%202.5.0%20Preview%20API.md) in python

> This is barely tested, and is for the most part, a concept, and may be subject to change

Python sync/async client for the Cider v2 local API (HTTP + Socket.IO).
* Full coverage of Cider v2 playback, queue, volume, repeat/shuffle/autoplay
* Apple Music API passthrough (`/v1/amapi/run-v3`)
* Sync + Async clients

## Quickstart

```python
from cider import CiderClient

cider = CiderClient()  # or CiderClient(api_token="...")
print("Active:", cider.ping())
print("Now playing:", cider.now_playing())
```