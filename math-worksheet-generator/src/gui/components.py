from tkinter import Button, Label, Entry, Frame

class CustomButton(Button):
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master, text=text, command=command, **kwargs)

class CustomLabel(Label):
    def __init__(self, master=None, text="", **kwargs):
        super().__init__(master, text=text, **kwargs)

class CustomEntry(Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

class ComponentFrame(Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

    def add_label(self, text):
        label = CustomLabel(self, text=text)
        label.pack()

    def add_entry(self):
        entry = CustomEntry(self)
        entry.pack()
        return entry

    def add_button(self, text, command):
        button = CustomButton(self, text=text, command=command)
        button.pack()