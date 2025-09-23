"""Button class for Tkinter applications."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

import psiutils.text as txt

from .constants import PAD, Pad
from .widgets import enter_widget, clickable_widget, HAND


class IconButton(ttk.Frame):
    def __init__(
            self,
            master,
            button_text,
            icon,
            command=None,
            dimmable: bool = False,
            sticky: str = '',
            icon_path: str = '',
            **kwargs):
        super().__init__(master, borderwidth=1, relief='raised', **kwargs)
        self.command = command
        self._state = tk.NORMAL
        self.text = button_text
        self.icon = icon

        # Icon and text
        if not icon_path:
            icon_path = f'{Path(__file__).parent}/icons/'
        image = Image.open(f'{icon_path}{icon}.png').resize((16, 16))
        photo_image = ImageTk.PhotoImage(image)

        self.button_label = ttk.Label(
            self, text=button_text, image=photo_image, compound=tk.LEFT)
        self.button_label.image = photo_image  # Prevent garbage collection
        self.button_label.pack(padx=(3, 5), pady=5)
        self.widget = self.button_label

        # Make the whole frame clickable
        self.bind_widgets()

        self.sticky = sticky
        self.dimmable = dimmable

    def __repr__(self) -> str:
        return f'IconButton: {self.text} {self.icon}'

    def state(self, *args, **kwargs) -> dict:
        return self._state

    def enable(self, enable: bool = True) -> None:
        state = tk.NORMAL if enable else tk.DISABLED
        self.button_label.configure(state=state)
        self._state = state

    def disable(self, disable: bool = True) -> None:
        state = tk.DISABLED if disable else tk.NORMAL
        self.button_label.configure(state=state)
        self._state = state

    def bind_widgets(self):
        for widget in (self, self.button_label):
            widget.bind('<Button-1>', self._on_click)
            widget.bind('<Enter>', self._enter_button)
            widget.bind('<Leave>', lambda e: self.config(relief='raised'))

    def _enter_button(self, event) -> None:
        if self._state == tk.DISABLED:
            return
        self.config(relief='sunken')
        event.widget.winfo_toplevel().config(cursor=HAND)

    def _on_click(self, *args):
        if self._state == tk.DISABLED:
            return
        if self.command:
            self.command()


class Button(ttk.Button):
    def __init__(
            self,
            *args,
            sticky: str = '',
            dimmable: bool = False,
            **kwargs: dict,
            ) -> None:
        super().__init__(*args, **kwargs)

        self.sticky = sticky
        self.dimmable = dimmable

    def enable(self, enable: bool = True) -> None:
        state = tk.NORMAL if enable else tk.DISABLED
        self['state'] = state

    def disable(self, disable: bool = True) -> None:
        state = tk.DISABLED if disable else tk.NORMAL
        self['state'] = state


class ButtonFrame(ttk.Frame):
    def __init__(
            self,
            master: tk.Frame,
            orientation: str = tk.HORIZONTAL,
            **kwargs: dict) -> None:
        super().__init__(master, **kwargs)
        self._buttons = []
        self._enabled = False
        self.orientation = orientation

        if 'enabled' in kwargs:
            self._enabled = kwargs['enabled']

        self.icon_buttons = {
            name: IconButton(self, button[0], button[1])
            for name, button in icon_buttons.items()
        }

    def icon_button(
            self,
            id_: str,
            command: object = None,
            dimmable: bool = False,) -> IconButton:
        button = self.icon_buttons[id_]
        button.dimmable = dimmable
        button.command = command
        return button

    @property
    def buttons(self) -> list[Button]:
        return self._buttons

    @buttons.setter
    def buttons(self, value: list[Button]) -> None:
        self._buttons = value

        if self.orientation == tk.VERTICAL:
            self._vertical_buttons()
        elif self.orientation == tk.HORIZONTAL:
            self._horizontal_buttons()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        state = tk.NORMAL if value else tk.DISABLED
        for button in self. buttons:
            button.widget['state'] = state

    def enable(self, enable: bool = True) -> None:
        self._enabled = enable
        self._enable_buttons(self.buttons, enable)

    def disable(self) -> None:
        self._enabled = False
        self._enable_buttons(self.buttons, False)

    def _vertical_buttons(self) -> None:
        self.rowconfigure(len(self.buttons)-1, weight=1)
        for row, button in enumerate(self.buttons):
            pady = PAD
            if row == 0:
                pady = Pad.S
            if row == len(self.buttons) - 1:
                self.rowconfigure(row, weight=1)
                row += 1
                pady = Pad.N

            button.grid(row=row, column=0, sticky=tk.EW, pady=pady)
            clickable_widget(button)

    def _horizontal_buttons(self) -> None:
        self.columnconfigure(len(self.buttons)-1, weight=1)
        for col, button in enumerate(self.buttons):
            padx = PAD
            if col == 0:
                padx = Pad.W
            if col == len(self.buttons) - 1:
                self.columnconfigure(col, weight=1)
                col += 1
            # if not button.sticky:
            #     button.sticky = tk.W
            button.grid(row=0, column=col, sticky=button.sticky, padx=padx)
            clickable_widget(button)

    @staticmethod
    def _enable_buttons(buttons: list[Button], enable: bool = True):
        state = tk.NORMAL if enable else tk.DISABLED
        for button in buttons:
            if button.dimmable:
                if isinstance(button, Button):
                    button['state'] = state
                    button.bind('<Enter>', enter_widget)
                elif isinstance(button, IconButton):
                    if enable:
                        button.enable()
                    else:
                        button.disable()


def enable_buttons(buttons: list[Button], enable: bool = True):
    state = tk.NORMAL if enable else tk.DISABLED
    for button in buttons:
        if button.dimmable:
            button['state'] = state
            button.bind('<Enter>', enter_widget)


icon_buttons = {
    'build': (txt.BUILD, 'build'),
    'check': (txt.CHECK, 'check'),
    'clear': (txt.CLEAR, 'clear'),
    'close': (txt.CLOSE, 'cancel'),
    'code': (txt.CODE, 'code'),
    'compare': (txt.COMPARE, 'compare'),
    'config': (txt.CONFIG, 'gear'),
    'copy_docs': (txt.COPY, 'copy_docs'),
    'copy_clipboard': (txt.COPY, 'copy_clipboard'),
    'delete': (txt.DELETE, 'delete'),
    'diff': (txt.DIFF, 'diff'),
    'done': (txt.DONE, 'done'),
    'edit': (txt.EDIT, 'edit'),
    'exit': (txt.EXIT, 'cancel'),
    'new': (txt.NEW, 'new'),
    'next': (txt.NEXT, 'next'),
    'open': (txt.OPEN, 'open'),
    'pause': (txt.PAUSE, 'pause'),
    'preferences': (txt.PREFERENCES, 'preferences'),
    'previous': (txt.PREVIOUS, 'previous'),
    'process': (txt.PROCESS, 'process'),
    'redo': (txt.REDO, 'redo'),
    'refresh': (txt.REFRESH, 'refresh'),
    'rename': (txt.RENAME, 'rename'),
    'report': (txt.REPORT, 'report'),
    'reset': (txt.RESET, 'reset'),
    'revert': (txt.REVERT, 'revert'),
    'run': (txt.RUN, 'start'),
    'save': (txt.SAVE, 'save'),
    'script': (txt.SCRIPT, 'script'),
    'search': (txt.SEARCH, 'search'),
    'send': (txt.SEND, 'send'),
    'start': (txt.START, 'start'),
    'update': (txt.UPDATE, 'update'),
    'upgrade': (txt.UPGRADE, 'upgrade'),
    'use': (txt.USE, 'done'),
    'windows': (txt.WINDOWS, 'windows'),
}


def list_icon_buttons() -> None:
    """List of icon_button."""
    name_length, text_length, icon_length = 15, 10, 15

    print(
        (f'{"name":<{name_length}} '
         f'{"text":<{text_length}} '
         f'{"icon":<{icon_length}}'))

    print(f'{"-"*name_length:<{name_length}} '
          f'{"-"*text_length:<{text_length}} '
          f'{"-"*icon_length:<{icon_length}}')

    for name, button in icon_buttons.items():
        print(f'{name:<{name_length}} '
              f'{button[0]:<{text_length}} '
              f'{button[1]:<{icon_length}}')
