# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 10:21:25 2023

@author: Maarten

In this script, the class Ethogramor is defined. The class EthogramEditor
codes a wizard to create and modify an ethogram
"""
#%% import packages
import os
import re
import shutil
import json
import numpy as np
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from tkinter import messagebox

from ask_string_dialog import AskStringDialog

#%%

class EthogramEditor(tk.Toplevel):
    """
    In this script, the class EthogramEditor is defined. The class EthogramEditor
    codes a wizard to create and modify an ethogram
    """
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.master = master

        self.ethogram = self.master.ethogram
        self.ethogram_list = self.ethogram.as_list()

        self.key_options = np.array(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                     "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                     "u", "v", "w", "x", "y", "z"])

        #set default size
        self.geometry('600x380')

        #set title
        self.title("Ethogram")

        #create frames
        self.frame_ethogram = tk.Frame(self)
        self.frame_buttons_edit = tk.Frame(self)
        self.frame_buttons_position = tk.Frame(self)

        #create labels

        #set default configurations of labels

        #create checkbuttons

        #create entry fields

        #create listbox and scrollbar for ethogram
        self.list_ethogram = tk.Listbox(master=self.frame_ethogram)
        self.scrollbar_ethogram = tk.Scrollbar(self.frame_ethogram,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar_ethogram.config(command=self.list_ethogram.yview)
        self.list_ethogram.config(yscrollcommand=self.scrollbar_ethogram.set)


        #set default configurations of fields

        #create buttons
        self.button_up = \
            tk.Button(self.frame_buttons_position,
                      text="Up",
                      command=lambda: self.move_class(direction=1))

        self.button_down = \
            tk.Button(self.frame_buttons_position,
                      text="Down",
                      command=lambda: self.move_class(direction=-1))

        self.button_new_class = \
            tk.Button(self.frame_buttons_edit,
                      text="New class",
                      command=lambda: self.new_class())

        self.button_new_subclass = \
            tk.Button(self.frame_buttons_edit,
                      text="New subclass",
                      command=lambda: self.new_subclass())

        self.button_rename = \
            tk.Button(self.frame_buttons_edit,
                      text="Rename",
                      command=lambda: self.rename())

        self.button_delete = \
            tk.Button(self.frame_buttons_edit,
                      text="Delete",
                      command=lambda: self.delete())

        self.button_ok = tk.Button(self,
                                   text="OK",
                                   command=self.confirm)

        #set default configurations of buttons


        #pack all elements
        #frame_ethogram
        self.list_ethogram.pack(side="left",
                               fill=tk.BOTH,
                               expand=True)
        self.scrollbar_ethogram.pack(side="left",
                                     fill="y")

        #frame_buttons_position
        self.button_up.pack(pady=5)
        self.button_down.pack(pady=5)

        #frame_buttons_edit
        self.button_new_class.pack(side="left", padx=5)
        self.button_new_subclass.pack(side="left", padx=5)
        self.button_rename.pack(side="left", padx=5)
        self.button_delete.pack(side="left", padx=5)

        #self
        self.button_ok.pack(side='bottom', pady=5)
        self.frame_buttons_edit.pack(anchor='center',side="bottom", pady=5)
        self.frame_ethogram.pack(anchor='w', side="left", pady=5, fill="both")
        self.frame_buttons_position.pack(anchor='center', side="left", padx=5, fill="y")

        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #bind method to resize entry field to <Configure> event
        self.bind("<Configure>", lambda event: self.resize_window())

        #load current ethogram
        self.load_ethogram()

        #disable buttons which are not yet implemented
        self.button_up.config(state="disabled")
        self.button_down.config(state="disabled")
        self.button_delete.config(state="disabled")

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def choose_directory(self, textvar):
        """
        Invoke dialog to choose a directory

        Parameters
        ----------
        textvar : tkinter.StringVar
            Variable to which the directory-string has to be assigned
        """
        path = tkfiledialog.askdirectory()
        textvar.set(path)

    def choose_file(self, textvar):
        """
        Invoke dialog to choose a file

        Parameters
        ----------
        textvar : tkinter.StringVar
            Variable to which the directory of the file has to be assigned
        """
        path = tkfiledialog.askopenfilename()
        textvar.set(path)

    def img_skeleton_checkbutton(self):
        """
        Configure all elements within frame_img_skeleton and frame_dir_skeleton

        If self.checkbut_img_skeleton was activated, disable all elements in
        frame_dir_skeleton (except the checkbutton) and enable all elements in
        frame_img_skeleton

        If self.checkbut_img_skeleton was deactivated, disable all elements in
        frame_img_skeleton (except the checkbutton) and enable all elements in
        frame_dir_skeleton
        """
        value = self.img_skeleton_bool.get()

        if value:
            self.label_img_skeleton.config(state='normal')
            self.field_img_skeleton.config(state='normal')
            self.button_img_skeleton.config(state='normal')
            self.dir_skeleton_bool.set(False)
            self.label_dir_skeleton.config(state='disabled')
            self.field_dir_skeleton.config(state='disabled')
            self.button_dir_skeleton.config(state='disabled')
        else: #not value
            self.label_img_skeleton.config(state='disabled')
            self.field_img_skeleton.config(state='disabled')
            self.button_img_skeleton.config(state='disabled')
            self.dir_skeleton_bool.set(True)
            self.label_dir_skeleton.config(state='normal')
            self.field_dir_skeleton.config(state='normal')
            self.button_dir_skeleton.config(state='normal')

    def dir_skeleton_checkbutton(self):
        """
        Configure all elements within frame_img_skeleton and frame_dir_skeleton

        If self.checkbut_dir_skeleton was activated, disable all elements in
        frame_img_skeleton (except the checkbutton) and enable all elements in
        frame_dir_skeleton

        If self.checkbut_dir_skeleton was deactivated, disable all elements in
        frame_dir_skeleton (except the checkbutton) and enable all elements in
        frame_img_skeleton
        """
        value = self.dir_skeleton_bool.get()

        if value:
            self.label_dir_skeleton.config(state='normal')
            self.field_dir_skeleton.config(state='normal')
            self.button_dir_skeleton.config(state='normal')
            self.img_skeleton_bool.set(False)
            self.label_img_skeleton.config(state='disabled')
            self.field_img_skeleton.config(state='disabled')
            self.button_img_skeleton.config(state='disabled')
        else: #not value
            self.label_dir_skeleton.config(state='disabled')
            self.field_dir_skeleton.config(state='disabled')
            self.button_dir_skeleton.config(state='disabled')
            self.img_skeleton_bool.set(True)
            self.label_img_skeleton.config(state='normal')
            self.field_img_skeleton.config(state='normal')
            self.button_img_skeleton.config(state='normal')

    def resize_window(self):
        """
        Resize the entry fields if the size of the new-project-dialog window
        changes
        """
        #get useable width
        uw = self.winfo_width()

        self.list_ethogram.config(width=int((uw - 100)/10))

    def new_class(self):
        #select last key at current behavioural level
        i = self.list_ethogram.curselection()[0]
        key = self.ethogram_list[i].split(" - ")[0]

        #obtain new key
        new_key = key
        keys_list = [a.split(" - ")[0] for a in self.ethogram_list]
        while new_key in keys_list:
            #get new key of behavioural class
            j = np.where(self.key_options == new_key[-1])[0] + 1
            if j == len(self.key_options):
                messagebox.showerror("Overload", "Maximum number of classes reached")
                return

            new_key = key[:-1] + self.key_options[j][0]

        #get position where to insert new key
        #position: after last behavioural class with same parent, but before the
        #next branch of the ethogram starts
        parent_classes = [key[:-1] for key in keys_list]
        parent_levels = [len(key) for key in parent_classes]

        k = np.where(np.array(parent_classes) == new_key[:-1])[0][-1]
        parent_level = parent_levels[k]

        condition = True
        while condition:
            k += 1
            if k == len(parent_levels):
                condition = False
            else:
                condition = parent_levels[k] > parent_level
                #this condition will become false when next branch of ethogram starts

        #get name for new behavioural class
        dialog = AskStringDialog(master=self,
                                 title="New class",
                                 prompt="Name/Description",
                                 width=250)

        class_name = dialog.string_input

        if class_name is None:
            return
        if class_name == '':
            return

        self.ethogram_list = self.ethogram_list[:k] +\
            [new_key + " - " + class_name] + self.ethogram_list[k:]

        self.load_ethogram()

    def new_subclass(self):

        #select last key at current behavioural level
        i = self.list_ethogram.curselection()[0]
        key = self.ethogram_list[i].split(" - ")[0]

        #obtain new key
        new_key = key + self.key_options[0] #new subclass -> extra character
        keys_list = [a.split(" - ")[0] for a in self.ethogram_list]
        while new_key in keys_list:
            #get new key of behavioural class
            j = np.where(self.key_options == new_key[-1])[0] + 1
            if j == len(self.key_options):
                messagebox.showerror("Overload", "Maximum number of classes reached")
                return

            new_key = key[:-1] + self.key_options[j][0]

        #get position where to insert new key
        #position: after last behavioural class with same parent, but before the
        #next branch of the ethogram starts
        parent_classes = keys_list
        parent_levels = [len(key) for key in parent_classes]

        k = np.where(np.array(parent_classes) == new_key[:-1])[0][-1]
        parent_level = parent_levels[k]

        condition = True
        while condition:
            k += 1
            if k == len(parent_levels):
                condition = False
            else:
                condition = parent_levels[k] > parent_level
                #this condition will become false when next branch of ethogram starts

        #get name for new behavioural class
        dialog = AskStringDialog(master=self,
                                 title="New subclass",
                                 prompt="Name/Description",
                                 width=250)

        class_name = dialog.string_input

        if class_name is None:
            return
        if class_name == '':
            return

        self.ethogram_list = self.ethogram_list[:k] +\
            [new_key + " - " + class_name] + self.ethogram_list[k:]

        self.load_ethogram()

    def rename(self):

        i = self.list_ethogram.curselection()[0]
        class_name = self.ethogram_list[i].split(" - ")[-1]
        class_key = self.ethogram_list[i].split(" - ")[0]

        dialog = AskStringDialog(master=self,
                                 title="Rename class",
                                 prompt="Name/Description",
                                 width=250,
                                 initial_value=class_name)

        class_name_new = dialog.string_input

        self.ethogram_list[i] = class_key + " - " + class_name_new

        self.load_ethogram()

    def delete_class(self):
        pass
        #not yet implemented

    def load_ethogram(self):
        self.list_ethogram.delete(0, "end")

        for i in self.ethogram_list:
            self.list_ethogram.insert("end", i)

    def move_class(self, direction):
        pass
        #not yet implemented

    def confirm(self):
        """
        create dictionary from ethogram_list and assign dict to self.ethogram
        """
        keys = [a.split(" - ")[0] for a in self.ethogram_list]
        descriptions = [a.split(" - ")[-1] for a in self.ethogram_list]
        levels = [len(key) - 1 for key in keys]

        ethogram = {}

        for level in range(max(levels)+1):
            for level_i, key, description in zip(levels, keys, descriptions):

                if level_i != level:
                    continue

                subethogram = ethogram
                for i in range(level):
                    subethogram = subethogram[key[i]]

                    if "subclasses" not in subethogram:
                        subethogram["subclasses"] = {}
                    subethogram = subethogram["subclasses"]

                subethogram[key[-1]] = {"description": description}

        self.ethogram.ethogram = ethogram
        self.ethogram.save()

        #close window
        self.destroy()
