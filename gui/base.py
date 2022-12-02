import threading
import logging
import tkinter as tk


class Base:
    def __init__(self, logger: logging.Logger):
        self._window = tk.Tk()
        self._window_closed = False
        self._logger = logger
        self._toggle_state_cnt = {}

    # noinspection PyUnusedLocal
    def on_close(self, *args):
        """
        Executed when user closes application window; sets window closed flag which should be checked by all
        pending threads for termination and starts polling for safe destroy
        """
        if self._window_closed:
            return
        self._window_closed = True
        if threading.active_count() > 1:
            self._logger.info('Waiting for running threads...')
        self._safe_destroy()

    def _safe_destroy(self):
        """
        Calls itself every 10 seconds until it's safe (no more active threads) to destroy application window
        """
        if threading.active_count() > 1:
            self._window.after(10, self._safe_destroy)
        else:
            self._window.destroy()

    def toggle_state(self, item: tk.Widget, state: bool = False):
        counter = self._get_counter(item)
        if not state:
            if counter.inc() == 1:
                if not isinstance(item, tuple):
                    item.configure(state=tk.DISABLED)
                else:
                    if isinstance(item[0], tk.Menu):
                        item[0].entryconfig(item[1], state=tk.DISABLED)
        else:
            if counter.dec() == 0:
                if not isinstance(item, tuple):
                    item.configure(state=tk.NORMAL)
                else:
                    if isinstance(item[0], tk.Menu):
                        item[0].entryconfig(item[1], state=tk.NORMAL)

    def _get_counter(self, item: tk.Widget):
        item_id = id(item)
        if item_id not in self._toggle_state_cnt:
            self._toggle_state_cnt[item_id] = Counter()
        return self._toggle_state_cnt[item_id]

    def state_disabled(self, item: tk.Widget):
        return self._get_counter(item).get() > 0

    @staticmethod
    def bind_ci(widget: tk.Widget, all_: bool = False, *, modifier: str = '', letter: str, callback,
                add: bool = False):
        if modifier and letter:
            modifier += '-'
        if all_:
            widget.bind_all(f'<{modifier}{letter.lower()}>', callback, add)
            widget.bind_all(f'<{modifier}{letter.upper()}>', callback, add)
        else:
            widget.bind(f'<{modifier}{letter.lower()}>', callback, add)
            widget.bind(f'<{modifier}{letter.upper()}>', callback, add)

    @staticmethod
    def unbind_ci(widget: tk.Widget, all_: bool = False, *, modifier: str = '', letter: str, callback=None):
        if modifier and letter:
            modifier += '-'
        if all_:
            widget.unbind_all(f'<{modifier}{letter.lower()}>')
            widget.unbind_all(f'<{modifier}{letter.upper()}>')
        else:
            widget.unbind(f'<{modifier}{letter.lower()}>', callback)
            widget.unbind(f'<{modifier}{letter.upper()}>', callback)


class Counter:
    def __init__(self):
        self._lock = threading.Lock()
        self._cnt = 0

    def inc(self):
        with self._lock:
            self._cnt += 1
        return self._cnt

    def dec(self):
        with self._lock:
            if self._cnt > 0:
                self._cnt -= 1
        return self._cnt

    def get(self):
        return self._cnt
