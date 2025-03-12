# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 12:43:30 2021

@author: Maarten

In this file, the ChangeOrderKeypoints class is defined, this class codes for
an interface allowing the user to change the order in which keypoints are
annotated
"""
#%% import packages
import tkinter as tk

#%%

class ChangeOrderKeypoints(tk.Toplevel):
    """
    Interface to change the order in which keypoints are annotated

    Attributes
    -----
    self.master : SkeletonCanvas
        Master object

    self.keypoints : list (n)
        Names of the keypoints in the skeleton

    self.order : list (n)
        Functional annotation order of the keypoints

    Methods
    -----
    self.up
        Move the current keypoint one position up in the annotation order

    self.down
        Move the current keypoint one position down in the annotation order

    self.confirm
        confirm the new annotation order
    """
    def __init__(self, master):

        #initiate frame
        tk.Toplevel.__init__(self, master)

        #assign master
        self.master = master

        #assign attributes
        self.keypoints = self.master.skeleton.keypoints #keypoitn names
        self.order = self.master.skeleton.func_annotation_order #initial order

        #set title of frame
        self.title("Change order keypoints")

        #format listbox
        self.listbox = tk.Listbox(self, width=30, height=20)
        #height is expressed in number of lines
        self.listbox.grid(row=0, column=0, padx=0, pady=0)

        #format buttons
        self.up_down_btn_frame = tk.Frame(self, width=200, height=40)
        self.up_down_btn_frame.grid(row=0, column=1)

        self.up_btn = tk.Button(self.up_down_btn_frame,
                                text='Up',
                                command=self.up)
        self.up_btn.grid(row=0, column=0, padx=10, pady=10)

        self.down_btn = tk.Button(self.up_down_btn_frame,
                                  text='Down',
                                  command=self.down)
        self.down_btn.grid(row=1, column=0, padx=10, pady=10)

        self.ok_btn = tk.Button(self,
                                text='OK',
                                command=self.confirm)
        self.ok_btn.grid(row=1, column=0, columnspan=2, pady=10)

        #add items to listbox
        for i in range(len(self.keypoints)):
            self.listbox.insert(i, self.keypoints[self.order[i]])

        #set focus on listbox
        self.listbox.focus_set()

        #select first element in listbox
        if len(self.keypoints) > 0:
            self.listbox.activate(i - 1)
            self.listbox.select_set(i - 1)

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def up(self):
        """
        Move the current keypoint one position up in the annotation order
        """
        if len(self.keypoints) > 0:
            i = self.listbox.curselection()[0]
            if i != 0:
                self.order = self.order[:i - 1] +  [self.order[i]] +\
                    [self.order[i - 1]] + self.order[i + 1:]

            self.listbox.delete(0, 'end')
            for j in range(len(self.keypoints)):
                self.listbox.insert(j, self.keypoints[self.order[j]])

            index_to_select = max(i - 1, 0)
            self.listbox.select_set(index_to_select)
            self.listbox.activate(index_to_select)

    def down(self):
        """
        Move the current keypoint one position down in the annotation order
        """
        if len(self.keypoints) > 0:
            i = self.listbox.curselection()[0]
            if i < len(self.keypoints) - 1:
                self.order = self.order[:i] +  [self.order[i + 1]] +\
                    [self.order[i]] + self.order[i + 2:]

            self.listbox.delete(0, 'end')
            for j in range(len(self.keypoints)):
                self.listbox.insert(j, self.keypoints[self.order[j]])

            index_to_select = min(i + 1, len(self.keypoints) - 1)
            self.listbox.select_set(index_to_select)
            self.listbox.activate(index_to_select)

    def confirm(self):
        """
        Confirm the new order
        """
        if self.order != self.master.skeleton.func_annotation_order:
            #set saved state of master to False
            self.master.currently_saved = False

            #update functional annotation order
            self.master.skeleton.func_annotation_order = self.order

            #update annotation order
            annotation_order = [0 for _ in self.master.skeleton.annotation_order]
            for i, index in enumerate(self.order):
                annotation_order[index] = i
            self.master.skeleton.annotation_order = annotation_order

        #destroy child window
        self.destroy()
        