from asyncio import Event
from rich.console import Console

debug = 0
console = Console(stderr=True)
tele_used = Event()
emby_used = Event()
subsonic_used = Event()
exit_handlers = []
use_mongodb_config = False
telegram_test_server = False
