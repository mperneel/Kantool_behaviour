# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:42:05 2021

@author: Maarten

In this script, the class ImportMaskTemplate is defined. The class ImportMaskTemplate
codes for a wizard that can import mask templates in order to apply generic mask
templates
"""
#%% import packages
import os
import re
import shutil
import json
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from tkinter import ttk
import pandas as pd

#%%

class ImportMaskTemplateDialog(tk.Toplevel):
    
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.master = master
        
        #get reference to annotation data
        self.annotations = self.master.annotations
        
        #check if mask templates are available
        if not self.check_template_availability():
            tkmessagebox.showinfo(title="No templates available",
                                  message="There are no mask templates available. You should first save a mask template before you canimport one")
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
        self.title("Import mask template")

        #create tkinter variables
        self.var_mask_template = tk.StringVar(value=self.template_names[0]) #name of mask template

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
                                   text="OK",
                                   command=self.confirm)
        self.button_cancel = tk.Button(self.frame_buttons,
                                       text="Cancel",
                                       command=self.cancel)

        #pack all elements
        #frame_mask_template
        self.label_mask_template.pack(side='left')
        self.field_mask_template.pack()
        
        #frame_buttons
        self.button_ok.pack(side="left", padx=5)
        self.button_cancel.pack(padx=5)

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
        #first store a possible mask under construction
        if len(self.annotations.points_mask)>0:
            #if it's possible to save the current (non-confirmed) mask,
            #save this mask
            self.annotations.new_mask()
            
        #get name of chosen template
        template_name = self.field_mask_template.get()
        
        #import mask template
        mask_template = self.templates_dict[template_name]       
       
        #write data in masks to right attribute dataframes of self
        mask_id = len(self.annotations.names_masks)
        
        for i in mask_template.keys():
            mask = mask_template[i]
            
            #add name to self.annotations.names_masks             
            df = self.annotations.names_masks
            if 'name' in mask:
                new_mask = pd.DataFrame(data=[[mask_id, mask["name"]]],
                                      columns=df.columns)
            else:
                #this case is present to keep compatability with annotations
                #made with a previous version of CoBRA annotation tool
                new_mask = pd.DataFrame(data=[[self.mask_id, i]],
                                      columns=df.columns)
            df = pd.concat([df, new_mask],
                           ignore_index=True)
            self.annotations.names_masks = df                
    
            #add points to self.annotations.annotation_points_masks
            points_dict = mask["points"]
            points = []
            for j in points_dict.keys():
                x = points_dict[j]["x"]
                y = points_dict[j]["y"]
                points.append([x, y])
            points = pd.DataFrame(data=points,
                              columns=["x", "y"])
            points["obj"] = mask_id
            self.annotations.annotation_points_masks = \
                pd.concat([self.annotations.annotation_points_masks, points],
                          ignore_index=True)
    
            #increase mask_id with 1
            mask_id += 1
        
        #set id of active mask correctly
        #active mask id = the id of the next mask that will be drawn
        self.annotations.mask_id = self.annotations.names_masks["obj"].max() + 1
        
        #load names of masks in object_canvas
        self.master.object_canvas.load_masks()
        
        #refresh all visualisations
        self.master.update_visualisations()
        
        #destroy child window
        self.destroy()
        
    def cancel(self):
        #destroy child window
        self.destroy()
            
        
