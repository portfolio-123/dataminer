from tkinter.scrolledtext import ScrolledText
import logging
import tkinter as tk


class ConsoleLoggerHandler(logging.Handler):
    def __init__(self, scrolled_text: ScrolledText):
        super().__init__()
        self._scrolled_text = scrolled_text
        self._scrolled_text.configure(font='TkFixedFont')
        self._scrolled_text.tag_config('INFO', foreground='black')
        self._scrolled_text.tag_config('DEBUG', foreground='gray')
        self._scrolled_text.tag_config('WARNING', foreground='orange')
        self._scrolled_text.tag_config('ERROR', foreground='red')
        self._scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        self._formatter = logging.Formatter('%(asctime)s: %(message)s')

    def handle(self, record):
        self.acquire()
        try:
            msg = self._formatter.format(record) if record.msg else ''
            self._scrolled_text.configure(state='normal')
            self._scrolled_text.insert('1.0', msg + '\n', record.levelname)
            self._scrolled_text.configure(state='disabled')
        finally:
            self.release()

    def clear(self):
        self.acquire()
        try:
            self._scrolled_text.configure(state='normal')
            self._scrolled_text.delete('1.0', tk.END)
            self._scrolled_text.configure(state='disabled')
        finally:
            self.release()
