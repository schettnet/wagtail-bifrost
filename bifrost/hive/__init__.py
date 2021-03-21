import asyncio
import threading

from ..settings import BIFROST_API_HIVE


def between_callback():
    from .connection import connect

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(connect())
    loop.close()


def start_connection_thread():
    _thread = threading.Thread(target=between_callback)
    _thread.setDaemon(True)
    _thread.start()


connect = lambda: start_connection_thread() if BIFROST_API_HIVE else None
