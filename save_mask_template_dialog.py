# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:42:05 2021

@author: Maarten

In this script, the class SaveMaskTemplate is defined. The class SaveMaskTemplate
codes for a wizard that can save mask templates in order to apply generic mask
templates
"""
#%% import packages
import os
import json
import tkinter as tk
import tkinter.messagebox as tkmessagebox

#%%

class SaveMaskTemplateDialog(tk.Toplevel):
    
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.master = master
        
        #get easy reference to annotations
        self.annotations = master.annotations
        
        #first check if there are masks drawn onthe current image
        masks_available = self.check_mask_availability()
        
        if not masks_available:
            self.destroy()
            return

        #set default size
        self.geometry('400x90')

        #set title
        self.title("Save mask template")

        #create tkinter variables
        self.var_name = tk.StringVar() #name of mask template

        #create frames       
        self.frame_name = tk.Frame(self)
        self.frame_buttons = tk.Frame(self)

        #create labels
        label_width = 6
        self.label_name = tk.Label(self.frame_name,
                                    text="Name", width=label_width, anchor='w')

        #create entry fields
        entry_width = 30
        self.field_name = tk.Entry(self.frame_name,
                                    width=entry_width,
                                    textvariable=self.var_name)

        #create buttons
        self.button_ok = tk.Button(self.frame_buttons,
                                   text="OK",
                                   command=self.confirm)
        self.button_cancel = tk.Button(self.frame_buttons,
                                       text="Cancel",
                                       command=self.cancel)

        #format all elements
        #frame_name
        self.label_name.pack(side='left')
        self.field_name.pack()
        
        #frame_buttons
        self.button_ok.pack(side='left', padx=5)
        self.button_cancel.pack(padx=5)

        #self
        self.frame_name.pack(pady=5)
        self.frame_buttons.pack(pady=5)        

        #set focus on first entryfield
        self.field_name.focus()

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
        
    def check_mask_availability(self):
        
        if len(self.annotations.points_mask)>0:
            #if it's possible to save the current (non-confirmed) mask,
            #save this mask
            self.annotations.new_mask()

        #all information that has to be saved is in self.annotations.annotation_points_masks and
        #self.annotations.names_masks
        
        if len(self.annotations.annotation_points_masks)==0:
            #there is no data to be saved or all data was removed
            
            tkmessagebox.showinfo(title="No masks present",
                                  message="No template can be created, since no masks are present")
        
            #destroy child window
            return False
        return True

    def confirm(self):
        
        #self.check_mask_availability was called previously, as a consequence,
        #we know there are masks present and all information that has to be
        #saved is in self.annotations.annotation_points_masks and
        #self.annotations.names_masks
        
        #get name of template
        template_name = self.var_name.get()        

        #fuse self.annotations.names_masks, self.annotations.annotation_points_masks
        #in one dictionary        
        names_masks = self.annotations.names_masks
        annotation_points_masks = self.annotations.annotation_points_masks
        
        data={}
        for mask_id in names_masks["obj"]:
            #get mask_name
            mask_name = names_masks.loc[names_masks["obj"]==mask_id, 'name'].iloc[0]
            
            #get mask points
            points = annotation_points_masks.loc[annotation_points_masks["obj"]==mask_id,\
                                                ["x","y"]].round(2)

            #convert points from pd.DataFrame to dict
            points_dict = {}
            for i in range(len(points)):
                points_dict[i] = points.iloc[i,].to_dict(({}))

            #assembly dict for object
            mask = {"name": mask_name,
                   "points": points_dict}

            #add object dict to data
            data[mask_id] = mask
            
        #check if there are already templates stored in this project
        #if this is the case, load the templates
        #if this is not the case, create an empty dictionary
        if "mask_templates.json" in os.listdir("project"):
            f = open("project/mask_templates.json")
            templates_dict = json.load(f)
            f.close()
        else:
            templates_dict = {}
            
        #add template to templates_dict
        templates_dict[template_name] = data

        #save all templates
        f = open("project/mask_templates.json", 'w')
        json.dump(templates_dict, f, indent = 3)
        f.close()
        
        #destroy child window
        self.destroy()
        
    def cancel(self):
        #destroy child window
        self.destroy()
