# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:09:09 2021

@author: Maarten

In this script, the SkeletonCanvas class is defined. The SkeletonCanvas class 
regulates all modifications to the skeleton
"""
#%% import packages
import os
import json
import tkinter as tk
import tkinter.messagebox as tkmessagebox
import pandas as pd
import numpy as np
import cv2
from PIL import Image, ImageTk

from general_image_canvas import GeneralImageCanvas
from keypoint_properties import KeypointProperties
from change_central_keypoint import ChangeCentralKeypoint
from change_order_keypoints import ChangeOrderKeypoints

#%%

class SkeletonCanvas(GeneralImageCanvas):
    """
    SkeletonCanvas regulates all modifications to the skeleton
    """
    def __init__(self,master, **kwargs):
        super().__init__(master, **kwargs)

        self.skeleton = master.skeleton
        self.settings = master.settings
        self.skeleton_name = ""
        self._image_photoimage = None
        self.keypoint_index = None
        self.current_keypoint_coordinates_memory = None
        self.image_inter_scale = 1.0 #scale of self.image_inter
        self.image_inter = None #intermediary image matrix
        #basic modifications to self.image are done once and then stored
        #in self.image_inter to speed up the code
        self.image_shown = None #matrix with shown image
        self.keypoint_reactivated = False
        self.retained_keypoints = [] #indices of retained keypoints
        self.currently_saved = True
        self.critical_changes = False
        #critical changes require modifications of all .csv files with annotations

        self.bind("<Button-1>",
                  self.button_1)
        self.bind("<Double-Button-1>",
                  lambda event: self.double_button_1())
        self.bind("<B1-Motion>",
                  self.mouse_movement_b1)
        self.bind("<Button-3>",
                  lambda event: self.button_3())

    def load_skeleton(self):
        """
        Import skeleton and load annotations (if available)
        """

        #import image
        os.chdir(self.wdir)
        image = cv2.imread(self.skeleton_name)
        self.skeleton.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        #also store a copy in this class
        self.image = self.skeleton.image

        #Load annotations
        json_file = open("project\\skeleton.json")
        skeleton = json.load(json_file)
        json_file.close()

        #test = json.load(json_file)

        keypoints = []
        coordinates = []
        parent = []
        color = []
        annotation_order = []

        for i in skeleton:
            keypoints.append(skeleton[i]["name"])
            coordinates.append(skeleton[i]["coordinates"])
            parent.append(skeleton[i]["parent"])
            color.append(skeleton[i]["color"])
            annotation_order.append(skeleton[i]["annotation_order"])

        coordinates = np.array(coordinates)
        parent = np.array(parent).astype(int)

        #construct functional annotation order
        func_annotation_order = [0 for _ in annotation_order] #functional annotation order

        for i, pos in enumerate(annotation_order):
            func_annotation_order[pos] = i

        self.skeleton.keypoints = keypoints
        self.skeleton.coordinates = coordinates
        self.skeleton.parent = parent
        self.skeleton.color = color
        self.skeleton.annotation_order = annotation_order
        self.skeleton.func_annotation_order = func_annotation_order

        self.retained_keypoints = [i for i, _ in enumerate(self.skeleton.keypoints)]
        #indices of retained keypoints
        
        #Set initial zoom level
        self.reset_zoom_level()

        self.update_image(mode=0)

    def update_image(self, mode=0):
        """
        Update the image

        Parameters
        ----------
        mode : Int, optional
            0 : the image is constructed from scratch\n
            1 : the code starts from the rescaled image (without any points or
            lines related to the skeleton).
            2 : the code starts from the image with the skeleton drawn and highlights
            The currently active keypoint category (when application is in
            annotation_mode)

            The default is 0
        """
        #Check if there is a skeleton loaded
        if self.skeleton.image is None:
            return

        #get scale and intercepts
        s = self.zoom_level
        dx = self.zoom_delta_x
        dy = self.zoom_delta_y

        #actions which should only be executed if image has to be updated from scratch
        if (mode == 0) or\
            (self.image_inter_scale != s):
            #resize skeleton
            skeleton_height, skeleton_width = self.skeleton.image.shape[:2]
            self.image_inter = cv2.resize(self.skeleton.image,
                                          dsize=(int(skeleton_width * s),
                                                 int(skeleton_height * s)))
            self.image_inter_scale = s
        
        if mode in [0, 1]:
            
            self.image_inter_1 = self.image_inter.copy()
            
            #draw lines
            skeleton = self.skeleton
            for i, _ in enumerate(skeleton.keypoints):
                end_point = skeleton.coordinates[i]
                parent = skeleton.parent[i]
                if parent != -1:
                    #draw line from parent to child in color of parent
                    start_point = skeleton.coordinates[parent]
                    color = skeleton.color[i]
    
                    start_point = tuple((start_point * s).astype(int))
                    end_point = tuple((end_point * s).astype(int))
    
                    self.image_inter_1 = cv2.line(self.image_inter_1,
                                                   start_point,
                                                   end_point,
                                                   color=color,
                                                   thickness=self.settings.linewidth)
    
            #draw points
            for i, _ in enumerate(skeleton.keypoints):
                coordinates = skeleton.coordinates[i]
                [x, y] = (coordinates * s).round().astype(int)
                color = skeleton.color[i]
    
                self.image_inter_1 = cv2.circle(self.image_inter_1,
                                         (x, y),
                                         radius=self.settings.point_size_skeleton,
                                         color=color,
                                         thickness=-1)
    
            #draw circle around active point
            if self.keypoint_reactivated:
                coordinates = self.skeleton.coordinates[self.keypoint_index]
                [x, y] = (coordinates * s).round().astype(int)
                color = self.skeleton.color[self.keypoint_index]
    
                self.image_inter_1 = cv2.circle(self.image_inter_1,
                                         (x, y),
                                         radius=self.settings.circle_radius,
                                         color=color,
                                         thickness=self.settings.linewidth)
        
        #action which should always be performed
        image_shown = self.image_inter_1.copy()
        
        if (mode in [0, 1, 2]) and\
            (self.master.mode == 0) and\
            (self.settings.highlight_skeleton_keypoint):
            #draw circle around active keypoint category
            annotations = self.master.annotations
            
            coordinates = self.skeleton.coordinates[annotations.keypoint_index]
            [x, y] = (coordinates * s).round().astype(int)
            color = self.skeleton.color[annotations.keypoint_index]

            image_shown = cv2.circle(image_shown,
                                     (x, y),
                                     radius=self.settings.circle_radius,
                                     color=color,
                                     thickness=self.settings.linewidth)
            

        #slice image_shown so slice fits in self.skeleton_canvas
        uw = self.winfo_width()
        uh = self.winfo_height()
        if (image_shown.shape[1] > uw) or\
            (image_shown.shape[0] > uh):
            image_shown = image_shown[dy : dy + uh,
                                      dx: dx + uw,
                                      :]

        #show image
        image_shown = Image.fromarray(image_shown)
        image_shown = ImageTk.PhotoImage(image_shown)

        self.itemconfigure(self.image_photoimage, image=image_shown)
        self._image_photoimage = image_shown

    def new_keypoint(self, event):
        """
        Add a new keypoint to the skeleton

        Parameters
        ----------
        event : tkinter.Event
            ButtonPress event
        """
        #get coordinates
        x, y = self.get_image_coordinates(event)

        #set keypoint properties
        KeypointProperties(self,
                           coordinates=[x, y])

        #update state booleans
        #self.currently_saved is updated by KeypointProperties
        self.critical_changes = True

    def move_current_keypoint(self, event):
        """
        Executive method to move a keypoint

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        
        #update mouse position
        self.mouse_x = event.x
        self.mouse_y = event.y

        #get coordinates
        x, y = self.get_image_coordinates(event)

        if (x <= self.image.shape[1]) and\
            (y <= self.image.shape[0]):
            self.skeleton.coordinates[self.keypoint_index, :] = [x, y]

        #update status booleans
        self.currently_saved = False

        #update image
        self.update_image(mode=1)

    def button_1(self, event):
        """
        Decisive method to add or activate a keypoint

        Parameters
        ----------
        event : tkinter.Event
            ButtonPress event
        """
        
        if self.master.mode != 1:
            #modifying the skeleton is only allowed in skeleton mode
            return
                
        #get scale        
        s = self.zoom_level

        #get coordinates
        x, y = self.get_image_coordinates(event)
        location = np.array([x, y])
        
        #check if no point was re-activated
        critical_distance = 10
        if len(self.skeleton.keypoints) > 0:
            distance = np.sqrt(np.sum((self.skeleton.coordinates - location)**2, axis=1))
            if np.min(distance) < critical_distance/s:
                self.keypoint_reactivated = True
                self.keypoint_index = np.nanargmin(distance)
                #if a keypoint is double clicked, first self.button_1 is executed
                #end ony thereafter self.double_button_1 is executed. To prevent
                #this would lead to a movement of the activated keypoint, a
                #keypoint coordinate memory is created
                self.current_keypoint_coordinates_memory = \
                    self.skeleton.coordinates[self.keypoint_index].copy()
                    
                #update image
                self.update_image(mode=1)
                return

        #check if a new keypoint shoud be created
        if not self.keypoint_reactivated:
            #check if there was clicked within the image
            if (self.image is not None) and\
                (x <= self.image.shape[1]) and\
                (y <= self.image.shape[0]):
                self.new_keypoint(event)                
        
        else: #self.keypoint_reactivated:
            #if a keypoint was activated, deactivate it
            self.keypoint_reactivated = False

        #update image
        self.update_image(mode=1)

    def double_button_1(self):
        """
        Change the properties of a keypoint
        """
        
        if self.master.mode != 1:
            #modifying the skeleton is only allowed in skeleton mode
            return
        
        #check if a point was re-activated
        if self.keypoint_reactivated:
            #clear all possible position changes due to self.move_current_keypoint
            self.skeleton.coordinates[self.keypoint_index] = \
                self.current_keypoint_coordinates_memory
            #update image so keypoint has again it's original position
            self.update_image(mode=1)

            #invoke KeypointProperties
            KeypointProperties(self,
                               index=self.keypoint_index)

            #deactivate keypoint and update image
            self.keypoint_reactivated = False
            self.update_image(mode=1)

    def save(self):
        """
        Decisive method to save skeleton
        """
        #check if a project is loaded
        if self.wdir is None:
            return

        #check if the skeleton has a correct hierarchy
        if not self.skeleton.check_hierarchy():
            message = "The skeleton isn't hierarchical. Not all keypoints " +\
                      "could be traced down to the central keypoint."
            tkmessagebox.showerror("Skeleton hierarchy",
                                   message=message)
            return

        if not self.critical_changes:
            #no critical changes were made
            self.save_skeleton()
        else: #self.critical_changes:
            #there were critical changes made
            message = "Do you want to configure the whole project to the new " +\
                       "skeleton architecture? \nAll data of removed keypoints " +\
                       "will be lost."
            answer = tkmessagebox.askyesnocancel('Save skeleton',
                                                 message)

            if answer is None:
                #do nothing
                return

            if answer:
                #save skeleton and reconfigure whole project
                self.save_skeleton()
                self.reconfigure_project()
                
                #reload image and annotation data to handle added and/or deleted
                #keypoints
                self.master.annotation_canvas.reload_image()
            elif not answer:
                #reload original skeleton
                self.load_skeleton()

    def save_skeleton(self):
        """
        Executive method to save skeleton
        """

        #construct dictionary
        skeleton_dict = {}

        for i, _ in enumerate(self.skeleton.keypoints):
            keypoint_dict = {}
            keypoint_dict["name"] = self.skeleton.keypoints[i]
            keypoint_dict["parent"] = self.skeleton.parent[i].item()
            keypoint_dict["coordinates"] = [j.item() for j in self.skeleton.coordinates[i]]
            keypoint_dict["color"] = self.skeleton.color[i]
            keypoint_dict["annotation_order"] = self.skeleton.annotation_order[i]
            #.item() converts numpy datatypes to standard Python datatypes

            skeleton_dict[str(i)] = keypoint_dict

        #save dictionary in .json file
        file = open("project\\skeleton.json", "w")
        json.dump(skeleton_dict,
                  file,
                  indent=4)
        file.close()

        #update save booleans
        self.keypoint_reactivated = False
        self.currently_saved = True

        #update image
        self.update_image(mode=1)

    def reconfigure_project(self):
        """
        Configure all annotation files (.csv) in the project to the changes made
        at the skeleton
        """

        #define which columns of the annotation files should be retained
        retained_columns = []
        for i in self.retained_keypoints:
            retained_columns.append(2 * i)
            retained_columns.append(2 * i + 1)

        #calculate number of added keypoints
        extra_keypoints = len(self.skeleton.keypoints) - len(self.retained_keypoints)

        #list all files in directory
        files_list = os.listdir()

        #loop over all files, if a .csv file is found with an according .png or
        #.jpg file, adapt the .csv file to the new skeleton architecture
        for file in files_list:
            if (len(file.split('.')) == 2) and\
                (file.split('.')[1] == "csv") and\
                ((file.split('.')[0] + '.png' in files_list) or\
                 (file.split('.')[0] + '.jpg' in files_list)):
                #file is a valid annotation file
                df = pd.read_csv(file,
                                 sep=",",
                                 header=None)

                #retain right columns
                df = df.iloc[:, retained_columns]

                #add appropriate number of extra columns
                for i in range(extra_keypoints):
                    df["extra_column_" + str(2 * i)] = np.nan
                    df["extra_column_" + str(2 * i + 1)] = np.nan

                #save modified annotations
                df.to_csv(file,
                          header=False,
                          index=False,
                          float_format='%.2f')

    def delete_keypoint(self):
        """
        Delete a keypoint.

        Keypoints may only be deleted if they have no children
        """
        #check if a project is loaded
        if self.wdir is None:
            return

        if self.keypoint_index in self.skeleton.parent:
            #only keypoints without children may be deleted
            message = "Only keypoints without children can be deleted"
            tkmessagebox.showerror(title="Delete keypoint",
                                   message=message)
            #clear all possible position changes due to self.move_current_keypoint
            self.skeleton.coordinates[self.keypoint_index] = \
                self.current_keypoint_coordinates_memory
            #deactivate keypoint
            self.keypoint_reactivated = False
            #update image
            self.update_image(mode=1)
        else:
            #the keypoint which one wants to delete has no children and may
            #thus be deleted
            self.critical_changes = True

            #update retained keypoints
            if self.keypoint_index in self.retained_keypoints:
                #if a keypoint was added and deleted again during the same
                #session, nothing has to be done
                del self.retained_keypoints[self.keypoint_index]

            #update skeleton
            del self.skeleton.keypoints[self.keypoint_index]
            self.skeleton.coordinates = np.delete(self.skeleton.coordinates,
                                                  self.keypoint_index,
                                                  axis=0)
            self.skeleton.parent = np.delete(self.skeleton.parent,
                                             self.keypoint_index)
            del self.skeleton.color[self.keypoint_index]

            #update annotation order
            annotation_pos = self.skeleton.annotation_order[self.keypoint_index]
            del self.skeleton.annotation_order[self.keypoint_index]

            for i, pos in enumerate(self.skeleton.annotation_order):
                if pos > annotation_pos:
                    self.skeleton.annotation_order[i] -= 1

            #update functional annotation order
            annotation_order = self.skeleton.annotation_order
            func_annotation_order = [0 for _ in annotation_order]

            for i, pos in enumerate(annotation_order):
                func_annotation_order[pos] = i

            self.skeleton.func_annotation_order = func_annotation_order

            #update state booleans
            self.keypoint_reactivated = False
            self.currently_saved = False

            #update image
            self.update_image(mode=1)

    def mouse_movement_b1(self, event):
        """
        Decisive method to move a keypoint

        If a keypoint is reactivated, and the mouse is moved while the left
        button of the mouse is still pressed, the keypoint moves together
        with the mouse

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        if self.keypoint_reactivated:
            self.move_current_keypoint(event)

    def change_central_keypoint(self):
        """
        Change the central/dominant keypoint

        This method invokes the ChangeCentralKeypoint class, which allows to
        change the central/dominant keypoint. Before this class is invoked,
        there's first checked if the skeleton has a valid hierarchy, if this is
        not the case, an error message is raised.
        """
        #check if a project is loaded
        if self.wdir is None:
            return
        
        #check if current hierarchy is valid
        if not self.skeleton.check_hierarchy():
            message = "The skeleton isn't hierarchical. Not all keypoints " +\
                      "could be traced down to the current central keypoint."
            tkmessagebox.showerror("Skeleton hierarchy",
                                   message)
            return

        #current hierarchy is valid
        ChangeCentralKeypoint(master=self)
        self.update_image(mode=1)

    def prepare_for_annotation_mode(self):
        """
        Prepare the skeleton canvas to switch from skeleton mode to annotation mode\n
        If one want to switch the mode from skeleton mode to annotation mode,
        this method checks if there are unsaved changes to the skeleton. If this
        is the case, the user is asked if the changes should be saved or not.
        """
        #check if the current changes in self.skeleton should be saved
        if not self.currently_saved:
            #there are currently unsaved changes in the skeleton
            message = "Do you want to save the changes you made to the skeleton?"
            answer = tkmessagebox.askyesnocancel("Save modifications",
                                                 message)
            if answer is True:
                #Save changes
                self.save()
                
            elif answer is False:
                #re-import original skeleton
                self.load_skeleton()
                self.currently_saved = True
            else:#answer is None:
                return False
        return True

    def button_3(self):
        """
        Deactivate (if possible) the currently activated keypoint

        If a keypoint is activated, pressing the right button of the mouse
        deactivates the currently activated keypoint
        """
        if self.keypoint_reactivated:
            self.keypoint_reactivated = False
            self.update_image(mode=1)

    def change_order_keypoints(self):
        """
        Change the order in which the keypoints are annotated
        """
        #check if a project is loaded
        if self.wdir is None:
            return

        if len(self.skeleton.keypoints) < 2:
            tk.messagebox.showerror("Error",
                                    "The skeleton needs at least two keypoints" +
                                    " before an annotation order can be defined")
        else:
            ChangeOrderKeypoints(master=self)
            
    def get_image_coordinates(self, event):
        """
        Get the image coordinates. The image coordinates are calculated by
        correcting the event coordinates for translation and scale used during
        visualisation
        
        Parameters
        ----------
        event : tkinter.Event
            Motion event
    
        Returns
        -------
        x : float
            x coordinate (horizontal axis, origin=left side)
        y : float
            y coordinate (vertical axis, origin=top)
    
        """
        #get scale of image        
        s = self.zoom_level
        
        #get x and y coordinate of event
        x = (event.x + self.zoom_delta_x - self.bd) / s
        y = (event.y + self.zoom_delta_y - self.bd) / s
        
        #limit coordinates to size image
        x = max(min(x, self.skeleton.image.shape[1] - 1), 0)
        y = max(min(y, self.skeleton.image.shape[0] - 1), 0)
        
        return (x, y)
                