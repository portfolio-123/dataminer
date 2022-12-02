from tkinter.scrolledtext import ScrolledText
from tkinter import TclError
from tkinter import Canvas


class ScrolledTextLineNumbers(ScrolledText):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        # create the canvas for line number
        self._canvas = Canvas(master, width=1)
        self._canvas.pack(side='left', fill='y')
        self.bind('<Configure>', self._redraw)
        self.bind('<<Redraw>>', self._redraw)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        try:
            result = self.tk.call(cmd)
        except TclError:
            return

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if args[0] in ('insert', 'replace', 'delete'):
            self.event_generate('<<TextModified>>', when='tail')
            self.event_generate('<<Redraw>>', when='tail')
        elif (args[0] in ('insert', 'replace', 'delete') or args[0:3] == ('mark', 'set', 'insert') or
                args[0:2] == ('xview', 'moveto') or args[0:2] == ('xview', 'scroll') or
                args[0:2] == ('yview', 'moveto') or args[0:2] == ('yview', 'scroll')):
            self.event_generate('<<Redraw>>', when='tail')

        # return what the actual widget returned
        return result

    # noinspection PyUnusedLocal
    def _redraw(self, *args):
        """redraw line numbers implementation"""
        self._canvas.delete('all')
        i = self.index('@1,0')
        digits = 1
        while True:
            d_line = self.dlineinfo(i)
            if d_line is None:
                break
            y = d_line[1]
            line_num = str(i).split('.')[0]
            if len(line_num) > digits:
                digits = len(line_num)
            self._canvas.create_text(2, y, anchor='nw', text=line_num, font='TkFixedFont')
            i = self.index('%s+1line' % i)
        self._canvas.configure(width=digits * 8 + 4)
