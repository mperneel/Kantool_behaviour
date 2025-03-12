# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:12:41 2021

@author: Maarten

In this file, the KeypointProperties class is defined, this class codes for an
interface allowing the user to set/modify the properties of a keypoint
"""
#%% import packages
import tkinter as tk
from tkinter import ttk
import numpy as np

#%%
class KeypointProperties(tk.Toplevel):
    """
    Interface to set/modify the properties of a keypoint

    Attributes
    -----
    self.master : SkeletonCanvas
        master object which invoked KeypointProperties

    self.coordinates : list (2)
        Coordinates of mouse when KeypointProperties was invoked. When
        KeypointProperties is invoked, coordinates may be a list as well as a
        tuple.

    self.index : int
        Index of the reactivated keypoint. None if a new keypoint is created

    self.central_keypoint : bool
        Boolean indicating if the central keypoint was reactivated

    self.name : tkinter Stringvar
        tkinter variable for the keypoint name

    self.parent : tkinter Stringvar
        tkinter variable for the parent name

    self.color_r : tkinter Stringvar
        tkinter variable for the color r value. An extra attribute (.old_value)
        was added to store the current/most recent correct value. Only integers
        in the interval [0, 255] are considered as correct values

    self.color_g : tkinter Stringvar
        tkinter variable for the color g value. An extra attribute (.old_value)
        was added to store the current/most recent correct value. Only integers
        in the interval [0, 255] are considered as correct values

    self.color_b : tkinter Stringvar
        tkinter variable for the color b value. An extra attribute (.old_value)
        was added to store the current/most recent correct value. Only integers
        in the interval [0, 255] are considered as correct values

    Methods
    -----
    self.check_color_value
        Check if the changes to self.color_r, self.color_g or self.color_b are
        valid, if this is not the case, the changes are undone by making use of
        the memory value stored in .old_value

    self.confirm
        Confirm the properties of a keypoint

    """
    def __init__(self, master, coordinates=(0, 0), index=None):

        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master

        #set variables

        self.index = index
        #index of the activated keypoint, None if new keypoint

        self.central_keypoint = False
        #boolean indicating if central keypoint was reactivate

        self.coordinates = list(coordinates)
        #coordinates of mouse when KeypointProperties was invoked

        self.name = tk.StringVar() #tkinter variable for the keypoint name
        self.parent = tk.StringVar() #tkinter variable for the parent name
        self.color_r = tk.StringVar() #tkinter variable for the color r value
        self.color_g = tk.StringVar() #tkinter variable for the color g value
        self.color_b = tk.StringVar() #tkinter variable for the color b value

        if self.index is None:
            #declare variables to store old values for the colors
            self.color_r.old_value = ''
            self.color_g.old_value = ''
            self.color_b.old_value = ''
        else:
            #set current name of the keypoint
            self.name.set(self.master.skeleton.keypoints[index])

            #set current name of the parent
            self.parent.set(self.master.skeleton.keypoints[self.master.skeleton.parent[index]])

            #set current values for color
            color = self.master.skeleton.color[index]
            self.color_r.set(str(int(color[0])))
            self.color_g.set(str(int(color[1])))
            self.color_b.set(str(int(color[2])))

            #create memory for the old values of the colors (for the case the
            #user enters an invalid value)
            self.color_r.old_value = str(int(color[0]))
            self.color_g.old_value = str(int(color[1]))
            self.color_b.old_value = str(int(color[2]))

        #set title of frame
        self.title("Keypoint properties")

        #create frames
        """
        |----------------------------|
        |         frame_name         |
        |----------------------------|
        |----------------------------|
        |        frame_parent        |
        |----------------------------|
        |----------------------------|
        |         frame_color        |
        ||------------||------------||
        || frame_rgb_ || frame_rgb_ ||
        ||   labels   ||   values   ||
        ||------------||------------||
        |----------------------------|
        |----------------------------|
        |          frame_btn         |
        |----------------------------|
        """

        self.frame_name = tk.Frame(self)
        self.frame_parent = tk.Frame(self)
        self.frame_color = tk.Frame(self)
        self.frame_btn = tk.Frame(self)
        self.frame_rgb_labels = tk.Frame(self.frame_color)
        self.frame_rgb_values = tk.Frame(self.frame_color)
        self.frame_rgb_sample = tk.Frame(self.frame_color)

        #create  entry fields

        #entry field for the name
        self.field_name = tk.Entry(self.frame_name,
                                   width=25,
                                   textvariable=self.name)

        #combobox for the parent
        self.field_parent = ttk.Combobox(self.frame_parent,
                                         width=22,
                                         textvariable=self.parent)
        #arrow takes space of three characters

        #entry fields for the color
        self.field_color_r = tk.Entry(self.frame_rgb_values,
                                      width=3,
                                      textvariable=self.color_r)
        self.field_color_g = tk.Entry(self.frame_rgb_values,
                                      width=3,
                                      textvariable=self.color_g)
        self.field_color_b = tk.Entry(self.frame_rgb_values,
                                      width=3,
                                      textvariable=self.color_b)
        
        #canvas to display sample of color
        self.canvas_color = tk.Canvas(self.frame_rgb_sample,
                                      bg="#ffffff",
                                      width=90,
                                      height=90)

        #Adding entries to drop down list of combobox
        values = []

        if (self.index is not None) and\
            (self.master.skeleton.parent[self.index] == -1):
            #the central keypoint was reactivated
            self.central_keypoint = True
        elif (self.index is None) and\
            (len(self.master.skeleton.keypoints) == 0):
            #a project with an empty skeleton was opened or a new project
            #was created
            #This is the first keypoint that is added to the skeleton
            #This keypoint can't have a parent and by consequence it will
            #be the initial central/dominant keypoint
            self.central_keypoint = True

        if self.central_keypoint:
            #The current keypoint is/will become the central/dominant keypoint

            #grey out the entry field for the parent name
            self.field_parent.config(state='disabled')

            #add "-" to list of values (only element of values list)
            values.append("-")

            #set value of self.parent to "-"
            self.parent.set("-")

        else:
            #new keypoint or not the central keypoint

            #new keypoint: add all keypoint names to values
            #reactivated keypoint: add all keypoint names to values, except the
            #name of the reactivated keypoint
            for keypoint in self.master.skeleton.keypoints:
                if (self.index is None) or\
                    (keypoint != self.master.skeleton.keypoints[self.index]):
                    values.append(keypoint)

        self.field_parent['values'] = tuple(values)

        #use .trace() to add a method to the tkinter variables that takes action
        #if the user entered an invalid value
        self.color_r.trace('w', self.check_color_value)
        self.color_g.trace('w', self.check_color_value)
        self.color_b.trace('w', self.check_color_value)

        #create buttons
        self.button_ok = tk.Button(self.frame_btn,
                                   text="OK",
                                   command=self.confirm)

        #create labels
        self.label_name = tk.Label(self.frame_name,
                                   text="Name ", width=6, anchor='w')
        self.label_parent = tk.Label(self.frame_parent,
                                     text="Parent", width=6, anchor='w')
        self.label_color = tk.Label(self.frame_color,
                                    text="Color", width=6, anchor='w')
        self.label_color_r = tk.Label(self.frame_rgb_labels,
                                      text="R", anchor='w')
        self.label_color_g = tk.Label(self.frame_rgb_labels,
                                      text="G", anchor='w')
        self.label_color_b = tk.Label(self.frame_rgb_labels,
                                      text="B", anchor='w')

        #position all labels, fields and buttons
        #frame_name
        self.label_name.pack(side='left')
        self.field_name.pack()
        self.frame_name.pack(anchor='w')

        #frame_parent
        self.label_parent.pack(side='left')
        self.field_parent.pack()
        self.frame_parent.pack(anchor='w')

        #frame_color
        self.label_color_r.pack()
        self.label_color_g.pack()
        self.label_color_b.pack()
        self.field_color_r.pack()
        self.field_color_g.pack()
        self.field_color_b.pack()
        self.canvas_color.pack()
        self.label_color.pack(side='left', anchor='nw')
        self.frame_rgb_labels.pack(side='left')
        self.frame_rgb_values.pack(side='left')
        self.frame_rgb_sample.pack()
        self.frame_color.pack(anchor='w')

        #frame_btn
        self.button_ok.pack()
        self.frame_btn.pack()

        #bind hitting return/enter key to invocation of button
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #activate first entry-field
        self.field_name.focus_set()
        
        #configure color sample
        self.update_color_sample()

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def check_color_value(self, *args):
        """
        Check if the changes to self.color_r, self.color_g or self.color_b still
        result in a valid entry.

        If the changes would result in an invalid entry (not an integer in the
        interval [0, 255]), the changes are undone by replacing the invalid
        entry with the value stored in the attribute .old_value

        If an integer greater than 255 is entered, the value is floored to 255
        """

        for textvar in [self.color_r, self.color_g, self.color_b]:
            if len(textvar.get()) > 3:
                #the textvar may only contain three characters (maximum number
                #of digits); reject this
                textvar.set(textvar.old_value)
            elif textvar.get().isdigit():
                #the current value only contains digits; accept this
                if float(textvar.get()) > 255:
                    #the current value is too high, floor to 255
                    textvar.set('255')
                #update textvar.old_value
                textvar.old_value = textvar.get()
            elif textvar.get() == '':
                #the field is empty (equal to a zero entry); accept this
                #update textvar.old_value
                textvar.old_value = textvar.get()
            else:
                # there's non-digit characters in the input; reject this
                textvar.set(textvar.old_value)
                
        #update color in sample canvas
        self.update_color_sample()
        
    def update_color_sample(self):
        """
        Update the color sample.
        """
        
        #initiate list for RGB values of color
        rgb_color = []     
        
        #counter for number of empty color fields
        empty_fields = 0
        
        #if entry fields of color values are empty, assume a color value of zero
        for textvar in [self.color_r, self.color_g, self.color_b]:
            if textvar.get() == '':
                #color field is empty
                rgb_color.append(0)
                empty_fields += 1
            else:
                #color field has a value
                rgb_color.append(int(textvar.get()))
                
        if empty_fields == 3:
            #all color entry fields are empty
            #show a white color sample
            self.canvas_color.configure(bg="#ffffff")
        else:
            self.canvas_color.configure(bg="#%02x%02x%02x" % tuple(rgb_color)) 

    def confirm(self):
        """
        Confirm the properties of a keypoint.

        First the validity of all properties is checked. If all properties are
        valid, self.master.skeleton is updated
        """
        skeleton = self.master.skeleton

        #check all properties

        #check if name is not empty
        if self.name.get() == '':
            tk.messagebox.showerror("Error", "Name is empty")
            return

        #check if name contains no spaces
        if ' ' in self.name.get():
            tk.messagebox.showerror("Error", "Name contains spaces")
            return

        #check if name is unique
        if self.name.get() in skeleton.keypoints:
            if self.index is None:
                tk.messagebox.showerror("Error", "Name is not unique")
                return

            if self.name.get() != skeleton.keypoints[self.index]:
                tk.messagebox.showerror("Error", "Name is not unique")
                return

        #check if the parent is an existing keypoint
        if (self.parent.get() not in skeleton.keypoints) and\
            (not self.central_keypoint):
            tk.messagebox.showerror("Error", "Parent should be a yet existing keypoint")
            return

        #if entry fields of color values are empty, assume a color value of zero
        for textvar in [self.color_r, self.color_g, self.color_b]:
            if textvar.get() == '':
                textvar.set('0')

        #assign properties to master
        if self.index is None:
            #new keypoint
            self.master.currently_saved = False

            #add keypoint name
            skeleton.keypoints.append(self.name.get())

            #add color
            skeleton.color.append([float(self.color_r.get()),
                                   float(self.color_g.get()),
                                   float(self.color_b.get())])
            
            #update annotation order
            skeleton.annotation_order.append(len(skeleton.annotation_order))

            #update functional annotation order
            skeleton.func_annotation_order.append(len(skeleton.func_annotation_order))

            if self.central_keypoint:
                #this is the first keypoint of the skeleton

                #initiate skeleton.coordinates
                skeleton.coordinates = np.array([self.coordinates])

                #initiate skeleton.parent
                skeleton.parent = np.array([-1])

            else:
                #add coordinates
                skeleton.coordinates = np.concatenate((skeleton.coordinates,
                                                       [self.coordinates]),
                                                      axis=0)

                #add parent
                for i, keypoint_name in enumerate(skeleton.keypoints):
                    if keypoint_name == self.parent.get():
                        skeleton.parent = np.concatenate((skeleton.parent,
                                                          [i]),
                                                         axis=0)

        else:
            #adjusted keypoint

            #update keypoint name
            if skeleton.keypoints[self.index] != self.name.get():
                self.master.currently_saved = False
                skeleton.keypoints[self.index] = self.name.get()

            #update keypoint parent
            if not self.central_keypoint:
                for i, keypoint_name in enumerate(skeleton.keypoints):
                    if keypoint_name == self.parent.get():
                        if i != skeleton.parent[self.index]:
                            self.master.currently_saved = False
                            skeleton.parent[self.index] = i

            #update keypoint color
            color = [float(self.color_r.get()),
                     float(self.color_g.get()),
                     float(self.color_b.get())]

            if color != skeleton.color[self.index]:
                self.master.currently_saved = False
                skeleton.color[self.index] = color

        #destroy child window
        self.destroy()
        