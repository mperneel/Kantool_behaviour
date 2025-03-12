# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:02:03 2021

@author: Maarten

In this file the class ChangeCentralKeypoint is defined. This class codes for
an interface to change the central/dominant keypoint
"""
#%%
import tkinter as tk

#%%
class ChangeCentralKeypoint(tk.Toplevel):
    """
    Interface to change the central/dominant keypoint

    Attributes
    -----
    self.master : SkeletonCanvas
        Master object

    self.keypoints : list
        List with the keypoint names

    Methods
    -----
    self.confirm
        Confirm the new central keypoint
    """
    def __init__(self, master):

        #initiate frame
        tk.Toplevel.__init__(self, master)

        #assign master
        self.master = master

        #set title of frame
        self.title("Change central keypoint")

        #format listbox
        self.listbox = tk.Listbox(self, width=30, height=20)
        #height is expressed in number of lines
        self.listbox.grid(row=0, column=0, padx=0, pady=0)

        #format button
        self.ok_btn = tk.Button(self,
                                text='OK',
                                command=self.confirm)
        self.ok_btn.grid(row=1, column=0, pady=10)

        #add items to listbox
        self.keypoints = self.master.skeleton.keypoints
        for i, keypoint in enumerate(self.keypoints):
            self.listbox.insert(i, keypoint)

        #set focus on listbox
        self.listbox.focus_set()

        #select current central keypoint in listbox
        central_keypoint_found = False
        i = -1
        while not central_keypoint_found:
            i += 1
            if self.master.skeleton.parent[i] == -1:
                self.listbox.activate(i)
                self.listbox.select_set(i)
                central_keypoint_found = True
            elif i == len(self.master.skeleton.parent) - 1:
                #normally this case won't be executed, however, this case is
                #implemented to prevent unwanted infinite loops
                central_keypoint_found = True

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def confirm(self):
        """
        Confirm the new central keypoint
        """
        #get index of new central keypoint
        central_keypoint = self.listbox.curselection()[0]

        #check if the central keypoint has changed
        if self.master.skeleton.parent[central_keypoint] == -1:
            #destroy window
            self.destroy()
            return

        #the central keypoint has changed
        self.master.currently_saved = False

        #list all connections
        connections = []
        for i, parent in enumerate(self.master.skeleton.parent):
            if parent != -1:
                connections.append([i, parent])

        #Update skeleton
        n_keypoints = len(self.master.skeleton.keypoints)
        used_connections = [False for _ in range(n_keypoints - 1)]
        hierarchy = [] #list to store the hierarchic levels
        classified_keypoints = 0 #number of classified keypoints

        next_level = [central_keypoint]
        self.master.skeleton.parent[central_keypoint] = -1
        while len(next_level) > 0:
            hierarchy.append(next_level)
            classified_keypoints += len(next_level)
            next_level = []
            for i in hierarchy[-1]:
                for j, connection in enumerate(connections):
                    if not used_connections[j]:
                        if connection[0] == i:
                            next_level.append(connection[1])
                            self.master.skeleton.parent[connection[1]] = connection[0]
                            used_connections[j] = True
                            classified_keypoints += 1
                        elif connection[1] == i:
                            next_level.append(connection[0])
                            self.master.skeleton.parent[connection[0]] = connection[1]
                            used_connections[j] = True
                            classified_keypoints += 1

        #destroy window
        self.destroy()
        