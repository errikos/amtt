from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

import version

WINDOW_TEXT = 'Welcome to the Availability Model Translation Toolkit!\n\n' + \
              'First, select the input type and fill the input path ' + \
              'or click "Browse" to select a file or folder.\n' + \
              'Afterwards, select the target software and fill the output ' + \
              'path or click "Browse" to select a file or folder.\n\n' + \
              'Finally, click "Translate" to begin the translation process.'


class Application(Frame):
    """
    Main UI class.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self._init_ui()

    def _init_ui(self):
        self._init_window()
        self._init_menu_bar()
        self._init_frame()

    def _init_window(self):
        self._parent.minsize(width=720, height=480)
        self._parent.resizable(width=False, height=False)
        self._parent.title("Availability Model Translation Toolkit")
        img = PhotoImage(file='../resources/icon64x64.png')
        self._parent.tk.call('wm', 'iconphoto', self._parent._w, img)

    def _init_menu_bar(self):
        # Create menu bar
        menu_bar = Menu(self._parent)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self._parent.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: AboutDialog(self))
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self._parent.config(menu=menu_bar)

    def _init_frame(self):
        self.pack(fill=BOTH, expand=1)
        # Set instruction label
        input_instruction = Label(self)
        input_instruction.config(text=WINDOW_TEXT)
        input_instruction.place(x=10, y=10)

        input_text = 'Select input'
        input_label = Label(self, font="-weight bold")
        input_label.config(text=input_text)
        input_label.place(x=10, y=120)

        input_choices = ['Excel', 'CSV', 'XML']
        input_selection = StringVar(self._parent)
        input_selection.set(input_choices[0])
        input_options = OptionMenu(self, input_selection, input_choices[0],
                                   *input_choices)
        input_options.config(width=15)
        input_options.place(x=10, y=150)

        input_label = Label(self)
        input_label.config(text="Path:")
        input_label.place(x=15, y=180)
        input_value = StringVar(self._parent)
        input_entry = Entry(self, textvariable=input_value)
        input_entry.config(width=95)
        input_entry.place(x=50, y=180)
        input_selection.trace("w", lambda *args: input_value.set(''))

        input_browse = Button(
            self,
            text="Browse...",
            command=lambda: self._open_input_file_dialog(input_selection.get(), input_value)
        )
        input_browse.place(x=630, y=178)

        target_text = 'Select target'
        target_label = Label(self, font="-weight bold")
        target_label.config(text=target_text)
        target_label.place(x=10, y=240)

        target_choices = ['Isograph']
        target_selection = StringVar(self._parent)
        target_selection.set(target_choices[0])
        target_options = OptionMenu(self, target_selection, target_choices[0],
                                    *target_choices)
        target_options.config(width=15)
        target_options.place(x=10, y=270)

        output_label = Label(self)
        output_label.config(text="Path:")
        output_label.place(x=15, y=300)
        output_value = StringVar(self._parent)
        output_entry = Entry(self, textvariable=output_value)
        output_entry.config(width=95)
        output_entry.place(x=50, y=300)
        target_selection.trace("w", lambda *args: output_value.set(''))

        output_browse = Button(
            self,
            text="Browse...",
            command=lambda: self._open_output_file_dialog(target_selection.get(), output_value)
        )
        output_browse.place(x=630, y=298)

        exit_button = Button(self, text="Exit", command=self.quit)
        exit_button.place(x=630, y=420)

        exit_button = Button(self, text="Translate")
        exit_button.place(x=540, y=420)

    @staticmethod
    def _open_input_file_dialog(input_type, input_label_value):
        if input_type == 'Excel':
            method = filedialog.askopenfilename
            kwargs = {'filetypes': [('Microsoft Excel files', '*.xls;*.xlsx')]}
        elif input_type == 'CSV':
            method = filedialog.askdirectory
            kwargs = {}
        elif input_type == 'XML':
            method = filedialog.askopenfilename
            kwargs = {'filetypes': [('XML files', '*.xml')]}
        else:
            raise ValueError("Unknown input type: {}".format(input_type))
        selected_file_path = method(**kwargs)
        input_label_value.set(selected_file_path)

    @staticmethod
    def _open_output_file_dialog(output_type, output_label_value):
        if output_type == 'Isograph':
            method = filedialog.asksaveasfilename
            kwargs = {'filetypes': [('Microsoft Excel files', '*.xls;*.xlsx')]}
        else:
            raise ValueError("Unknown output type: {}".format(output_type))
        selected_file_path = method(**kwargs)
        output_label_value.set(selected_file_path)


class AboutDialog(object):

    DISCLAIMER = """
Availability Model Translation Toolkit - Version {version}

Copyright (c) 2017, CERN

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
    """.format(version=version.__version__)

    def __init__(self, parent):
        # Create dialog and set text content
        top = self.top = Toplevel(parent)
        top.title("About")
        top.resizable(width=False, height=False)
        msg = Label(top, text=self.DISCLAIMER)
        msg.pack(padx=10)
        # Create close button
        button = Button(top, text="Close", command=top.destroy)
        button.pack(pady=10)
        # Grab focus until dismissed
        top.grab_set()


def run_ui():
    top = Tk()
    Application(top)
    top.mainloop()


if __name__ == '__main__':
    run_ui()
