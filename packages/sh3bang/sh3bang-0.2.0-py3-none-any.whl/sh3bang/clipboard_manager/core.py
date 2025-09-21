import time
from threading import Event, Thread
from typing import Optional

import pyperclip

from .storage import Storage

_storage = Storage()
_watcher_thread: Optional[Thread] = None
_watcher_stop_event: Optional[Event] = None


def save_text(text: str) -> int:
    """Save text to storage and return inserted id."""
    text = text.strip()
    if not text:
        return -1
    # avoid saving duplicates (most recent)
    recent = _storage.list(limit=1)
    if recent and recent[0][1] == text:
        return recent[0][0]
    return _storage.add(text)


def list_items(limit: int = 100):
    return _storage.list(limit=limit)


def get_item(clip_id: int):
    return _storage.get(clip_id)


def copy_item(clip_id: int) -> bool:
    row = get_item(clip_id)
    if not row:
        return False
    pyperclip.copy(row[1])
    return True


def clear_history():
    _storage.clear()


def _watcher_loop(poll_interval: float, stop_event: Event):
    last = None
    try:
        last = pyperclip.paste()
    except Exception:
        last = None
    while not stop_event.is_set():
        try:
            current = pyperclip.paste()
        except Exception:
            current = None
        if current and current != last:
            save_text(current)
            last = current
        time.sleep(poll_interval)


def start_watcher(poll_interval: float = 0.5, foreground: bool = False) -> None:
    """Start a background thread that watches the clipboard.

    If foreground==True, this call will block and run in the current thread until KeyboardInterrupt.
    """
    global _watcher_thread, _watcher_stop_event
    if _watcher_thread and _watcher_thread.is_alive():
        return  # already running
    stop_event = Event()
    thread = Thread(
        target=_watcher_loop, args=(poll_interval, stop_event), daemon=not foreground
    )
    _watcher_stop_event = stop_event
    _watcher_thread = thread
    thread.start()
    if foreground:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_event.set()


def stop_watcher():
    global _watcher_stop_event, _watcher_thread
    if _watcher_stop_event:
        _watcher_stop_event.set()
    if _watcher_thread:
        _watcher_thread.join(timeout=1)
