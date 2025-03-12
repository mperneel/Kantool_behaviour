# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:24:45 2023

@author: Maarten

Dialog to ask the user for a string value
"""
#%%
import tkinter as tk



#%%

class AskStringDialog(tk.Toplevel):
    """
    Dialog to ask the user for a string value
    """

    def __init__(self, master, title, prompt, width=None, height=None, initial_value=""):
        tk.Toplevel.__init__(self, master)
        self.master = master

        self.string_input = None

        #set default size
        if width is None:
            width=600
        if height is None:
            height=150

        self.geometry(f'{width}x{height}')

        #set title
        self.title(title)

        #create variables
        self.string_input_var = tk.StringVar(value=initial_value)

        #create frames
        self.frm_entry = tk.Frame(self) #frame with entry field for string
        self.frm_btns = tk.Frame(self) #frame with buttons

        #create labels
        self.label_prompt = tk.Label(self.frm_entry,
                                     text=prompt)

        #create entry field
        self.entry_string = tk.Entry(self.frm_entry,
                                     textvariable=self.string_input_var,
                                     width=50)

        #create buttons
        self.btn_ok = tk.Button(self.frm_btns,
                                text="OK",
                                command= lambda: self.confirm())
        self.btn_cancel = tk.Button(self.frm_btns,
                                    text="Cancel",
                                    command=self.destroy)

        #position all elements

        #frm_entry
        self.label_prompt.pack(anchor="w", pady=5)
        self.entry_string.pack(pady=5,padx=5, fill="x")

        #frm_btns
        self.btn_ok.pack(side="left", padx=5)
        self.btn_cancel.pack(side="left", padx=5)

        #self
        self.frm_entry.pack(fill="both")
        self.frm_btns.pack()


        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def confirm(self):
        """
        Confirm string input
        """
        self.string_input = self.string_input_var.get()
        self.destroy()

