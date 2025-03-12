# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 12:43:30 2021

@author: Maarten

In this file, the MaskTemplateManager class is defined, this class codes for
an interface allowing the user to delete mask templates and to change the order
in which mask templates are shown in dialogs and to delete mask templates
"""
#%% import packages
import tkinter as tk
import os
import json
from tkinter import messagebox as tkmessagebox

#%%

class MaskTemplateManager(tk.Toplevel):
   
    def __init__(self, master):

        #initiate frame
        tk.Toplevel.__init__(self, master)

        #assign master
        self.master = master
        
        #read mask templates
        if 'mask_templates.json' in os.listdir('project'):
            f = open("project\mask_templates.json")
            self.templates_dict = json.load(f)
            f.close()
            
            #get names of mask templates
            self.names = list(self.templates_dict.keys())
        else:
            #no mask templates are present
            #show warning and destroy child window
            tkmessagebox.showinfo(title="No mask templates present",
                                  message="No mask templates were yet defined in the current project")
            
            self.destroy()
            return

        #set title of frame
        self.title("Mask templates manager")

        #format listbox
        self.listbox = tk.Listbox(self, width=30, height=20)
        #height is expressed in number of lines
        
        #create frames
        self.modifications_frm = tk.Frame(self, width=200, height=40)        
        
        #create buttons
        button_width = 10
        self.up_btn = tk.Button(self.modifications_frm,
                                text='Up',
                                command=self.up,
                                width=button_width)
        self.down_btn = tk.Button(self.modifications_frm,
                                  text='Down',
                                  command=self.down,
                                  width=button_width)
        self.delete_btn = tk.Button(self.modifications_frm,
                                    text="Delete",
                                    command=self.delete,
                                    width=button_width)
        self.ok_btn = tk.Button(self,
                                text='OK',
                                command=self.confirm,
                                width=button_width)

        #format all elements   
        self.ok_btn.pack(side="bottom",
                         pady=5)
        self.listbox.pack(side="left",
                          pady=5, padx=5)
        self.modifications_frm.pack(side="left",
                                    pady=5, padx=5)
        
        self.up_btn.pack(pady=3)
        self.down_btn.pack(pady=3)
        self.delete_btn.pack(pady=20)

        #add items to listbox
        for i, name in enumerate(self.names):
            self.listbox.insert(i, name)

        #set focus on listbox
        self.listbox.focus_set()

        #select first element in listbox
        if len(self.names) > 0:
            self.listbox.activate(i - 1)
            self.listbox.select_set(i - 1)

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def update_listbox(self):
        """
        Reload all names in the listbox
        """
        
        self.listbox.delete(0, 'end')
        for i, name in enumerate(self.names):
            self.listbox.insert(i, name)
            
    def delete(self):
        """
        Delete the selecte template
        """
        
        i = self.listbox.curselection()[0]
        del self.names[i]
        self.update_listbox()     
        

    def up(self):
        """
        Move the current keypoint one position up in the annotation order
        """
        if len(self.names) == 0:
            return        

        i = self.listbox.curselection()[0]
        if i != 0:
            self.names = self.names[:i - 1] +  [self.names[i]] +\
                [self.names[i - 1]] + self.names[i + 1:]

        self.update_listbox()

        index_to_select = max(i - 1, 0)
        self.listbox.select_set(index_to_select)
        self.listbox.activate(index_to_select)

    def down(self):
        """
        Move the current keypoint one position down in the annotation order
        """
        if len(self.names) == 0:
            return
        
        i = self.listbox.curselection()[0]
        if i < len(self.names) - 1:
            self.names = self.names[:i] +  [self.names[i + 1]] +\
                [self.names[i]] + self.names[i + 2:]

        self.update_listbox()

        index_to_select = min(i + 1, len(self.names) - 1)
        self.listbox.select_set(index_to_select)
        self.listbox.activate(index_to_select)

    def confirm(self):
        """
        Confirm all modifications
        
        possible modifications:
            - deletion of a mask template
            - change of order of mask templates
        """
       
        #create a dict contatining all information about the mask templates
        templates_dict_new = {}
        for name in self.names:
            templates_dict_new[name] = self.templates_dict[name]
            
        f = open("project\mask_templates.json", 'w')
        json.dump(templates_dict_new, f, indent=3)
        f.close()

        #destroy child window
        self.destroy()
        