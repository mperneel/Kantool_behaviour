# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:42:05 2021

@author: Maarten

In this script, the class AskMaskTemplate is defined. The class AskMaskTemplate
asks for a mask template when images are imported into the project
"""
#%% import packages
import os
import json
import tkinter as tk
from tkinter import ttk

#%%
class AskMaskTemplate(tk.Toplevel):
    
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.master = master
        
        #check if mask templates are available
        if not self.check_template_availability():
            self.master.settings.default_mask_template = None
            
            #destroy child window
            self.destroy()            
            return
            
        
        #read mask templates
        f = open("project/mask_templates.json")
        self.templates_dict = json.load(f)
        f.close()
        
        #get all names of templates
        self.template_names = list(self.templates_dict.keys())

        #set default size
        self.geometry('500x100')

        #set title
        self.title("Mask template")

        #create tkinter variables
        self.var_mask_template = tk.StringVar(value=None) #name of mask template

        #create frames       
        self.frame_mask_template = tk.Frame(self)
        self.frame_buttons = tk.Frame(self)

        #create labels
        label_width = 14
        self.label_mask_template = tk.Label(self.frame_mask_template,
                                    text="Mask template", width=label_width, anchor='w')

        #create combobox
        self.field_mask_template = ttk.Combobox(self.frame_mask_template,
                                                width=30,
                                                values=self.template_names,
                                                textvariable=self.var_mask_template)

        #create buttons
        self.button_ok = tk.Button(self.frame_buttons,
                                   text="Next",
                                   command=self.confirm)
        self.button_skip = tk.Button(self.frame_buttons,
                                       text="Skip",
                                       command=self.skip)

        #pack all elements
        #frame_mask_template
        self.label_mask_template.pack(side='left')
        self.field_mask_template.pack()
        
        #frame_buttons
        self.button_ok.pack(side="left", padx=5)
        self.button_skip.pack(padx=5)

        #self
        self.frame_mask_template.pack(pady=5)
        self.frame_buttons.pack(pady=5)

        #set focus on first entryfield
        self.field_mask_template.focus()

        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())
        self.bind_class("Checkbutton",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def check_template_availability(self):            
        #check if there are mask templates available
        if "mask_templates.json" not in os.listdir("project"):
            return False
        return True       
        
    def confirm(self):
        #get name of chosen template
        template_name = self.field_mask_template.get()
        
        if template_name != '' :        
            #get data mask template
            self.master.settings.default_mask_template =\
                self.templates_dict[template_name]   
        else:
            self.master.settings.default_mask_template = None
       
        #destroy child window
        self.destroy()
        
    def skip(self):
        
        self.master.settings.default_mask_template = None
            
        #destroy child window
        self.destroy()
            
        
