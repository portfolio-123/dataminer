import csv
from tkinter import messagebox
import threading
from p123api import Client, ClientException
import tkinter as tk
from tkinter import ttk
from gui.base import Base as GuiBase
import logging
import cons
from gui.misc import custom_paste
import functools
from gui.scrolled_text_line_numbers import ScrolledTextLineNumbers
from tkinter.scrolledtext import ScrolledText
from gui.console_logger_handler import ConsoleLoggerHandler
import yaml
import tkinter.filedialog as filedialog
import os
from utils.config import Config
import p123.operation as operation
import platform
from pathlib import Path
from gui.scrolled_text_horizontal import ScrolledTextHorizontal
import datetime
import re
import traceback


class Gui(GuiBase):
    """Application GUI and operations"""
    def __init__(self):
        super().__init__(logging.getLogger('p123'))

        self._auth = None
        self._main = None

        config_file = 'config.ini'
        if platform.system() == 'Darwin':
            app_user_folder = '{}/Library/Preferences/DataMiner'.format(Path.home())
            Path(app_user_folder).mkdir(parents=True, exist_ok=True)
            config_file = app_user_folder + '/' + config_file
        elif platform.system() == 'Windows' or platform.system() == 'Linux':
            app_user_folder = '{}/DataMiner'.format(Path.home())
            Path(app_user_folder).mkdir(parents=True, exist_ok=True)
            config_file = app_user_folder + '/' + config_file
        self._config = Config(self._logger, config_file)

        self._operation = None

        self._window.title(f'{cons.NAME} - v{cons.VERSION}')
        self._window.rowconfigure(0, weight=1, minsize=500)
        self._window.columnconfigure(0, weight=1, minsize=800)

        threading.Thread(target=self._init_api_client).start()

        self._window.bind_class('Entry', '<<Paste>>', custom_paste)
        self._window.bind_class('Text', '<<Paste>>', custom_paste)
        self._window.bind_class('ScrolledText', '<<Paste>>', custom_paste)
        self._window.protocol('WM_DELETE_WINDOW', self._on_close)
        self._window.mainloop()

    def _init_api_client(self):
        api_id = self._config.get('API', 'id') if self._config.has_option('API', 'id') else None
        api_key = self._config.get('API', 'key') if self._config.has_option('API', 'key') else None
        if api_id and api_key:
            self._api_client = Client(api_id=api_id, api_key=api_key)
            self._api_client.set_timeout(3600)
            if self._config.has_option('API', 'endpoint'):
                endpoint = self._config.get('API', 'endpoint')
                if endpoint:
                    self._api_client.set_endpoint(endpoint)

            frame = ttk.Frame(self._window)
            frame.grid(row=0, column=0, sticky='NSEW')
            ttk.Label(frame, text='Authenticating...').pack(expand=1)
            try:
                self._api_client.auth()
            except ClientException:
                self._api_client = None
                self._config.remove_option('API', 'key')
                self._config.save()
            frame.destroy()
        else:
            self._api_client = None

        if self._api_client:
            self._build_main_frame()
        else:
            self._build_auth_frame()

    # noinspection PyUnusedLocal
    def _on_close(self, *args):
        if self._api_client and self._main and self._main.get('input_changed'):
            if not messagebox.askokcancel(
                    'Quit', 'Unsaved changes will be lost, are you sure you want to continue?'):
                return
        if self._operation:
            self._operation.pause()
        self.on_close()

    # noinspection PyUnusedLocal
    def _auth_submit(self, event=None):
        if self._auth['submit_in_progress']:
            return
        api_id = self._auth['api_id_var'].get()
        api_key = self._auth['api_key_var'].get()
        if not api_id or not api_key:
            messagebox.showwarning(message='API ID and key are required')
            return
        self._auth['submit_in_progress'] = True
        self._auth['submit_btn'].configure(text='Please wait...')
        self._auth['submit_btn'].configure(state=tk.DISABLED)
        threading.Thread(target=self._auth_check_credentials, args=(api_id, api_key)).start()

    def _auth_check_credentials(self, api_id, api_key):
        self._api_client = Client(api_id=api_id, api_key=api_key)
        self._api_client.set_timeout(3600)
        if self._config.has_option('API', 'endpoint'):
            endpoint = self._config.get('API', 'endpoint')
            if endpoint:
                self._api_client.set_endpoint(endpoint)

        error = None
        try:
            self._api_client.auth()
        except ClientException as e:
            error = e
        self._auth['submit_btn'].configure(state=tk.NORMAL)
        self._auth['submit_btn'].configure(text='Confirm')
        if error:
            messagebox.showwarning(message=error)
        else:
            if self._auth['save_credentials_var'].get():
                if not self._config.has_section('API'):
                    self._config.add_section('API')
                self._config.set('API', 'id', api_id)
                self._config.set('API', 'key', api_key)
                self._config.save()
            self._build_main_frame()
            self._auth['save_credentials_var'].set(0)
            self._auth['api_id_var'].set('')
            self._auth['api_key_var'].set('')
        self._auth['submit_in_progress'] = False

    def _build_auth_frame(self):
        if self._auth is None:
            self._auth = {
                'save_credentials_var': tk.IntVar(),
                'api_id_var': tk.StringVar(),
                'api_key_var': tk.StringVar(),
                'frame': ttk.Frame(self._window),
                'submit_in_progress': False
            }
            self._auth['frame'].grid(row=0, column=0, sticky='NSEW')
            self._auth['frame'].rowconfigure(0, weight=1)
            self._auth['frame'].rowconfigure(1, weight=0)
            self._auth['frame'].rowconfigure(2, weight=0)
            self._auth['frame'].rowconfigure(3, weight=1)
            self._auth['frame'].columnconfigure(0, weight=1)
            self._auth['frame'].columnconfigure(1, weight=1)
            ttk.Label(self._auth['frame'], text='Api ID').grid(row=0, column=0, sticky='SE')
            self._auth['api_id_entry'] = ttk.Entry(self._auth['frame'], width=40,
                                                   textvariable=self._auth['api_id_var'])
            self._auth['api_id_entry'].grid(row=0, column=1, sticky='SW', padx=5)
            ttk.Label(self._auth['frame'], text='Api Key').grid(row=1, column=0, sticky='E', pady=5)
            api_key_entry = ttk.Entry(self._auth['frame'], width=40, textvariable=self._auth['api_key_var'])
            api_key_entry.grid(row=1, column=1, sticky='W', padx=5, pady=5)
            checkbox = ttk.Checkbutton(
                self._auth['frame'], text='remember credentials', var=self._auth['save_credentials_var'])
            checkbox.grid(row=2, column=1, sticky='W', padx=5)
            self._auth['submit_btn'] = ttk.Button(self._auth['frame'], text='Confirm', command=self._auth_submit)
            self._auth['submit_btn'].grid(row=3, column=1, sticky='NW', padx=5, pady=5)

            self._auth['api_id_entry'].bind('<Return>', self._auth_submit)
            api_key_entry.bind('<Return>', self._auth_submit)
            checkbox.bind('<Return>', self._auth_submit)
            self._auth['submit_btn'].bind('<Return>', self._auth_submit)

        self._auth['frame'].tkraise()
        self._auth['api_id_entry'].focus()

    def _build_main_frame(self):
        if self._main is None:
            self._main = {
                'frame': ttk.Frame(self._window, padding=(5, 10, 5, 5))
            }

            self._main['frame'].grid(row=0, column=0, sticky='NSEW')

            self._main['paned_window'] = ttk.PanedWindow(self._main['frame'], orient=tk.VERTICAL)
            self._main['paned_window'].place(relwidth=1, relheight=1)

            main_frame = ttk.Frame(self._main['paned_window'])
            self._main['paned_window'].add(main_frame, weight=2)

            inner_frame = ttk.Frame(main_frame)
            inner_frame.place(relwidth=1, relheight=1)
            inner_frame.rowconfigure(0, weight=0)
            inner_frame.rowconfigure(1, weight=1)
            inner_frame.columnconfigure(0, weight=1)

            frame = ttk.Frame(inner_frame, padding=(0, 0, 0, 10))
            frame.grid(row=0, column=0, sticky='W')
            self._main['btn_validate'] = ttk.Button(frame, text='Validate', command=self._validate_input)
            self._main['btn_validate'].pack(side=tk.LEFT)
            ttk.Separator(frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5, pady=3)
            self._main['btn_execute'] = ttk.Button(frame, text='Execute', command=self._execute)
            self._main['btn_execute'].pack(side=tk.LEFT)
            self._main['btn_execute_stop'] = ttk.Button(frame, text='Stop', command=self._execute_stop)
            self._main['btn_execute_stop'].pack_forget()
            ttk.Separator(frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5, pady=3)
            self._main['btn_copy_output'] = ttk.Button(frame, text='Copy output', command=self._copy_output)
            self._main['btn_copy_output'].pack(side=tk.LEFT)
            self._main['btn_save_output'] = ttk.Button(frame, text='Save output', command=self._save_output)
            self._main['btn_save_output'].pack(side=tk.LEFT, padx=(5, 0))

            self._auto_save_output_init()
            ttk.Checkbutton(
                frame,
                text='Auto save output',
                variable=self._auto_save,
                command=self._auto_save_output_toggle
            ).pack(side=tk.LEFT, padx=(5, 0))

            self._main['btn_auto_save_output_folder'] = ttk.Label(
                frame,
                text='(' + self._auto_save_folder + ')' if self._auto_save.get() else ''
            )
            self._main['btn_auto_save_output_folder'].pack(side=tk.LEFT)

            self._main['notebook'] = ttk.Notebook(inner_frame)
            self._main['notebook'].grid(row=1, column=0, sticky='NSEW')

            self._build_input_frame()
            self._build_output_frame()
            self._build_console_frame()

        self._main['frame'].tkraise()
        self._build_menu()

    def _auto_save_output_init(self):
        self._auto_save = tk.IntVar()
        if not self._config.has_section('OUTPUT'):
            self._config.add_section('OUTPUT')
        if self._config.has_option('OUTPUT', 'auto_save'):
            self._auto_save.set(1)
        self._auto_save_folder = self._config.get('OUTPUT', 'auto_save_folder') if self._auto_save.get() else None

    def _auto_save_output_toggle(self, init: bool = True):
        if init:
            threading.Thread(target=self._auto_save_output_toggle, args=[False]).start()
            return

        if not self._auto_save.get():
            self._config.remove_option('OUTPUT', 'auto_save')
        else:
            self._auto_save_folder = filedialog.askdirectory()
            if not self._auto_save_folder:
                self._auto_save.set(0)
                return
            self._config.set('OUTPUT', 'auto_save', 'yes')
            self._config.set('OUTPUT', 'auto_save_folder', self._auto_save_folder)
        self._main['btn_auto_save_output_folder'].configure(
            text='(' + self._auto_save_folder + ')' if self._auto_save.get() else ''
        )
        self._config.save()

    def _build_menu(self):
        save_callback = functools.partial(self._save_input, False, True)
        save_as_callback = functools.partial(self._save_input, True, True)

        if not self._main.get('menu_bar'):
            self._main['menu_bar'] = tk.Menu(self._window)

            input_menu = tk.Menu(self._main['menu_bar'], tearoff=0)
            input_menu.add_command(label='Open', underline=0, accelerator="Ctrl+O", command=self._open_input_file)
            input_menu.add_command(
                label='Close', underline=0, accelerator="Ctrl+Shift+C", command=self._close_input_file)
            input_menu.add_command(label='Save', underline=0, accelerator="Ctrl+S", command=save_callback)
            input_menu.add_command(label='Save As', underline=5, accelerator="Ctrl+Shift+S",
                                   command=save_as_callback)
            self._main['menu_bar'].add_cascade(label='Input', underline=0, menu=input_menu)

            try:
                samples_menu = tk.Menu(self._main['menu_bar'], tearoff=0)
                path = 'samples'
                for level1 in os.listdir(path):
                    entry = os.path.join(path, level1)
                    if os.path.isfile(entry):
                        samples_menu.add_command(label=level1)
                    else:
                        regex = re.compile(rf'^{level1}(\s*-\s*)?|\.yaml$', re.IGNORECASE)
                        entries = os.listdir(entry)
                        submenu = tk.Menu(tearoff=0)
                        for level2 in entries:
                            name = regex.sub('', level2)
                            submenu.add_command(
                                label=name,
                                command=functools.partial(
                                    self._open_input_file, True, os.path.join(entry, level2), True)
                            )
                        samples_menu.add_cascade(label=level1, menu=submenu)
                self._main['menu_bar'].add_cascade(label='Samples', underline=1, menu=samples_menu)
            except Exception:
                pass

            session_menu = tk.Menu(self._main['menu_bar'], tearoff=0)
            session_menu.add_command(label=f'API ID: {self._api_client.get_api_id()}')
            session_menu.add_command(label='Logout', underline=0, accelerator="Ctrl+L", command=self._logout)
            session_menu.add_command(label='Quit', underline=0, accelerator="Ctrl+Q", command=self._on_close)
            self._main['menu_bar'].add_cascade(label='Session', underline=0, menu=session_menu)

            self._main['menu_input_open_cmd'] = (input_menu, 0)
            self._main['menu_input_close_cmd'] = (input_menu, 1)
            self._main['menu_input_save_cmd'] = (input_menu, 2)
            self._main['menu_input_save_as_cmd'] = (input_menu, 3)
            self._main['menu_session_api_id'] = (session_menu, 0)
            self._main['menu_session_logout'] = (session_menu, 1)
            self.toggle_state(self._main['menu_input_close_cmd'])
            self.toggle_state(self._main['menu_input_save_cmd'])
        else:
            self._main['menu_session_api_id'][0].entryconfig(
                self._main['menu_session_api_id'][1], label=f'API ID: {self._api_client.get_api_id()}')

        self._window.config(menu=self._main['menu_bar'])

        GuiBase.bind_ci(self._window, True, modifier='Control', letter='o', callback=self._open_input_file)
        GuiBase.bind_ci(self._window, True, modifier='Control-Shift', letter='c', callback=self._close_input_file)
        GuiBase.bind_ci(self._window, True, modifier='Control', letter='s', callback=save_callback)
        GuiBase.bind_ci(self._window, True, modifier='Control-Shift', letter='s', callback=save_as_callback)
        GuiBase.bind_ci(self._window, True, modifier='Control', letter='l', callback=self._logout)
        GuiBase.bind_ci(self._window, True, modifier='Control', letter='q', callback=self._on_close)

        GuiBase.bind_ci(self._window, True, modifier='Control-Shift', letter='v', callback=self._validate_input)
        GuiBase.bind_ci(self._window, True, modifier='Control', letter='e', callback=self._execute)

    # noinspection PyUnusedLocal
    def _close_input_file(self, init: bool = True):
        if self.state_disabled(self._main['menu_input_close_cmd']):
            return

        if init:
            if self._main.get('input_changed'):
                if not messagebox.askokcancel(
                        'Close file', 'Unsaved changes will be lost, are you sure you want to continue?'):
                    return
            return threading.Thread(target=self._close_input_file, args=[False]).start()

        self._input_text_modified_event_toggle(False)
        self._main['input'].delete('1.0', tk.END)
        self._input_text_modified_event_toggle()

        self.toggle_state(self._main['menu_input_close_cmd'])
        self.toggle_state(self._main['menu_input_save_cmd'])
        del self._main['opened_file']
        self._update_displayed_file_name()

    def _destroy_menu(self):
        self._window.config(menu=tk.Menu(self._window))

        GuiBase.unbind_ci(self._window, True, modifier='Control', letter='o')
        GuiBase.unbind_ci(self._window, True, modifier='Control-Shift', letter='c')
        GuiBase.unbind_ci(self._window, True, modifier='Control', letter='s')
        GuiBase.unbind_ci(self._window, True, modifier='Control-Shift', letter='s')
        GuiBase.unbind_ci(self._window, True, modifier='Control', letter='l')
        GuiBase.unbind_ci(self._window, True, modifier='Control', letter='q')

        GuiBase.unbind_ci(self._window, True, modifier='Control-Shift', letter='v')
        GuiBase.unbind_ci(self._window, True, modifier='Control', letter='e')

    # noinspection PyUnusedLocal
    def _logout(self, *args):
        if self.state_disabled(self._main['menu_session_logout']):
            return

        if self._config.has_section('API'):
            self._config.remove_option('API', 'id')
            self._config.remove_option('API', 'key')
            self._config.save()

        self._api_client = None
        self._destroy_menu()
        self._build_auth_frame()

    # noinspection PyUnusedLocal
    def _input_tab_to_spaces(self, arg):
        self._main['input'].insert(tk.INSERT, ' ' * 4)
        return 'break'

    def _build_input_frame(self):
        main_frame = ttk.Frame(self._main['notebook'], padding=5)
        self._main['notebook'].add(main_frame, text='Input')

        self._main['input'] = ScrolledTextLineNumbers(main_frame, undo=True)
        self._main['input'].pack(side='right', fill='both', expand=True)
        self._main['input'].bind('<Tab>', self._input_tab_to_spaces)
        self._main['input'].bind('<<Paste>>', self._handle_input_paste)
        self._input_text_modified_event_toggle()
        GuiBase.bind_ci(
            self._main['input'], modifier='Control', letter='o',
            callback=lambda x: self._open_input_file(True) or 'break')

    def _input_text_modified_event_toggle(self, state: bool = True):
        if self._main.get('input_text_modified_callback') is None:
            self._main['input_text_modified_callback'] = functools.partial(self._update_displayed_file_name, True)
        if state:
            if self._main.get('input_text_modified_unbind') is None:
                self._main['input_text_modified_unbind'] =\
                    self._main['input'].bind('<<TextModified>>', self._main['input_text_modified_callback'])
        elif self._main.get('input_text_modified_unbind'):
            self._main['input'].unbind('<<TextModified>>', self._main['input_text_modified_unbind'])
            del self._main['input_text_modified_unbind']

    # noinspection PyUnusedLocal
    @staticmethod
    def _handle_input_paste(event):
        custom_paste(event, str(event.widget.clipboard_get()).replace('\t', ' ' * 4))
        return 'break'

    # noinspection PyUnusedLocal
    def _input_undo(self, *args):
        try:
            self._main['input'].edit_undo()
        except tk.TclError:
            pass

    # noinspection PyUnusedLocal
    def _input_redo(self, *args):
        try:
            self._main['input'].edit_redo()
        except tk.TclError:
            pass

    def _build_output_frame(self):
        main_frame = ttk.Frame(self._main['notebook'], padding=5)
        self._main['notebook'].add(main_frame, text='Output')

        self._main['output'] = ScrolledTextHorizontal(main_frame, state='disabled')
        self._main['output'].place(relwidth=1, relheight=1)

    def _build_console_frame(self):
        main_frame = ttk.LabelFrame(self._main['paned_window'], text='Console', padding=5)
        self._main['paned_window'].add(main_frame, weight=1)

        inner_frame = tk.Frame(main_frame)
        inner_frame.place(relwidth=1, relheight=1)
        inner_frame.rowconfigure(0, weight=0)
        inner_frame.rowconfigure(1, weight=1)
        inner_frame.columnconfigure(0, weight=1)

        frame = ttk.Frame(inner_frame, padding=(0, 0, 0, 5))
        frame.grid(row=0, column=0, sticky='W')
        ttk.Button(frame, text='Clear', command=self._clear_console).pack(side=tk.LEFT)

        frame = ttk.Frame(inner_frame)
        frame.grid(row=1, column=0, sticky='NSEW')
        console = ScrolledText(frame, state='disabled')
        console.place(relwidth=1, relheight=1)
        self._logger.setLevel(logging.INFO)
        self._logger_handler = ConsoleLoggerHandler(console)
        self._logger.addHandler(self._logger_handler)

    def _save_output(self, init: bool = True, from_btn: bool = True):
        """
        Dumps content of the output (as csv) into user selected file.
        Calls itself in a separate thread to avoid blocking and blocks operations that might
        cause a lock.
        """
        if init:
            self.toggle_state(self._main['btn_execute'])
            self.toggle_state(self._main['btn_save_output'])
            threading.Thread(target=self._save_output, args=[False, from_btn]).start()
            return

        try:
            rows = self._operation.get_result() if self._operation is not None else None
            if rows:
                if from_btn:
                    file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('csv', '*.csv')])
                else:
                    file = self._auto_save_folder + '/' + str(self._operation.get_name()).lower() + '_' +\
                           datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
                if file:
                    with open(file, 'w', newline='') as stream:
                        csv_writer = csv.writer(stream)
                        csv_writer.writerows(rows)
                        self._logger.info('Output saved to ' + file)
            else:
                self._logger.error('Output is empty')
        except OSError as e:
            self._logger.error(e)
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        self.toggle_state(self._main['btn_execute'], True)
        self.toggle_state(self._main['btn_save_output'], True)

    def _copy_output(self, init: bool = True):
        """
        Dumps content of the output (tab separated) into the clipboard.
        Calls itself in a separate thread to avoid blocking and blocks operations that might
        cause a lock.
        """
        if init:
            self.toggle_state(self._main['btn_execute'])
            self.toggle_state(self._main['btn_copy_output'])
            threading.Thread(target=self._copy_output, args=[False]).start()
            return

        try:
            rows = self._operation.get_result() if self._operation is not None else None
            if rows:
                if len(rows) <= 1000:
                    data = ''
                    for row in rows:
                        data += '\t'.join(str(val if val is not None else '') for val in row) + '\n'
                    self._window.clipboard_clear()
                    self._window.clipboard_append(data.strip())
                    self._logger.info('Output copied to clipboard')
                else:
                    self._logger.warning('Output is too big, please use "Save output"')
            else:
                self._logger.error('Output is empty')
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        self.toggle_state(self._main['btn_execute'], True)
        self.toggle_state(self._main['btn_copy_output'], True)

    # noinspection PyUnusedLocal
    def _save_input(self, save_as: bool = False, init: bool = True, *args):
        """
        Dumps content of the input scrolledtext element into user selected file.
        Calls itself in a separate thread to avoid blocking and blocks operations that might
        cause a lock.
        """
        if init:
            if not save_as and self.state_disabled(self._main['menu_input_save_cmd']):
                save_as = True

            if save_as and self.state_disabled(self._main['menu_input_save_as_cmd']):
                return

            self.toggle_state(self._main['menu_input_open_cmd'])
            self.toggle_state(self._main['menu_input_close_cmd'])
            self.toggle_state(self._main['menu_input_save_as_cmd' if save_as else 'menu_input_save_cmd'])
            self.toggle_state(self._main['input'])
            threading.Thread(target=self._save_input, args=[save_as, False]).start()
            return

        try:
            content = self._main['input'].get('1.0', tk.END).strip()
            if content:
                if save_as:
                    file_path = filedialog.asksaveasfilename(defaultextension='.yaml',
                                                             filetypes=[('yaml', '*.yaml')])
                else:
                    file_path = self._main['opened_file']['path']
                if file_path:
                    with open(file_path, 'w') as stream:
                        stream.write(content)
                    if save_as:
                        self.toggle_state(self._main['menu_input_save_cmd'], True)
                        self.toggle_state(self._main['menu_input_close_cmd'], True)
                        self._main['opened_file'] = {
                            'path': file_path,
                            'name': file_path.split('/')[-1]
                        }
                    self._update_displayed_file_name()
                    self._logger.info('Input saved to ' + file_path)
            else:
                self._logger.error('Input is empty')
        except OSError as e:
            self._logger.error(e)
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        self.toggle_state(self._main['menu_input_open_cmd'], True)
        self.toggle_state(self._main['menu_input_close_cmd'], True)
        self.toggle_state(self._main['menu_input_save_as_cmd' if save_as else 'menu_input_save_cmd'], True)
        self.toggle_state(self._main['input'], True)

    def _open_input_file(self, init: bool = True, file_path: str = None, anonymous_mode: bool = False):
        """
        Opens user selected file and dumps its content into the input scrolledtext element.
        Calls itself in a separate thread to avoid blocking and blocks operations that might cause a lock.
        """
        if init:
            if self.state_disabled(self._main['menu_input_open_cmd']):
                return

            if self._main.get('input_changed'):
                if not messagebox.askokcancel(
                        'Open File', 'Unsaved changes will be lost, are you sure you want to continue?'):
                    return

            self.toggle_state(self._main['menu_input_open_cmd'])
            self.toggle_state(self._main['menu_input_close_cmd'])
            self.toggle_state(self._main['menu_input_save_cmd'])
            self.toggle_state(self._main['menu_input_save_as_cmd'])
            self.toggle_state(self._main['btn_validate'])
            self.toggle_state(self._main['btn_execute'])
            self.toggle_state(self._main['input'])
            threading.Thread(target=self._open_input_file, args=[False, file_path, anonymous_mode]).start()
            return

        try:
            if file_path is None:
                file_path = filedialog.askopenfilename(filetypes=[('yaml', '*.yaml'), ('All Files', '*.*')])
            if file_path:
                with open(file_path) as stream:
                    if os.fstat(stream.fileno()).st_size <= 10000000:
                        content = stream.read().replace('\t', ' ' * 4)
                        self.toggle_state(self._main['input'], True)

                        self._input_text_modified_event_toggle(False)
                        self._main['input'].delete('1.0', tk.END)
                        self._main['input'].insert(tk.END, content)
                        self._input_text_modified_event_toggle()

                        self._logger.info(f'File "{file_path}" loaded')

                        if anonymous_mode:
                            if self._main.get('opened_file') is not None:
                                del self._main['opened_file']
                                self.toggle_state(self._main['menu_input_close_cmd'])
                                self.toggle_state(self._main['menu_input_save_cmd'])
                        else:
                            self._main['opened_file'] = {
                                'path': file_path,
                                'name': re.split(r'[\\/]', file_path)[-1]
                            }
                            self.toggle_state(self._main['menu_input_close_cmd'], True)
                            self.toggle_state(self._main['menu_input_save_cmd'], True)
                        self._update_displayed_file_name()
                        self._main['notebook'].select(0)
                    else:
                        self._logger.error('File is too big (max 10Mb)')
        except OSError as e:
            self._logger.error(e)
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        self.toggle_state(self._main['menu_input_open_cmd'], True)
        self.toggle_state(self._main['menu_input_close_cmd'], True)
        self.toggle_state(self._main['menu_input_save_cmd'], True)
        self.toggle_state(self._main['menu_input_save_as_cmd'], True)
        self.toggle_state(self._main['btn_validate'], True)
        self.toggle_state(self._main['btn_execute'], True)
        self.toggle_state(self._main['input'], True)

    # noinspection PyUnusedLocal
    def _update_displayed_file_name(self, changed: bool = False, *args):
        if changed and self._main.get('input_changed'):
            return
        opened_file = self._main.get('opened_file')
        if opened_file:
            self._window.title('{} - v{} - {}{}'.format(
                cons.NAME, cons.VERSION, opened_file['name'], '*' if changed else ''))
        else:
            self._window.title('{} - v{}{}'.format(cons.NAME, cons.VERSION, ' - *' if changed else ''))
        self._main['input_changed'] = changed

    def _validate_yaml_input(self) -> dict:
        try:
            data = self._main['input'].get('1.0', tk.END)
            data = yaml.safe_load(data)
            if operation.process_input(data=data, logger=self._logger):
                self._logger.info('Input validated')
                return data
        except yaml.YAMLError as e:
            self._logger.error(e)

    def _validate_input(self, init: bool = True):
        """
        Validates input. Calls itself in a separate thread to avoid blocking and blocks operations that might
        cause a lock.
        """
        if init:
            if self.state_disabled(self._main['btn_validate']):
                return

            self.toggle_state(self._main['menu_input_open_cmd'])
            self.toggle_state(self._main['menu_input_close_cmd'])
            self.toggle_state(self._main['btn_validate'])
            self.toggle_state(self._main['btn_execute'])
            self.toggle_state(self._main['input'])
            threading.Thread(target=self._validate_input, args=[False]).start()
            return

        try:
            self._validate_yaml_input()
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        self.toggle_state(self._main['menu_input_open_cmd'], True)
        self.toggle_state(self._main['menu_input_close_cmd'], True)
        self.toggle_state(self._main['btn_validate'], True)
        self.toggle_state(self._main['btn_execute'], True)
        self.toggle_state(self._main['input'], True)

    def _execute(self, init: bool = True):
        """
        Validates input and runs backtests defined in it; supports pausing/resuming.
        Calls itself in a separate thread to avoid blocking and blocks operations that might cause a lock.
        """
        if init:
            if self.state_disabled(self._main['btn_execute']):
                return

            if self._operation is None or self._operation.is_finished():
                # start
                self.toggle_state(self._main['menu_input_open_cmd'])
                self.toggle_state(self._main['menu_input_close_cmd'])
                self.toggle_state(self._main['menu_session_logout'])
                self.toggle_state(self._main['btn_validate'])
                self._main['btn_execute'].configure(text='Pause')
                self.toggle_state(self._main['btn_copy_output'])
                self.toggle_state(self._main['btn_save_output'])
                self.toggle_state(self._main['input'])
            else:
                if not self._operation.is_paused():
                    # pause
                    self._operation.pause()
                    self.toggle_state(self._main['btn_execute'])
                    self._main['btn_execute'].configure(text='Pausing...')
                    return
                else:
                    # resume
                    self._operation.resume()
                    self._main['btn_execute'].configure(text='Pause')
                    self._main['btn_execute_stop'].pack_forget()
                    self._logger.info('Resumed')
            threading.Thread(target=self._execute, args=[False]).start()
            return

        try:
            if self._operation is None or self._operation.is_finished():
                data = self._validate_yaml_input()
                if data is not None:
                    self._main['output'].configure(state='normal')
                    self._main['output'].delete('1.0', tk.END)
                    self._main['output'].configure(state='disabled')
                    self._main['notebook'].select(1)
                    self._operation = operation.Operation.init(
                        api_client=self._api_client,
                        data=data,
                        output=self._main['output'],
                        logger=self._logger
                    )
            if self._operation is not None and not self._operation.is_finished():
                self._operation.run()
        except Exception:
            print_to_log(traceback.format_exc())
            self._logger.error('Internal error')

        if self._operation is None or not self._operation.is_paused() or self._operation.is_finished():
            self._execute_stop(False)
        else:
            self.toggle_state(self._main['btn_execute'], True)
            self._main['btn_execute'].configure(text='Resume')
            self._main['btn_execute_stop'].pack(side=tk.LEFT, padx=(5, 0), after=self._main['btn_execute'])
            self._logger.info('Paused')

    def _execute_stop(self, from_btn: bool = True):
        self.toggle_state(self._main['menu_input_open_cmd'], True)
        self.toggle_state(self._main['menu_input_close_cmd'], True)
        self.toggle_state(self._main['menu_session_logout'], True)
        self.toggle_state(self._main['btn_validate'], True)
        self.toggle_state(self._main['btn_execute'], True)
        self._main['btn_execute'].configure(text='Execute')
        self._main['btn_execute_stop'].pack_forget()
        self.toggle_state(self._main['btn_copy_output'], True)
        self.toggle_state(self._main['btn_save_output'], True)
        self.toggle_state(self._main['input'], True)
        if from_btn:
            if self._operation is not None:
                self._operation.stop()
            self._logger.info('Stopped')
        elif self._auto_save.get():
            self._save_output(True, False)

    def _clear_console(self):
        self._logger_handler.clear()


def print_to_log(msg):
    try:
        with open('app.log', 'a') as stream:
            stream.write(str(datetime.datetime.now()) + '\n')
            stream.write(msg)
            stream.write('\n')
            print(msg)
    except Exception:
        pass


if __name__ == '__main__':
    gui = Gui()
